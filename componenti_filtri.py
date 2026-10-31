from datetime import date

import streamlit as st

from persistenza import salva_filtri


# =========================================================
# OPZIONI FILTRI
# =========================================================

TIPI_CRIMINE = [
    "Tutti",
    "THEFT",
    "BATTERY",
    "CRIMINAL DAMAGE",
    "NARCOTICS",
    "ASSAULT",
    "ROBBERY",
    "BURGLARY",
    "MOTOR VEHICLE THEFT",
    "DECEPTIVE PRACTICE",
    "OTHER OFFENSE"
]


DISTRETTI = ["Tutti"] + [
    str(numero)
    for numero in range(1, 26)
]


OPZIONI_ARRESTO = [
    "Tutti",
    "Sì",
    "No"
]


# Intervallo temporale disponibile nel dataset.
DATA_MINIMA = date(2001, 1, 1)

def data_massima():
    """Restituisce la data odierna, così il limite si aggiorna automaticamente."""
    return date.today()


# =========================================================
# STILE TITOLI FILTRI
# =========================================================

def titolo_filtro(icona, titolo):
    """Icone SVG incorporate: funzionano anche senza font esterni."""
    from html import escape
    forme = {
        "calendar_month": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 11h18M7 15h2m4 0h2M7 18h2"/>',
        "warning": '<path d="M12 3L2 21h20Z M12 9v5m0 3v1"/>',
        "location_on": '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
        "local_police": '<path d="M12 2L3 6v6c0 5 9 10 9 10s9-5 9-10V6Z M8 12l3 3 5-6"/>',
        "select_all": '<path d="M3 8V3h5m8 0h5v5m0 8v5h-5m-8 0H3v-5"/><rect x="7" y="7" width="10" height="10" rx="1"/>',
    }
    svg = ('<svg viewBox="0 0 24 24" width="24" height="24" fill="none" '
           'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true">' + forme.get(icona, forme["select_all"]) + '</svg>')
    st.markdown(
        '<div class="filter-section-title">'
        f'<span class="filter-section-emoji">{svg}</span>'
        f'<span>{escape(titolo)}</span></div>', unsafe_allow_html=True
    )


# =========================================================
# PANNELLO FILTRI GLOBALI
# =========================================================

