import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, \
    QMessageBox, QProgressDialog
from PyQt5.QtGui import QPixmap
import requests
from io import BytesIO
from zipfile import ZipFile


class ModInstaller(QWidget):
    def __init__(self):
        super().__init__()

        self.mod_folder_path = None

        self.init_ui()

    def init_ui(self):
        folder_label = QLabel('Выберите папку модов:')
        self.folder_entry = QLineEdit(self)
        browse_button = QPushButton('Обзор', self)
        browse_button.clicked.connect(self.browse_mod_folder)

        install_button = QPushButton('Установить моды', self)
        install_button.clicked.connect(self.install_mods)

        layout = QVBoxLayout()
        layout.addWidget(folder_label)
        layout.addWidget(self.folder_entry)
        layout.addWidget(browse_button)
        layout.addWidget(install_button)

        self.setLayout(layout)

    def browse_mod_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Выберите папку модов')
        if folder_path:
            self.folder_entry.setText(folder_path)
            self.mod_folder_path = folder_path

    def install_mods(self):
        if not self.mod_folder_path:
            self.show_error('Ошибка', 'Выберите папку модов')
            return

        confirmation = QMessageBox.question(self, 'Подтверждение',
                                           'Вы уверены, что хотите установить моды в выбранную папку?\n'
                                           'Папка модов будет предварительно очищена.',
                                           QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            progress_dialog = QProgressDialog("Идет установка модов...", "Отмена", 0, 100, self)
            progress_dialog.setWindowModality(2)

            self.clear_mod_folder(self.mod_folder_path)
            mod_url = "http://mods.qs-api.ru/.zip"
            self.download_mods(mod_url, self.mod_folder_path, progress_dialog)
            self.show_info('Успех', 'Моды успешно установлены!')

    def clear_mod_folder(self, folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    for sub_file_name in os.listdir(file_path):
                        sub_file_path = os.path.join(file_path, sub_file_name)
                        os.unlink(sub_file_path)
                    os.rmdir(file_path)
            except Exception as e:
                print(f"Ошибка при удалении файла/папки {file_path}: {e}")

    def download_mods(self, mod_url, folder_path, progress_dialog):
        try:
            response = requests.get(mod_url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))

            zip_path = os.path.join(folder_path, "mods.zip")
            with open(zip_path, "wb") as zip_file:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=1024):
                    downloaded_size += len(chunk)
                    zip_file.write(chunk)
                    progress = int((downloaded_size / total_size) * 100)
                    progress_dialog.setValue(progress)
                    QApplication.processEvents()

            with ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(folder_path)

            os.remove(zip_path)

        except requests.exceptions.RequestException as e:
            self.show_error('Ошибка', f"Ошибка при скачивании модов: {e}")

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message, QMessageBox.Ok)

    def show_info(self, title, message):
        QMessageBox.information(self, title, message, QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModInstaller()
    window.setWindowTitle('Менеджер модов')
    window.show()
    sys.exit(app.exec_())
