import os
import torch
import torchaudio
from speechbrain.inference.speaker import EncoderClassifier
import numpy as np
import soundfile as sf
from pathlib import Path

class SpeakerRecognizer:
    def __init__(self, saved_model_dir="./pretrained_models", device="cpu"):
        self.device = device
        # ECAPA-TDNN modeli, konuşmacı tanıma için endüstri standardıdır
        print("Model yükleniyor... (İlk çalıştırmada indirme yapabilir)")
        self.classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir=saved_model_dir,
            run_opts={"device": self.device}
        )
        print("Model yüklendi.")
        
        # Veritabanı yolları
        self.speakers_dir = Path("data/speakers")
        self.embeddings_dir = Path("data/embeddings")
        self._ensure_directories()
        
        self.known_embeddings = {}
        self.load_embeddings()

    def _ensure_directories(self):
        self.speakers_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)

    
    import soundfile as sf # Import soundfile for direct loading

    def extract_embedding(self, audio_path):
        """Bir ses dosyasından embedding vektörü çıkarır"""
        # Torchaudio bazen codec sorunu çıkarıyor, bu yüzden doğrudan soundfile kullanıyoruz
        try:
            # soundfile (Time, Channels) döner veya (Time,)
            data, fs = sf.read(audio_path)
            
            # Numpy -> Tensor
            signal = torch.from_numpy(data).float()
            
            # Eğer mono ise (Time,) -> (1, Time)
            if len(signal.shape) == 1:
                signal = signal.unsqueeze(0)
            # Eğer stereo ise (Time, Channels) -> (Channels, Time)
            else:
                signal = signal.transpose(0, 1)
                # Stereo ise mono'ya çevir (Ortalama al)
                if signal.shape[0] > 1:
                    signal = torch.mean(signal, dim=0, keepdim=True)
            
            # SpeechBrain embedding modeli genellikle 16kHz bekler, 
            # ancak ECAPA-TDNN modeli bazen esnektir. 
            # Yine de burada basitlik için resampling yapmıyoruz (AudioRecorder zaten 16k kaydediyor)
             
        except Exception as e:
            # Fallback olarak yine de torchaudio deneyelim
            print(f"Soundfile hatası, torchaudio deneniyor: {e}")
            signal, fs = torchaudio.load(audio_path, backend="soundfile")
            
        embeddings = self.classifier.encode_batch(signal)
        return embeddings.squeeze().cpu().numpy()

    def save_speaker(self, name, audio_path):
        """Yeni bir konuşmacı kaydeder"""
        try:
            # Embedding çıkar
            embedding = self.extract_embedding(audio_path)
            
            # Embedding'i kaydet
            emb_path = self.embeddings_dir / f"{name}.npy"
            np.save(emb_path, embedding)
            
            # Ses dosyasını da arşivle (opsiyonel ama iyi bir pratik)
            # shutil.copy(...) eklenebilir
            
            # Hafızayı güncelle
            self.known_embeddings[name] = embedding
            return True, "Kayıt başarılı."
        except Exception as e:
            return False, str(e)

    def load_embeddings(self):
        """Kaydedilmiş tüm konuşmacıların embedding'lerini yükler"""
        self.known_embeddings = {}
        for emb_file in self.embeddings_dir.glob("*.npy"):
            name = emb_file.stem
            self.known_embeddings[name] = np.load(emb_file)
        print(f"{len(self.known_embeddings)} konuşmacı yüklendi.")

    def identify_speaker(self, audio_path, threshold=0.25):
        """Verilen sesin kime ait olduğunu bulur"""
        if not self.known_embeddings:
            return "Bilinmiyor", 0.0

        target_embedding = self.extract_embedding(audio_path)
        
        best_score = -1.0
        best_speaker = "Bilinmiyor"
        
        # Cosine Similarity hesapla
        for name, emb in self.known_embeddings.items():
            # Cosine similarity: (A . B) / (||A|| * ||B||)
            # SpeechBrain embeddingleri genellikle normalize edilmiştir ama emin olmak için:
            score = np.dot(target_embedding, emb) / (np.linalg.norm(target_embedding) * np.linalg.norm(emb))
            
            if score > best_score:
                best_score = score
                best_speaker = name
        
        if best_score < threshold:
            return "Bilinmiyor", float(best_score)
            
        return best_speaker, float(best_score)
