from datetime import date

import streamlit as st

from persistenza import carica_filtri


def inizializza_stato():

    # =====================================================
    # VALORI PREDEFINITI
    # =====================================================

    valori_predefiniti = {
        "data_inizio": date(2015, 1, 1),
        "data_fine": date(2015, 12, 31),

        "tipo_crimine": "Tutti",
        "distretto": "Tutti",
        "arresto": "Tutti",

        "area_disegnata": None,
        "area_filtro_attiva": False,

        "filtri_applicati": False,
        "versione_filtri": 0
    }


    # =====================================================
    # PRIMA INIZIALIZZAZIONE DELLA SESSIONE
    # =====================================================

    for chiave, valore in valori_predefiniti.items():

        if chiave not in st.session_state:
            st.session_state[chiave] = valore


    # =====================================================
    # CARICAMENTO DA FILE
    # =====================================================
    #
    # Viene eseguito UNA SOLA VOLTA per sessione.
    # =====================================================

    if "_stato_persistente_caricato" not in st.session_state:

        salvati = carica_filtri()

        if salvati is not None:

            try:

                st.session_state.data_inizio = (
                    date.fromisoformat(
                        salvati["data_inizio"]
                    )
                )

                st.session_state.data_fine = (
                    date.fromisoformat(
                        salvati["data_fine"]
                    )
                )

                st.session_state.tipo_crimine = (
                    salvati.get(
                        "tipo_crimine",
                        "Tutti"
                    )
                )

                st.session_state.distretto = (
                    salvati.get(
                        "distretto",
                        "Tutti"
                    )
                )

                st.session_state.arresto = (
                    salvati.get(
                        "arresto",
                        "Tutti"
                    )
                )

                st.session_state.area_disegnata = (
                    salvati.get(
                        "area_disegnata"
                    )
                )

                st.session_state.area_filtro_attiva = (
                    salvati.get(
                        "area_filtro_attiva",
                        False
                    )
                )

                st.session_state.filtri_applicati = (
                    salvati.get(
                        "filtri_applicati",
                        False
                    )
                )

            except (
                KeyError,
                ValueError,
                TypeError
            ):

                pass


        st.session_state._stato_persistente_caricato = True