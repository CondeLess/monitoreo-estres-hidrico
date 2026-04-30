import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# 1. Configuración básica de la página
st.set_page_config(page_title="Dashboard IoT - Vigna unguiculata Estrés Hídrico", layout="wide")

st.title("🌱 Monitoreo IoT: Estrés Hídrico en Vigna unguiculata")
st.markdown("Sube tu propio archivo de datos generado por el ESP32 o visualiza la simulación por defecto.")
st.markdown("---")

# 2. Generación de datos simulados
@st.cache_data
def generar_datos_simulados():
    fechas = pd.date_range(start="2026-03-01", periods=48, freq="h")
    humedad_control = np.linspace(60, 50, 48) + np.random.normal(0, 1, 48)
    humedad_estres = np.linspace(60, 25, 48) + np.random.normal(0, 1.5, 48)
    temperatura = 22 + 8 * np.sin(np.linspace(0, 4 * np.pi, 48)) + np.random.normal(0, 0.5, 48)
    return pd.DataFrame({
        'Fecha_Hora': fechas,
        'Control_Humedad(%)': humedad_control,
        'Estres_Humedad(%)': humedad_estres,
        'Temperatura(°C)': temperatura
    })

# 3. Panel lateral: LÓGICA DE CONFIGURACIÓN (Corregido)
st.sidebar.header("⚙️ Gestión de Datos")
archivo_subido = st.sidebar.file_uploader("Selecciona un archivo .csv", type=["csv"])

st.sidebar.markdown("---")
st.sidebar.subheader("🌱 Configuración del Suelo")

pmp_teoricos = {
    "Arenoso (Sable)": 7.0,
    "Franco (Loam)": 14.0,
    "Arcilloso (Clay)": 24.0,
    "Personalizado": 20.0
}

textura = st.sidebar.selectbox(
    "Textura del Suelo del Ensayo",
    options=list(pmp_teoricos.keys()),
    index=1,
    help="Define el punto de partida del umbral crítico basado en la capacidad de retención del suelo."
)

# --- INICIALIZACIÓN CRÍTICA (Debe ir antes de los sliders) ---
if 'umbral_dinamico' not in st.session_state:
    st.session_state.umbral_dinamico = pmp_teoricos[textura]

# Si el usuario cambia la textura en el selectbox, actualizamos el umbral
if st.sidebar.button("Aplicar valor de textura"):
    st.session_state.umbral_dinamico = pmp_teoricos[textura]

# Un solo slider consolidado para el umbral crítico
umbral_final = st.sidebar.slider(
    "Ajuste de Umbral Crítico (%)", 
    5.0, 40.0, 
    value=float(st.session_state.umbral_dinamico),
    key="slider_umbral",
    help="Este valor define el Punto de Marchitez Permanente (PMP) para los cálculos."
)
st.session_state.umbral_dinamico = umbral_final

# Logo del CIATEC
st.sidebar.markdown("---") 
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width="stretch")
    st.sidebar.caption("Desarrollado para CIATEC") 

# 4. Procesamiento de datos
if archivo_subido is not None:
    try:
        datos = pd.read_csv(archivo_subido)
        st.success("¡Archivo cargado correctamente!")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        datos = generar_datos_simulados()
else:
    datos = generar_datos_simulados()

tiene_temp = 'Temperatura(°C)' in datos.columns

# 5. Métricas (KPIs)
st.subheader("Métricas Actuales (Última Lectura)")
col1, col2, col3 = st.columns(3)
if tiene_temp:
    col1.metric("Temperatura Actual", f"{datos['Temperatura(°C)'].iloc[-1]:.1f} °C")
col2.metric("Humedad - Control", f"{datos['Control_Humedad(%)'].iloc[-1]:.1f} %")
col3.metric("Humedad - Estrés", f"{datos['Estres_Humedad(%)'].iloc[-1]:.1f} %", delta="- Crítico", delta_color="inverse")

# 6. Gráficos e Historial
st.markdown("### Análisis Temporal")
grafico_humedad = px.line(datos, x='Fecha_Hora', y=['Control_Humedad(%)', 'Estres_Humedad(%)'], title='Evolución de la Humedad del Suelo')
st.plotly_chart(grafico_humedad, use_container_width=True)

# 7. Análisis Estadístico y Predictivo
st.markdown("### 📊 Inteligencia Agronómica")
col_stat1, col_stat2 = st.columns(2)

with col_stat1:
    dif_medias = datos['Control_Humedad(%)'].mean() - datos['Estres_Humedad(%)'].mean()
    st.metric("Diferencia Media de Humedad", f"{dif_medias:.1f}%")
    st.caption("Brecha hídrica promedio entre tratamientos.")

with col_stat2:
    area_estres = np.trapezoid(datos['Control_Humedad(%)'] - datos['Estres_Humedad(%)'])
    st.metric("Integral de Estrés Acumulado", f"{area_estres:.2f} %-hora")
    st.caption("Cuantifica la severidad acumulada del déficit hídrico.")

# Predictor con Regresión
st.markdown("---")
st.subheader("🔮 Pronóstico de Agotamiento")
y = datos['Estres_Humedad(%)'].values
x = np.arange(len(y))
coef = np.polyfit(x, y, 1)
pendiente = coef[0]

if pendiente < 0:
    horas_restantes = (st.session_state.umbral_dinamico - y[-1]) / pendiente
    if horas_restantes > 0:
        st.warning(f"⚠️ El umbral de {st.session_state.umbral_dinamico:.1f}% se alcanzará en aprox. **{horas_restantes:.1f} horas**.")
    else:
        st.error(f"🚨 El cultivo ya superó el umbral crítico de {st.session_state.umbral_dinamico:.1f}%.")
else:
    st.success("✅ Tendencia estable. No se proyecta déficit inmediato.")

# 8. Validación Biológica
st.markdown("---")
st.markdown("### 🌿 Validación Biológica (Ground Truth)")
col_btn, col_txt = st.columns([1, 2])

with col_btn:
    if st.button("Marcar Estrés Visual"):
        st.session_state.umbral_dinamico = datos['Estres_Humedad(%)'].iloc[-1]
        st.rerun()

with col_txt:
    st.info(f"Umbral actual: **{st.session_state.umbral_dinamico:.1f}%**. Presiona el botón si observas marchitez en campo para recalibrar.")
