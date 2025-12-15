import os
import time
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# 1. Cargar secretos
load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")

print(f"Probando conexión con API Key: {api_key[:5]}... (oculto)")

if not api_key:
    print("Error: No se encontró PINECONE_API_KEY en el archivo .env")
    exit()

try:
    # 2. Inicializar Cliente
    pc = Pinecone(api_key=api_key)
    
    # 3. Listar Índices
    indexes = pc.list_indexes()
    print(f"Índices encontrados en tu cuenta: {[i.name for i in indexes]}")

    # 4. Verificar si existe el nuestro
    if any(i.name == index_name for i in indexes):
        print(f"¡Éxito! El índice '{index_name}' existe y es accesible.")
        
        # Opcional: Ver estadísticas
        idx = pc.Index(index_name)
        stats = idx.describe_index_stats()
        print(f"Estadísticas actuales: {stats}")
    else:
        print(f"El índice '{index_name}' no aparece. ¿Lo creaste con el nombre correcto en la web?")

except Exception as e:
    print(f"Error de conexión: {e}")