import pika
import pytesseract
from PIL import Image
import pdf2image
import os
import time

# Verbindung zu RabbitMQ herstellen
def connect_to_queue():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq',
                    credentials=pika.PlainCredentials('sophia', 'Login4rabbitMQ')
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue='documentQueue')
            channel.queue_declare(queue='ocrResultQueue')
            print("Connected to RabbitMQ")
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            print("Connection to RabbitMQ failed, retrying in 5 seconds...")
            time.sleep(5)

def perform_ocr_on_pdf(pdf_path):
    text_result = ""
    try:
        images = pdf2image.convert_from_path(pdf_path)
        for image in images:
            text_result += pytesseract.image_to_string(image) + "\n"
    except Exception as e:
        print(f"OCR failed: {e}")
        text_result = "OCR failed"
    return text_result

def on_message(ch, method, properties, body):
    pdf_path = body.decode()
    print(f"Received file path for OCR: {pdf_path}")

    result_text = perform_ocr_on_pdf(pdf_path)
    ch.basic_publish(exchange='', routing_key='ocrResultQueue', body=result_text)
    print("OCR result sent to ocrResultQueue")


def start_worker():
    connection, channel = connect_to_queue()
    channel.basic_consume(queue='documentQueue', on_message_callback=on_message, auto_ack=True)
    print("OCR Worker is waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()
