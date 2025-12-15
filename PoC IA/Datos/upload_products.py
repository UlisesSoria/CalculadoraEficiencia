import os
import time
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from dotenv import load_dotenv

# 1. Cargar claves
load_dotenv()
KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

print("Iniciando proceso de Ingesta Inteligente...")

# 2. Configurar el Modelo de Embeddings (El Traductor)
# Usamos 'text-embedding-3-small' que genera vectores de 1536 dimensiones (compatible con tu índice)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 3. Función para procesar texto crudo y extraer Metadata (Filtros)
def procesar_archivo_productos(filepath):
    docs = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Separamos por el delimitador que pusimos en el txt
    productos_raw = content.split("---")
    
    for p in productos_raw:
        if not p.strip(): continue
        
        lines = p.strip().split('\n')
        meta = {}
        texto_completo = ""
        
        # Extracción rudimentaria de metadata (Marca, Precio)
        for line in lines:
            if line.startswith("Marca:"):
                meta["marca"] = line.split(":")[1].strip()
            elif line.startswith("Precio:"):
                try:
                    meta["precio"] = float(line.split(":")[1].strip())
                except:
                    meta["precio"] = 0
            elif line.startswith("Nombre:"):
                meta["nombre"] = line.split(":")[1].strip()
            
            texto_completo += line + "\n"
            
        # Creamos el Documento LangChain
        # page_content: Lo que se busca semánticamente (descripción)
        # metadata: Lo que se usa para filtrar (marca, precio)
        doc = Document(page_content=texto_completo, metadata=meta)
        docs.append(doc)
        
    return docs

# 4. Cargar y Procesar
path_datos = "./datos/productos_prueba.txt"
if os.path.exists(path_datos):
    documentos = procesar_archivo_productos(path_datos)
    print(f"Procesados {len(documentos)} productos del archivo.")
else:
    print(f"No encontré el archivo en {path_datos}")
    exit()

# 5. Subir a Pinecone
print("Subiendo vectores a Pinecone (esto puede tardar unos segundos)...")

import os
import time
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from dotenv import load_dotenv

# 1. Cargar claves
load_dotenv()
KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

print("Iniciando proceso de Ingesta Inteligente...")

# 2. Configurar el Modelo de Embeddings (El Traductor)
# Usamos 'text-embedding-3-small' que genera vectores de 1536 dimensiones (compatible con tu índice)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 3. Función para procesar texto crudo y extraer Metadata (Filtros)
def procesar_archivo_productos(filepath):
    docs = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Separamos por el delimitador que pusimos en el txt
    productos_raw = content.split("---")
    
    for p in productos_raw:
        if not p.strip(): continue
        
        lines = p.strip().split('\n')
        meta = {}
        texto_completo = ""
        
        # Extracción rudimentaria de metadata (Marca, Precio)
        for line in lines:
            if line.startswith("Marca:"):
                meta["marca"] = line.split(":")[1].strip()
            elif line.startswith("Precio:"):
                try:
                    meta["precio"] = float(line.split(":")[1].strip())
                except:
                    meta["precio"] = 0
            elif line.startswith("Nombre:"):
                meta["nombre"] = line.split(":")[1].strip()
            
            texto_completo += line + "\n"
            
        # Creamos el Documento LangChain
        # page_content: Lo que se busca semánticamente (descripción)
        # metadata: Lo que se usa para filtrar (marca, precio)
        doc = Document(page_content=texto_completo, metadata=meta)
        docs.append(doc)
        
    return docs

# 4. Cargar y Procesar
path_datos = "./datos/productos_prueba.txt"
if os.path.exists(path_datos):
    documentos = procesar_archivo_productos(path_datos)
    print(f"Procesados {len(documentos)} productos del archivo.")
else:
    print(f"No encontré el archivo en {path_datos}")
    exit()

# 5. Subir a Pinecone
print("Subiendo vectores a Pinecone (esto puede tardar unos segundos)...")

try:
    vectorstore = PineconeVectorStore.from_documents(
        documents=documentos,
        embedding=embeddings,
        index_name=INDEX_NAME
    )
    print("¡Éxito! Productos indexados correctamente.")
    print("Ve a tu dashboard de Pinecone y verifica que el 'Record Count' haya subido.")

except Exception as e:
    print(f"Error al subir: {e}")