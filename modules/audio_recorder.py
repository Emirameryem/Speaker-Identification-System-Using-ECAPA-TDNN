import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time
import os

class AudioRecorder:
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.frames = []
        self.stream = None

    def start_recording(self):
        if self.recording:
            return
        self.recording = True
        self.frames = []
        self.stream = sd.InputStream(samplerate=self.sample_rate,
                                     channels=self.channels,
                                     callback=self._callback)
        self.stream.start()
        print("Kayıt başladı...")

    def stop_recording(self, output_path):
        if not self.recording:
            return
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        print("Kayıt durduruldu.")
        
        # Veriyi kaydet
        if len(self.frames) > 0:
            audio_data = np.concatenate(self.frames, axis=0)
            sf.write(output_path, audio_data, self.sample_rate)
            return output_path
        return None

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.frames.append(indata.copy())

    def record_fixed_duration(self, duration, output_path):
        """Belirli bir süre için kayıt yapar (bloklayıcı işlem)"""
        print(f"{duration} saniye kayıt yapılıyor...")
        recording = sd.rec(int(duration * self.sample_rate), 
                           samplerate=self.sample_rate, 
                           channels=self.channels)
        sd.wait()  # Kaydın bitmesini bekle
        sf.write(output_path, recording, self.sample_rate)
        print(f"Kayıt tamamlandı: {output_path}")
        return output_path
