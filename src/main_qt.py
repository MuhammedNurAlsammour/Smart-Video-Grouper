import os
import shutil
import glob
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QComboBox, QTextEdit, QFileDialog, QMessageBox,
                           QProgressBar, QSpinBox, QGroupBox, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

class VideoOrganizerThread(QThread):
    progress_signal = pyqtSignal(str)
    progress_value = pyqtSignal(int)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, source_path, videos_per_folder, sort_order, naming_pattern):
        super().__init__()
        self.source_path = source_path
        self.videos_per_folder = videos_per_folder
        self.sort_order = sort_order
        self.naming_pattern = naming_pattern

    def run(self):
        try:
            if not os.path.exists(self.source_path):
                self.error_signal.emit(f"İletilen yol bulunamadı: {self.source_path}")
                return

            video_extensions = ['*.mp4', '*.avi', '*.mkv', '*.mov', '*.wmv', '*.flv']
            video_files = []
            
            for ext in video_extensions:
                video_files.extend(glob.glob(os.path.join(self.source_path, ext)))
            
            if not video_files:
                self.error_signal.emit("Videolar bulunamadı")
                return
            
            self.progress_signal.emit(f"{len(video_files)} video dosyası bulundu")
            
            if self.sort_order == "Artan (Eskiden Yeniye)":
                video_files.sort(key=lambda x: os.path.getctime(x))
            else:
                video_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
            
            total_videos = len(video_files)
            processed_videos = 0
            
            folder_count = 1
            for i in range(0, total_videos, self.videos_per_folder):
                # Klasör adını belirtilen şekilde oluştur
                if self.naming_pattern == "Gün_Numara":
                    folder_name = f"Gün_{folder_count}"
                elif self.naming_pattern == "Grup_Numara":
                    folder_name = f"Grup_{folder_count}"
                elif self.naming_pattern == "Tarih":
                    # En eski videodan tarih al
                    video_date = datetime.datetime.fromtimestamp(os.path.getctime(video_files[i]))
                    folder_name = f"{video_date.strftime('%Y-%m-%d')}"
                else:
                    folder_name = f"Klasör_{folder_count}"
                
                folder_path = os.path.join(self.source_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                
                for video in video_files[i:i+self.videos_per_folder]:
                    video_name = os.path.basename(video)
                    new_path = os.path.join(folder_path, video_name)
                    shutil.move(video, new_path)
                    processed_videos += 1
                    progress_percent = int((processed_videos / total_videos) * 100)
                    self.progress_value.emit(progress_percent)
                    self.progress_signal.emit(f"{video_name} {folder_name} klasörüne taşındı")
                
                folder_count += 1
            
            self.progress_signal.emit(f"{total_videos} video {folder_count-1} klasöre taşındı")
            self.finished_signal.emit()
            
        except Exception as e:
            self.error_signal.emit(f"Hata: {str(e)}")

class VideoOrganizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Akıllı Video Düzenleyici")
        self.setGeometry(100, 100, 900, 700)
        self.setup_ui()

    def setup_ui(self):
        # Stil uygulama
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
            QLineEdit, QSpinBox, QComboBox {
                padding: 8px;
                border: 1px solid #34495e;
                border-radius: 4px;
                background-color: #34495e;
            }
            QTextEdit {
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 8px;
                background-color: #34495e;
            }
            QLabel {
                font-size: 14px;
                color: #ecf0f1;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding-top: 15px;
                margin-top: 10px;
                color: #34495e;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            QProgressBar {
                border: 1px solid #34495e;
                border-radius: 4px;
                text-align: center;
                height: 20px;
                background-color: #34495e;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                width: 10px;
            }
        """)

        # Uygun arapça yazı tipi
        app_font = QFont("Arial", 10)
        self.setFont(app_font)

        # Ana pencere ve düzenleme
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Dosya ayarları grubu
        file_group = QGroupBox("Dosya Ayarları")
        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(10)

        # Yol seçimi
        path_layout = QHBoxLayout()
        path_label = QLabel("Video Yolu:")
        self.path_entry = QLineEdit()
        self.path_entry.setPlaceholderText("Video klasörünü seçin...")
        browse_btn = QPushButton("Gözat")
        browse_btn.setIcon(QIcon.fromTheme("folder-open"))
        browse_btn.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_entry)
        path_layout.addWidget(browse_btn)
        file_layout.addLayout(path_layout)

        # Düzenleme ayarları grubu
        org_group = QGroupBox("Düzenleme Ayarları")
        org_layout = QVBoxLayout(org_group)
        org_layout.setSpacing(10)

        # Videoların sayısı
        count_layout = QHBoxLayout()
        count_label = QLabel("Her klasördeki video sayısı:")
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(3)
        self.count_spin.setFixedWidth(100)
        
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.count_spin)
        count_layout.addStretch()
        org_layout.addLayout(count_layout)

        # Sıralama seçimi
        sort_layout = QHBoxLayout()
        sort_label = QLabel("Sıralama:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Artan (Eskiden Yeniye)", "Azalan (Yeniden Eskiye)"])
        self.sort_combo.setFixedWidth(200)
        
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)
        sort_layout.addStretch()
        org_layout.addLayout(sort_layout)

        # Klasör isimlendirme şekli
        naming_layout = QHBoxLayout()
        naming_label = QLabel("Klasör İsimlendirme:")
        self.naming_combo = QComboBox()
        self.naming_combo.addItems(["Gün_Numara", "Grup_Numara", "Tarih"])
        self.naming_combo.setFixedWidth(200)
        
        naming_layout.addWidget(naming_label)
        naming_layout.addWidget(self.naming_combo)
        naming_layout.addStretch()
        org_layout.addLayout(naming_layout)

        # Başlat düğmesi
        start_layout = QHBoxLayout()
        self.start_btn = QPushButton("Düzenlemeyi Başlat")
        self.start_btn.setFixedHeight(40)
        self.start_btn.clicked.connect(self.start_organizing)
        
        start_layout.addStretch()
        start_layout.addWidget(self.start_btn)
        start_layout.addStretch()

        # İlerleme çubuğu
        progress_layout = QVBoxLayout()
        progress_label = QLabel("İlerleme:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)

        # Sonuçlar grubu
        results_group = QGroupBox("İşlem Kaydı")
        results_layout = QVBoxLayout(results_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.clear_log_btn = QPushButton("Kaydı Temizle")
        self.clear_log_btn.clicked.connect(self.clear_log)
        
        results_layout.addWidget(self.result_text)
        results_layout.addWidget(self.clear_log_btn)

        # Tüm grupları ana düzenlemeye ekle
        main_layout.addWidget(file_group)
        main_layout.addWidget(org_group)
        main_layout.addLayout(start_layout)
        main_layout.addLayout(progress_layout)
        main_layout.addWidget(results_group)

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if folder_path:
            self.path_entry.setText(folder_path)

    def update_result(self, message):
        self.result_text.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {message}")
        # Otomatik kaydırma
        scrollbar = self.result_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def start_organizing(self):
        source_path = self.path_entry.text()
        if not source_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir klasör seçin")
            return

        videos_per_folder = self.count_spin.value()

        self.result_text.append("=== Yeni Düzenleme İşlemi ===")
        self.start_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        self.thread = VideoOrganizerThread(
            source_path,
            videos_per_folder,
            self.sort_combo.currentText(),
            self.naming_combo.currentText()
        )
        self.thread.progress_signal.connect(self.update_result)
        self.thread.progress_value.connect(self.update_progress)
        self.thread.finished_signal.connect(self.organizing_finished)
        self.thread.error_signal.connect(self.organizing_error)
        self.thread.start()

    def organizing_finished(self):
        self.start_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Başarılı", "Videolar başarıyla düzenlendi!")

    def organizing_error(self, error_message):
        self.start_btn.setEnabled(True)
        self.update_result(f"Hata: {error_message}")
        QMessageBox.critical(self, "Hata", error_message)

    def clear_log(self):
        self.result_text.clear()

if __name__ == "__main__":
    app = QApplication([])
    window = VideoOrganizer()
    window.show()
    app.exec()