import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_NAME_2 = os.getenv('DB_NAME_2')
DB_NAME_3 = os.getenv('DB_NAME_3')
AES_KEY = os.getenv('AES_KEY')
AES_IV = os.getenv('AES_IV')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Example usage
print(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_NAME_2, DB_NAME_3)