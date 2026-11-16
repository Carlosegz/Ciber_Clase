# Import usando estándar PEP8
# Librerías de Python
from time import sleep
# Librerías de Terceros
import streamlit as st
# Librerías Locales

# Definimos la Configuración de la Página
st.set_page_config(
    page_title="Bienvenido",
    page_icon="✨",
    layout="centered",
)

# Main section
st.title("➿ Bienvenidos al Ciber-Proyecto")
st.markdown(
    "> **Hecho por**: Carlos Guayambuco, Camilo Puentes y Jesus Figueroa"
)

st.write("""
Este es un sitio simple para explorar la autenticación usando un método de 2FA como lo es la configuración de OTPs
""")

if st.button("🚀 Iniciar Sesión", type="primary"):
    st.success("Dirigiendosé a la autenticación ;D")
    sleep(1)

    st.switch_page("all_pages/2_auth_page.py")
    st.stop()

st.caption("Es una muy buena idea iniciar sesión ;)")

# Footer
st.divider()
st.markdown(
    ">© 2026 Ciberseguridad | Sin Derechos Registrados :(",
    unsafe_allow_html=True,
    text_alignment="center"
)
