import numpy as np

def matrix_factorization(I, K, steps=5000, alpha=0.002, beta=0.02):
    """
    I     : User-Item etkileşim matrisi (N x M)
    K     : Gizli özelliklerin (latent features) sayısı
    steps : Gradient descent iterasyon sayısı
    alpha : Öğrenme katsayısı (learning rate)
    beta  : Aşırı öğrenmeyi önlemek için düzenlileştirme (regularization) parametresi
    """
    N = len(I)     # Kullanıcı sayısı
    M = len(I[0])  # Ürün sayısı

    # U (User) ve T (Item) matrislerini rastgele değerlerle başlatıyoruz
    np.random.seed(42)
    U = np.random.rand(N, K)
    T = np.random.rand(K, M)

    # Gradient Descent Optimizasyonu
    for step in range(steps):
        for i in range(N):
            for j in range(M):
                if I[i][j] > 0: # Sadece puan verilmiş (0'dan büyük) hücreleri kullanıyoruz
                    # Tahmin edilen değeri hesapla: U satırı ile T sütununun çarpımı
                    eij = I[i][j] - np.dot(U[i, :], T[:, j])
                    
                    # Gradient'lere göre U ve T matrislerini güncelle
                    for k in range(K):
                        U[i][k] = U[i][k] + alpha * (2 * eij * T[k][j] - beta * U[i][k])
                        T[k][j] = T[k][j] + alpha * (2 * eij * U[i][k] - beta * T[k][j])

        # Hata hesaplama (isteğe bağlı, gidişatı görmek için)
        e = 0
        for i in range(N):
            for j in range(M):
                if I[i][j] > 0:
                    e = e + pow(I[i][j] - np.dot(U[i, :], T[:, j]), 2)
                    for k in range(K):
                        e = e + (beta / 2) * (pow(U[i][k], 2) + pow(T[k][j], 2))
        
        if e < 0.001:
            break
            
    return U, T

# === HOCANIN İSTEDİĞİ YAPILARIN KODDAKİ YERLERİ ===

# 1. User-item interaction matrix I (Kullanıcı-Ürün Etkileşim Matrisi)
# 0'lar kullanıcının o ürüne henüz puan vermediğini (sparsity) gösterir.
I = [
    [5, 3, 0, 1],
    [4, 0, 0, 1],
    [1, 1, 0, 5],
    [1, 0, 0, 4],
    [0, 1, 5, 4],
]

# 2. Users, items and ratings in matrix I
# Users (Kullanıcılar)  -> I matrisinin satırlarıdır (Örn: I[0] ilk kullanıcıdır)
# Items (Ürünler)       -> I matrisinin sütunlarıdır (Örn: Tüm satırların 0. indeksi ilk üründür)
# Ratings (Puanlar)     -> I matrisinin içindeki 0 harici değerlerdir (Örn: I[0][0] = 5)

I = np.array(I)

# K = 2 diyerek her kullanıcı ve ürün için 2 adet "gizli özellik" belirliyoruz.
K = 2 

# 3. U ve T Matrislerinin Oluşturulması
U_result, T_result = matrix_factorization(I, K)

print("Kullanıcı Matrisi (U):")
print(np.round(U_result, 2))
print("\nÜrün Matrisi (T):")
print(np.round(T_result, 2))

print("\nTahmin Edilmiş Tam Matris (I_predicted = U x T):")
I_predicted = np.dot(U_result, T_result)
print(np.round(I_predicted, 2))