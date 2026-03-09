import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Configuración básica de la página
st.set_page_config(page_title="Dashboard IoT - Vigna unguiculata", layout="wide")

st.title("🌱 Monitoreo IoT: Estrés Hídrico en Vigna unguiculata")
st.markdown("Panel interactivo para la visualización de datos de humedad y temperatura capturados mediante microcontrolador ESP32.")
st.markdown("---")

# 2. Generación de datos simulados del ESP32
@st.cache_data
def generar_datos():
    # Simulamos 48 horas de lectura de sensores
    fechas = pd.date_range(start="2026-03-01", periods=48, freq="H")
    
    # Simulamos la humedad cayendo más rápido en el tratamiento de estrés
    humedad_control = np.linspace(60, 50, 48) + np.random.normal(0, 1, 48)
    humedad_estres = np.linspace(60, 25, 48) + np.random.normal(0, 1.5, 48)
    
    # Simulamos temperatura con un ciclo día/noche
    temperatura = 22 + 8 * np.sin(np.linspace(0, 4 * np.pi, 48)) + np.random.normal(0, 0.5, 48)

    df = pd.DataFrame({
        'Fecha_Hora': fechas,
        'Control_Humedad(%)': humedad_control,
        'Estres_Humedad(%)': humedad_estres,
        'Temperatura(°C)': temperatura
    })
    return df

datos = generar_datos()

# 3. Creación de métricas rápidas (KPIs)
st.subheader("Métricas Actuales (Última Lectura)")
col1, col2, col3 = st.columns(3)
col1.metric("Temperatura Actual", f"{datos['Temperatura(°C)'].iloc[-1]:.1f} °C")
col2.metric("Humedad - Grupo Control", f"{datos['Control_Humedad(%)'].iloc[-1]:.1f} %")
col3.metric("Humedad - Estrés Hídrico", f"{datos['Estres_Humedad(%)'].iloc[-1]:.1f} %", delta="- Crítico", delta_color="inverse")

# 4. Gráficos interactivos
st.markdown("### Análisis Temporal")
grafico_humedad = px.line(datos, x='Fecha_Hora', y=['Control_Humedad(%)', 'Estres_Humedad(%)'], 
                          title='Evolución de la Humedad del Suelo',
                          labels={'value': 'Humedad (%)', 'variable': 'Tratamiento'})

grafico_temp = px.line(datos, x='Fecha_Hora', y='Temperatura(°C)', 
                       title='Variación de la Temperatura Ambiental',
                       color_discrete_sequence=['red'])

col_graf1, col_graf2 = st.columns(2)
with col_graf1:
    st.plotly_chart(grafico_humedad, use_container_width=True)
with col_graf2:
    st.plotly_chart(grafico_temp, use_container_width=True)

# 5. Mostrar tabla de datos en bruto
with st.expander("Ver base de datos cruda (Exportable)"):
    st.dataframe(datos)