# 1) Базовый образ
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# 2) Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 3) Рабочая директория
WORKDIR /app

# 4) Зависимости
# Если используешь requirements.txt
COPY requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 5) Копируем проект
COPY . /app/

# 6) Собираем статику (если нужен collectstatic)
# Важно: должен быть настроен DJANGO_SETTINGS_MODULE и STATIC_ROOT
ENV DJANGO_SETTINGS_MODULE=core.settings
RUN mkdir -p /app/staticfiles && \
    python manage.py collectstatic --noinput

# 7) Пользователь без root
RUN useradd -ms /bin/bash django
USER django

# 8) Запуск через gunicorn
# Заменить your_project.wsgi на имя твоего проекта
CMD ["sh", "-c", "python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:${APP_PORT:-8000} --workers 4"]
