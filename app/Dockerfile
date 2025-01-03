FROM python:3.8-slim

RUN apt-get update && apt-get install -y tini && apt-get clean

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["/usr/bin/tini", "--"]  

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
