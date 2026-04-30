import streamlit as st
from streamlit_lottie import st_lottie
import requests

def load_lottieurl(url: str):
    """Carga animaciones desde una URL de LottieFiles."""
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def render_header_animation():
    """Muestra una animación sutil de una planta al inicio."""
    # Animación de una planta creciendo (puedes cambiar el link por otro de LottieFiles)
    lottie_plant = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_m6cu96ze.json")
    if lottie_plant:
        st_lottie(lottie_plant, height=120, key="header_plant")

def apply_branding():
    """Aplica el pie de página y etiquetas de autoría."""
    st.markdown("---")
    st.caption("© 2026 Carlos Condemarin | Círculo de Investigación en Agrotecnología (CIATEC)")
    st.caption("Investigación Agronómica de Precisión - UNALM")

def set_sidebar_logo(logo_path):
    """Maneja la visualización del logo en la barra lateral."""
    import os
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
