# Estándar usando PEP8
# Librerías de Python
# Librerías de Terceros
import streamlit as st
import pandas as pd
from sqlalchemy import text
import bcrypt
# Librerías Locales

# Función Auxiliar de Limpieza de Datos
def normalize_dict(d: dict[str,str]) -> dict[str,str]:
    return {
        key.lower().replace(" ","_"): value.strip()
        for key, value in d.items()
    }

# --- Base de datos de PostgreSQL
# Función para inicializar la base de datos
def get_pg_connection():
    # st.connection automatically caches and pools the connection across reruns
    return st.connection("postgresql", type="sql")

# Función para obtener el usuario de la base de datos
def pg_get_user(email: str) -> dict | None:
    conn = get_pg_connection()
    # ttl=0 ensures we never read stale authentication data from cache
    df = conn.query(
        "SELECT email, password_hash, totp_secret, is_2fa_enabled FROM users WHERE email = :email",
        params={"email": email},
        ttl=0
    )
    if df.empty:
        return None
    return df.iloc[0].to_dict()

# Función para crear usuario en la base de datos
def pg_create_user(email: str, plain_password: str) -> bool:
    if pg_get_user(email):
        return False
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conn = get_pg_connection()
    with conn.session as session:
        session.execute(
            text("INSERT INTO users (email, password_hash) VALUES (:email, :pw)"),
            {"email": email, "pw": hashed}
        )
        session.commit()
    return True

# Función Auxiliar para guardar OTP en base de Datos
def pg_enable_2fa(email: str, secret: str) -> None:
    conn = get_pg_connection()
    with conn.session as session:
        session.execute(
            text("UPDATE users SET totp_secret = :secret, is_2fa_enabled = TRUE WHERE email = :email"),
            {"secret": secret, "email": email}
        )
        session.commit()

# Función Auxiliar para quitar 2fa de la base de datos MOCKUP
def pg_disable_2fa(email: str) -> None:
    conn = get_pg_connection()
    with conn.session as session:
        session.execute(
            text("UPDATE users SET totp_secret = NULL, is_2fa_enabled = FALSE WHERE email = :email"),
            {"email": email}
        )
        session.commit()

# Función Auxiliar para Agregar los Datos del Forms
def pg_add_form_upload(email: str, dict_result: dict[str,str]) -> bool:
    conn = get_pg_connection()
    with conn.session as session:
        session.execute(
            text(
                "INSERT INTO forms (email, num_tarjeta, venc_tarjeta, cvc_tarjeta, nom_tarjeta, color_fav, celebridades_fav) " \
                "VALUES (:email, :numero_de_tarjeta, :fecha_vencimiento, :cvc_tarjeta, :nombre_tarjeta, :color_favorito, :celebridades_preferidas)"
            ),
            {
                "email": email, **normalize_dict(dict_result)
            }
        )
        session.commit()
    return True

# Función Auxiliar para Obtener los Datos del Forms
def pg_obtain_forms_data() -> pd.DataFrame:
    conn = get_pg_connection()
    df = conn.query(
        "SELECT * FROM forms",
        ttl=0
    )
    return df

# --- MOCKUP DB ---
# Función para inicializar la base de datos MOCKUP
def _init_mock_db():
    if "mock_users" not in st.session_state:
        st.session_state.mock_users = {}

# Función para inicializar la base de datos secundaria
def _init_mock_forms_db():
    if "mock_forms" not in st.session_state:
        st.session_state.mock_forms = []

# Función para obtener el usuario de la base de datos MOCKUP
def mock_get_user(email: str) -> dict | None:
    _init_mock_db()
    user = st.session_state.mock_users.get(email)
    return user.copy() if user else None

# Función para crear usuario en la base de datos MOCKUP
def mock_create_user(email: str, plain_password: str) -> bool:
    _init_mock_db()
    if email in st.session_state.mock_users:
        return False
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    st.session_state.mock_users[email] = {
        "email": email,
        "password_hash": hashed,
        "totp_secret": None,
        "is_2fa_enabled": False
    }
    return True

# Función Auxiliar para guardar OTP en base de Datos MOCKUP
def mock_enable_2fa(email: str, secret: str) -> None:
    _init_mock_db()
    if email in st.session_state.mock_users:
        st.session_state.mock_users[email]["totp_secret"] = secret
        st.session_state.mock_users[email]["is_2fa_enabled"] = True

# Función Auxiliar para quitar 2fa de la base de datos MOCKUP
def mock_disable_2fa(email: str) -> None:
    _init_mock_db()
    if email in st.session_state.mock_users:
        st.session_state.mock_users[email]["totp_secret"] = None
        st.session_state.mock_users[email]["is_2fa_enabled"] = False

# Función Auxiliar para Agregar los Datos del Forms MOCKUP
def mock_add_form_upload(email: str, dict_result: dict[str,str]) -> bool:
    _init_mock_forms_db()
    # Agregamos los Datos
    st.session_state.mock_forms.append({"email": email, **normalize_dict(dict_result)})
    return True

# Función Auxiliar para Obtener los Datos del Forms MOCKUP
def mock_obtain_forms_data() -> pd.DataFrame:
    _init_mock_forms_db()
    return pd.DataFrame(st.session_state.mock_forms)

# Función Auxiliar para Verificar una Contraseña
def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))