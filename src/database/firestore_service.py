import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

class FirestoreService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirestoreService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        load_dotenv()
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        print(f"Attempting to load credentials from: {os.path.abspath(cred_path)}")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def get_db(self):
        return self.db