# Estándar usando PEP8_CEGZ (osea hecho manual ;D)
# Librerías de Python
from io import BytesIO
from time import sleep
# Librerías de Terceros
import streamlit as st
import qrcode
import pyotp
import numpy as np
# Librerías Locales
import db_helpers as db # type: ignore

# Inicializamos un Par de Llaves
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "auth_stage" not in st.session_state:
    st.session_state.auth_stage = "login"

using_mockup_db = st.session_state.get("using_mockup_db",True)

# Definimos la Conexión a la Base de Datos
get_user = db.pg_get_user if not using_mockup_db else  db.mock_get_user
create_user_db = db.pg_create_user  if not using_mockup_db else db.mock_create_user # type: ignore
enable_2fa = db.pg_enable_2fa   if not using_mockup_db else db.mock_enable_2fa
disable_2fa = db.pg_disable_2fa  if not using_mockup_db else db.mock_disable_2fa

# Funciones de Ayuda
# Función para Obtener el Bytes del Código QR
def generate_qr_code(provisioning_uri: str) -> BytesIO:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG") # type: ignore
    buf.seek(0)
    return buf
# Función para salir de la cuenta actual
def logout():
    st.session_state.auth_stage = "login"
    st.session_state.current_user = None
    st.session_state.pop("temp_secret", None)
    st.rerun()
# Función Auxiliar para hacerle perder el tiempo al usuario
def better_timing():
    with st.spinner("Protegiendo tu cuenta por seguridad con OTP Versión nueva", show_time=True):
        my_prog = st.progress(value=1/5, text="Iniciando Protección")
        sleep(1)
        my_prog.progress(value=2/5,text="Instalando la nueva versión del Software")
        sleep(3)
        my_prog.progress(value=3/5,text="Aplicando la nueva versión del Software")
        sleep(2)
        my_prog.progress(value=4/5, text="Verificando LPE con ChatGPT")
        sleep(5)
        my_prog.progress(value=2/5, text="3 LPEs Encontrados!! Creando Parches")
        sleep(5)
        my_prog.progress(value=3/5,text="Probando Parches en VM Aislada")
        sleep(1.5)
        my_prog.progress(value=4/5,text="Aplicando Parches en Contenedor Local")
        sleep(1.5)
        my_prog.progress(value=4/5, text="Revisando Tests con ChatGPT")
        sleep(3)
        my_prog.progress(value=5/5, text="De vuelta en Línea !!!")
        sleep(0.5)

# UI Completo
st.set_page_config(page_title="Autenticación", page_icon="🔐", layout="centered")
st.title("**#️⃣ Autenticación para Ingreso a la Aplicación**", text_alignment="center")

st.toggle("**😁 Usar base de datos Mockup**",value=True,key="using_mockup_db")
st.caption("Esto es para usar una base de datos local de streamlit ;D")

st.divider()

# Definimos las Funciones de Ayuda para mostrar los diferentes Logins
# Login Inicial
def initial_login():
    st.header("**🔐 Inicio de Sesión**", text_alignment="center")
    st.divider()

    with st.container(width=600):
        # Ponemos Inputs de Correo y Contraseña
        correo = st.text_input(
            label="**📨 Correo**",
            type="email",
            placeholder="admin@1234.com",
            value=None,
            width="stretch"
        )
        st.caption("Asegurate de poner el correo con el que iniciaste sesión no? Jjasjasjsa")
        contra_user = st.text_input(
            label="**🗝️ Contraseña**",
            type="password",
            placeholder="Ej: lacontraseñaescontraseña",
            value=None,
            width="stretch"
        )

        if contra_user == "1234":
            st.error("Esta contraseña ya la usa el Admin 😡")
            st.stop()
        elif contra_user == "contraseña":
            st.success("La mejor contraseñá es contraseña 😁")

        # Verificamos que ambos inputs esten con datos
        credentials_fill = not((correo is None) or (contra_user is None))

        # Creamos el Botón de Ingreso
        with st.container(horizontal_alignment="center"):
            # Creamos Botón para Registrar cuenta
            registrar_cuenta = st.button(
                type="tertiary",
                label="Quiero crear una cuenta",
            )
            ingresar_cuenta = st.button(
                label="🫂Ingresar a Cuenta",
                type="primary",
                disabled= not credentials_fill,
            )

        # Validamos si se quiere registrar una cuenta
        if registrar_cuenta:
            st.session_state["auth_stage"] = "register"
            st.rerun()

        # Validamos Credenciales y Usuario
        if ingresar_cuenta and credentials_fill:
            user_creds = get_user(email=correo) # type: ignore
            if not(user_creds is None) and db.verify_password(plain_password=contra_user, password_hash=user_creds.get("password_hash")): # type: ignore
                # Guardamos el usuario
                st.session_state["current_user"] = correo
                # 2 Posibles Caminos: Verificar OTP o Registrar OTP
                if user_creds.get("is_2fa_enabled"):
                    st.session_state["auth_stage"] = "verify_otp"
                else:
                    st.session_state["auth_stage"] = "setup_otp"

                # Por último hacemos un st.rerun
                st.rerun()
            else:
                st.error("Esa no es la info del Inicio de Sesión ;D")


