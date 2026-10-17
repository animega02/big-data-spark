import streamlit as st

from pyspark.sql.functions import (
    col,
    concat_ws,
    desc,
    lower
)

from dati import carica_dataset
from filtri_crimini import applica_filtri_globali
from stato_app import inizializza_stato
from componenti_filtri import mostra_filtri_globali


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

# =========================================================
# TITOLO
# =========================================================

st.title("📋 Crimini")

mostra_filtri_globali()

st.caption(
    "Eventi corrispondenti all'ultima ricerca "
    "eseguita nella pagina Mappa."
)


# =========================================================
# NESSUNA RICERCA ANCORA ESEGUITA
# =========================================================

if not st.session_state.filtri_applicati:

    st.info(
        "Esegui prima una ricerca nella pagina 🗺️ Mappa. "
        "I risultati compariranno automaticamente qui."
    )

    st.stop()


# =========================================================
# FILTRI ATTIVI
# =========================================================

st.subheader("Filtri attivi")

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Dal",
    st.session_state.data_inizio.strftime(
        "%d/%m/%Y"
    )
)


col2.metric(
    "Al",
    st.session_state.data_fine.strftime(
        "%d/%m/%Y"
    )
)


col3.metric(
    "Tipo",
    st.session_state.tipo_crimine
)


col4.metric(
    "Arresto",
    st.session_state.arresto
)


if st.session_state.distretto != "Tutti":

    st.caption(
        f"📍 Distretto: "
        f"{st.session_state.distretto}"
    )


if st.session_state.area_filtro_attiva:

    st.info(
        "📐 Filtro geografico attivo: "
        "sono mostrati soltanto i crimini "
        "all'interno dell'area selezionata sulla Mappa."
    )


# =========================================================
# OPZIONI DELLA LISTA
# =========================================================

st.divider()

col_ricerca, col_limite = st.columns(
    [3, 1]
)


with col_ricerca:

    ricerca_testuale = st.text_input(
        "🔎 Cerca nei risultati",

        placeholder=(
            "Tipo, descrizione, luogo o indirizzo..."
        )
    )


with col_limite:

    limite = st.selectbox(
        "Risultati da mostrare",

        [
            50,
            100,
            250,
            500
        ],

        index=1
    )


# =========================================================
# DATASET
# =========================================================

crimini = carica_dataset()


# =========================================================
# AREA ATTIVA
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
# QUERY AUTOMATICA
# =========================================================
# =========================================================
# CONTROLLO CACHE
# =========================================================

deve_ricaricare = (
    st.session_state.cache_crimini_versione
    != st.session_state.versione_filtri
)


# Anche una ricerca testuale richiede una nuova interrogazione
# perché è un filtro locale della pagina Crimini.
if ricerca_testuale.strip():
    deve_ricaricare = True


# Se cambia il numero di record visualizzati dobbiamo
# rigenerare almeno la lista mostrata.
chiave_visualizzazione = (
    st.session_state.versione_filtri,
    ricerca_testuale.strip().lower(),
    limite
)

if "cache_crimini_chiave" not in st.session_state:
    st.session_state.cache_crimini_chiave = None

if (
    st.session_state.cache_crimini_chiave
    != chiave_visualizzazione
):
    deve_ricaricare = True


# =========================================================
# QUERY SPARK SOLO SE NECESSARIA
# =========================================================

if deve_ricaricare:

    with st.spinner(
        "Caricamento dei crimini..."
    ):

        risultato = applica_filtri_globali(
            crimini,
            st.session_state.data_inizio,
            st.session_state.data_fine,
            st.session_state.tipo_crimine,
            st.session_state.distretto,
            st.session_state.arresto,
            area_attiva
        )


        # -------------------------------------------------
        # RICERCA TESTUALE
        # -------------------------------------------------

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


        # -------------------------------------------------
        # CONTEGGIO
        # -------------------------------------------------

        totale = risultato.count()


        # -------------------------------------------------
        # RECORD
        # -------------------------------------------------

        risultato_visualizzato = (
            risultato

            .orderBy(
                desc("_data_timestamp")
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


        dati = risultato_visualizzato.toPandas()


        # -------------------------------------------------
        # NOMI COLONNE
        # -------------------------------------------------

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


        # -------------------------------------------------
        # BOOLEANI
        # -------------------------------------------------

        if not dati.empty:

            dati["Arresto"] = dati["Arresto"].map(
                {
                    True: "Sì",
                    False: "No"
                }
            )

            dati["Domestico"] = dati["Domestico"].map(
                {
                    True: "Sì",
                    False: "No"
                }
            )


        # -------------------------------------------------
        # SALVA CACHE
        # -------------------------------------------------

        st.session_state.cache_crimini_dati = dati

        st.session_state.cache_crimini_totale = totale

        st.session_state.cache_crimini_versione = (
            st.session_state.versione_filtri
        )

        st.session_state.cache_crimini_chiave = (
            chiave_visualizzazione
        )


else:

    dati = st.session_state.cache_crimini_dati

    totale = st.session_state.cache_crimini_totale


# =========================================================
# NOMI COLONNE
# =========================================================

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


# =========================================================
# BOOLEANI
# =========================================================

if not dati.empty:

    dati["Arresto"] = dati["Arresto"].map(
        {
            True: "Sì",
            False: "No"
        }
    )

    dati["Domestico"] = dati["Domestico"].map(
        {
            True: "Sì",
            False: "No"
        }
    )


# =========================================================
# METRICHE
# =========================================================

st.divider()

col1, col2 = st.columns(2)


col1.metric(
    "Crimini trovati",
    f"{totale:,}"
)


col2.metric(
    "Record visualizzati",
    f"{len(dati):,}"
)


# =========================================================
# TABELLA
# =========================================================

st.subheader("Eventi")


if dati.empty:

    st.warning(
        "Nessun crimine trovato "
        "con i filtri attualmente applicati."
    )


else:

    st.dataframe(
        dati,

        use_container_width=True,

        hide_index=True,

        height=600
    )


    # =====================================================
    # DOWNLOAD CSV
    # =====================================================

    csv = dati.to_csv(
        index=False
    ).encode(
        "utf-8"
    )


    st.download_button(
        "⬇️ Esporta i record visualizzati in CSV",

        data=csv,

        file_name="chicago_crimes.csv",

        mime="text/csv",

        use_container_width=True
    )