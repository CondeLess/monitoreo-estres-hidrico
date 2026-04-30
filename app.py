def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Llamar a la función al principio del script
local_css("style.css")

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# =================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# =================================================================
st.set_page_config(page_title="Dashboard IoT - Vigna unguiculata", layout="wide", page_icon="🌱")

st.title("🌱 Monitoreo IoT: Estrés Hídrico en Vigna unguiculata")
st.markdown("""
Esta plataforma permite el análisis en tiempo real de datos recolectados por nodos sensores ESP32. Desarrollado para el **Semillero de Investigación en Agrotecnología (CIATEC)**.
""")
st.markdown("---")

# =================================================================
# 2. FUNCIONES DE APOYO (Datos y Simulación)
# =================================================================
@st.cache_data
def generar_datos_simulados():
    """Genera un set de datos coherente con el comportamiento de la Vigna."""
    fechas = pd.date_range(start="2026-03-01", periods=48, freq="h")
    # Simulación física de desecación
    fechas = pd.date_range(start="2026-03-01", periods=48, freq="h")
    h_control = np.linspace(60, 50, 48) + np.random.normal(0, 1, 48)
    h_estres = np.linspace(60, 25, 48) + np.random.normal(0, 1.5, 48)
    temp = 22 + 8 * np.sin(np.linspace(0, 4 * np.pi, 48)) + np.random.normal(0, 0.5, 48)
    return pd.DataFrame({'Fecha_Hora': fechas, 'Control_Humedad(%)': h_control, 'Estres_Humedad(%)': h_estres, 'Temperatura(°C)': temp})

# =================================================================
# 3. PANEL LATERAL (SIDEBAR) - CONFIGURACIÓN EDÁFICA
# =================================================================
st.sidebar.header("⚙️ Gestión y Carga de Datos")
archivo_subido = st.sidebar.file_uploader("Sube tu reporte (.csv)", type=["csv"])

with st.sidebar.expander("Ver formato requerido del CSV"):
    st.code("""
- Fecha_Hora
- Control_Humedad(%)
- Estres_Humedad(%)
- Temperatura(°C) (Opcional)
    """)
# Diccionario ampliado de texturas
st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Caracterización del Suelo")
pmp_teoricos = {
    "Arena": 5.0, "Arena Franca": 7.0, "Franco Arenoso": 10.0, 
    "Franco": 14.0, "Franco Limoso": 18.0, "Franco Arcillo-Arenoso": 20.0,
    "Franco Arcilloso": 22.0, "Arcilla": 28.0, "Personalizado": 15.0
}

textura = st.sidebar.selectbox(
    "Textura del Suelo",
    options=list(pmp_teoricos.keys()),
    index=3,
    help="Define el PMP teórico inicial según la capacidad de retención."
)
# Estructura del Suelo (Influencia en porosidad)
estructuras = {
    "Granular (Óptima)": 1.0,
    "Bloques Subangulares": 1.1,
    "Prismática": 1.2,
    "Masiva / Compactada": 0.8,
    "Plaminar": 0.9
}
estructura = st.sidebar.selectbox("Estructura del Suelo", options=list(estructuras.keys()), index=0, 
                                  help="La estructura modifica la retención hídrica real más allá de la textura.")

# Inicialización segura del Session State
if 'umbral_dinamico' not in st.session_state:
    st.session_state.umbral_dinamico = pmp_teoricos[textura] * estructuras[estructura]

# Lógica de Umbral Manual
if textura == "Personalizado":
    pmp_manual = st.sidebar.number_input("PMP Manual (%)", 1.0, 45.0, float(st.session_state.umbral_dinamico))
    st.session_state.umbral_dinamico = pmp_manual
else:
    if st.sidebar.button("Calcular Umbral Teórico"):
        st.session_state.umbral_dinamico = pmp_teoricos[textura] * estructuras[estructura]

# AJUSTE FINO DEL UMBRAL
st.session_state.umbral_dinamico = st.sidebar.slider("Ajuste Fino de Umbral (%)", 1.0, 45.0, 
                                                     float(st.session_state.umbral_dinamico),
                                                     help="Modifica manualmente el punto crítico para los cálculos predictivos.")

# Branding CIATEC
st.sidebar.markdown("---") 
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
    st.sidebar.caption("Investigación Agronómica - UNALM") 

# =================================================================
# 4. LÓGICA DE DATOS Y KPIs
# =================================================================
datos = pd.read_csv(archivo_subido) if archivo_subido else generar_datos_simulados()
tiene_temp = 'Temperatura(°C)' in datos.columns

