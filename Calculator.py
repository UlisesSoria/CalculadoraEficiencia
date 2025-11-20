import streamlit as st
import pandas as pd

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Calculadora de Valor Industrial", layout="wide", page_icon="🏭")

# TÍTULO Y ENCABEZADO
st.title("🏭 Calculadora de Ingeniería de Valor")

# CSS PARA ESTILO "BRUTAL"
st.markdown("""
<style>
    .metric-box {
        background-color: #f0f2f6;
        border-left: 5px solid #ff4b4b;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .success-box {
        background-color: #e6fffa;
        border-left: 5px solid #00cc96;
        padding: 15px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- PESTAÑAS DE NAVEGACIÓN ---
tab1, tab2 = st.tabs(["💰 ROI Operativo (OEE)", "🛡️ ROI Ciberseguridad"])

# ==============================================================================
# TAB 1: ROI OPERATIVO (La Verdad Financiera)
# ==============================================================================
with tab1:
    st.header("Análisis de Retorno por Eficiencia (OEE)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1. Datos de Planta")
        prod_anual = st.number_input("Producción Anual (Unidades)", value=500000, step=1000)
        precio_unit = st.number_input("Precio de Venta Unitario ($)", value=10.0)
        margen_pct = st.slider("Margen de Ganancia Neto (%)", 5, 60, 30) / 100
        
        st.subheader("2. Datos Operativos")
        horas_anuales = st.number_input("Horas Operativas Anuales", value=4000)
        costo_hora_duro = st.number_input("Costo Operativo por Hora (Nómina+Luz) ($)", value=500.0, help="Solo costos que se pagan sí o sí. NO incluyas lucro cesante aquí.")
        
        st.subheader("3. Tu Solución")
        costo_solucion = st.number_input("Inversión Anual Proyecto ($)", value=15000.0)
        mejora_oee = st.slider("Mejora Estimada de Eficiencia (%)", 1, 15, 5, help="Sé conservador. 5-7% es realista al inicio.") / 100

    with col2:
        st.subheader("Resultados Financieros")
        
        # CÁLCULOS (Lógica Corregida)
        # 1. Ganancia por Volumen (Opportunity Cost)
        unidades_hora = prod_anual / horas_anuales
        horas_ganadas = horas_anuales * mejora_oee
        unidades_extra = horas_ganadas * unidades_hora
        ganancia_extra = unidades_extra * precio_unit * margen_pct
        
        # 2. Ahorro por Eficiencia (Hard Costs)
        ahorro_costos = horas_ganadas * costo_hora_duro
        
        # 3. Totales
        beneficio_total = ganancia_extra + ahorro_costos
        net_value = beneficio_total - costo_solucion
        roi = (net_value / costo_solucion) * 100 if costo_solucion > 0 else 0
        payback = (costo_solucion / beneficio_total) * 12 if beneficio_total > 0 else 0
        
        # VISUALIZACIÓN
        c1, c2, c3 = st.columns(3)
        c1.metric("Beneficio Total Anual", f"${beneficio_total:,.0f}")
        c2.metric("ROI del Proyecto", f"{roi:.1f}%", delta_color="normal")
        c3.metric("Tiempo de Retorno", f"{payback:.1f} Meses", delta_color="inverse")
        
        st.markdown("---")
        st.write("### Desglose del Valor Generado")
        
        st.info(f"""
        **1. Dinero Nuevo (Ventas Adicionales):** ${ganancia_extra:,.2f}
        *Se genera al producir {int(unidades_extra):,} unidades más con los mismos recursos.*
        
        **2. Dinero Ahorrado (Eficiencia):** ${ahorro_costos:,.2f}
        *Se recupera al eliminar {int(horas_ganadas)} horas de desperdicio operativo (energía, nómina muerta).*
        """)
        
        if roi > 100:
            st.success("✅ **VEREDICTO:** El proyecto se paga solo en menos de un año fiscal. Es financieramente irresponsable no hacerlo.")
        elif roi > 0:
            st.warning("⚠️ **VEREDICTO:** El proyecto es rentable, pero el margen es ajustado. Requiere ejecución impecable.")
        else:
            st.error("🛑 **VEREDICTO:** No es viable con estos números. Necesitamos reducir el costo de la solución o encontrar más ineficiencias.")

# ==============================================================================
# TAB 2: ROI CIBERSEGURIDAD (El Slider de la Verdad)
# ==============================================================================
with tab2:
    st.header("Análisis de Riesgo Financiero (ALE)")
    
    col_cyber1, col_cyber2 = st.columns([1, 2])
    
    with col_cyber1:
        ingreso_diario = st.number_input("Ingreso Diario de la Planta ($)", value=50000.0)
        dias_paro = st.slider("Días de Paro por Ransomware", 1, 30, 14, help="El promedio de la industria es 21 días para recuperación total.")
        probabilidad = st.slider("Probabilidad de Ataque Anual (%)", 1, 50, 10, help="Deja que el cliente mueva esto.") / 100
        costo_ciber = st.number_input("Costo Solución Ciberseguridad ($)", value=12000.0)
        mitigacion = st.slider("Capacidad de Mitigación (%)", 50, 99, 85) / 100
        
    with col_cyber2:
        # CÁLCULOS
        impacto_evento = (ingreso_diario * dias_paro) * 1.2 # 1.2 factor de recuperación técnica
        ale_actual = impacto_evento * probabilidad
        ale_futuro = ale_actual * (1 - mitigacion)
        ahorro_riesgo = ale_actual - ale_futuro
        roi_ciber = ((ahorro_riesgo - costo_ciber) / costo_ciber) * 100 if costo_ciber > 0 else 0
        
        st.subheader("Exposición al Riesgo")
        
        c_a, c_b = st.columns(2)
        c_a.metric("Costo de UN evento catastrófico", f"${impacto_evento:,.0f}")
        c_b.metric("Pérdida Anual Esperada (ALE Actual)", f"${ale_actual:,.0f}", delta="- Riesgo Puro")
        
        st.markdown("---")
        st.subheader("Impacto de la Protección")
        st.write(f"Al reducir el riesgo un **{mitigacion*100:.0f}%**, proteges valor por:")
        st.title(f"${ahorro_riesgo:,.0f} / año")
        
        st.metric("ROI de la Protección", f"{roi_ciber:.1f}%")
        
        chart_data = pd.DataFrame({
            "Escenario": ["Riesgo Actual", "Riesgo con Solución"],
            "Pérdida Esperada ($)": [ale_actual, ale_futuro]
        })
        st.bar_chart(chart_data, x="Escenario", y="Pérdida Esperada ($)")

# ==============================================================================
# TAB 3: SIMULADOR DE ESTRATEGIA (Lógica de Dependencias)
# ==============================================================================
# with tab3:
#     st.header("Priorización de Inversiones")
#     st.markdown("Simulador de presupuesto basado en dependencias técnicas (No puedes predecir sin medir).")
#     
#     presupuesto = st.number_input("💰 Presupuesto Disponible ($)", value=40000.0, step=5000.0)
#     
#     st.write("Selecciona los módulos a implementar:")
#     
#     col_s1, col_s2 = st.columns(2)
#     
#     with col_s1:
#         check_monitoreo = st.checkbox("1. Monitoreo Básico (OEE)", value=True, help="Costo: $10k. Requisito base.")
#         check_integracion = st.checkbox("2. Integración IT/OT (Gateway)", value=False, help="Costo: $15k. Requiere Monitoreo.")
#         check_predictivo = st.checkbox("3. Analítica Predictiva (IA)", value=False, help="Costo: $25k. Requiere Integración.")
#         check_ciber = st.checkbox("4. Ciberseguridad Industrial", value=False, help="Costo: $8k. Crítico.")
#         
#     # LÓGICA DE DEPENDENCIAS Y PRESUPUESTO
#     costos_items = {
#         "Monitoreo": 10000, "Integración": 15000, "Predictivo": 25000, "Ciberseguridad": 8000
#     }
#     impacto_items = { # Impacto en productividad
#         "Monitoreo": 0.05, "Integración": 0.03, "Predictivo": 0.12, "Ciberseguridad": 0.0
#     }
#     
#     gasto_total = 0
#     impacto_total = 0
#     mensajes = []
#     estado = "OK"
#     
#     # Validación Lógica
#     if check_monitoreo:
#         gasto_total += costos_items["Monitoreo"]
#         impacto_total += impacto_items["Monitoreo"]
#     
#     if check_integracion:
#         if not check_monitoreo:
#             mensajes.append("❌ ERROR: No puedes integrar IT/OT sin Monitoreo base.")
#             estado = "ERROR"
#         else:
#             gasto_total += costos_items["Integración"]
#             impacto_total += impacto_items["Integración"]
#             
#     if check_predictivo:
#         if not check_integracion:
#             mensajes.append("❌ ERROR: La IA Predictiva requiere Integración IT/OT (Datos limpios).")
#             estado = "ERROR"
#         else:
#             gasto_total += costos_items["Predictivo"]
#             impacto_total += impacto_items["Predictivo"]
#             
#     if check_ciber:
#         gasto_total += costos_items["Ciberseguridad"]
#         # No suma productividad directa, pero es necesaria.
# 
#     with col_s2:
#         st.subheader("Análisis de Viabilidad")
#         
#         if estado == "ERROR":
#             for msg in mensajes:
#                 st.error(msg)
#         else:
#             # Chequeo de Presupuesto
#             if gasto_total > presupuesto:
#                 st.error(f"💸 PRESUPUESTO EXCEDIDO por ${gasto_total - presupuesto:,.0f}")
#             else:
#                 st.success(f"✅ Estrategia Viable. Sobran ${presupuesto - gasto_total:,.0f}")
#                 
#                 st.markdown(f"""
#                 <div class="success-box">
#                     <h3>Resultados Proyectados:</h3>
#                     <ul>
#                         <li><strong>Inversión Total:</strong> ${gasto_total:,.0f}</li>
#                         <li><strong>Mejora Productiva Estimada:</strong> {impacto_total*100:.1f}%</li>
#                         <li><strong>Estado de Seguridad:</strong> {'🔒 Protegido' if check_ciber else '⚠️ RIESGO ALTO (Sin Ciberseguridad)'}</li>
#                     </ul>
#                 </div>
#                 """, unsafe_allow_html=True)
#                 
#                 # Barra de progreso del presupuesto
#                 pct_uso = gasto_total / presupuesto
#                 st.write(f"Uso de Presupuesto: {pct_uso*100:.1f}%")
#                 st.progress(pct_uso)