# core/supabase_service.py

from dotenv import load_dotenv
import os 
import uuid
import hashlib

import requests

load_dotenv()

project_url = os.getenv("SUPA_URL")
api_key = os.getenv("SUPA_KEY")
bucket_name = os.getenv("BUCKET_NAME")
image_data_table_name = os.getenv("SUPA_TABLE_NAME")


class SupaBaseService:
    def __init__(self):
        pass
    
    def insert_image_metadata(self,path,folder,hash,public_url):
        headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

        data = {
            "path"       : path,
            "folder"     : folder,
            "hash"       : hash,
            "public_url" : public_url
        }

        response = requests.post(
            f"{project_url}/rest/v1/{image_data_table_name}", 
            headers=headers, 
            json=data
        )

        if not response.status_code == 201 : 
            response.raise_for_status()
        
        return True

    def image_hash_exists(self,hash):
        headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.get(
            headers=headers,
            url=f"{project_url}/rest/v1/{image_data_table_name}?hash=eq.{hash}"
        )
        
        if response.status_code != 200:
            raise ValueError(f"❌ Error: {response.status_code} - {response.text}")
        
        return response.json() != []
        
    @staticmethod
    def get_image_hash(image_bytes):
        return hashlib.sha256(image_bytes).hexdigest()
    
    def upload_image(self,image_bytes , folder):
        headers = {
                "apikey": api_key,
                "Authorization": f"Bearer {api_key}"
        }

        image_hash = SupaBaseService.get_image_hash(image_bytes)

        if self.image_hash_exists(image_hash) : 
            print("\nImage Is Allready Uploaded\n")
            return

        path = f"{folder}/image_{uuid.uuid4().hex}.jpg"
        upload_url = f"{project_url}/storage/v1/object/{bucket_name}/{path}"
        
        response = requests.put(
            upload_url,
            headers={
                **headers,
                "Content-Type": "image/jpeg",
            },
            data=image_bytes
        )

        if response.status_code not in [200, 201]:
            print(f"❌ Upload failed: {response.status_code} | {response.text}")
            return None
        
        if not self.insert_image_metadata(
            path,
            folder,
            image_hash,
            upload_url
        ): 
            raise ValueError("Error On Insert Data")
        
        return True