import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import pandas as pd
import json
import io
import time
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Licitacion AI", layout="wide")

# --- APARIENCIA ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .glass-box { background-color: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 20px; border-radius: 10px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1); }
    
    /* Toggle Switch Style for Radio Buttons */
    div[data-testid="stRadio"] > div {
        background-color: #1e293b;
        padding: 4px;
        border-radius: 12px;
        display: inline-flex;
        gap: 0px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    div[data-testid="stRadio"] label {
        background-color: transparent;
        border-radius: 8px;
        padding: 8px 24px;
        margin: 0 !important;
        transition: all 0.3s ease;
        border: none;
        color: #94a3b8;
        cursor: pointer;
    }
    
    div[data-testid="stRadio"] label:hover {
        color: #e2e8f0;
        background-color: rgba(255,255,255,0.05);
    }

    /* Hide the default circle */
    div[data-testid="stRadio"] label > div:first-child {
        display: none;
    }
    
    /* Selected State */
    div[data-testid="stRadio"] label:has(input:checked) {
        background-color: #8b5cf6; /* Violeta Premium */
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    div[data-testid="stRadio"] p {
        font-size: 16px;
    }

    /* Estilo para el chat */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

CATALOGO_MOCK = """
1. SKU: CS-9200L-48P | Marca: Cisco | Switch Catalyst 9200L 48 puertos PoE+. Precio: $4,500.
2. SKU: DL-R750-XS | Marca: Dell | Servidor PowerEdge R750 Xeon Gold. Precio: $12,500.
3. SKU: FG-60F-BDL | Marca: Fortinet | Firewall FortiGate 60F. Precio: $950.
"""

# --- 1. CARGA DE ARCHIVOS ---
def procesar_archivo_individual(file_obj, filename):
    """Lee un archivo PDF y devuelve su texto."""
    if isinstance(file_obj, str): 
         with open(file_obj, "rb") as f: file_bytes = f.read()
    else: 
        file_bytes = file_obj.getvalue()

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        texto_archivo = f"\n\n--- INICIO DOCUMENTO: {filename} ---\n"
        for i, page in enumerate(reader.pages):
            texto_archivo += page.extract_text() or ""
        texto_archivo += f"\n--- FIN DOCUMENTO: {filename} ---\n"
        return texto_archivo
    except Exception as e:
        return f"\n[ERROR LEYENDO {filename}]: {str(e)}\n"

# --- 2. LLAMADA A IA (EXTRACCIÓN) ---
def llamada_segura_ia(model, prompt, modulo_nombre):
    """Realiza una llamada a la API con manejo de errores y reintentos."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            res = model.generate_content(prompt)
            clean = res.text.replace("```json", "").replace("```", "").strip()
            if "{" in clean: clean = clean[clean.find("{"):clean.rfind("}")+1]
            return json.loads(clean)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait = (attempt + 1) * 10
                st.toast(f"Cuota excedida. Esperando {wait}s para módulo {modulo_nombre}...", icon="⏸️")
                time.sleep(wait)
            else:
                return {} 
    return {}

def ejecutar_analisis_modular(text, gemini_key, enfoque):
    genai.configure(api_key=gemini_key)
    # Usamos flash para la extracción inicial
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    resultados_totales = {}
    
    # --- ANALISIS GENERAL (Resumen y Cronograma) ---
    with st.spinner("Análisis Estratégico y Cronograma..."):
        prompt_1 = f"""
        ERES: Un Analista Senior de Licitaciones.
        
        INSTRUCCIONES DE EXTRACCIÓN (SECCIÓN GENERAL):
        1. RESUMEN EJECUTIVO:
           - Identifica la ENTIDAD compradora.
           - Genera un párrafo describiendo el OBJETO.
           - Genera un breve resumen de la licitación.
        
        2. CRONOGRAMA DE EVENTOS:
           - Extrae eventos clave (Junta de Aclaraciones, Fallo, Visita a instalaciones, etc.) y sus fechas (DD/MM/AAAA).
           - Si menciona un RESPONSABLE o nota específica, agrégalo.
        
        3. ANÁLISIS ESTRATÉGICO:
           - Método de Evaluación (Costo, Puntos, Binario).
           - Presupuesto máximo.

        DOCUMENTO CONSOLIDADO: {text[:500000]} 
        
        SALIDA JSON: 
        {{ 
            "resumen": {{ "entidad": "...", "objeto": "...", "presupuesto": "..." }}, 
            "eventos": [ {{ "evento": "...", "fecha": "...", "responsable_notas": "..." }} ],
            "evaluacion": {{ "metodo": "...", "detalles": "..." }}
        }}
        """
        data_1 = llamada_segura_ia(model, prompt_1, "General")
        resultados_totales.update(data_1)
    
    time.sleep(2)

    # --- ANALISIS LEGAL (Control y Cumplimiento) ---
    with st.spinner("Auditoría Legal y Documental (DA/DT)..."):
        prompt_2 = f"""
        ERES: Abogado Auditor de Licitaciones.
        ENFOQUE: "{enfoque}"
        
        INSTRUCCIONES DE EXTRACCIÓN (SECCIÓN LEGAL):
        1. MATRIZ DE CONTROL (DOCUMENTAL):
           - Lista de documentos obligatorios (Legal, Admin, Financiero).
           - Extrae el nombre exacto y los CRITERIOS DE EVALUACIÓN específicos.
        
        2. MATRIZ DE CUMPLIMIENTO (PROCESO):
           - Reglas de negocio y causas de desechamiento.
           - Indica si es INDISPENSABLE o si es causas de desechamiento o no.
        
        Utiliza una evaluación binaria (SI/NO).

        DOCUMENTO CONSOLIDADO: {text[:500000]}
        
        SALIDA JSON: 
        {{ 
            "matriz_control": [ {{ "documento": "...", "criterio": "...", "tipo": "LEGAL/FINANCIERO" }} ], 
            "matriz_cumplimiento": [ {{ "requisito": "...", "indispensable": "SI/NO", "causa_incumplimiento": "..." }} ] 
        }}
        """
        data_2 = llamada_segura_ia(model, prompt_2, "Legal")
        resultados_totales.update(data_2)

    time.sleep(2) 

    # --- ANALISIS TECNICO (Productos) ---
    with st.spinner("Ingeniería y Catálogo..."):
        prompt_3 = f"""
        ERES: Ingeniero Preventa Experto.
        CATÁLOGO PROPIO: {CATALOGO_MOCK}
        
        INSTRUCCIONES DE EXTRACCIÓN (SECCIÓN TÉCNICA):
        1. MATCHING TÉCNICO (PRODUCTOS):
           - Extrae las partidas de hardware/software.
           - Extrae el nombre exacto y los CRITERIOS DE EVALUACIÓN específicos.
           - Cruza con CATÁLOGO PROPIO. 
           - Si Match > 70%, asigna SKU y marca origen como "INTERNO".
           - Si NO encuentras en catálogo, marca como "COTIZAR MANUAL" (No busques en web).
           - Si es Obra Civil/Torres/Infraestructura, marca "TERCERIA".

        DOCUMENTO CONSOLIDADO: {text[:500000]}
        
        SALIDA JSON: 
        {{ 
            "matriz_tecnica": [ {{ "partida": "...", "descripcion": "...", "propuesta": "...", "score": "...", "origen": "..." }} ] 
        }}
        """
        data_3 = llamada_segura_ia(model, prompt_3, "Técnico")
        resultados_totales.update(data_3)

    return resultados_totales

# --- 3. FUNCIÓN DE CHAT ---
def generar_respuesta_chat(prompt_usuario, contexto_texto, contexto_datos, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash') # Flash es ideal para ventanas de contexto grandes (1M tokens)
    
    # Construimos un prompt que incluye el contexto de la licitación
    prompt_sistema = f"""
    ERES: Un Asistente Experto en Licitaciones (LiciBot).
    TU TAREA: Responder dudas del usuario basándote EXCLUSIVAMENTE en la información de la licitación proporcionada.
    
    CONTEXTO ESTRUCTURADO (Resumen de lo que ya analizaste):
    {json.dumps(contexto_datos, ensure_ascii=False)}
    
    CONTEXTO COMPLETO DEL DOCUMENTO (Referencia cruda):
    {contexto_texto[:800000]} 

    PREGUNTA DEL USUARIO: {prompt_usuario}
    
    REGLAS:
    1. Sé directo y profesional.
    2. Cita la sección o página si es posible (basado en el texto).
    3. Si la respuesta no está en el documento, dilo claramente.
    """
    
    try:
        response = model.generate_content(prompt_sistema)
        return response.text
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

# --- 4. EXPORTAR EXCEL ---
def format_excel(writer, df, sheet):
    wb = writer.book
    ws = writer.sheets[sheet]
    fmt = wb.add_format({'bold': True, 'bg_color': '#1f497d', 'font_color': 'white', 'border': 1, 'text_wrap': True, 'valign': 'top'})
    text_fmt = wb.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
    
    for col_num, value in enumerate(df.columns.values):
        ws.write(0, col_num, value, fmt)
        ws.set_column(col_num, col_num, 25, text_fmt)

# --- UI ---
def main():
    # --- GESTIÓN DE ESTADO (SESSION STATE) ---
    # Inicializamos variables para que no se borren al usar el chat
    if "analisis_completo" not in st.session_state:
        st.session_state.analisis_completo = False
    if "resultados" not in st.session_state:
        st.session_state.resultados = {}
    if "texto_completo" not in st.session_state:
        st.session_state.texto_completo = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    with st.sidebar:
        st.title("Configuración")
        api_key = st.text_input("Gemini API Key", type="password")
        st.success("OCR Activo")
        
        if st.session_state.analisis_completo:
            if st.button("Limpiar Análisis"):
                st.session_state.analisis_completo = False
                st.session_state.resultados = {}
                st.session_state.texto_completo = ""
                st.session_state.chat_history = []
                st.rerun()

    st.title("Licitacion AI")
    st.markdown("Carga licitaciones complejas (Bases + Anexos), analiza y **chatea con el documento**.")

    # --- SELECTOR DE LICITACION ---
    st.write("Tipo de Análisis:")
    tipo_licitacion = st.radio(
        "Tipo de Análisis:", 
        ["Simple", "Compleja"], 
        horizontal=True,
        label_visibility="collapsed"
    )
    
    archivos_procesar = []

    # Lógica de Selección de Archivos
    if tipo_licitacion == "Simple":
        f = st.file_uploader("Cargar Bases", type="pdf")
        if f: archivos_procesar = [(f, f.name)]

    elif tipo_licitacion == "Compleja":
        files = st.file_uploader("Cargar Documentación Completa", type="pdf", accept_multiple_files=True)
        if files: archivos_procesar = [(f, f.name) for f in files]

    enfoque = st.text_input("Enfoque:", "Cumplimiento estricto de formatos DA/DT")

    # Botón de análisis (Solo procesa si no se ha hecho ya)
    if st.button("INICIAR ANÁLISIS") and archivos_procesar:
        if not api_key: 
            st.error("Falta API Key")
        else:
            # 1. Ingesta de Documentos
            texto_consolidado = ""
            barra = st.progress(0)
            status_text = st.empty()
            
            for i, (archivo, nombre) in enumerate(archivos_procesar):
                status_text.text(f"Leyendo: {nombre}...")
                texto_doc = procesar_archivo_individual(archivo, nombre)
                texto_consolidado += texto_doc
                barra.progress((i + 1) / len(archivos_procesar))
            
            status_text.empty()
            barra.empty()
            
            # 2. Análisis Modular
            data = ejecutar_analisis_modular(texto_consolidado, api_key, enfoque)
            
            if not data:
                st.error("Hubo un error crítico al procesar los módulos.")
            else:
                # GUARDAR EN SESSION STATE
                st.session_state.resultados = data
                st.session_state.texto_completo = texto_consolidado
                st.session_state.analisis_completo = True
                st.success("¡Análisis Completado!")

    # --- MOSTRAR RESULTADOS (Si ya existen en memoria) ---
    if st.session_state.analisis_completo:
        data = st.session_state.resultados
        
        # Resumen
        res = data.get('resumen', {})
        st.info(f"Proyecto: {res.get('objeto', 'N/A')}")
        
        # Tabs de Tablas
        tabs = st.tabs(["Documental", "Técnica", "Cronograma"])
        with tabs[0]: 
            if data.get('matriz_control'): st.dataframe(pd.DataFrame(data.get('matriz_control')), use_container_width=True)
            else: st.warning("Sin datos documentales.")
        with tabs[1]: 
            if data.get('matriz_tecnica'): st.dataframe(pd.DataFrame(data.get('matriz_tecnica')), use_container_width=True)
            else: st.warning("Sin datos técnicos.")
        with tabs[2]: 
            if data.get('eventos'): st.dataframe(pd.DataFrame(data.get('eventos')), use_container_width=True)

        # Botón de Descarga Excel
        buff = io.BytesIO()
        with pd.ExcelWriter(buff, engine='xlsxwriter') as writer:
            if data.get('matriz_control'): 
                pd.DataFrame(data['matriz_control']).to_excel(writer, sheet_name='Control', index=False)
                format_excel(writer, pd.DataFrame(data['matriz_control']), 'Control')
            if data.get('matriz_cumplimiento'): 
                pd.DataFrame(data['matriz_cumplimiento']).to_excel(writer, sheet_name='Cumplimiento', index=False)
                format_excel(writer, pd.DataFrame(data['matriz_cumplimiento']), 'Cumplimiento')
            if data.get('matriz_tecnica'): 
                pd.DataFrame(data['matriz_tecnica']).to_excel(writer, sheet_name='Tecnica', index=False)
                format_excel(writer, pd.DataFrame(data['matriz_tecnica']), 'Tecnica')
            if data.get('eventos'): 
                pd.DataFrame(data['eventos']).to_excel(writer, sheet_name='Cronograma', index=False)
                format_excel(writer, pd.DataFrame(data['eventos']), 'Cronograma')
            pd.DataFrame([res]).to_excel(writer, sheet_name='Resumen', index=False)

        st.download_button("Bajar Reporte Excel", buff.getvalue(), "Reporte_Licitacion.xlsx")

        # --- SECCIÓN DE CHATBOT ---
        st.divider()
        st.subheader("Chat con la Licitación")
        st.markdown("Pregunta sobre penalizaciones, direcciones de entrega, o detalles específicos.")

        # Mostrar historial de chat
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input de chat
        if prompt := st.chat_input("Escribe tu pregunta aquí..."):
            if not api_key:
                st.error("Se requiere API Key para chatear.")
            else:
                # Mostrar mensaje usuario
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Generar respuesta
                with st.chat_message("assistant"):
                    with st.spinner("Consultando las bases..."):
                        respuesta = generar_respuesta_chat(
                            prompt, 
                            st.session_state.texto_completo, 
                            st.session_state.resultados, 
                            api_key
                        )
                        st.markdown(respuesta)
                
                # Guardar respuesta
                st.session_state.chat_history.append({"role": "assistant", "content": respuesta})

if __name__ == "__main__":
    main()