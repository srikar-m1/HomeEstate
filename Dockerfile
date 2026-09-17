FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY HomeEstate/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
WORKDIR /app/HomeEstate

CMD ["gunicorn", "HomeEstate.wsgi:application", "--bind", "0.0.0.0:8000"]
