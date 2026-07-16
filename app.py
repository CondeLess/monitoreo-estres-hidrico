import streamlit as st
import pandas as pd
import plotly.express as px
import visuals
import numpy as np
import requests
import io
from datetime import datetime

# =================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# =================================================================
st.set_page_config(
    page_title="Dashboard IoT - Vigna unguiculata", 
    layout="wide", 
    page_icon="🌱",
    initial_sidebar_state="expanded"
)

# Cargar CSS externo (Glassmorphism)
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Si no encuentra el archivo temporalmente, no detiene la app

local_css("style.css")

# Renderizar animación Lottie
visuals.render_header_animation()

# --- INICIALIZAR MEMORIA TEMPORAL ---
if 'historial_demo' not in st.session_state:
    st.session_state.historial_demo = pd.DataFrame(columns=["Fecha_Hora", "Humedad_Media", "Humedad_T1_Control", "Humedad_T5_Estres", "Temperatura"])
if 'umbral_dinamico' not in st.session_state:
    st.session_state.umbral_dinamico = 15.0 # PMP por defecto

# =================================================================
# 2. ENCABEZADO Y PRESENTACIÓN
# =================================================================
st.title("🌱 Monitoreo IoT: Estrés Hídrico en Vigna unguiculata")
st.markdown("""
Plataforma telemétrica en tiempo real para el análisis ecofisiológico mediante biosensores capacitivos.  
**Equipo:** Semillero de Investigación en Agrotecnología (CIATEC) - UNALM.
""")
st.markdown("---")

# =================================================================
# 3. PANEL LATERAL (SIDEBAR)
# =================================================================
visuals.set_sidebar_logo("logo.png")

st.sidebar.header("⚙️ Configuración del Ensayo")
st.sidebar.markdown("Los parámetros edáficos ajustan las alertas predictivas de desecación.")

texturas = {"Arena al 50%": 10.0, "Arena Franca": 7.0, "Franco": 14.0, "Arcilla": 28.0}
textura = st.sidebar.selectbox("Sustrato del Ensayo", options=list(texturas.keys()), index=0)

# Ajuste Fino del Umbral
st.session_state.umbral_dinamico = st.sidebar.slider(
    "Umbral Crítico de Marchitez (%)", 1.0, 45.0, 
    float(texturas[textura]),
    help="Punto de Marchitez Permanente teórico. Si la humedad cae por debajo, se activan las alertas."
)

st.sidebar.markdown("---")
st.sidebar.info("La captura de datos ocurre en ciclos de 45 minutos para aislar el ruido de radiofrecuencia (RF) del conversor analógico-digital.")

# =================================================================
# 4. CONEXIÓN A FIREBASE Y CARGA DE DATOS
# =================================================================
FIREBASE_URL = "https://ciatec-peg-default-rtdb.firebaseio.com/TramaActual.json"

@st.cache_data(ttl=5)
def cargar_datos():
    try:
        respuesta = requests.get(FIREBASE_URL)
        if respuesta.status_code == 200 and respuesta.json():
            texto_csv = respuesta.json()
            df = pd.read_csv(
                io.StringIO(texto_csv),
                names=["Tiempo_Activo_ms", "ID_Sensor", "Humedad(%)", "Estado", "Valor_RAW", "Temp_C", "Hum_Amb_Pct", "Pres_hPa"]
            )
            orden_correcto = [f"S{i}" for i in range(1, 16)]
            df['ID_Sensor'] = pd.Categorical(df['ID_Sensor'], categories=orden_correcto, ordered=True)
            return df.sort_values('ID_Sensor')
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error de conexión telemétrica: {e}")
        return pd.DataFrame()

df_sensores = cargar_datos()

