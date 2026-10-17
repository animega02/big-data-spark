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


# =========================================================
# PANNELLO FILTRI GLOBALI
# =========================================================

def mostra_filtri_globali():

    with st.popover(
        "⚙️ Filtri",
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

            st.markdown("#### 📅 Periodo")

            col_inizio, col_fine = st.columns(2)


            with col_inizio:

                data_inizio = st.date_input(
                    "Data iniziale",
                    value=st.session_state.data_inizio,
                    format="DD/MM/YYYY"
                )


            with col_fine:

                data_fine = st.date_input(
                    "Data finale",
                    value=st.session_state.data_fine,
                    format="DD/MM/YYYY"
                )


            # =============================================
            # TIPO DI CRIMINE
            # =============================================

            st.markdown("#### 🚨 Crimine")

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

            st.markdown("#### 📍 Distretto")

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

            st.markdown("#### 👮 Arresto")

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

            st.markdown("#### 📐 Area geografica")


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