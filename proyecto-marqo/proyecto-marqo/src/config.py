"""Configuración general del proyecto."""
import os
from dotenv import load_dotenv

load_dotenv()

MARQO_URL = os.getenv("MARQO_URL", "http://localhost:8882")
INDEX_NAME = os.getenv("INDEX_NAME", "mi-indice-proyecto")
