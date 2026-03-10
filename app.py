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
    fechas = pd.date_range(start="2026-03-01", periods=48, freq="H")
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


# 3. Panel lateral para subir un archivo .csv
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
# --- Logo al final del panel lateral ---
st.sidebar.markdown("---") 
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
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
        st.plotly_chart(grafico_humedad, use_container_width=True)
    with col_graf2:
        grafico_temp = px.line(datos, x='Fecha_Hora', y='Temperatura(°C)', 
                               title='Variación de la Temperatura Ambiental',
                               color_discrete_sequence=['red'])
        st.plotly_chart(grafico_temp, use_container_width=True)
else:
    # Si no hay temperatura, el gráfico de humedad se expande a lo ancho
    st.plotly_chart(grafico_humedad, use_container_width=True)

# 6. Mostrar tabla de datos en bruto
with st.expander("Ver base de datos cruda (Exportable)"):
    st.dataframe(datos)
