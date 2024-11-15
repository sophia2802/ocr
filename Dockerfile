# Verwende ein Python-Basisimage
FROM python:3.9-slim

# Tesseract OCR installieren
RUN apt-get update && apt-get install -y tesseract-ocr

# Arbeitsverzeichnis erstellen
WORKDIR /app

# Kopiere die Abhängigkeitsliste und installiere Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install -r requirements.txt

# Kopiere den restlichen Anwendungs-Code
COPY . .

# Starte den OCR-Worker
CMD ["python", "ocr_worker.py"]