# =================================================================
# 5. LÓGICA DE DATOS Y KPIs
# =================================================================
if not df_sensores.empty:
    temp_actual = df_sensores["Temp_C"].mean()
    promedio_humedad = df_sensores['Humedad(%)'].mean()
    
    # Asumimos que T1 (Control) son los sensores S1, S2, S3 y T5 (Máx Estrés) son S13, S14, S15
    control_mean = df_sensores[df_sensores['ID_Sensor'].isin(['S1', 'S2', 'S3'])]['Humedad(%)'].mean()
    estres_mean = df_sensores[df_sensores['ID_Sensor'].isin(['S13', 'S14', 'S15'])]['Humedad(%)'].mean()
    
    maceta_min = df_sensores.loc[df_sensores['Humedad(%)'].idxmin()]

    st.subheader("📊 Monitoreo Telemétrico")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(label="🌡️ Temp. Ambiental", value=f"{temp_actual:.1f} °C", delta=f"{df_sensores['Hum_Amb_Pct'].mean():.1f}% HR")
    kpi2.metric(label="💧 Humedad Control (T1)", value=f"{control_mean:.1f} %")
    kpi3.metric(label="⚠️ Humedad T5 (-0.4 MPa)", value=f"{estres_mean:.1f} %", delta=f"{estres_mean - control_mean:.1f}% vs Control", delta_color="inverse")
    kpi4.metric(label="🚨 Alerta (Más seca)", value=f"{maceta_min['ID_Sensor']}", delta=f"{maceta_min['Humedad(%)']:.1f}%")

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Registrar Ciclo en Historial", use_container_width=True):
            st.cache_data.clear()
            nuevo_dato = pd.DataFrame({
                "Fecha_Hora": [datetime.now()],
                "Humedad_Media": [promedio_humedad],
                "Humedad_T1_Control": [control_mean],
                "Humedad_T5_Estres": [estres_mean],
                "Temperatura": [temp_actual]
            })
            st.session_state.historial_demo = pd.concat([st.session_state.historial_demo, nuevo_dato], ignore_index=True)
            st.rerun()

    # =================================================================
    # 6. CALCULADORA TERMODINÁMICA (MICHEL, 1983)
    # =================================================================
    st.divider()
    st.subheader("🧪 Dosificación Osmótica (Carbowax PEG-6000)")
    st.markdown(f"Ecuación calibrada a **3.5 Litros** de agua purificada con la temperatura ambiental en tiempo real (`{temp_actual:.1f} °C`).")
    
    def calcular_gramos_peg(mpa_objetivo, temp_c):
        psi_bars = mpa_objetivo * 10 
        a = (1.29 * temp_c) - 140
        b = -4.0
        c = -psi_bars 
        raices = np.roots([a, b, c])
        raices_positivas = raices[np.isreal(raices)].real[raices[np.isreal(raices)].real > 0]
        return (raices_positivas[0] * 3500) if len(raices_positivas) > 0 else 0.0

    niveles_estres = [-0.1, -0.2, -0.3, -0.4]
    tratamientos = ["T2 (-0.1 MPa)", "T3 (-0.2 MPa)", "T4 (-0.3 MPa)", "T5 (-0.4 MPa)"]
    pesos_requeridos = [calcular_gramos_peg(mpa, temp_actual) for mpa in niveles_estres]
    
    df_peg = pd.DataFrame({
        "Tratamiento": tratamientos,
        "Potencial Hídrico": [f"{mpa} MPa" for mpa in niveles_estres],
        "PEG-6000 (para 3.5 L)": [f"{peso:.2f} g" for peso in pesos_requeridos]
    })
    
    c_peg1, c_peg2 = st.columns([1, 2])
    with c_peg1:
        st.dataframe(df_peg, use_container_width=True, hide_index=True)
    with c_peg2:
        st.success("**Protocolo de Reemplazo:** Pesa los gramos exactos indicados en la tabla y dilúyelos hasta alcanzar un volumen de saturación de 3.5 Litros. El volumen garantiza el desplazamiento termodinámico del soluto anterior en la zona radicular.")

    # =================================================================
    # 7. VISUALIZACIONES Y ANÁLISIS PREDICTIVO
    # =================================================================
    st.divider()
    col_grafico, col_analisis = st.columns([2, 1])

    with col_grafico:
        st.subheader("📡 Mapa Dieléctrico por Tratamiento")
        fig_bar = px.bar(
            df_sensores, x="ID_Sensor", y="Humedad(%)", color="Humedad(%)",
            color_continuous_scale="RdYlGn", range_color=[0, 100]
        )
        fig_bar.add_hline(y=st.session_state.umbral_dinamico, line_dash="dot", line_width=2, line_color="#FF4B4B", annotation_text=f"Umbral Crítico ({st.session_state.umbral_dinamico}%)")
        fig_bar.update_layout(margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_analisis:
        st.subheader("🧬 Inteligencia Agronómica")
        if len(st.session_state.historial_demo) > 2:
            df_hist = st.session_state.historial_demo
            
            # Integral del Estrés
            area = np.trapezoid(df_hist['Humedad_T1_Control'] - df_hist['Humedad_T5_Estres'])
            st.metric("Carga de Estrés Acumulado", f"{area:.1f} %-t")
            
            # Pronóstico Mínimos Cuadrados
            y = df_hist['Humedad_T5_Estres'].values
            x = np.arange(len(y))
            slope, intercept = np.polyfit(x, y, 1)

            st.markdown("**Pronóstico de Agotamiento (T5):**")
            if slope < 0:
                ciclos_restantes = (st.session_state.umbral_dinamico - y[-1]) / slope
                if ciclos_restantes > 0:
                    st.warning(f"⚠️ El umbral se alcanzará en **{ciclos_restantes:.1f} ciclos** si se mantiene la tasa de secado.")
                else:
                    st.error("🚨 Umbral crítico superado en el tratamiento de mayor estrés.")
            else:
                st.success("✅ Estabilidad radicular detectada. Sin riesgo inminente.")
        else:
            st.info("Se requieren al menos 3 registros en el historial para activar el motor predictivo y la integral de estrés.")

    # =================================================================
    # 8. CURVAS DE REACCIÓN HISTÓRICAS
    # =================================================================
    st.divider()
    st.subheader("📈 Curva de Desecación (T1 vs T5)")
    if not st.session_state.historial_demo.empty:
        df_melted = st.session_state.historial_demo.melt(
            id_vars=["Fecha_Hora"], 
            value_vars=["Humedad_T1_Control", "Humedad_T5_Estres"],
            var_name="Tratamiento", value_name="Humedad (%)"
        )
        fig_line = px.line(df_melted, x="Fecha_Hora", y="Humedad (%)", color="Tratamiento", markers=True)
        fig_line.update_traces(line_width=3, marker_size=8)
        fig_line.update_yaxes(range=[0, 100])
        st.plotly_chart(fig_line, use_container_width=True)

else:
    st.info("⏳ Esperando telemetría del ESP32... Verifica la conexión Wi-Fi del datalogger o los permisos en Firebase.")

st.markdown("---")
st.caption("© 2026 Carlos Condemarin | Semillero de Investigación en Agrotecnología (CIATEC) - UNALM")