def mostra_filtri_globali():

    with st.popover(
            "Filtri",
            icon=":material/tune:",
            use_container_width=True
    ):

        st.subheader("Filtri")

        st.caption(
            "I filtri sono condivisi tra "
            "Mappa, Crimini e Analisi."
        )


        # =================================================
        # FORM
        # =================================================

        with st.form(
            "form_filtri_globali"
        ):

            # =============================================
            # DATE
            # =============================================

            titolo_filtro(
                "calendar_month",
                "Periodo"
            )


            col_inizio, col_fine = st.columns(2)


            with col_inizio:

                data_inizio = st.date_input(
                    "Data iniziale",
                    value=st.session_state.data_inizio,
                    min_value=DATA_MINIMA,
                    max_value=data_massima(),
                    format="DD/MM/YYYY"
                )


            with col_fine:

                data_fine = st.date_input(
                    "Data finale",
                    value=st.session_state.data_fine,
                    min_value=DATA_MINIMA,
                    max_value=data_massima(),
                    format="DD/MM/YYYY"
                )


            # =============================================
            # TIPO DI CRIMINE
            # =============================================

            titolo_filtro(
                "warning",
                "Crimine"
            )


            tipo = st.selectbox(
                "Tipo di crimine",
                TIPI_CRIMINE,

                index=(
                    TIPI_CRIMINE.index(
                        st.session_state.tipo_crimine
                    )
                    if st.session_state.tipo_crimine
                    in TIPI_CRIMINE
                    else 0
                )
            )


            # =============================================
            # DISTRETTO
            # =============================================

            titolo_filtro(
                "location_on",
                "Distretto"
            )


            distretto = st.selectbox(
                "Distretto",
                DISTRETTI,

                index=(
                    DISTRETTI.index(
                        str(st.session_state.distretto)
                    )
                    if str(st.session_state.distretto)
                    in DISTRETTI
                    else 0
                )
            )


            # =============================================
            # ARRESTO
            # =============================================

            titolo_filtro(
                "local_police",
                "Arresto"
            )


            arresto = st.radio(
                "Stato arresto",
                OPZIONI_ARRESTO,

                index=(
                    OPZIONI_ARRESTO.index(
                        st.session_state.arresto
                    )
                    if st.session_state.arresto
                    in OPZIONI_ARRESTO
                    else 0
                ),

                horizontal=True
            )


            # =============================================
            # AREA GEOGRAFICA
            # =============================================

            titolo_filtro(
                "select_all",
                "Area geografica"
            )


            if (
                st.session_state.area_disegnata
                is not None
            ):

                usa_area = st.checkbox(
                    "Usa l'area selezionata sulla Mappa",
                    value=st.session_state.area_filtro_attiva
                )

                st.caption(
                    "L'area può essere modificata "
                    "dalla pagina Mappa."
                )


            else:

                usa_area = False

                st.caption(
                    "Nessuna area selezionata. "
                    "Puoi disegnarne una dalla pagina Mappa."
                )


            # =============================================
            # BOTTONE
            # =============================================

            st.divider()


            applica = st.form_submit_button(
                "Applica filtri",
                type="primary",
                use_container_width=True
            )


        # =================================================
        # APPLICAZIONE FILTRI
        # =================================================

        if applica:

            # ---------------------------------------------
            # CONTROLLO DATE
            # ---------------------------------------------

            if data_inizio > data_fine:

                st.error(
                    "La data iniziale non può essere "
                    "successiva alla data finale."
                )

                return


            # ---------------------------------------------
            # FILTRI GLOBALI
            # ---------------------------------------------

            st.session_state.data_inizio = (
                data_inizio
            )

            st.session_state.data_fine = (
                data_fine
            )

            st.session_state.tipo_crimine = (
                tipo
            )

            st.session_state.distretto = (
                distretto
            )

            st.session_state.arresto = (
                arresto
            )

            st.session_state.area_filtro_attiva = (
                usa_area
            )


            # ---------------------------------------------
            # FILTRI APPLICATI
            # ---------------------------------------------

            st.session_state.filtri_applicati = True

            st.session_state.versione_filtri += 1


            # ---------------------------------------------
            # INVALIDAZIONE CACHE CRIMINI
            # ---------------------------------------------

            st.session_state.cache_crimini_versione = None

            st.session_state.cache_crimini_chiave = None

            st.session_state.cache_crimini_dati = None

            st.session_state.cache_crimini_totale = None


            # ---------------------------------------------
            # INVALIDAZIONE CACHE ANALISI
            # ---------------------------------------------

            st.session_state.cache_analisi_chiave = None

            st.session_state.cache_analisi_dati = None

            st.session_state.cache_analisi_titolo = None

            st.session_state.cache_analisi_categoria = None

            st.session_state.cache_analisi_grafico = None

            st.session_state.cache_panoramica_versione = None

            st.session_state.cache_panoramica_dati = None


            # ---------------------------------------------
            # INVALIDAZIONE MAPPA
            # ---------------------------------------------
            #
            # Se cambiano i filtri, i vecchi punti
            # non rappresentano più la ricerca corrente.
            # ---------------------------------------------

            st.session_state.punti_mappa = None

            st.session_state.modalita_ricerca_mappa = None


            # ---------------------------------------------
            # SALVATAGGIO SU FILE
            # ---------------------------------------------

            salva_filtri(
                st.session_state
            )


            # ---------------------------------------------
            # AGGIORNA PAGINA
            # ---------------------------------------------

            st.rerun()