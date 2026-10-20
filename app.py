import streamlit as st

from ui import applica_stile_globale


# =========================================================
# CONFIGURAZIONE
# =========================================================

st.set_page_config(
    page_title="Chicago Crime Explorer",
    page_icon="🌃",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DESIGN SYSTEM
# =========================================================

applica_stile_globale()


# =========================================================
# PAGINE
# =========================================================

pagina_home = st.Page(
    "pages/home.py",
    title="Overview",
    icon="🏠",
    default=True
)


pagina_mappa = st.Page(
    "pages/mappa.py",
    title="Crime Map",
    icon="🗺️"
)


pagina_crimini = st.Page(
    "pages/crimini.py",
    title="Records",
    icon="📋"
)


pagina_analisi = st.Page(
    "pages/analisi.py",
    title="Analytics",
    icon="📊"
)


pagina_machine_learning = st.Page(
    "pages/machine_learning.py",
    title="Machine Learning",
    icon="🤖"
)


# =========================================================
# NAVIGAZIONE
# =========================================================

navigazione = st.navigation(
    {
        "Chicago Crime Intelligence": [
            pagina_home,
            pagina_mappa,
            pagina_crimini,
            pagina_analisi
        ],

        "Advanced": [
            pagina_machine_learning
        ]
    }
)


navigazione.run()