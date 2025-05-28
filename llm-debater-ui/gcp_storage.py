from google.cloud import storage
from pathlib import Path
import json
import os
import sys

def log_debug(message):
    """Print to stderr for Cloud Run logging"""
    print(message, file=sys.stderr, flush=True)

class LocalStorageManager:
    def __init__(self, base_dir="local_storage"):
        """Initialize local storage with a base directory"""
        self.base_dir = Path(base_dir)
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            log_debug(f"Successfully initialized local storage at: {self.base_dir}")
        except Exception as e:
            log_debug(f"Failed to initialize local storage: {str(e)}")
            raise

    def save_json(self, data, file_path):
        """Save JSON data to local filesystem"""
        try:
            # Ensure the full path exists
            full_path = self.base_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Custom JSON encoder to handle special types
            class CustomJSONEncoder(json.JSONEncoder):
                def default(self, obj):
                    if str(type(obj)) == "<class 'numpy.bool_'>":
                        return bool(obj)
                    if isinstance(obj, bool):
                        return bool(obj)
                    try:
                        return obj.item()
                    except:
                        return json.JSONEncoder.default(self, obj)
            
            # Save the file
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
            
            log_debug(f"Successfully saved data to {full_path}")
            return True
        except Exception as e:
            log_debug(f"Failed to save data locally: {str(e)}")
            raise

class GCPStorageManager:
    def __init__(self, bucket_name="llm_fact_check_debate"):
        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(bucket_name)
            if not self.bucket.exists():
                raise Exception(f"Bucket {bucket_name} does not exist")
            log_debug(f"Successfully connected to bucket: {bucket_name}")
        except Exception as e:
            log_debug(f"Failed to initialize GCP Storage: {str(e)}")
            raise

    def save_json(self, data, blob_path):
        """Save JSON data to GCP bucket"""
        try:
            log_debug(f"Attempting to save data to path: {blob_path}")
            blob = self.bucket.blob(blob_path)
            
            class CustomJSONEncoder(json.JSONEncoder):
                def default(self, obj):
                    if str(type(obj)) == "<class 'numpy.bool_'>":
                        return bool(obj)
                    if isinstance(obj, bool):
                        return bool(obj)
                    try:
                        return obj.item()
                    except:
                        return json.JSONEncoder.default(self, obj)
            
            json_str = json.dumps(data, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
            blob.upload_from_string(json_str, content_type='application/json')
            log_debug(f"Successfully saved data to {blob_path}")
            return True
        except Exception as e:
            log_debug(f"Failed to save data to {blob_path}: {str(e)}")
            raise

class CloudStorageInterface:
    def __init__(self, bucket_name="llm_fact_check_debate", local_dir="local_storage"):
        """Initialize storage interface with fallback to local storage"""
        self.storage_manager = None
        self.using_local = False
        self.base_path = ""
        
        try:
            log_debug("Attempting to initialize GCP Storage...")
            self.storage_manager = GCPStorageManager(bucket_name)
            log_debug("Successfully initialized GCP Storage")
        except Exception as e:
            log_debug(f"GCP Storage initialization failed, falling back to local storage: {str(e)}")
            self.storage_manager = LocalStorageManager(local_dir)
            self.using_local = True

    def set_base_path(self, path):
        """Set base path for storage operations"""
        self.base_path = path
        log_debug(f"Set base path to: {path}")
    
    def save_transcript(self, data, filepath):
        """Save transcript data to storage"""
        try:
            if isinstance(filepath, Path):
                filepath = str(filepath)
            
            # Normalize path
            full_path = os.path.join(self.base_path, filepath.lstrip('/'))
            
            # Replace backslashes with forward slashes for consistency
            full_path = full_path.replace('\\', '/')
            
            log_debug(f"Saving transcript to: {full_path} ({'local storage' if self.using_local else 'GCP'})")
            success = self.storage_manager.save_json(data, full_path)
            
            if success:
                storage_type = "local storage" if self.using_local else "GCP storage"
                log_debug(f"Successfully saved transcript to {storage_type}")
            return success
        except Exception as e:
            log_debug(f"Failed to save transcript: {str(e)}")
            raise
