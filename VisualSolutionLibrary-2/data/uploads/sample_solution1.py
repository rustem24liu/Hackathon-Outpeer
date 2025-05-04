# Step 1: Импортируем необходимые библиотеки
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Step 2: Генерируем тестовые данные
np.random.seed(42)
X = 2 * np.random.rand(100, 1)
y = 4 + 3 * X + np.random.randn(100, 1)

# Step 3: Разделяем данные на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Создаем и обучаем модель линейной регрессии
model = LinearRegression()
model.fit(X_train, y_train)

# Step 5: Выводим коэффициенты модели
print(f'Коэффициент наклона: {model.coef_[0][0]:.2f}')
print(f'Свободный член: {model.intercept_[0]:.2f}')

# Step 6: Делаем предсказания на тестовой выборке
y_pred = model.predict(X_test)

# Step 7: Оцениваем качество модели
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f'Среднеквадратическая ошибка: {mse:.2f}')
print(f'Коэффициент детерминации (R²): {r2:.2f}')

# Step 8: Визуализируем результаты
plt.figure(figsize=(10, 6))
plt.scatter(X_train, y_train, color='blue', label='Обучающие данные')
plt.scatter(X_test, y_test, color='green', label='Тестовые данные')
plt.plot(X, model.predict(X), color='red', linewidth=2, label='Линейная модель')
plt.xlabel('X')
plt.ylabel('y')
plt.title('Линейная регрессия')
plt.legend()
plt.grid(True)
plt.show()