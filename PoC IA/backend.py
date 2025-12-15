import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import pandas as pd
import json
import io
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="LiciBot - Segmentación Lógica", layout="wide")

# --- ESTILOS ---
st.markdown("""
<style>
    .logic-step { border-left: 4px solid #3b82f6; padding: 10px; background: #eff6ff; margin-bottom: 10px; border-radius: 4px; }
    .ocr-warning { background-color: #fff7ed; color: #c2410c; padding: 5px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

CATALOGO_MOCK = """
1. SKU: CS-9200L-48P | Marca: Cisco | Switch Catalyst 9200L 48 puertos PoE+. Precio: $4,500.
2. SKU: DL-R750-XS | Marca: Dell | Servidor PowerEdge R750 Xeon Gold. Precio: $12,500.
3. SKU: FG-60F-BDL | Marca: Fortinet | Firewall FortiGate 60F. Precio: $950.
"""

# --- 1. PIPELINE DE EXTRACCIÓN HÍBRIDA (SPRINT 2) ---
def procesar_pdf_hibrido(uploaded_file, umbral_caracteres=50):
    reader = PdfReader(uploaded_file)
    texto_completo = ""
    log_procesamiento = [] 

    barra = st.progress(0)
    total_paginas = len(reader.pages)

    for i, page in enumerate(reader.pages):
        texto_nativo = page.extract_text() or ""
        
        # Semáforo de Decisión
        if len(texto_nativo.strip()) < umbral_caracteres:
            texto_ocr = f"\n[PÁGINA {i+1} - IMAGEN DETECTADA (OCR)]: (Contenido simulado de anexo escaneado...)\n"
            texto_completo += texto_ocr
            log_procesamiento.append("OCR")
        else:
            texto_completo += texto_nativo
            log_procesamiento.append("NATIVO")
        
        barra.progress((i + 1) / total_paginas)

    return texto_completo, log_procesamiento

# --- 2. MOTOR DE RAZONAMIENTO CON SEGMENTACIÓN LÓGICA (SPRINT PLANNING) ---
def analizar_con_logica(text, api_key, input_usuario):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # AQUÍ ESTÁ LA MAGIA: El Prompt refleja tu diagrama de "Segmentación Lógica"
    prompt = f"""
    ERES: El "LiciBot", un motor de análisis de licitaciones experto.
    
    TU MISIÓN: Ejecutar un "Chunking Estratégico" de la información basándote en 3 Inputs Lógicos.
    
    --- INPUTS DEL SISTEMA ---
    CATÁLOGO DISPONIBLE: {CATALOGO_MOCK}
    PREFERENCIA DEL USUARIO: "{input_usuario}"
    
    --- PROCESO DE PENSAMIENTO (Cadena de Razonamiento) ---
    
    PASO 1: ANÁLISIS DEL MODELO DE CONTRATO (Legal y Riesgos)
    - Escanea el documento buscando cláusulas de penalización, tiempos de entrega y garantías.
    - Ignora los detalles técnicos por ahora. Céntrate en las reglas del juego.
    
    PASO 2: ANÁLISIS DE CRITERIOS DE EVALUACIÓN (Estrategia)
    - Busca la sección "Forma de Evaluación". ¿Cómo ganamos?
    - Clasifica en: COSTO, PUNTOS o BINARIO.
    
    PASO 3: MATCHING TÉCNICO FILTRADO POR PREFERENCIA
    - Ahora sí, busca los productos.
    - Aplica la "Preferencia del Usuario" como filtro prioritario.
    - Cruza con el Catálogo. Si no existe, sugiere TERCERIA.
    
    DOCUMENTO A PROCESAR:
    {text[:500000]}
    
    --- SALIDA ESTRUCTURADA (JSON) ---
    Responde SOLO con este JSON:
    {{
        "segmento_contrato": {{
            "riesgos_detectados": ["Riesgo 1", "Riesgo 2"],
            "condiciones_pago": "Texto breve"
        }},
        "segmento_evaluacion": {{
            "metodo": "COSTO / PUNTOS / BINARIO",
            "detalles": "Resumen de cómo puntúan"
        }},
        "segmento_tecnico": [
            {{
                "partida": "1",
                "requerimiento": "...",
                "solucion_propuesta": "...",
                "match_status": "CATALOGO / TERCERIA",
                "nota_ajuste": "Cumple con preferencia de usuario porque..."
            }}
        ]
    }}
    """
    
    try:
        res = model.generate_content(prompt)
        clean = res.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception as e:
        return {"error": str(e)}

# --- UI ---
def main():
    st.sidebar.title("Licitation AI")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    
    st.title("Licitation AI")
    
    # Input 1: Documento
    uploaded_file = st.file_uploader("1. Cargar Licitación (PDF Mixto)", type="pdf")
    
    # Input 2: Preferencia de Usuario (Crucial para el paso 3 de la lógica)
    input_usuario = st.text_input(
        "2. Preferencias de Usuario (Input Lógico):",
        placeholder="Ej: Priorizar marcas americanas, ignorar garantías extendidas..."
    )

    if uploaded_file and st.button("Ejecutar"):
        if not api_key:
            st.error("Falta API Key")
            return

        # 1. EJECUCIÓN INGESTA HÍBRIDA
        with st.status("Paso 1: Ingesta y Clasificación Híbrida...", expanded=True) as status:
            texto, logs = procesar_pdf_hibrido(uploaded_file)
            ocr_count = logs.count("OCR")
            st.write(f"Procesadas {len(logs)} páginas. ({ocr_count} requirieron OCR).")
            status.update(label="Ingesta Completada", state="complete", expanded=False)

        # 2. EJECUCIÓN RAZONAMIENTO
        with st.spinner("Ejecutando Chunking Estratégico (Contrato -> Evaluación -> Técnico)"):
            data = analizar_con_logica(texto, api_key, input_usuario)
            
            if "error" in data:
                st.error(f"Fallo en razonamiento: {data['error']}")
            else:
                # VISUALIZACIÓN DE LOS 3 SEGMENTOS LÓGICOS
                
                st.divider()
                
                # Segmento 1: Contrato
                with st.container():
                    st.subheader("Modelo de Contrato (Riesgos)")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown("Condiciones Pago:")
                        st.info(data['segmento_contrato'].get('condiciones_pago', 'N/A'))
                    with col2:
                        st.markdown("Alertas de Riesgo:")
                        for r in data['segmento_contrato'].get('riesgos_detectados', []):
                            st.warning(r)

                st.divider()

                # Segmento 2: Evaluación
                with st.container():
                    st.subheader("Criterios de Evaluación")
                    metodo = data['segmento_evaluacion'].get('metodo', 'N/A')
                    st.metric("Método Ganador", value=metodo, delta="Estrategia Definida")
                    st.caption(f"Detalle: {data['segmento_evaluacion'].get('detalles')}")

                st.divider()

                # Segmento 3: Técnico (Filtrado)
                with st.container():
                    st.subheader(f"Solución Técnica (Ajustada a: '{input_usuario}')")
                    df = pd.DataFrame(data.get('segmento_tecnico', []))
                    st.dataframe(
                        df,
                        column_config={
                            "match_status": st.column_config.TextColumn("Origen"),
                            "nota_ajuste": st.column_config.TextColumn("Lógica Aplicada")
                        },
                        use_container_width=True
                    )

if __name__ == "__main__":
    main()