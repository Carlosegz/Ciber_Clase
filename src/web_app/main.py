import streamlit as st

all_pages = [
    st.Page("all_pages/1_landing_page.py", title="Inicio", icon="➿"),
    st.Page("all_pages/2_auth_page.py", title="Inicio de Sesión", icon="♻️"),
    st.Page("all_pages/3_forms_page.py", title="Forms de Obtención de Datos", visibility="hidden", icon="👌"),
]

def main() -> None:
    pg = st.navigation(all_pages)
    pg.run()

if __name__ == "__main__":
    main()
