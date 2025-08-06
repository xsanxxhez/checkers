FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "-k", "gevent", "-w", "1", "-b", "0.0.0.0:10000", "app:app"]