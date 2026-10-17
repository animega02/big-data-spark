import streamlit as st


st.set_page_config(
    page_title="Chicago Crime Explorer",
    page_icon="🌃",
    layout="wide"
)


# =========================================================
# PAGINE
# =========================================================

pagina_home = st.Page(
    "pages/home.py",
    title="Home",
    icon="🏠",
    default=True
)


pagina_mappa = st.Page(
    "pages/mappa.py",
    title="Mappa",
    icon="🗺️"
)


pagina_crimini = st.Page(
    "pages/crimini.py",
    title="Crimini",
    icon="📋"
)


pagina_analisi = st.Page(
    "pages/analisi.py",
    title="Analisi",
    icon="📊"
)


# =========================================================
# NAVIGAZIONE
# =========================================================

navigazione = st.navigation(
    [
        pagina_home,
        pagina_mappa,
        pagina_crimini,
        pagina_analisi
    ]
)


navigazione.run()