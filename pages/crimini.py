import streamlit as st

from pyspark.sql.functions import (
    col,
    concat_ws,
    desc,
    lower
)

from componenti_filtri import mostra_filtri_globali
from dati import carica_dataset
from filtri_crimini import applica_filtri_globali
from stato_app import inizializza_stato

from ui import (
    mostra_header_pagina,
    mostra_chip_filtri
)


# =========================================================
# STATO
# =========================================================

inizializza_stato()


if "cache_crimini_versione" not in st.session_state:
    st.session_state.cache_crimini_versione = None


if "cache_crimini_dati" not in st.session_state:
    st.session_state.cache_crimini_dati = None


if "cache_crimini_totale" not in st.session_state:
    st.session_state.cache_crimini_totale = None


if "cache_crimini_chiave" not in st.session_state:
    st.session_state.cache_crimini_chiave = None


# =========================================================
# HEADER
# =========================================================

mostra_header_pagina(
    "▤ Crime Intelligence",
    "Records",
    "Consulta i singoli eventi criminali corrispondenti "
    "ai filtri globali e cerca direttamente nel dataset."
)


# =========================================================
# TOOLBAR
# =========================================================

col_filtri_attivi, col_filtri = st.columns(
    [5, 1.3],
    vertical_alignment="center"
)


with col_filtri_attivi:

    mostra_chip_filtri()


with col_filtri:

    mostra_filtri_globali()


# =========================================================
# CONTROLLO FILTRI
# =========================================================

if not st.session_state.filtri_applicati:

    st.info(
        "Imposta i filtri tramite il pannello ⚙ Filtri "
        "oppure esegui una ricerca dalla Crime Map."
    )

    st.stop()


# =========================================================
# SEARCH RECORDS
# =========================================================

st.divider()


st.markdown(
    '<div class="crime-section-label">'
    '⌕ Search Records'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    "## Cerca nel dataset"
)


with st.container(
    border=True,
    key="panel-cyan-ricerca"
):

    col_ricerca, col_limite = st.columns(
        [3, 1]
    )


    with col_ricerca:

        ricerca_testuale = st.text_input(
            "Ricerca testuale",

            placeholder=(
                "Tipo, descrizione, luogo o indirizzo..."
            )
        )


    with col_limite:

        limite = st.selectbox(
            "Record da mostrare",

            [
                50,
                100,
                250,
                500
            ],

            index=1
        )


    st.caption(
        "La ricerca viene eseguita su tipo di crimine, "
        "descrizione, luogo e indirizzo."
    )


# =========================================================
# DATASET
# =========================================================

crimini = carica_dataset()


# =========================================================
# AREA GEOGRAFICA ATTIVA
# =========================================================

area_attiva = None


if (
    st.session_state.area_filtro_attiva
    and
    st.session_state.area_disegnata is not None
):

    area_attiva = (
        st.session_state.area_disegnata
    )


# =========================================================
# CHIAVE VISUALIZZAZIONE
# =========================================================

chiave_visualizzazione = (
    st.session_state.versione_filtri,
    ricerca_testuale.strip().lower(),
    limite
)


# =========================================================
# CONTROLLO CACHE
# =========================================================

deve_ricaricare = (
    st.session_state.cache_crimini_versione
    !=
    st.session_state.versione_filtri

    or

    st.session_state.cache_crimini_chiave
    !=
    chiave_visualizzazione

    or

    st.session_state.cache_crimini_dati
    is None

    or

    st.session_state.cache_crimini_totale
    is None
)


# =========================================================
# QUERY SPARK
# =========================================================

