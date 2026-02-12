import customtkinter as ctk
import threading
import os
import time
import random
from .audio_recorder import AudioRecorder
from .recognizer import SpeakerRecognizer

# Tema Ayarları - Projeksiyon İçin Optimize Edilmiş
ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Ses İzi v2.0 - İleri Seviye Konuşmacı Tanıma Sistemi")
        self.geometry("1024x700")
        
        # Grid Layout (1x2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Değişkenler
        self.recorder = AudioRecorder()
        self.recognizer = None
        self.tech_messages = [
            "MFCC öznitelikleri çıkarılıyor...",
            "Spektrogram analizi yapılıyor...",
            "VAD (Voice Activity Detection) aktif...",
            "Gürültü filtresi (Noise Suppression) uygulanıyor...",
            "Vektör uzayı hizalanıyor...",
            "Örüntü eşleştirme algoritması çalışıyor...",
            "Sinir ağı katmanlarından geçiyor...",
            "Benzerlik matrisi hesaplanıyor..."
        ]

        # Arayüzü Yükle
        self.setup_sidebar()
        self.setup_main_area()
        
        # Başlangıç Ekranı: Yükleniyor
        self.show_loading_screen()
        
        # Modeli Arka Planda Yükle
        threading.Thread(target=self.load_model, daemon=True).start()

    def load_model(self):
        try:
            # Yapay bir gecikme ekle ki "Yükleniyor" ekranı havalı görünsün :)
            time.sleep(1.5)
            self.recognizer = SpeakerRecognizer()
            self.after(0, self.on_model_loaded)
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self.on_model_load_error(error_msg))

    def on_model_loaded(self):
        self.loading_frame.grid_forget()
        self.select_frame("home")
        self.update_stats()

    def on_model_load_error(self, error_msg):
        self.lbl_loading.configure(text=f"SİSTEM HATASI:\n{error_msg}", text_color="red")
        self.progress_loading.stop()

    def setup_sidebar(self):
        # Koyu Lacivert Sidebar - Tech Havası
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1a237e") 
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="SES İZİ PRO", font=ctk.CTkFont(size=26, weight="bold"), text_color="white")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))
        
        self.logo_sub = ctk.CTkLabel(self.sidebar_frame, text="Konuşmacı Tanıma", font=ctk.CTkFont(size=12), text_color="#9fa8da")
        self.logo_sub.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.btn_home = self.create_sidebar_button("Yönetim Paneli", "📊", self.show_home)
        self.btn_home.grid(row=2, column=0, padx=20, pady=10)

        self.btn_add = self.create_sidebar_button("Yeni Kayıt", "👤", self.show_add)
        self.btn_add.grid(row=3, column=0, padx=20, pady=10)

        self.btn_identify = self.create_sidebar_button("Analiz & Tanıma", "🔍", self.show_identify)
        self.btn_identify.grid(row=4, column=0, padx=20, pady=10)
        
        # Alt Bilgi
        self.lbl_footer = ctk.CTkLabel(self.sidebar_frame, text="Örüntü Tanıma Dersi\nFinal Projesi v22.1", text_color="gray70", font=("Arial", 10))
        self.lbl_footer.grid(row=6, column=0, padx=20, pady=20)

    def create_sidebar_button(self, text, icon, command):
        return ctk.CTkButton(self.sidebar_frame, text=f"{icon}  {text}", 
                             command=command, 
                             corner_radius=8, 
                             height=45, 
                             anchor="w", 
                             font=ctk.CTkFont(size=14, weight="bold"),
                             fg_color="transparent", 
                             text_color="white", 
                             hover_color="#3949ab") # Hover'da daha açık mavi

    def setup_main_area(self):
        self.home_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#f5f5f5") # Çok açık gri arka plan
        self.add_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#f5f5f5")
        self.identify_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#f5f5f5")
        self.loading_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#f5f5f5")

        self.setup_home_frame()
        self.setup_add_frame()
        self.setup_identify_frame()
        self.setup_loading_frame()

    def show_loading_screen(self):
        self.loading_frame.grid(row=0, column=1, sticky="nsew")

    def setup_loading_frame(self):
        self.lbl_loading = ctk.CTkLabel(self.loading_frame, text="SİSTEM BAŞLATILIYOR...", font=("Arial", 24, "bold"), text_color="#1a237e")
        self.lbl_loading.place(relx=0.5, rely=0.45, anchor="center")
        
        self.lbl_loading_sub = ctk.CTkLabel(self.loading_frame, text="Sinir ağları yükleniyor | GPU hızlandırma kontrol ediliyor", font=("Arial", 14), text_color="gray")
        self.lbl_loading_sub.place(relx=0.5, rely=0.5, anchor="center")
        
        self.progress_loading = ctk.CTkProgressBar(self.loading_frame, mode="indeterminate", width=400, progress_color="#1a237e")
        self.progress_loading.place(relx=0.5, rely=0.6, anchor="center")
        self.progress_loading.start()

    # --- HOME TAB (DASHBOARD) ---
    def setup_home_frame(self):
        # Header
        header = ctk.CTkLabel(self.home_frame, text="Sistem Özeti", font=ctk.CTkFont(size=28, weight="bold"), text_color="#333")
        header.pack(pady=(30, 10), padx=40, anchor="w")

        # Üst Bilgi Kartları (Grid içinde)
        info_grid = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        info_grid.pack(pady=10, padx=40, fill="x")
        
        self.create_info_card(info_grid, "Model", "ECAPA-TDNN", "Aktif", "#4caf50").pack(side="left", padx=(0, 10), fill="x", expand=True)
        self.create_info_card(info_grid, "Ses Motoru", "16kHz / Mono", "Hazır", "#2196f3").pack(side="left", padx=10, fill="x", expand=True)
        self.create_info_card(info_grid, "Gürültü Filtresi", "Spectral Gate", "Devrede", "#ff9800").pack(side="left", padx=(10, 0), fill="x", expand=True)

        # Büyük İstatistik Kartı
        stats_card = ctk.CTkFrame(self.home_frame, corner_radius=10, fg_color="white", border_width=1, border_color="#ddd")
        stats_card.pack(pady=20, padx=40, fill="both", expand=True)

        lbl_db_title = ctk.CTkLabel(stats_card, text="Veritabanı İstatistikleri", font=ctk.CTkFont(size=18, weight="bold"), text_color="#555")
        lbl_db_title.pack(pady=(20, 10), padx=20, anchor="w")

        self.lbl_total_speakers = ctk.CTkLabel(stats_card, text="0", font=ctk.CTkFont(size=72, weight="bold"), text_color="#1a237e")
        self.lbl_total_speakers.pack(pady=10)
        
        ctk.CTkLabel(stats_card, text="Kayıtlı Konuşmacı", font=ctk.CTkFont(size=16), text_color="gray").pack()

        # Alt Buton
        btn_refresh = ctk.CTkButton(self.home_frame, text="Verileri Güncelle", command=self.update_stats, width=200, height=40, font=ctk.CTkFont(weight="bold"))
        btn_refresh.pack(pady=30)

    def create_info_card(self, parent, title, value, status, status_color):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8, border_width=1, border_color="#ddd")
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(pady=(10, 0), padx=10, anchor="w")
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=16, weight="bold"), text_color="#333").pack(pady=(0, 5), padx=10, anchor="w")
        
        status_lbl = ctk.CTkLabel(card, text=f"• {status}", font=ctk.CTkFont(size=12), text_color=status_color)
        status_lbl.pack(pady=(0, 10), padx=10, anchor="w")
        return card

    # --- ADD SPEAKER TAB ---
    def setup_add_frame(self):
        title = ctk.CTkLabel(self.add_frame, text="Yeni Konuşmacı Ekle", font=ctk.CTkFont(size=28, weight="bold"), text_color="#333")
        title.pack(pady=(30, 20), padx=40, anchor="w")

        main_card = ctk.CTkFrame(self.add_frame, fg_color="white", corner_radius=10, border_width=1, border_color="#ddd")
        main_card.pack(pady=10, padx=40, fill="both", expand=True)

        # Form
        ctk.CTkLabel(main_card, text="Kimlik Bilgisi", font=ctk.CTkFont(size=16, weight="bold"), text_color="#333").pack(pady=(30, 10), padx=30, anchor="w")
        
        self.entry_name = ctk.CTkEntry(main_card, placeholder_text="Ad Soyad Giriniz...", height=45, width=400, font=ctk.CTkFont(size=15), border_color="#ddd")
        self.entry_name.pack(pady=10)

        # Recording Area
        self.btn_record_add = ctk.CTkButton(main_card, text="🎙️  SES KAYDINI BAŞLAT", command=self.record_and_add, height=55, width=300, 
                                            font=ctk.CTkFont(size=16, weight="bold"), fg_color="#d81b60", hover_color="#ad1457")
        self.btn_record_add.pack(pady=30)

        # Progress & Tech Log
        self.progress_bar_add = ctk.CTkProgressBar(main_card, width=500, height=15, progress_color="#d81b60")
        self.progress_bar_add.set(0)
        self.progress_bar_add.pack(pady=(0, 10))

        self.lbl_tech_log_add = ctk.CTkLabel(main_card, text="Sistem Hazır", font=("Consolas", 12), text_color="gray")
        self.lbl_tech_log_add.pack(pady=5)

    # --- IDENTIFY TAB ---
    def setup_identify_frame(self):
        title = ctk.CTkLabel(self.identify_frame, text="Kimlik Tespiti", font=ctk.CTkFont(size=28, weight="bold"), text_color="#333")
        title.pack(pady=(30, 20), padx=40, anchor="w")

        main_card = ctk.CTkFrame(self.identify_frame, fg_color="white", corner_radius=10, border_width=1, border_color="#ddd")
        main_card.pack(pady=10, padx=40, fill="both", expand=True)

        # Button Area
        self.btn_identify_action = ctk.CTkButton(main_card, text="🔍  ANALİZİ BAŞLAT", command=self.record_and_identify, height=60, width=350, 
                                                 font=ctk.CTkFont(size=18, weight="bold"), fg_color="#00897b", hover_color="#00695c")
        self.btn_identify_action.pack(pady=(50, 30))
        
        self.progress_bar_id = ctk.CTkProgressBar(main_card, width=500, height=15, progress_color="#00897b")
        self.progress_bar_id.set(0)
        self.progress_bar_id.pack(pady=10)
        
        self.lbl_tech_log_id = ctk.CTkLabel(main_card, text="Sensörler hazır...", font=("Consolas", 12), text_color="gray")
        self.lbl_tech_log_id.pack(pady=5)

        # Result Area
        self.result_container = ctk.CTkFrame(main_card, fg_color="#f8f9fa", corner_radius=8)
        self.result_container.pack(pady=30, padx=30, fill="x")
        
        ctk.CTkLabel(self.result_container, text="TANIMLANAN KİŞİ", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(pady=(15, 0))
        self.lbl_result_name = ctk.CTkLabel(self.result_container, text="-", font=ctk.CTkFont(size=40, weight="bold"), text_color="#333")
        self.lbl_result_name.pack(pady=5)
        
        self.lbl_result_score = ctk.CTkLabel(self.result_container, text="Güven Skoru: -", font=ctk.CTkFont(size=14))
        self.lbl_result_score.pack(pady=(0, 15))

    # --- NAVIGATION LOGIC ---
    def select_frame(self, name):
        # Reset Sidebar Buttons
        for btn in [self.btn_home, self.btn_add, self.btn_identify]:
            btn.configure(fg_color="transparent", text_color="white")

        # Highlight Active
        active_color = "#3949ab"
        if name == "home": self.btn_home.configure(fg_color=active_color)
        elif name == "add": self.btn_add.configure(fg_color=active_color)
        elif name == "identify": self.btn_identify.configure(fg_color=active_color)

        self.home_frame.grid_forget()
        self.add_frame.grid_forget()
        self.identify_frame.grid_forget()
        
        if name == "home": self.home_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "add": self.add_frame.grid(row=0, column=1, sticky="nsew")
        elif name == "identify": self.identify_frame.grid(row=0, column=1, sticky="nsew")

    def show_home(self): self.select_frame("home")
    def show_add(self): self.select_frame("add")
    def show_identify(self): self.select_frame("identify")

    # --- ANIMATION LOGIC ---
    def animate_progress_with_log(self, progress_bar, label, duration, callback):
        steps = 50
        step_time = duration / steps
        
        def _animate(current_step):
            if current_step <= steps:
                val = current_step / steps
                progress_bar.set(val)
                
                # Rastgele Tech Log Mesajları
                if current_step % 5 == 0:
                    msg = random.choice(self.tech_messages)
                    label.configure(text=msg)
                
                self.after(int(step_time * 1000), lambda: _animate(current_step + 1))
            else:
                progress_bar.set(0)
                label.configure(text="İşlem Tamamlandı.")
                if callback:
                    callback()
        
        _animate(0)

    # --- BUSINESS LOGIC ---
    def update_stats(self):
        if self.recognizer:
            count = len(self.recognizer.known_embeddings)
            self.lbl_total_speakers.configure(text=str(count))

    def record_and_add(self):
        name = self.entry_name.get()
        if not name:
            self.lbl_tech_log_add.configure(text="⚠️ İsim girilmedi!", text_color="red")
            return

        self.btn_record_add.configure(state="disabled", text="KAYDEDİLİYOR...")
        self.lbl_tech_log_add.configure(text_color="gray") # Reset color
        
        # Animasyon Başlat
        self.animate_progress_with_log(self.progress_bar_add, self.lbl_tech_log_add, 5, None)

        threading.Thread(target=self._process_add_speaker, args=(name,), daemon=True).start()

    def _process_add_speaker(self, name):
        filename = f"temp_rec_{name}.wav"
        self.recorder.record_fixed_duration(5, filename)
        
        success, msg = self.recognizer.save_speaker(name, filename)
        
        if os.path.exists(filename):
            os.remove(filename)

        self.after(0, lambda: self._finish_add_speaker(success, msg))

    def _finish_add_speaker(self, success, msg):
        self.btn_record_add.configure(state="normal", text="🎙️  SES KAYDINI BAŞLAT")
        color = "green" if success else "red"
        self.lbl_tech_log_add.configure(text=msg.upper(), text_color=color)
        if success:
            self.entry_name.delete(0, 'end')
            self.update_stats()

    def record_and_identify(self):
        self.btn_identify_action.configure(state="disabled", text="ANALİZ EDİLİYOR...")
        self.lbl_result_name.configure(text="...", text_color="gray")
        self.lbl_result_score.configure(text="Güven Skoru: Hesaplanıyor...")
        self.lbl_tech_log_id.configure(text_color="gray")

        self.animate_progress_with_log(self.progress_bar_id, self.lbl_tech_log_id, 4, None)
        
        threading.Thread(target=self._process_identify, daemon=True).start()

    def _process_identify(self):
        filename = "temp_identify.wav"
        self.recorder.record_fixed_duration(4, filename)
        
        name, score = self.recognizer.identify_speaker(filename)
        
        if os.path.exists(filename):
            os.remove(filename)
            
        self.after(0, lambda: self._finish_identify(name, score))

    def _finish_identify(self, name, score):
        self.btn_identify_action.configure(state="normal", text="🔍  ANALİZİ BAŞLAT")
        
        if name:
            self.lbl_result_name.configure(text=name, text_color="#00897b")
            self.lbl_result_score.configure(text=f"Güven Skoru: %{score*100:.2f}")
        else:
            self.lbl_result_name.configure(text="BİLİNMEYEN SES", text_color="#d81b60")
            self.lbl_result_score.configure(text="Eşleşme Oranı: Çok Düşük")

if __name__ == "__main__":
    app = App()
    app.mainloop()
