from datetime import date

import streamlit as st

from persistenza import carica_filtri


DATA_MINIMA = date(2001, 1, 1)

def data_massima():
    """Limite superiore dinamico: la data corrente."""
    return date.today()


def limita_data(valore):
    """Mantiene una data dentro l'intervallo 01/01/2001 - oggi."""
    return max(DATA_MINIMA, min(valore, data_massima()))


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

                st.session_state.data_inizio = limita_data(
                    date.fromisoformat(
                        salvati["data_inizio"]
                    )
                )

                st.session_state.data_fine = limita_data(
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

                # L'area geografica NON viene caricata dal disco.
                # Deve vivere solo nella sessione Streamlit corrente:
                # resta disponibile passando da una pagina all'altra,
                # ma una nuova sessione parte sempre senza rettangolo.

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


        # Garantisce sempre un intervallo cronologico valido.
        if st.session_state.data_inizio > st.session_state.data_fine:
            st.session_state.data_inizio = st.session_state.data_fine

        st.session_state._stato_persistente_caricato = True