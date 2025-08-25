from dotenv import load_dotenv
import psycopg2

import os 


load_dotenv()

class DatabaseManger:
    _instance = None
    _initialized = False 

    def __new__(cls):   
        if cls._instance is None :
            cls._instance = super().__new__(cls)
            cls._instance._check_data()
        return cls._instance
    
    def _check_data(self):
        require_env_vars = {'DB_HOST','DB_PORT','DB_USER','DB_NAME','DB_PASS','DB_TABLE'}
        
        if any(os.getenv(var) is None for var in require_env_vars):
            raise ValueError("Missed DB Key In '.env' File")
    
    def _get_connection(self):
        conn = psycopg2.connect(
            host     = os.getenv('DB_HOST'),
            port     = os.getenv('DB_PORT'),
            user     = os.getenv('DB_USER'),
            dbname   = os.getenv('DB_NAME'),
            password = os.getenv('DB_PASS'),
            sslmode  = "require"
        )

        return conn
    
    def __init__(self):
        if self._initialized : 
            return
        
        self.conn = self._get_connection()
        self.cur  = self.conn.cursor()

        self._initialized = True
    
    def close(self):
        self.cur.close()
        self.conn.commit()
        self.conn.close()
    
    def check_image_hash(self,image_hash):
        query = f"SELECT * FROM {os.getenv('DB_TABLE')} WHERE hash_sha256 = %s" 
        
        self.cur.execute(query , (image_hash,))
        data = self.cur.fetchall()

        return bool(data)
    
    def check_image_phash(self,image_phash):
        query = f"SELECT * FROM {os.getenv('DB_TABLE')} WHERE phash = %s" 
        
        self.cur.execute(query , (image_phash,))
        data = self.cur.fetchall()

        return bool(data)
    
    def insert_image_data(self,image_data):
        query = f"""
        INSERT INTO {os.getenv('DB_TABLE')} (filename,category,keyword,phash,source_url,hash_sha256)
        VALUES(
            %(filename)s,
            %(category)s,
            %(keyword)s,
            %(phash)s,
            %(source_url)s,
            %(hash_sha256)s
        )
        """

        self.cur.execute(query,image_data)
        self.conn.commit()  