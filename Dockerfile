# Многоступенчатая сборка для оптимизации размера
FROM python:3.11-slim as builder

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Финальный образ
FROM python:3.11-slim

WORKDIR /app

# Копирование зависимостей из builder
COPY --from=builder /root/.local /root/.local

# Копирование кода
COPY . .

# Обновление PATH
ENV PATH=/root/.local/bin:$PATH

# Создание папки для логов
RUN mkdir -p logs

# Запуск
CMD ["python", "cli.py"]