# Creación de Usuario
def create_user():

    # Ponemos Botón para volver a Login
    if st.button("⏬Volver a Inicio de Sesión"):
        st.session_state.auth_stage = "login"
        st.rerun()

    st.header("🥸 Creación de Cuenta de Usuario")
    st.caption("Que no se te olviden tus credenciales ;)")

    with st.container(width=600):
        # Ponemos Inputs de Correo y Contraseña
        correo = st.text_input(
            label="**📨 Correo**",
            type="email",
            placeholder="admin@1234.com",
            value=None,
            width="stretch"
        )
        st.caption("Asegurate de poner el correo con el que iniciaste sesión no? Jjasjasjsa")
        contra_user = st.text_input(
            label="**🗝️ Contraseña**",
            type="password",
            placeholder="Ej: lacontraseñaescontraseña",
            value=None,
            width="stretch"
        )

        if contra_user == "1234":
            st.error("Esta contraseña ya la usa el Admin 😡")
            st.stop()
        elif contra_user == "contraseña":
            st.success("La mejor contraseñá es contraseña 😁")

        # Verificamos que ambos inputs esten con datos
        credentials_fill = not((correo is None) or (contra_user is None))

        # Creamos el Botón de Ingreso
        with st.container(horizontal_alignment="center"):
            registrar_cuenta = st.button(
                label="🫂Registrar la Cuenta",
                type="primary",
                disabled= not credentials_fill,
                width="stretch"
            )


        # Validamos Credenciales y Usuario
        if registrar_cuenta and credentials_fill:
            # Guardamos el Usuario
            create_user_db(email = correo, plain_password = contra_user)
            # Guardamos el usuario y Ponemos Fase de Iniciar OTP
            st.session_state["current_user"] = correo
            st.session_state["auth_stage"] = "setup_otp"
            # Por último hacemos un st.rerun
            st.rerun()

# Construir OTP
def setup_otp():
    if st.button(
        label= "Volver a inicio de Sesión",
        type="tertiary"
        ):
        logout()
    
    st.header("♻️Configura tu Factor de Autenticación")
    st.info("Para esto necesitas una App Autenticadora", icon="#️⃣")

    # Creamos el OTP
    if not ("temp_secret" in st.session_state):
        st.session_state["temp_secret"] = pyotp.random_base32()

    secret = st.session_state.temp_secret
    totp = pyotp.TOTP(secret) # type: ignore
    uri = totp.provisioning_uri(name=st.session_state["current_user"], issuer_name="Ciber-Clase-OTP")

    # Mostramos el QR
    st.image(generate_qr_code(uri), width="stretch")
    st.caption("Te dejamos también el código manual por si lo deseas")
    st.code(secret, language="text")

    st.divider()
    my_otp_code = st.text_input(
        label="🔢Ingresa el Código",
        max_chars=6
    )

    if my_otp_code is None:
        st.stop()

    # Inicializamos los Intentos con 0
    if not "attempted_otp" in st.session_state:
        st.session_state["attempted_otp"] = 0

    # Si lleva >= 3 Intentos se espera a modo de "procesamiento"
    if st.session_state["attempted_otp"] == 3:
        better_timing()
        # Reinicamos los intentos
        st.session_state["attempted_otp"] = 0

    # Vamos a Verificar el OTP
    if st.button(
        label="😒Verificar Código",
        type="primary"
    ):
        if totp.verify(my_otp_code, valid_window=2):
            enable_2fa(email=st.session_state["current_user"],secret=st.session_state["temp_secret"])
            # Eliminamos el Secreto 
            del st.session_state["temp_secret"]
            # Cambiamos la Vista a la del Formulario
            st.session_state["auth_stage"] = "show_forms"
            # Re-ejecutamos el App
            st.rerun()
        else:
            st.error("Hmmm seguro que no es {:06d}? Puede ser ;)".format(
                (int(my_otp_code) + 1) if my_otp_code.isnumeric() else int(np.random.randint(low=0,high=1_000_000))
            ))
            # Agregamos un Intento
            st.session_state["attempted_otp"] += 1

