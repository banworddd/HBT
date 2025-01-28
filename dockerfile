# Используем образ Python 3.13
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Открываем порт
EXPOSE 8000

# Команда запуска сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]