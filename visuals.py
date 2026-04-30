import streamlit as st
from streamlit_lottie import st_lottie
import requests

# Agregamos caché para que solo descargue la animación la primera vez
@st.cache_data
def load_lottieurl(url: str):
    """Carga animaciones desde una URL de manera eficiente."""
    try:
        # IMPORTANTE: Usamos la variable 'url' que recibe la función
        r = requests.get(url, timeout=5) 
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

def render_header_animation():
    # URL directa al archivo JSON
    url_json = "https://cdnl.iconscout.com/lottie/premium/preview-watermark/plant-growing-animation-gif-download-7873132.mp4"
    lottie_plant = load_lottieurl(url_json)
    
    if lottie_plant is not None:
        st_lottie(lottie_plant, height=150, key="header_plant")
    else:
        # Esto te avisará si el problema es la descarga
        st.error("No se pudo cargar la animación de la planta")

def set_sidebar_logo(logo_path):
    """Maneja el logo en la barra lateral."""
    import os
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)
