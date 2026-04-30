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
    """Muestra la animación sin ralentizar la app."""
    # URL directa al archivo JSON (no a la página web)
    url_json = "https://lottie.host/80862080-60b6-455a-8b8d-519b78a9c372/U5T1hS7L6I.json"
    lottie_plant = load_lottieurl(url_json)
    
    if lottie_plant:
        # El parámetro 'speed' ayuda a que se vea más fluida
        st_lottie(lottie_plant, height=150, key="header_plant", speed=1)

def apply_branding():
    """Aplica el pie de página profesional."""
    st.markdown("---")
    st.caption("© 2026 Carlos Condemarin | Círculo de Investigación en Agrotecnología (CIATEC)")
    st.caption("Investigación Agronómica de Precisión - UNALM")

def set_sidebar_logo(logo_path):
    """Maneja el logo en la barra lateral."""
    import os
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)
