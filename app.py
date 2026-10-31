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
    icon=":material/home:",
    default=True
)


pagina_mappa = st.Page(
    "pages/mappa.py",
    title="Crime Map",
    icon=":material/map:"
)


pagina_crimini = st.Page(
    "pages/crimini.py",
    title="Records",
    icon=":material/table_rows:"
)


pagina_analisi = st.Page(
    "pages/analisi.py",
    title="Analytics",
    icon=":material/bar_chart:"
)


pagina_machine_learning = st.Page(
    "pages/machine_learning.py",
    title="Machine Learning",
    icon=":material/auto_awesome:"
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
    },
    position="hidden"
)


# =========================================================
# AVVIO PAGINA
# =========================================================

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">⌁</div><div><strong>Chicago Crime</strong><small>EXPLORER</small></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-label">WORKSPACE</div>', unsafe_allow_html=True)
    for pagina in (pagina_home, pagina_mappa, pagina_crimini, pagina_analisi):
        with st.container(key="nav_active" if navigazione.url_path == pagina.url_path else "nav_" + pagina.url_path):
            st.page_link(pagina, use_container_width=True)
    st.markdown('<div class="nav-label">LABORATORIO</div>', unsafe_allow_html=True)
    with st.container(key="nav_active" if navigazione.url_path == pagina_machine_learning.url_path else "nav_ml"):
        st.page_link(pagina_machine_learning, use_container_width=True)
    st.markdown('<div class="sidebar-note"><strong>Una ricerca, più prospettive</strong>I filtri sono condivisi tra Mappa, Records e Analytics.<br><span>Imposta il tuo perimetro di analisi.</span></div>', unsafe_allow_html=True)

navigazione.run()