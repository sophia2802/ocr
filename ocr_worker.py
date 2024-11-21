import pika
import pytesseract
from PIL import Image
import pdf2image
import os
import time
import tempfile
import logging
from minio_client import upload_file, download_file  # Importiere MinIO-Funktionen

logging.basicConfig(
    filename='/app/ocr_worker.log',  # In Docker, speichere es in /app
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BUCKET_NAME = "documents"

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
    logger.info(f"Starting OCR on file: {pdf_path}")
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
    object_name = body.decode()
    print(f"Received file for OCR: {object_name}")

    download_path = os.path.join(tempfile.gettempdir(), object_name)
    result_path = os.path.join(tempfile.gettempdir(), f"{object_name}_result.txt")
    logger.info(f"Download path: {download_path}")
    logger.info(f"result_path: {download_path}")


    try:
        download_file(BUCKET_NAME, object_name, download_path)

        result_text = perform_ocr_on_pdf(download_path)

        with open(result_path, "w") as result_file:
            result_file.write(result_text)

        result_object_name = os.path.join("shared-files", f"{object_name}_result.txt")
        logger.info(f"result_object_name: {result_object_name}")
        upload_file(BUCKET_NAME, result_path, result_object_name)

        ch.basic_publish(exchange='', routing_key='ocrResultQueue', body=result_text)
        print(f"OCR result uploaded to MinIO and sent to ocrResultQueue: '{result_object_name}'")
    except Exception as e:
        print(f"Failed to process file '{object_name}': {e}")



def start_worker():
    connection, channel = connect_to_queue()
    channel.basic_consume(queue='documentQueue', on_message_callback=on_message, auto_ack=True)
    print("OCR Worker is waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()
