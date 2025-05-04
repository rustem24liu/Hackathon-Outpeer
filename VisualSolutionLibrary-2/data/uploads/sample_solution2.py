# Step 1: Импортируем необходимые библиотеки
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Step 2: Генерируем тестовые данные
np.random.seed(42)
# Создаем три группы точек
n_samples = 150
X = np.concatenate([
    np.random.normal(0, 1, (n_samples, 2)),  # Группа 1
    np.random.normal(5, 1, (n_samples, 2)),  # Группа 2
    np.random.normal(10, 1, (n_samples, 2))  # Группа 3
])

# Step 3: Нормализуем данные
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 4: Определяем оптимальное количество кластеров с помощью метода локтя
inertia = []
k_range = range(1, 11)
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X_scaled)
    inertia.append(kmeans.inertia_)

# Step 5: Визуализируем метод локтя для выбора оптимального количества кластеров
plt.figure(figsize=(10, 6))
plt.plot(k_range, inertia, 'bo-')
plt.xlabel('Количество кластеров')
plt.ylabel('Инерция')
plt.title('Метод локтя для определения оптимального k')
plt.grid(True)
plt.show()

# Step 6: Обучаем модель KMeans с оптимальным количеством кластеров
optimal_k = 3
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
y_pred = kmeans.fit_predict(X_scaled)

# Step 7: Применяем PCA для визуализации результатов в 2D
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Step 8: Визуализируем результаты кластеризации
plt.figure(figsize=(12, 8))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y_pred, cmap='viridis', alpha=0.8, s=50)
centers_pca = pca.transform(kmeans.cluster_centers_)
plt.scatter(centers_pca[:, 0], centers_pca[:, 1], c='red', s=200, alpha=0.8, marker='X')
plt.colorbar(scatter, label='Кластер')
plt.title('Результаты кластеризации KMeans (PCA)')
plt.xlabel('Главная компонента 1')
plt.ylabel('Главная компонента 2')
plt.grid(True)
plt.show()

# Step 9: Выводим информацию о кластерах
for i in range(optimal_k):
    print(f'Кластер {i}:')
    print(f'  Количество точек: {np.sum(y_pred == i)}')
    print(f'  Центр кластера: {kmeans.cluster_centers_[i]}')
    print()

# Step 10: Создаем DataFrame с результатами
df_results = pd.DataFrame({
    'x1': X[:, 0],
    'x2': X[:, 1],
    'cluster': y_pred
})
print(df_results.head())