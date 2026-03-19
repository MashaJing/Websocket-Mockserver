FROM python:3.9.25-alpine

ENV PORT=8000

WORKDIR /app

COPY main.py .
COPY requirements.txt .
COPY websocket_mockserver ./websocket_mockserver

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["python", "main.py"]