st.subheader("📊 Monitoreo en Tiempo Real")
col_k1, col_k2, col_k3 = st.columns(3)
if tiene_temp:
    col_k1.metric("Temp. Ambiente", f"{datos['Temperatura(°C)'].iloc[-1]:.1f} °C")
col_k2.metric("Humedad Control", f"{datos['Control_Humedad(%)'].iloc[-1]:.1f} %")
col_k3.metric("Humedad Tratamiento", f"{datos['Estres_Humedad(%)'].iloc[-1]:.1f} %", delta="- Crítico", delta_color="inverse")

# =================================================================
# 5. ANÁLISIS TEMPORAL Y VISUALIZACIÓN de DATOs
# =================================================================
st.markdown("### 📈 Dinámica Temporal.")
if tiene_temp:
    cg1, cg2 = st.columns(2)
    with cg1:
        st.plotly_chart(px.line(datos, x='Fecha_Hora', y=['Control_Humedad(%)', 'Estres_Humedad(%)'], 
                                title='Dinámica de Humedad del Suelo'), use_container_width=True)
    with cg2:
        st.plotly_chart(px.line(datos, x='Fecha_Hora', y='Temperatura(°C)', 
                                title='Dinámica de Temperatura', color_discrete_sequence=['orange']), use_container_width=True)
else:
    st.plotly_chart(px.line(datos, x='Fecha_Hora', y=['Control_Humedad(%)', 'Estres_Humedad(%)'], 
                            title='Dinámica de Humedad del Suelo'), use_container_width=True)

# =================================================================
# 6. MÓDULO DE INTELIGENCIA AGRONÓMICA
# =================================================================
st.markdown("### 🧬 Análisis Estadístico Avanzado")
c_st1, c_st2, c_st3 = st.columns(3)

with c_st1:
    # DIFERENCIA DE MEDIAS
    diff = datos['Control_Humedad(%)'].mean() - datos['Estres_Humedad(%)'].mean()
    st.metric("Diferencia Media", f"{diff:.1f}%")
    st.caption("Representa la magnitud de la brecha hídrica constante generada por el tratamiento de estrés.")

with c_st2:
    # CORRELACIÓN
    if tiene_temp:
        r_pearson = datos[['Control_Humedad(%)', 'Temperatura(°C)']].corr().iloc[0,1]
        st.metric("Correlación (H-T)", f"{r_pearson:.2f}")
        st.caption("Coeficiente de Pearson. Si es negativo, el calor está forzando la desecación del suelo.")

with c_st3:
    # INTEGRAL DE ESTRÉS
    area = np.trapezoid(datos['Control_Humedad(%)'] - datos['Estres_Humedad(%)'])
    st.metric("Estrés Acumulado", f"{area:.1f} %-h")
    st.caption("Integral numérica: Regla del trapecio. Cuantifica la severidad acumulada del déficit hídrico en el tiempo.")

# =================================================================
# 7. PRONÓSTICO Y MODELADO PREDICTIVO
# =================================================================
st.markdown("---")
st.subheader("🔮 Pronóstico de Agotamiento (Mínimos Cuadrados)")
y = datos['Estres_Humedad(%)'].values
x = np.arange(len(y))
slope, intercept = np.polyfit(x, y, 1)

if slope < 0:
    t_restante = (st.session_state.umbral_dinamico - y[-1]) / slope
    if t_restante > 0:
        st.warning(f"⚠️ El umbral de **{st.session_state.umbral_dinamico:.1f}%** se alcanzará en **{t_restante:.1f} horas**.")
    else:
        st.error(f"🚨 Alerta: Umbral crítico de **{st.session_state.umbral_dinamico:.1f}%** ya ha sido superado.")
else:
    st.success("✅ Estabilidad hídrica detectada. No se proyecta estrés inmediato.")

# =================================================================
# 8. VALIDACIÓN BIOLÓGICA Y DATOS CRUDOS
# =================================================================
st.markdown("### 🌿 Validación Biológica (Ground Truth)")
cb1, cb2 = st.columns([1, 2])

with cb1:
    if st.button("Marcar Estrés Visual"):
        st.session_state.umbral_dinamico = datos['Estres_Humedad(%)'].iloc[-1]
        st.rerun()

with cb2:
    st.info(f"**Umbral actual calibrado:** {st.session_state.umbral_dinamico:.1f}%.")
    st.caption("Usa el botón al observar marchitez foliar para sincronizar el modelo con la fisiología vegetal.")

with st.expander("Inspeccionar Base de Datos"):
    st.dataframe(datos, use_container_width=True)

st.markdown("---")
st.caption(f"© 2026 Carlos Condemarin | CIATEC - UNALM | Suelo: {textura} - {estructura}")
