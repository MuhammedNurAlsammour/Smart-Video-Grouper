import os
import shutil
from datetime import datetime
import glob
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class VideoOrganizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Akıllı Video Düzenleyici")
        self.root.geometry("600x400")
        
        # Kullanıcı arayüzü oluşturma
        self.create_ui()
        
    def create_ui(self):
        # Yol çerçevesi
        path_frame = tk.Frame(self.root)
        path_frame.pack(pady=10)
        
        tk.Label(path_frame, text="Video Yolu:").pack(side=tk.LEFT)
        self.path_entry = tk.Entry(path_frame, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5)
        
        browse_btn = tk.Button(path_frame, text="Gözat", command=self.browse_folder)
        browse_btn.pack(side=tk.LEFT)
        
        # Video sayısı çerçevesi
        count_frame = tk.Frame(self.root)
        count_frame.pack(pady=10)
        
        tk.Label(count_frame, text="Her Klasördeki Video Sayısı:").pack(side=tk.LEFT)
        self.count_entry = tk.Entry(count_frame, width=5)
        self.count_entry.insert(0, "3")
        self.count_entry.pack(side=tk.LEFT, padx=5)
        
        # Sıralama seçenekleri çerçevesi
        sort_frame = tk.Frame(self.root)
        sort_frame.pack(pady=10)
        
        tk.Label(sort_frame, text="Sıralama:").pack(side=tk.LEFT)
        self.sort_var = tk.StringVar(value="Artan (En Eski)")
        self.sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var, state="readonly")
        self.sort_combo['values'] = ("Artan (En Eski)", "Azalan (En Yeni)")
        self.sort_combo.pack(side=tk.LEFT, padx=5)
        
        # Başlat butonu
        start_btn = tk.Button(self.root, text="Düzenlemeyi Başlat", command=self.start_organizing)
        start_btn.pack(pady=20)
        
        # Sonuç alanı
        self.result_text = tk.Text(self.root, height=10, width=60)
        self.result_text.pack(pady=10)
        
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_path)
    
    def organize_videos(self, source_path, videos_per_folder):
        try:
            # Yol kontrolü
            if not os.path.exists(source_path):
                self.update_result(f"Yol bulunamadı: {source_path}")
                return
            
            # Tüm video dosyalarını al
            video_extensions = ['*.mp4', '*.avi', '*.mkv', '*.mov']
            video_files = []
            
            for ext in video_extensions:
                video_files.extend(glob.glob(os.path.join(source_path, ext)))
            
            if not video_files:
                self.update_result("Video dosyası bulunamadı")
                return
            
            # Oluşturma tarihine göre sırala
            sort_order = self.sort_var.get()
            if sort_order == "Artan (En Eski)":
                video_files.sort(key=lambda x: os.path.getctime(x))
            else:
                video_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
            
            # Klasörleri oluştur ve videoları düzenle
            folder_count = 1
            for i in range(0, len(video_files), videos_per_folder):
                # Yeni klasör oluştur
                folder_name = f"Gün_{folder_count}"
                folder_path = os.path.join(source_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                
                # Videoları yeni klasöre taşı
                for video in video_files[i:i+videos_per_folder]:
                    video_name = os.path.basename(video)
                    new_path = os.path.join(folder_path, video_name)
                    shutil.move(video, new_path)
                    self.update_result(f"{video_name} {folder_name} taşındı")
                
                folder_count += 1
            
            self.update_result(f"{len(video_files)} video {folder_count-1} klasörde düzenlendi")
            messagebox.showinfo("Başarılı", "Videolar başarıyla düzenlendi!")
            
        except Exception as e:
            self.update_result(f"Hata oluştu: {str(e)}")
            messagebox.showerror("Hata", f"Düzenleme sırasında hata oluştu: {str(e)}")
    
    def update_result(self, message):
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
    
    def start_organizing(self):
        source_path = self.path_entry.get()
        try:
            videos_per_folder = int(self.count_entry.get())
            if videos_per_folder <= 0:
                messagebox.showerror("Hata", "Video sayısı sıfırdan büyük olmalıdır")
                return
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin")
            return
        
        self.result_text.delete(1.0, tk.END)
        
        thread = threading.Thread(
            target=self.organize_videos,
            args=(source_path, videos_per_folder)
        )
        thread.start()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = VideoOrganizer()
    app.run()
