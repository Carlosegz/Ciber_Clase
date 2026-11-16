# Estándar usando librerías de Python
# Librerías de Python
from time import sleep
# Librerías de Terceros
import streamlit as st
# Librerías Locales
import db_helpers as db # type: ignore

# Obtenemos los Parámetros 
query_params = st.query_params
# Ahora los Limpiamos
st.query_params.clear()

# Guardamos el usuario
if query_params:
    st.session_state["current_user"] = query_params["user_email"]

st.success("Sesión Iniciada Correctamente `{}`".format(
        st.session_state["current_user"]
    ))

st.divider()
st.header("🥸Forms 100% Limpio No Fake")
st.caption("Tu información esta segura (`se supone`)")
usando_mockup = st.toggle("😁Usar Base de Datos Mockup", value=True)

# Vamos a Mostrar por el Momento 3 Inputs:
# Numeros de Tarjeta de Crédito, Color Favorito y Personalidades a las que apoyas

# Ahora Tarjetas de Crédito
with st.container(height=300,vertical_alignment="bottom", border=True):
    st.header("#️⃣Datos de tu Tarjeta de Crédito")

    # Input de Número y Vencimiento
    colNum, colVenc = st.columns([3,1])
    with colNum:
        st.caption("**💳Número de Tarjeta**")
        st.code(st.session_state.get("card-code","0000 0000 0000 0000"))
    with colVenc:
        st.caption("**📅Fecha de Vencimiento**")
        st.code(st.session_state.get("fecha-venc","12/31"))

    # Input de Código y Nombre
    colCod, colNombre = st.columns([1,3])
    with colCod:
        st.caption("**🗝️Código del CVC**")
        st.code(st.session_state.get("cvc-code","313"))
    with colNombre:
        st.caption("**📨Nombre de la Tarjeta**")
        st.code(st.session_state.get("name-code","ANDRES GUSTAVO ROJAS PINILLA").title())

# Input de Número y Vencimiento
colNum, colVenc = st.columns([3,1])
with colNum:
    codigo_card = st.text_input("💳Número de Tarjeta",key="card-code")
with colVenc:
    vencimiento_card = st.text_input("📅Fecha de Vencimiento",key="fecha-venc")

# Input de Código y Nombre
colCod, colNombre = st.columns([1,3])
with colCod:
    cvc_card = st.text_input("**🗝️Código del CVC**",key="cvc-code",max_chars=3)
with colNombre:
    nombre_card = st.text_input("**📨Nombre de la Tarjeta**",key="name-code")

# Ahora Color Favorito
st.space("medium")

color_fav = st.selectbox(
    "😁Selecciona tu Color Favorito",
    options= ["Rojo","Verde","Amarillo","Azul"],
    accept_new_options = True
)

# Por Último, Celebridades Preferidas
celebridades_preferidas = st.pills(
    "🙍Celebridades Preferidas",
    options = ["Donald Trump","Jeffrey Dahmer","Ricky Martin","Nicolas Cage","Will Smith"],
    selection_mode="multi"
)

# Ahora Creamos el Diccionario Validador
validator_dict = {
    "Numero de Tarjeta": codigo_card,
    "Fecha Vencimiento": vencimiento_card,
    "CVC Tarjeta": cvc_card,
    "Nombre Tarjeta": nombre_card,
    "Color Favorito": color_fav,
    "Celebridades Preferidas": ",".join(celebridades_preferidas)
}
# Definimos si los datos están listos para subir
faltan_por_llenar = []
for nombre, valor in validator_dict.items():
    if (valor is None) or (valor == ""):
        faltan_por_llenar.append(nombre)

if faltan_por_llenar:
    st.error("😡No puedes subir el formulario sin llenarlo todo, faltan estas:\n- {}".format(
        "\n- ".join(faltan_por_llenar)
    ))

# Mostramos el Botón de Subida
key_ya_subido = "forms_ya_subido_{}".format(st.session_state["current_user"])
if st.button("⏬Subir Información del Forms", disabled=(len(faltan_por_llenar) > 0) or st.session_state.get(key_ya_subido,False), type="primary"):
    # Definimos la Función a usar
    upload_forms = db.mock_add_form_upload if usando_mockup else db.pg_add_form_upload
    # La aplicamos
    if upload_forms(email=st.session_state["current_user"], dict_result=validator_dict):
        st.success("Forms Subido con Éxito", icon="✅")
        st.session_state[key_ya_subido] = True
        sleep(1)
        st.rerun()

if st.session_state.get(key_ya_subido,False):
    st.info("Ya subiste el formulario, por lo que puedes descargar la Info 😁")
    # Definimos la Función a Usar
    download_forms_info = db.mock_obtain_forms_data if usando_mockup else db.pg_obtain_forms_data
    # Obtenemos los Datos y los Guardamos
    if not ("data_forms" in st.session_state):
        st.session_state.data_forms = download_forms_info()
        st.session_state.data_csv = st.session_state.data_forms.to_csv().encode("utf-8")

    # Ahora Obtenemos el DF
    df_forms = st.session_state.data_forms
    csv_forms = st.session_state.data_csv
    # Lo Mostramos
    with st.expander("Datos del Formulario", expanded=True):
        st.dataframe(df_forms)

    # Creamos el Botón de Descarga
    st.download_button(
        label="Descargar la Información de Usuarios",
        data=csv_forms,
        file_name="data_forms.csv",
        mime="text/csv",
        icon=":material/download:",
    )

else:
    st.warning("Para descargar la Info tienes que subir el Formulario",icon="⚠️")

# Agregamos botón de Cerrar sesión
if st.button("Cerrar Sesión",key="close-session-forms"):
    st.session_state.auth_stage = "login"
    st.session_state.current_user = None
    st.session_state.pop("temp_secret", None)
    # Vamos a la Página de Inicio
    st.switch_page("all_pages/1_landing_page.py")