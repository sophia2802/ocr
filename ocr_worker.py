import pika
import pytesseract
from PIL import Image
import os
import time

# Verbindung zu RabbitMQ herstellen
def connect_to_queue():
    while True:
        try:
            # Verbindung mit den korrekten Zugangsdaten herstellen
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq',
                    credentials=pika.PlainCredentials('sophia', 'Login4rabbitMQ')
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue='ocrQueue')
            channel.queue_declare(queue='ocrResultQueue')
            print("Connected to RabbitMQ")
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            print("Connection to RabbitMQ failed, retrying in 5 seconds...")
            time.sleep(5)

def perform_ocr(file_path):
    # OCR auf das Bild anwenden
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"OCR failed: {e}")
        return "OCR failed"

def on_message(ch, method, properties, body):
    file_path = body.decode()
    print(f"Received file path for OCR: {file_path}")

    # OCR durchführen und das Ergebnis senden
    result_text = perform_ocr(file_path)
    ch.basic_publish(exchange='', routing_key='ocrResultQueue', body=result_text)
    print("OCR result sent to ocrResultQueue")

def start_worker():
    connection, channel = connect_to_queue()
    channel.basic_consume(queue='ocrQueue', on_message_callback=on_message, auto_ack=True)
    print("OCR Worker is waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()
