import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# 1. Configuración básica de la página
st.set_page_config(page_title="Dashboard IoT - Vigna unguiculata `Estrés Hídrico", layout="wide")

st.title("🌱 Monitoreo IoT: Estrés Hídrico en Vigna unguiculata")
st.markdown("Sube tu propio archivo de datos generado por el ESP32 o visualiza la simulación por defecto.")
st.markdown("---")

# 2. Generación de datos simulados del ESP32 (si es que no se sube nada)
@st.cache_data
def generar_datos_simulados():
    # Simulamos 48 horas de lectura de sensores
    fechas = pd.date_range(start="2026-03-01", periods=48, freq="h")
    # Simulamos la humedad cayendo más rápido en el tratamiento de estrés
    humedad_control = np.linspace(60, 50, 48) + np.random.normal(0, 1, 48)
    humedad_estres = np.linspace(60, 25, 48) + np.random.normal(0, 1.5, 48)
    # Simulamos temperatura con un ciclo día/noche
    temperatura = 22 + 8 * np.sin(np.linspace(0, 4 * np.pi, 48)) + np.random.normal(0, 0.5, 48)

    return pd.DataFrame({
        'Fecha_Hora': fechas,
        'Control_Humedad(%)': humedad_control,
        'Estres_Humedad(%)': humedad_estres,
        'Temperatura(°C)': temperatura
    })


# 3. Panel lateral
st.sidebar.header("⚙️ Carga de Datos")
st.sidebar.markdown("Sube tu reporte en formato `.csv`.")
archivo_subido = st.sidebar.file_uploader("Selecciona un archivo", type=["csv"])

st.sidebar.markdown("---")
st.sidebar.markdown("**Columnas que deberían estar presentes en el CSV:**")
st.sidebar.code("""
- Fecha_Hora
- Control_Humedad(%)
- Estres_Humedad(%)
- Temperatura(°C)
                """)
st.sidebar.caption("La columna de temperatura es opcional.")

st.sidebar.subheader("📍 Parámetros del Cultivo")
umbral_personalizado = st.sidebar.slider(
    "Definir Umbral Crítico (PMP) %", 
    min_value=5.0, 
    max_value=40.0, 
    value=20.0,
    help="Ajusta este valor según la capacidad de campo y el punto de marchitez del suelo ensayado."
)
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
    index=1,  # Por defecto inicia en Franco
    help="Define el punto de partida del umbral crítico basado en la capacidad de retención del suelo."
)
# Permitimos ajuste manual fino sobre el valor de la textura
umbral_final = st.sidebar.slider(
    "Ajuste Fino de Umbral (%)", 
    5.0, 40.0, 
    float(st.session_state.umbral_dinamico),
    key="slider_umbral"
)

# --- Logo al final del panel lateral ---
st.sidebar.markdown("---") 
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width="stretch")
    st.sidebar.caption("Desarrollado para CIATEC") 

# 4. Lógica para leer el archivo o usar los datos simulados
if archivo_subido is not None:
    try:
        datos = pd.read_csv(archivo_subido)
        st.success("¡Archivo cargado correctamente!")
    except Exception as e:
        st.error(f"Hubo un error al leer el archivo: {e}")
        datos = generar_datos_simulados()
else:
    st.info("ℹ️ Mostrando datos simulados. Usa el panel izquierdo para subir tus propias lecturas.")
    datos = generar_datos_simulados()

# Verificamos si la columna de temperatura existe en el DataFrame actual
tiene_temp = 'Temperatura(°C)' in datos.columns

# 5. Creación de métricas rápidas (KPIs)
st.subheader("Métricas Actuales (Última Lectura)")

# Mostramos 3 o 2 columnas de métricas dependiendo de si hay temperatura
if tiene_temp:
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperatura Actual", f"{datos['Temperatura(°C)'].iloc[-1]:.1f} °C")
    col2.metric("Humedad - Grupo Control", f"{datos['Control_Humedad(%)'].iloc[-1]:.1f} %")
    col3.metric("Humedad - Estrés Hídrico", f"{datos['Estres_Humedad(%)'].iloc[-1]:.1f} %", delta="- Crítico", delta_color="inverse")
else:
    col1, col2 = st.columns(2)
    col1.metric("Humedad - Grupo Control", f"{datos['Control_Humedad(%)'].iloc[-1]:.1f} %")
    col2.metric("Humedad - Estrés Hídrico", f"{datos['Estres_Humedad(%)'].iloc[-1]:.1f} %", delta="- Crítico", delta_color="inverse")

# 6. Gráficos interactivos
st.markdown("### Análisis Temporal")

