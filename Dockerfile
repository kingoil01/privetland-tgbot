# Базовый образ с Python 3.11
FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда запуска бота
CMD ["python", "main.py"]