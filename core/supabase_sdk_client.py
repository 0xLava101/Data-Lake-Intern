# core/subpabase_old.py

from dotenv import load_dotenv
import os
import json

from supabase import create_client, Client

load_dotenv()


bucket_name = os.getenv('BUCKET_NAME')

class SupabaseClient:
    _instance = None
    _initialized = False 

    def __new__(cls):
        if cls._instance is None :
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized : 
            return

        url = os.getenv('SUPA_URL')
        api_key =  os.getenv('SUPA_KEY')
        
        if None in [url,api_key]: 
            raise ValueError('Error On .env File Check Values [PROJECT_URL , API_KEY]')

        self.supabase: Client = create_client(
            url,
            api_key
        )

        if self.supabase is None : 
            raise ValueError('Error On Authentication')
        
        self._initialized = True
    
    # def upload_image(self,image,path) -> str:
    #     unique_filename = f"{path}/image_{uuid.uuid4().hex}.jpg"
        
    #     try:
    #         self.supabase.storage.from_(bucket_name).upload(
    #             path=unique_filename,
    #             file=image,
    #             file_options={"content-type": "image/jpeg"}
    #         )
    #     except Exception as e : 
    #         return False
        
    #     return True 

    def get_images_urls_structured(self,path=""):
        items = self.supabase.storage.from_(bucket_name).list(path=path)

        if not items:
            return {}

        first_item = items[0]

        if first_item["metadata"] is None:
            return {
                item["name"]: self.get_images_urls_structured(f"{path}/{item['name']}" if path else item['name'])
                for item in items
            }
        
        else:
            return [
                self.supabase.storage.from_(bucket_name).get_public_url(
                    f"{path}/{item['name']}" if path else item['name']
                )
                for item in items
            ]