# El gráfico de humedad siempre se genera
grafico_humedad = px.line(datos, x='Fecha_Hora', y=['Control_Humedad(%)', 'Estres_Humedad(%)'], 
                          title='Evolución de la Humedad del Suelo',
                          labels={'value': 'Humedad (%)', 'variable': 'Tratamiento'})

# Mostramos los gráficos adaptándonos al espacio
if tiene_temp:
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.plotly_chart(grafico_humedad, width="stretch")
    with col_graf2:
        grafico_temp = px.line(datos, x='Fecha_Hora', y='Temperatura(°C)', 
                               title='Variación de la Temperatura Ambiental',
                               color_discrete_sequence=['red'])
        st.plotly_chart(grafico_temp, width="stretch")
else:
    # Si no hay temperatura, el gráfico de humedad se expande a lo ancho
    st.plotly_chart(grafico_humedad, width="stretch")

# 6. Mostrar tabla de datos en bruto
with st.expander("Ver base de datos cruda (Exportable)"):
    st.dataframe(datos)

# 7. Análisis Estadístico
st.markdown("### 📊 Análisis Estadístico Avanzado")
col_stat1, col_stat2 = st.columns(2)

with col_stat1:
    # Correlación entre Humedad y Temperatura
    if tiene_temp:
        corr = datos[['Control_Humedad(%)', 'Temperatura(°C)']].corr().iloc[0,1]
        st.metric("Correlación (Humedad vs Temp)", f"{corr:.2f}")
        st.caption("Coeficiente de Pearson. Mide la relación entre variables: si es negativo, el aumento de temperatura está forzando la desecación del suelo.")

with col_stat2:
    # Diferencia de Medias (Simulando un análisis de impacto)
    dif_medias = datos['Control_Humedad(%)'].mean() - datos['Estres_Humedad(%)'].mean()
    st.metric("Diferencia Media de Humedad", f"{dif_medias:.1f}%")
    st.caption("Diferencia aritmética de los promedios. Representa la magnitud de la brecha hídrica constante generada por el tratamiento de estrés.")

# 7.2. Cálculo de la Integral de Estrés (Área entre curvas)
# Usamos la regla del trapecio para integrar la diferencia
area_estres = np.trapezoid(datos['Control_Humedad(%)'] - datos['Estres_Humedad(%)'])
st.metric("Integral de Estrés Acumulado", f"{area_estres:.2f} %-hora")
st.caption("Regla del trapecio (Integral). Cuantifica la severidad acumulada del déficit; esencial para predecir mermas en el rendimiento biológico.")


# 8. Análisis Predictivo
st.markdown("---")
st.subheader("🔮 Pronóstico de Agotamiento Hídrico")

# Usamos numpy para una regresión lineal simple de la serie de estrés
y = datos['Estres_Humedad(%)'].values
x = np.arange(len(y))
coef = np.polyfit(x, y, 1) # Pendiente y el intercepto
pendiente = coef[0]

if pendiente < 0:
    horas_restantes = (umbral_personalizado - y[-1]) / pendiente
    if horas_restantes > 0:
        st.warning(f"⚠️ Se estima que el cultivo alcanzará el umbral crítico ({umbral_personalizado}%) en aproximadamente **{horas_restantes:.1f} horas**.")
    else:
        st.error(f"🚨 El cultivo ya ha superado el umbral crítico de {umbral_personalizado}%.")
else:
    st.success("✅ La humedad se mantiene estable o en aumento. No se proyecta déficit crítico inmediato.")

st.caption("Proyección basada en regresión lineal de mínimos cuadrados sobre la tendencia actual de agotamiento.")



# Inicializamos el estado con el valor teórico de la textura seleccionada
if 'umbral_dinamico' not in st.session_state:
    st.session_state.umbral_dinamico = pmp_teoricos[textura]

# Sincronizamos el estado con el slider
st.session_state.umbral_dinamico = umbral_final

st.markdown("### 🌿 Validación Biológica (Ground Truth)")
col_btn, col_txt = st.columns([1, 2])

with col_btn:
    if st.button("Marcar Estrés Visual"):
        # Captura la humedad actual del sensor y la fija como nuevo umbral
        nueva_humedad = datos['Estres_Humedad(%)'].iloc[-1]
        st.session_state.umbral_dinamico = nueva_humedad
        st.rerun() # Recarga para actualizar las predicciones

with col_txt:
    st.caption(f"**Umbral actual:** {st.session_state.umbral_dinamico:.1f}%")
    st.info("Presiona el botón si observas marchitez foliar. El sistema ajustará las predicciones automáticamente.")
