# Step 1: Импортируем необходимые библиотеки
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline

# Step 2: Загружаем и подготавливаем данные
# В данном примере используем синтетические данные
np.random.seed(42)
n_samples = 1000

# Создаем синтетический набор данных
age = np.random.normal(35, 10, n_samples)
income = 20000 + age * 1000 + np.random.normal(0, 10000, n_samples)
education_years = np.random.randint(9, 20, n_samples)
debt = np.random.normal(10000, 5000, n_samples)
credit_score = np.random.normal(650, 100, n_samples)

# Определяем вероятность дефолта на основе признаков
default_prob = 1 / (1 + np.exp(-(
    -10 +
    -0.1 * age +
    -0.0001 * income +
    -0.2 * education_years +
    0.0001 * debt +
    -0.01 * credit_score
)))

# Генерируем класс (дефолт/не дефолт) на основе вероятности
default = np.random.binomial(1, default_prob)

# Создаем DataFrame
data = pd.DataFrame({
    'age': age,
    'income': income,
    'education_years': education_years,
    'debt': debt,
    'credit_score': credit_score,
    'default': default
})

# Step 3: Анализируем данные
print("Размер набора данных:", data.shape)
print("\nПервые 5 строк:")
print(data.head())

print("\nОписательная статистика:")
print(data.describe())

print("\nРаспределение целевой переменной:")
print(data['default'].value_counts())
print(f"Процент дефолтов: {data['default'].mean() * 100:.2f}%")

# Step 4: Подготовка данных для обучения
X = data.drop('default', axis=1)
y = data['default']

# Разделяем данные на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Step 5: Создаем и обучаем модель случайного леса
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('rf', RandomForestClassifier(random_state=42))
])

# Определяем сетку гиперпараметров для поиска
param_grid = {
    'rf__n_estimators': [50, 100, 200],
    'rf__max_depth': [None, 10, 20],
    'rf__min_samples_split': [2, 5, 10]
}

# Step 6: Проводим поиск по сетке с перекрестной проверкой
grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train, y_train)

# Выводим лучшие параметры
print("\nЛучшие параметры:", grid_search.best_params_)
print("Лучшая оценка при перекрестной проверке:", grid_search.best_score_)

# Step 7: Оцениваем модель на тестовой выборке
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)

# Выводим метрики качества
print("\nТочность на тестовой выборке:", accuracy_score(y_test, y_pred))
print("\nОтчет о классификации:")
print(classification_report(y_test, y_pred))

# Step 8: Вычисляем и визуализируем матрицу путаницы
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.title('Матрица путаницы')
plt.colorbar()
classes = ['Нет дефолта', 'Дефолт']
tick_marks = np.arange(len(classes))
plt.xticks(tick_marks, classes, rotation=45)
plt.yticks(tick_marks, classes)

# Добавляем подписи на матрицу путаницы
thresh = cm.max() / 2
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        plt.text(j, i, format(cm[i, j], 'd'),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

plt.ylabel('Истинный класс')
plt.xlabel('Предсказанный класс')
plt.tight_layout()
plt.show()

# Step 9: Анализируем важность признаков
feature_importances = best_model.named_steps['rf'].feature_importances_
features = X.columns

# Сортируем признаки по важности
indices = np.argsort(feature_importances)[::-1]
sorted_feature_importances = feature_importances[indices]
sorted_features = [features[i] for i in indices]

# Визуализируем важность признаков
plt.figure(figsize=(10, 6))
plt.title('Важность признаков')
plt.bar(range(X.shape[1]), sorted_feature_importances, align='center')
plt.xticks(range(X.shape[1]), sorted_features, rotation=90)
plt.tight_layout()
plt.show()

# Step 10: Делаем выводы
print("\nВыводы:")
print("1. Точность модели:", accuracy_score(y_test, y_pred))
print("2. Наиболее важные признаки для предсказания дефолта:")
for i in range(len(sorted_features)):
    print(f"   - {sorted_features[i]}: {sorted_feature_importances[i]:.4f}")
print("3. Рекомендации для оценки кредитоспособности клиентов:")
print("   - Обратить особое внимание на признаки с высокой важностью")
print("   - Установить пороговое значение вероятности для классификации с учетом бизнес-требований")