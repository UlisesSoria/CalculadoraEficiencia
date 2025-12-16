import os
from dotenv import load_dotenv

# Cargar llaves
load_dotenv()

print("--- DIAGNÓSTICO DE ENTORNO ---")
if os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY"):
    print("API Key de IA detectada.")
else:
    print("FALTA API KEY de IA en .env")

try:
    import langchain
    import streamlit
    print(f"Librerías instaladas correctamente. LangChain v{langchain.__version__}")
except ImportError:
    print("Error en librerías.")

print("Listo para la Fase 1: Ingesta.")