if deve_ricaricare:

    with st.spinner(
        "Caricamento degli eventi..."
    ):

        # =================================================
        # FILTRI GLOBALI
        # =================================================

        risultato = applica_filtri_globali(
            crimini,
            st.session_state.data_inizio,
            st.session_state.data_fine,
            st.session_state.tipo_crimine,
            st.session_state.distretto,
            st.session_state.arresto,
            area_attiva
        )


        # =================================================
        # RICERCA TESTUALE
        # =================================================

        if ricerca_testuale.strip():

            testo = (
                ricerca_testuale
                .strip()
                .lower()
            )


            campo_ricerca = concat_ws(
                " ",
                col("Primary Type"),
                col("Description"),
                col("Location Description"),
                col("Block")
            )


            risultato = risultato.filter(
                lower(
                    campo_ricerca
                ).contains(
                    testo
                )
            )


        # =================================================
        # NUMERO TOTALE RISULTATI
        # =================================================

        totale = risultato.count()


        # =================================================
        # RECORD DA VISUALIZZARE
        # =================================================

        risultato_visualizzato = (
            risultato

            .orderBy(
                desc(
                    "_data_timestamp"
                )
            )

            .select(
                "Date",
                "Primary Type",
                "Description",
                "Location Description",
                "Block",
                "District",
                "Arrest",
                "Domestic"
            )

            .limit(
                limite
            )
        )


        dati = (
            risultato_visualizzato
            .toPandas()
        )


        # =================================================
        # NOMI COLONNE
        # =================================================

        dati = dati.rename(
            columns={
                "Date": "Data",
                "Primary Type": "Tipo",
                "Description": "Descrizione",
                "Location Description": "Luogo",
                "Block": "Indirizzo",
                "District": "Distretto",
                "Arrest": "Arresto",
                "Domestic": "Domestico"
            }
        )


        # =================================================
        # BOOLEANI
        # =================================================

        if not dati.empty:

            dati["Arresto"] = (
                dati["Arresto"]
                .map(
                    {
                        True: "Sì",
                        False: "No"
                    }
                )
            )


            dati["Domestico"] = (
                dati["Domestico"]
                .map(
                    {
                        True: "Sì",
                        False: "No"
                    }
                )
            )


        # =================================================
        # CACHE
        # =================================================

        st.session_state.cache_crimini_dati = (
            dati
        )


        st.session_state.cache_crimini_totale = (
            totale
        )


        st.session_state.cache_crimini_versione = (
            st.session_state.versione_filtri
        )


        st.session_state.cache_crimini_chiave = (
            chiave_visualizzazione
        )


else:

    dati = (
        st.session_state.cache_crimini_dati
    )


    totale = (
        st.session_state.cache_crimini_totale
    )


# =========================================================
# RISULTATI
# =========================================================

st.divider()


st.markdown(
    '<div class="crime-section-label">'
    '◈ Results'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    "## Risultati"
)


# =========================================================
# KPI
# =========================================================

col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Eventi corrispondenti",
        f"{totale:,}"
    )


with col2:

    st.metric(
        "Record visualizzati",
        f"{len(dati):,}"
    )


# =========================================================
# RECORD
# =========================================================

st.markdown(
    "### ▤ Crime Records"
)


if dati.empty:

    st.warning(
        "Nessun evento trovato con i filtri "
        "attualmente applicati."
    )


else:

    st.caption(
        f"Visualizzazione di {len(dati):,} record "
        f"su {totale:,} eventi corrispondenti."
    )


    # =====================================================
    # TABELLA
    # =====================================================

    st.dataframe(
        dati,

        use_container_width=True,

        hide_index=True,

        height=600,

        column_config={

            "Data":
                st.column_config.TextColumn(
                    "Data",
                    width="medium"
                ),

            "Tipo":
                st.column_config.TextColumn(
                    "Tipo",
                    width="medium"
                ),

            "Descrizione":
                st.column_config.TextColumn(
                    "Descrizione",
                    width="large"
                ),

            "Luogo":
                st.column_config.TextColumn(
                    "Luogo",
                    width="large"
                ),

            "Indirizzo":
                st.column_config.TextColumn(
                    "Indirizzo",
                    width="medium"
                ),

            "Distretto":
                st.column_config.NumberColumn(
                    "Distretto",
                    format="%d"
                ),

            "Arresto":
                st.column_config.TextColumn(
                    "Arresto",
                    width="small"
                ),

            "Domestico":
                st.column_config.TextColumn(
                    "Domestico",
                    width="small"
                )
        }
    )


    # =====================================================
    # EXPORT
    # =====================================================

    st.markdown(
        '<div class="crime-section-label">'
        '↓ Export'
        '</div>',
        unsafe_allow_html=True
    )


    csv = (
        dati
        .to_csv(
            index=False
        )
        .encode(
            "utf-8"
        )
    )


    col_spazio, col_download = st.columns(
        [3, 1]
    )


    with col_download:

        st.download_button(
            "↓ Esporta CSV",

            data=csv,

            file_name="chicago_crimes.csv",

            mime="text/csv",

            use_container_width=True
        )