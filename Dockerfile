FROM --platform=linux/amd64 python:3.10-slim-bullseye AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM --platform=linux/amd64 python:3.10-slim-bullseye

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

COPY main.py .
COPY parser.py .
COPY classifier.py .

CMD ["python", "main.py"]