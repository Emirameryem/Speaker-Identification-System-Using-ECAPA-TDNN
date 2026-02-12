import os
import sys
import shutil

# ==============================================================================
# YAMALAR (PATCHES) - Bu bölüm, diğer importlardan ÖNCE gelmelidir.
# ==============================================================================

# --- 1. Torchaudio Uyumluluk Yaması ---
import torchaudio
if not hasattr(torchaudio, "list_audio_backends"):
    def _list_audio_backends():
        return ["soundfile"]
    torchaudio.list_audio_backends = _list_audio_backends

# --- 2. HuggingFace Hub Uyumluluk ve 404 Hatası Yaması ---
import huggingface_hub
from huggingface_hub.utils import EntryNotFoundError, RepositoryNotFoundError
from requests.exceptions import HTTPError

_original_hf_hub_download = huggingface_hub.hf_hub_download

def _patched_hf_hub_download(*args, **kwargs):
    # 'use_auth_token' parametresini 'token' ile değiştir
    if 'use_auth_token' in kwargs:
        kwargs['token'] = kwargs.pop('use_auth_token')
    
    # İndirmeyi dene
    try:
        return _original_hf_hub_download(*args, **kwargs)
    except (EntryNotFoundError, RepositoryNotFoundError, HTTPError) as e:
        filename = kwargs.get('filename') or (args[1] if len(args) > 1 else "")
        if "custom.py" in filename and ("404" in str(e) or isinstance(e, EntryNotFoundError)):
            print(f"UYARI: {filename} bulunamadı. Sahte (dummy) dosya ile devam ediliyor.")
            
            dummy_dir = os.path.join(os.getcwd(), "pretrained_models", "dummy_cache")
            os.makedirs(dummy_dir, exist_ok=True)
            dummy_path = os.path.join(dummy_dir, "custom.py")
            
            if not os.path.exists(dummy_path):
                with open(dummy_path, "w") as f:
                    f.write("# Dummy custom.py created by patch\n")
            
            return dummy_path
            
        raise e

huggingface_hub.hf_hub_download = _patched_hf_hub_download

# --- 3. Windows Symlink Yetki Yaması ---
if os.name == 'nt':
    _original_symlink = getattr(os, "symlink", None)

    def _patched_symlink(src, dst, target_is_directory=False, *, dir_fd=None):
        # Detaylı debug bas
        print(f"DEBUG: Symlink isteği -> SRC: {src} | DST: {dst}")
        
        # SRC path'i normalize et
        if not os.path.isabs(src):
            # Eğer relative ise, DST'nin bulunduğu klasöre göre relative olabilir mi?
            # os.symlink(src, dst) için src, linkin göstereceği yoldur.
            # Windows'ta copy için full path gerekir.
            pass
            
        if not os.path.exists(src):
            print(f"DEBUG: Kaynak dosya bulunamadı! ({src})")
            # Yine de kopyalamayı denemek mantıksız ama belki dosya yeni inmiştir?
            # Windows'ta copy işlemi için kaynak şart.
            # Belki de src, symlink'in gösterdiği yerdir ve henüz orada değildir?
            # Symlink oluşmazsa dosya hiç oluşmaz.
            
            # Belki de src, bir 'blob' dosyasıdır ve huggingface cache yapısındadır.
        
        try:
            if _original_symlink:
                _original_symlink(src, dst, target_is_directory=target_is_directory, dir_fd=dir_fd)
            else:
                raise OSError("Symlink not supported")
        except OSError:
            try:
                print("DEBUG: Symlink başarısız, kopyalama deneniyor...")
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                
                # Eğer src relative ise ve os.path.exists(src) False dediyse,
                # Python'un çalıştığı klasöre göre bakıyordur.
                # Ama symlinkler relative olabilir. 
                # DST'nin dizini baz alarak absolute yapmayı deneyelim.
                real_src = src
                if not os.path.isabs(src):
                    dst_dir = os.path.dirname(dst)
                    real_src = os.path.normpath(os.path.join(dst_dir, src))
                    print(f"DEBUG: Relative path çözüldü -> {real_src}")

                if os.path.isdir(real_src):
                    shutil.copytree(real_src, dst)
                elif os.path.isfile(real_src):
                    shutil.copy2(real_src, dst)
                else:
                     print(f"DEBUG: Kopyalanacak kaynak bulunamadı! {real_src}")

            except Exception as copy_err:
                print(f"DEBUG: Symlink fallback (kopya) başarısız: {copy_err}")

    os.symlink = _patched_symlink

# ==============================================================================
# UYGULAMA İMPORTLARI
# ==============================================================================
import speechbrain
from modules.gui import App

if __name__ == "__main__":
    print("--------------------------------------------------")
    print(f"Python Sürümü: {sys.version}")
    try:
        print(f"SpeechBrain Sürümü: {speechbrain.__version__}")
    except:
        pass
    print("--------------------------------------------------")
    
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        input("Çıkmak için Enter'a basın...")
