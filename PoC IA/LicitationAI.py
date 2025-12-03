import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import pandas as pd
import json
import io

# --- Configuración de ventana ---
st.set_page_config(page_title="Licitation AI", layout="wide")

# --- Formato ---
st.markdown("""
<style>
    .stAlert { border-radius: 8px; }
    .metric-card { background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; text-align: center; }
    .metric-value { font-size: 24px; font-weight: bold; color: #0f172a; }
    .metric-label { font-size: 14px; color: #64748b; }
</style>
""", unsafe_allow_html=True)

# --- CATÁLOGO MOCK (reemplazar por el nuestro) ---
CATALOGO_MOCK = """
1. SKU: CS-9200L-48P | Marca: Cisco | Switch Catalyst 9200L 48 puertos PoE+. Precio: $4,500.
2. SKU: DL-R750-XS | Marca: Dell | Servidor PowerEdge R750 Xeon Gold. Precio: $12,500.
3. SKU: FG-60F-BDL | Marca: Fortinet | Firewall FortiGate 60F. Precio: $950.
4. SKU: MS-OFF-PRO | Marca: Microsoft | Licencia Office Pro 2021. Precio: $350.
"""

def get_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def analizar_completo(text, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash') # Usar Flash para velocidad, Pro para razonamiento complejo
    
    # --- Prompt ---
    prompt = f"""
    ERES: Un Analista Senior de Licitaciones y Preventa Técnica.
    
    OBJETIVO: Analizar el pliego de licitación y extraer datos estructurados Administrativos y Técnicos.
    
    CATÁLOGO PROPIO:
    {CATALOGO_MOCK}
    
    INSTRUCCIONES DE EXTRACCIÓN:
    
    1. SECCIÓN ADMINISTRATIVA (Clasificación):
       - Tipo de Evaluación: Elige EXACTAMENTE UNO de: ["COSTO_MINIMO", "PUNTOS_Y_PORCENTAJES", "BINARIO", "DESCONOCIDO"].
       - Fechas Clave: Extrae 'Junta de Aclaraciones', 'Presentación de Propuestas' y 'Fallo'. Formato DD/MM/AAAA.
       - Presupuesto: Si se menciona un techo presupuestal, extráelo. Si no, pon "NO MENCIONADO".
    
    2. SECCIÓN TÉCNICA (Productos):
       - Identifica cada partida requerida.
       - Cruza con el CATÁLOGO PROPIO.
       - Asigna el producto si Match > 80%. Si no, pon "TERCERIA".
    
    DOCUMENTO DE ENTRADA:
    {text[:200000]} 
    
    FORMATO DE SALIDA (JSON ÚNICO):
    {{
        "resumen_ejecutivo": {{
            "entidad_convocante": "Nombre de la dependencia",
            "metodo_evaluacion": "ENUM_SELECCIONADO",
            "nivel_riesgo_admin": "ALTO/MEDIO/BAJO",
            "justificacion_riesgo": "Texto breve..."
        }},
        "cronograma": [
            {{ "evento": "Junta Aclaraciones", "fecha": "DD/MM/AAAA" }},
            {{ "evento": "Presentación Propuestas", "fecha": "DD/MM/AAAA" }}
        ],
        "partidas_tecnicas": [
            {{
                "partida": 1,
                "descripcion_licitacion": "...",
                "producto_propuesto": "SKU o TERCERIA",
                "match_score": 90,
                "comentario": "..."
            }}
        ]
    }}
    Responde SOLO con el JSON.
    """
    
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        st.error(f"Error en el análisis: {e}")
        try:
            st.warning("Intentando listar modelos disponibles...")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    st.write(f"- {m.name}")
        except Exception as list_e:
            st.error(f"No se pudieron listar los modelos: {list_e}")
        return None

# --- UI ---
def main():
    st.sidebar.title("Configuración")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    
    st.title("Licitation AI")
    st.markdown("Extracción simultánea de **Criterios de Evaluación** (Estrategia) y **Productos** (Técnica).")
    
    uploaded = st.file_uploader("Subir Pliego (PDF)", type="pdf")
    
    if uploaded and st.button("Ejecutar Análisis Maestro"):
        if not api_key:
            st.warning("Falta API Key")
            return
            
        with st.spinner("Leyendo, Clasificando y Cruzando datos..."):
            text = get_pdf_text(uploaded)
            data = analizar_completo(text, api_key)
            
            if data:
                # 1. Dashboard Estrategico
                st.subheader("1. Estrategia de Licitación")
                resumen = data.get("resumen_ejecutivo", {})
                
                c1, c2, c3 = st.columns(3)
                
                # Lógica visual
                metodo = resumen.get('metodo_evaluacion', 'N/A')
                color_metodo = "green" if metodo == "COSTO_MINIMO" else "blue"
                
                c1.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Método Evaluación</div>
                    <div class="metric-value" style="color:{color_metodo}">{metodo}</div>
                </div>
                """, unsafe_allow_html=True)
                
                c2.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Riesgo Admin</div>
                    <div class="metric-value">{resumen.get('nivel_riesgo_admin')}</div>
                </div>
                """, unsafe_allow_html=True)

                c3.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Dependencia</div>
                    <div class="metric-value" style="font-size:16px">{resumen.get('entidad_convocante')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.info(f"**Insight:** {resumen.get('justificacion_riesgo')}")

                # 2. Crono
                st.subheader("2. Fechas Fatales")
                fechas_df = pd.DataFrame(data.get("cronograma", []))
                st.table(fechas_df)

                # 3. Productos sugeridos
                st.subheader("3. Matriz Técnica")
                prod_df = pd.DataFrame(data.get("partidas_tecnicas", []))
                st.dataframe(prod_df, use_container_width=True)
                
                # Descarga del excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    prod_df.to_excel(writer, sheet_name='Productos', index=False)
                    fechas_df.to_excel(writer, sheet_name='Fechas', index=False)
                    pd.DataFrame([resumen]).to_excel(writer, sheet_name='Estrategia', index=False)
                    
                st.download_button(
                    label="Descargar Excel Completo (.xlsx)",
                    data=buffer.getvalue(),
                    file_name="analisis_licitacion.xlsx",
                    mime="application/vnd.ms-excel"
                )

if __name__ == "__main__":
    main()