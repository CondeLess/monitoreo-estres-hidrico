import streamlit as st
import os

def set_sidebar_logo(logo_path):
    """Maneja el logo en la barra lateral sin errores de espacio."""
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)
        st.sidebar.markdown("<br>", unsafe_allow_html=True)

def apply_branding():
    """Pie de página institucional."""
    st.markdown("---")
    st.caption("© 2026 Carlos Condemarin | Círculo de Investigación en Agrotecnología (CIATEC)")
