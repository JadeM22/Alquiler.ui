import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME")
MONGODB_URI = os.getenv("MONGODB_URI")  

def get_collection( col ):
    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi("1"),
    
    )
    client.admin.command("ping")
    print("conectado correctamente a MongoDB")  
    return client[DATABASE_NAME][col]







