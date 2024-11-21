from minio import Minio

# MinIO-Client konfigurieren
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

def upload_file(bucket_name, file_path, object_name):
    try:
        normalized_object_name = object_name.lstrip("/")  # Entfernt führende "/"
        minio_client.fput_object(bucket_name, normalized_object_name, file_path)
        print(f"File '{file_path}' uploaded to bucket '{bucket_name}' as '{normalized_object_name}'.")
    except Exception as e:
        print(f"Failed to upload file: {e}")

def download_file(bucket_name, object_name, download_path):
    try:
        normalized_object_name = object_name.lstrip("/")
        minio_client.fget_object(bucket_name, normalized_object_name, download_path)
        print(f"File '{normalized_object_name}' downloaded from bucket '{bucket_name}' to '{download_path}'.")
    except Exception as e:
        print(f"Failed to download file: {e}")