# Verificar OTP
def verify_otp():
    if st.button(
        label= "Volver a inicio de Sesión",
        type="tertiary"
    ):
        logout()

    st.header("**✡️Verificación de Segundo Factor**")
    st.caption("Tienes que preparar tu app de autenticación")

    st.divider()
    st.badge(label="Iniciando Sesión como {}".format(
        st.session_state["current_user"]
    ), color="blue",icon="📨")

    # Obtenemos el Usuario
    user_creds = get_user(st.session_state["current_user"])
    # Obtenemos su Código de Verificación
    otp_code = user_creds["totp_secret"] # type: ignore
    # Creamos el Objeto
    totp = pyotp.TOTP(otp_code) # type: ignore

    # Ahora mostramos los Inputs
    my_otp_code = st.text_input(
        label="🔢 Código OTP",
        max_chars=6
    )

    if my_otp_code is None:
        st.stop()

    # Inicializamos los Intentos con 0
    if not "attempted_otp" in st.session_state:
        st.session_state["attempted_otp"] = 0

    # Verifcamos la cantidad de intentos que lleva
    curr_atts = st.session_state.get("attempted_otp",0)

    # Si lleva >= 3 Intentos se espera a modo de "procesamiento"
    if curr_atts == 3:
        better_timing()
        # Reinicamos los intentos
        st.session_state["attempted_otp"] = 0

    # Vamos a Verificar el OTP
    if st.button(
        label="😒Verificar Código",
        type="primary"
    ):
        if totp.verify(my_otp_code, valid_window=1):
            # Cambiamos la Vista a la del Formulario
            st.session_state["auth_stage"] = "show_forms"
            # Re-ejecutamos el App
            st.rerun()
        else:
            st.error("Hmmm seguro que no es {:06d}? Puede ser ;)".format(
                (int(my_otp_code) + 1) if my_otp_code.isnumeric() else int(np.random.randint(low=0,high=1_000_000))
            ))
            st.warning(f"🛠️ **Debug — Server Expected OTP:** `{totp.now()}` (Secret: `{user_creds['totp_secret']}`)")
            # Agregamos un Intento
            st.session_state["attempted_otp"] += 1

# Mostrar Siguiente Página
def show_forms():
    st.switch_page("all_pages/3_forms_page.py", query_params={"user_email": st.session_state["current_user"]})

    # Mostramos un Botón de Salir de la Sesión
    if st.button("Cerrar Sesión"):
        logout()

    st.stop()


# Llave no Coincide
def not_coincide():
    st.error("Esto no debería pasar, el estado de sesión es: {}".format(
        st.session_state["auth_stage"]
    ))
    st.stop()

# Por último mostramos la página específicada
especified_page_dict = {
    "login": initial_login,
    "register": create_user,
    "setup_otp": setup_otp,
    "verify_otp": verify_otp,
    "show_forms": show_forms
}

# Obtenemos el Estado Actual
actual_auth_stage = st.session_state["auth_stage"]

# Obtenemos la Página a Mostrar
page_mostrar_func = especified_page_dict.get(actual_auth_stage, not_coincide)

# Ejecutamos la Función
page_mostrar_func()

# Ahora agregamos un logout si ya hay usuario
if not (st.session_state.get("current_user") is None):
    st.divider()
    st.button(
        label="❌Cerrar Sesión",
        on_click=logout,
        type="secondary"
    )