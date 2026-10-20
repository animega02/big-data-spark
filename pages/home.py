import streamlit as st

from stato_app import inizializza_stato
from ui import (
    mostra_hero,
    mostra_chip_filtri
)


inizializza_stato()


# =========================================================
# HERO
# =========================================================

mostra_hero()


# =========================================================
# STATO ATTUALE
# =========================================================

mostra_chip_filtri()


# =========================================================
# SEZIONI
# =========================================================

st.markdown(
    '<div class="crime-section-label">'
    'Workspace'
    '</div>',
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)


with col1:

    with st.container(border=True):

        st.markdown("### ◎ Esplorazione geografica")

        st.caption(
            "Visualizza gli eventi sulla mappa, "
            "disegna aree personalizzate e applica "
            "filtri geografici."
        )

        if st.button(
            "Apri Crime Map →",
            use_container_width=True
        ):

            st.switch_page(
                "pages/mappa.py"
            )


with col2:

    with st.container(border=True):

        st.markdown("### ◫ Analytics")

        st.caption(
            "Analizza distribuzioni, trend temporali, "
            "distretti, categorie di crimine e arresti."
        )

        if st.button(
            "Apri Analytics →",
            use_container_width=True
        ):

            st.switch_page(
                "pages/analisi.py"
            )


col3, col4 = st.columns(2)


with col3:

    with st.container(border=True):

        st.markdown("### ▤ Crime Records")

        st.caption(
            "Consulta i singoli eventi corrispondenti "
            "ai filtri globali e cerca nel dataset."
        )

        if st.button(
            "Apri Records →",
            use_container_width=True
        ):

            st.switch_page(
                "pages/crimini.py"
            )


with col4:

    with st.container(border=True):

        st.markdown("### ✦ Machine Learning")

        st.caption(
            "Classificazione degli arresti, "
            "threshold tuning e clustering geografico K-Means."
        )

        if st.button(
            "Apri Machine Learning →",
            use_container_width=True
        ):

            st.switch_page(
                "pages/machine_learning.py"
            )