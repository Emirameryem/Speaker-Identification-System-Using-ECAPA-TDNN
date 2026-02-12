This project presents a deep learning-based speaker identification system built on the ECAPA-TDNN architecture. Using a pretrained model from the SpeechBrain library, the system extracts speaker embeddings from audio signals and identifies speakers through cosine similarity comparison.

Transfer learning is applied with the VoxCeleb dataset, enabling reliable speaker recognition even with a limited local dataset. The project includes audio preprocessing, embedding extraction, similarity-based decision making with a threshold mechanism, and a user-friendly graphical interface for speaker enrollment and identification.

This study demonstrates the practical implementation of modern speaker recognition techniques and deep learning models in a real-world application.


Bu proje, ECAPA-TDNN mimarisi üzerine kurulu derin öğrenme tabanlı bir konuşmacı tanıma sistemini sunmaktadır. SpeechBrain kütüphanesindeki önceden eğitilmiş model kullanılarak ses sinyallerinden konuşmacıya özgü gömülü vektörler (embeddings) çıkarılmakta ve kosinüs benzerliği yöntemi ile konuşmacı tanımlama yapılmaktadır.

VoxCeleb veri seti üzerinde eğitilmiş model kullanılarak transfer öğrenme yaklaşımı uygulanmış ve küçük ölçekli veri setleriyle dahi güvenilir sonuçlar elde edilmiştir. Projede ses ön işleme, embedding çıkarımı, eşik değerine dayalı karar mekanizması ve konuşmacı kaydı ile tanıma işlemlerini içeren kullanıcı dostu bir grafik arayüz geliştirilmiştir.

Bu çalışma, modern konuşmacı tanıma tekniklerinin ve derin öğrenme modellerinin gerçek bir uygulama üzerinde nasıl kullanılabileceğini göstermektedir.
