import pika
from elasticsearch import Elasticsearch

# Verbindung zu Elasticsearch
es = Elasticsearch("http://elasticsearch:9200")

def index_document(index_name, doc_id, content):
    try:
        # Indexieren des Dokuments
        es.index(index=index_name, id=doc_id, document=content)
        print(f"Document indexed: {doc_id}")
    except Exception as e:
        print(f"Failed to index document: {e}")

def on_message(ch, method, properties, body):
    message = body.decode()
    print(f"Received message for indexing: {message}")
    # Dokument mit Textinhalt indexieren
    index_document("ocr_results", None, {"content": message})

def start_indexing_worker():
    credentials = pika.PlainCredentials('sophia', 'Login4rabbitMQ')

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='rabbitmq',
        port=5672,
        credentials=credentials
    ))
    channel = connection.channel()

    channel.queue_declare(queue='ocrResultQueue')

    channel.basic_consume(queue='ocrResultQueue', on_message_callback=on_message, auto_ack=True)
    print("Indexing Worker is waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    start_indexing_worker()
