import os
import sys
import time
import json
import struct
import socket
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

import mainwindow
import SendDialog
import RecvDialog

# Networking Constants
DEFAULT_PORT = 14400
CHUNK_SIZE = 64 * 1024  # 64 KB per stream read/write


def get_local_ip() -> str:
    """Detects the primary outbound local network (LAN) IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connecting to a public IP (without sending packets) picks the default LAN interface route
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def format_bytes(num_bytes: int) -> str:
    """Converts raw byte count into human-readable representation."""
    if num_bytes < 0:
        num_bytes = 0
    val = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if val < 1024.0:
            return f"{val:.1f} {unit}" if unit != "B" else f"{int(val)} B"
        val /= 1024.0
    return f"{val:.1f} PB"


def get_unique_path(directory: Path, filename: str) -> Path:
    """Generates a non-colliding destination path if filename already exists."""
    safe_name = os.path.basename(filename)
    target = directory / safe_name
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    counter = 1
    while target.exists():
        target = directory / f"{stem} ({counter}){suffix}"
        counter += 1
    return target


def send_exact(sock: socket.socket, data: bytes) -> None:
    """Sends all bytes across the socket stream reliably."""
    sock.sendall(data)


def recv_exact(sock: socket.socket, num_bytes: int) -> bytes:
    """Reads exactly num_bytes from the socket stream, handling partial chunks."""
    buffer = bytearray()
    while len(buffer) < num_bytes:
        chunk = sock.recv(min(num_bytes - len(buffer), CHUNK_SIZE))
        if not chunk:
            raise ConnectionResetError("Connection closed before all expected bytes were received")
        buffer.extend(chunk)
    return bytes(buffer)


def send_framed_json(sock: socket.socket, payload: dict) -> None:
    """Sends a JSON message preceded by a 4-byte big-endian length prefix."""
    raw = json.dumps(payload).encode("utf-8")
    header = struct.pack("!I", len(raw))
    send_exact(sock, header + raw)


def recv_framed_json(sock: socket.socket) -> dict:
    """Reads a length-prefixed JSON message from the socket stream."""
    header = recv_exact(sock, 4)
    length = struct.unpack("!I", header)[0]
    raw = recv_exact(sock, length)
    return json.loads(raw.decode("utf-8"))


class SenderWorker(QThread):
    # Use 64-bit integers (qint64) to support files larger than 2 GB without 32-bit integer overflow
    progress_changed = Signal("qint64", "qint64")  # (sent_bytes, total_bytes)
    status_changed = Signal(str)
    ip_discovered = Signal(str)
    transfer_finished = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, filepath: str, port: int = DEFAULT_PORT):
        super().__init__()
        self.filepath = filepath
        self.port = port
        self.filename = os.path.basename(filepath)
        self.filesize = os.path.getsize(filepath)
        self._is_stopped = False
        self._server_sock: Optional[socket.socket] = None
        self._client_sock: Optional[socket.socket] = None

    def stop(self):
        """Cleanly aborts the worker and closes active sockets."""
        self._is_stopped = True
        if self._client_sock:
            try:
                self._client_sock.close()
            except Exception:
                pass
        if self._server_sock:
            try:
                self._server_sock.close()
            except Exception:
                pass

    def run(self):
        local_ip = get_local_ip()
        self.ip_discovered.emit(f"{local_ip}:{self.port}")
        self.status_changed.emit(f"Waiting for receiver on {local_ip}:{self.port}...")

        try:
            self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Enable SO_REUSEADDR to prevent 'Address already in use' during quick reconnects
            self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_sock.bind(("0.0.0.0", self.port))
            self._server_sock.listen(1)
            self._server_sock.settimeout(1.0)  # Polling interval to allow graceful thread cancellation

            while not self._is_stopped:
                try:
                    self._client_sock, client_addr = self._server_sock.accept()
                    break
                except socket.timeout:
                    continue

            if self._is_stopped or not self._client_sock:
                return

            self._client_sock.settimeout(None)
            self.status_changed.emit(f"Connected to receiver ({client_addr[0]}). Sending metadata...")

            # 1. Send file metadata
            metadata = {
                "filename": self.filename,
                "filesize": self.filesize,
            }
            send_framed_json(self._client_sock, metadata)

            # 2. Wait for receiver acceptance response
            response = recv_framed_json(self._client_sock)
            if response.get("status") != "ACCEPT":
                err_msg = response.get("message", "Receiver rejected file transfer")
                self.error_occurred.emit(err_msg)
                return

            # 3. Stream file data in chunks
            self.status_changed.emit("Transferring file...")
            total_sent = 0
            last_emit = 0.0
            with open(self.filepath, "rb") as f:
                while total_sent < self.filesize and not self._is_stopped:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    send_exact(self._client_sock, chunk)
                    total_sent += len(chunk)

                    # Throttle progress emissions to ~20 Hz to avoid flooding the Qt event loop
                    now = time.time()
                    if now - last_emit >= 0.05 or total_sent == self.filesize:
                        last_emit = now
                        self.progress_changed.emit(total_sent, self.filesize)

            if not self._is_stopped:
                self.progress_changed.emit(self.filesize, self.filesize)
                self.status_changed.emit("Transfer completed successfully!")
                self.transfer_finished.emit(self.filename)

        except Exception as e:
            if not self._is_stopped:
                self.error_occurred.emit(f"Sender Error: {e}")
        finally:
            self.stop()


class ReceiverWorker(QThread):
    # Use 64-bit integers (qint64) to support files larger than 2 GB without 32-bit integer overflow
    progress_changed = Signal("qint64", "qint64")  # (recv_bytes, total_bytes)
    status_changed = Signal(str)
    file_info_received = Signal(str, "qint64")  # (filename, filesize)
    transfer_finished = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, host: str, port: int = DEFAULT_PORT, dest_dir: Optional[str] = None):
        super().__init__()
        self.host = host
        self.port = port
        self.dest_dir = Path(dest_dir) if dest_dir else Path.home() / "Downloads"
        self._is_stopped = False
        self._sock: Optional[socket.socket] = None

    def stop(self):
        """Cleanly aborts the worker and closes the receiver socket."""
        self._is_stopped = True
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass

    def run(self):
        self.status_changed.emit(f"Connecting to {self.host}:{self.port}...")
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(10.0)  # Connection timeout
            self._sock.connect((self.host, self.port))
            self._sock.settimeout(None)

            self.status_changed.emit("Connected. Receiving file metadata...")

            # 1. Receive file metadata
            metadata = recv_framed_json(self._sock)
            filename = metadata["filename"]
            filesize = metadata["filesize"]
            self.file_info_received.emit(filename, filesize)

            # Ensure destination directory exists and prepare non-colliding path
            self.dest_dir.mkdir(parents=True, exist_ok=True)
            target_path = get_unique_path(self.dest_dir, filename)

            # 2. Accept file transfer
            send_framed_json(self._sock, {"status": "ACCEPT"})

            # 3. Stream file data to disk
            self.status_changed.emit(f"Downloading {filename}...")
            total_recv = 0
            last_emit = 0.0
            with open(target_path, "wb") as f:
                while total_recv < filesize and not self._is_stopped:
                    remaining = filesize - total_recv
                    chunk_to_read = min(remaining, CHUNK_SIZE)
                    chunk = self._sock.recv(chunk_to_read)
                    if not chunk:
                        raise ConnectionResetError("Connection severed prematurely by sender")
                    f.write(chunk)
                    total_recv += len(chunk)

                    # Throttle progress emissions to ~20 Hz to avoid flooding the Qt event loop
                    now = time.time()
                    if now - last_emit >= 0.05 or total_recv == filesize:
                        last_emit = now
                        self.progress_changed.emit(total_recv, filesize)

            if not self._is_stopped:
                self.progress_changed.emit(filesize, filesize)
                self.status_changed.emit(f"Saved to: {target_path.name}")
                self.transfer_finished.emit(str(target_path))

        except Exception as e:
            if not self._is_stopped:
                self.error_occurred.emit(f"Receiver Error: {e}")
        finally:
            self.stop()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.SendButton.clicked.connect(self.openSendDiag)
        self.ui.RecvButton.clicked.connect(self.openRecvDiag)

    def openSendDiag(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Send")
        if not file_path:
            return  # User cancelled selection

        diag = SendDialogWidget(file_path, parent=self)
        diag.exec()

    def openRecvDiag(self):
        diag = RecvDialogWidget(parent=self)
        diag.exec()


class SendDialogWidget(QDialog):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.ui = SendDialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.filepath = path
        filename = os.path.basename(path)
        self.ui.FileNameEditLabel.setText(filename)
        self.ui.progressBar.setValue(0)
        self.ui.StatusLabel.setText("Initializing...")

        self.worker = SenderWorker(path, DEFAULT_PORT)
        self.worker.ip_discovered.connect(self.on_ip_discovered)
        self.worker.progress_changed.connect(self.on_progress)
        self.worker.status_changed.connect(self.on_status)
        self.worker.transfer_finished.connect(self.on_finished)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def on_ip_discovered(self, address_str: str):
        self.ui.CodeEditLabel.setText(address_str)

    def on_progress(self, sent_bytes: int, total_bytes: int):
        percent = int((sent_bytes / total_bytes) * 100) if total_bytes > 0 else 0
        self.ui.progressBar.setValue(percent)
        self.ui.StatusLabel.setText(f"{format_bytes(sent_bytes)} / {format_bytes(total_bytes)} ({percent}%)")

    def on_status(self, text: str):
        self.ui.StatusLabel.setText(text)

    def on_finished(self, filename: str):
        self.ui.progressBar.setValue(100)
        self.ui.StatusLabel.setText("Transfer completed successfully!")

    def on_error(self, error_msg: str):
        self.ui.StatusLabel.setText(f"Error: {error_msg}")
        QMessageBox.critical(self, "Transfer Error", error_msg)

    def closeEvent(self, event):
        if self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1500)
        super().closeEvent(event)


class RecvDialogWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = RecvDialog.Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.progressBar.setValue(0)
        self.ui.StatusLabel.setText("Enter Sender Address to Connect")
        self.ui.FileNameEditLabel.setText("Waiting for sender...")

        # Replace static IPEditLabel with editable input and connect button
        self.ui.IPEditLabel.hide()

        self.input_layout = QHBoxLayout()
        self.input_layout.setContentsMargins(0, 0, 0, 0)

        self.ip_input = QLineEdit(self)
        self.ip_input.setText(f"127.0.0.1:{DEFAULT_PORT}")
        self.ip_input.setPlaceholderText("Sender IP:Port (e.g. 192.168.1.5:14400)")

        self.connect_btn = QPushButton("Connect", self)
        self.connect_btn.clicked.connect(self.start_transfer)
        self.ip_input.returnPressed.connect(self.start_transfer)

        self.input_layout.addWidget(self.ip_input)
        self.input_layout.addWidget(self.connect_btn)
        self.ui.verticalLayout_3.addLayout(self.input_layout)

        self.worker: Optional[ReceiverWorker] = None

    def start_transfer(self):
        address_text = self.ip_input.text().strip()
        if not address_text:
            QMessageBox.warning(self, "Input Error", "Please enter the sender's IP address.")
            return

        if ":" in address_text:
            parts = address_text.split(":")
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Invalid port number.")
                return
        else:
            host = address_text
            port = DEFAULT_PORT

        self.ip_input.setEnabled(False)
        self.connect_btn.setEnabled(False)
        self.ui.StatusLabel.setText("Connecting...")

        self.worker = ReceiverWorker(host, port)
        self.worker.file_info_received.connect(self.on_file_info)
        self.worker.progress_changed.connect(self.on_progress)
        self.worker.status_changed.connect(self.on_status)
        self.worker.transfer_finished.connect(self.on_finished)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def on_file_info(self, filename: str, filesize: int):
        self.ui.FileNameEditLabel.setText(filename)
        self.ui.StatusLabel.setText(f"Receiving {filename} ({format_bytes(filesize)})...")

    def on_progress(self, recv_bytes: int, total_bytes: int):
        percent = int((recv_bytes / total_bytes) * 100) if total_bytes > 0 else 0
        self.ui.progressBar.setValue(percent)
        self.ui.StatusLabel.setText(f"{format_bytes(recv_bytes)} / {format_bytes(total_bytes)} ({percent}%)")

    def on_status(self, text: str):
        self.ui.StatusLabel.setText(text)

    def on_finished(self, saved_path: str):
        self.ui.progressBar.setValue(100)
        self.ui.StatusLabel.setText(f"Saved: {os.path.basename(saved_path)}")
        QMessageBox.information(self, "Download Complete", f"File saved successfully to:\n{saved_path}")

    def on_error(self, error_msg: str):
        self.ui.StatusLabel.setText(f"Error: {error_msg}")
        self.ip_input.setEnabled(True)
        self.connect_btn.setEnabled(True)
        QMessageBox.critical(self, "Transfer Error", error_msg)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1500)
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())