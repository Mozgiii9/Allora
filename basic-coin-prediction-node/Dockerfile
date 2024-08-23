# Используем официальный образ Python в качестве базового
FROM amd64/python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . /app/

# Устанавливаем зависимости из requirements.txt
RUN pip install --upgrade pip setuptools \
    && pip install -r requirements.txt

# Устанавливаем команду запуска с gunicorn
CMD ["gunicorn", "--conf", "/app/gunicorn_conf.py", "main:app"]

