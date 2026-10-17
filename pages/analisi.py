import altair as alt
import streamlit as st

from dati import carica_dataset
from filtri_crimini import applica_filtri_globali
from stato_app import inizializza_stato
from componenti_filtri import mostra_filtri_globali

from query_crimini import (
    top_tipi_crimine,
    top_distretti,
    distribuzione_arresti,
    top_luoghi,
    andamento_annuale,
    andamento_mensile
)


# =========================================================
# STATO
# =========================================================

inizializza_stato()


# =========================================================
# CACHE ANALISI
# =========================================================

if "cache_analisi_chiave" not in st.session_state:
    st.session_state.cache_analisi_chiave = None

if "cache_analisi_dati" not in st.session_state:
    st.session_state.cache_analisi_dati = None

if "cache_analisi_titolo" not in st.session_state:
    st.session_state.cache_analisi_titolo = None

if "cache_analisi_categoria" not in st.session_state:
    st.session_state.cache_analisi_categoria = None

if "cache_analisi_grafico" not in st.session_state:
    st.session_state.cache_analisi_grafico = None


# =========================================================
# TITOLO
# =========================================================

st.title("📊 Analisi")

mostra_filtri_globali()

st.caption(
    "Interrogazioni aggregate sul dataset Chicago Crimes "
    "eseguite tramite Apache Spark."
)


# =========================================================
# CONTROLLO RICERCA MAPPA
# =========================================================

if not st.session_state.filtri_applicati:

    st.info(
        "Esegui prima una ricerca nella pagina 🗺️ Mappa. "
        "Le analisi utilizzeranno automaticamente gli stessi filtri."
    )

    st.stop()


# =========================================================
# FILTRI ATTIVI
# =========================================================

st.subheader("Filtri attivi")

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Dal",
    st.session_state.data_inizio.strftime("%d/%m/%Y")
)


col2.metric(
    "Al",
    st.session_state.data_fine.strftime("%d/%m/%Y")
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
        f"📍 Distretto: {st.session_state.distretto}"
    )


if st.session_state.area_filtro_attiva:

    st.info(
        "📐 Le analisi sono limitate "
        "all'area geografica selezionata sulla Mappa."
    )


# =========================================================
# SELEZIONE ANALISI
# =========================================================

st.divider()

TIPI_ANALISI = [
    "Tipi di crimine più frequenti",
    "Distretti con più crimini",
    "Distribuzione arresti",
    "Luoghi più frequenti",
    "Andamento annuale",
    "Andamento mensile"
]


ANALISI_CON_TOP = [
    "Tipi di crimine più frequenti",
    "Distretti con più crimini",
    "Luoghi più frequenti"
]


OPZIONI_TOP = [
    5,
    10,
    15,
    20
]


# =========================================================
# RECUPERO ULTIMA ANALISI DALLA CACHE
# =========================================================

analisi_predefinita = TIPI_ANALISI[0]
top_predefinito = 10


if st.session_state.cache_analisi_chiave is not None:

    versione_cache = (
        st.session_state.cache_analisi_chiave[0]
    )

    # Recuperiamo la vecchia selezione solamente se
    # appartiene ancora agli stessi filtri globali.
    if (
        versione_cache
        == st.session_state.versione_filtri
    ):

        analisi_cache = (
            st.session_state.cache_analisi_chiave[1]
        )

        top_cache = (
            st.session_state.cache_analisi_chiave[2]
        )

        if analisi_cache in TIPI_ANALISI:

            analisi_predefinita = analisi_cache

        if top_cache in OPZIONI_TOP:

            top_predefinito = top_cache


# =========================================================
# WIDGET
# =========================================================

col_analisi, col_top = st.columns(
    [3, 1]
)


with col_analisi:

    tipo_analisi = st.selectbox(
        "Tipo di analisi",
        TIPI_ANALISI,
        index=TIPI_ANALISI.index(
            analisi_predefinita
        )
    )


with col_top:

    top_n = st.selectbox(
        "Top N",
        OPZIONI_TOP,
        index=OPZIONI_TOP.index(
            top_predefinito
        ),
        disabled=(
            tipo_analisi
            not in ANALISI_CON_TOP
        )
    )




esegui = st.button(
    "▶️ Esegui analisi",
    type="primary",
    use_container_width=True
)


# =========================================================
# CHIAVE CACHE
# =========================================================

top_cache = (
    top_n
    if tipo_analisi in ANALISI_CON_TOP
    else None
)

chiave_analisi = (
    st.session_state.versione_filtri,
    tipo_analisi,
    top_cache
)


# =========================================================
# ESECUZIONE ANALISI
# =========================================================

if esegui:

    crimini = carica_dataset()


    # -----------------------------------------------------
    # AREA GEOGRAFICA
    # -----------------------------------------------------

    area_attiva = None

    if (
        st.session_state.area_filtro_attiva
        and
        st.session_state.area_disegnata is not None
    ):

        area_attiva = st.session_state.area_disegnata


    with st.spinner(
        "Spark sta elaborando l'analisi..."
    ):

        # -------------------------------------------------
        # FILTRI GLOBALI
        # -------------------------------------------------

        crimini_filtrati = applica_filtri_globali(
            crimini,
            st.session_state.data_inizio,
            st.session_state.data_fine,
            st.session_state.tipo_crimine,
            st.session_state.distretto,
            st.session_state.arresto,
            area_attiva
        )


        # -------------------------------------------------
        # QUERY
        # -------------------------------------------------

        if tipo_analisi == "Tipi di crimine più frequenti":

            risultato = top_tipi_crimine(
                crimini_filtrati,
                top_n
            )

            categoria = "Primary Type"

            titolo = (
                "Tipi di crimine più frequenti"
            )

            tipo_grafico = "bar"


        elif tipo_analisi == "Distretti con più crimini":

            risultato = top_distretti(
                crimini_filtrati,
                top_n
            )

            categoria = "District"

            titolo = (
                "Distretti con più crimini"
            )

            tipo_grafico = "bar"


        elif tipo_analisi == "Distribuzione arresti":

            risultato = distribuzione_arresti(
                crimini_filtrati
            )

            categoria = "Arrest"

            titolo = "Distribuzione degli arresti"

            tipo_grafico = "bar"


        elif tipo_analisi == "Luoghi più frequenti":

            risultato = top_luoghi(
                crimini_filtrati,
                top_n
            )

            categoria = "Location Description"

            titolo = "Luoghi più frequenti"

            tipo_grafico = "bar"


        elif tipo_analisi == "Andamento annuale":

            risultato = andamento_annuale(
                crimini_filtrati
            )

            categoria = "Year"

            titolo = "Andamento annuale dei crimini"

            tipo_grafico = "line"


        else:

            risultato = andamento_mensile(
                crimini_filtrati
            )

            categoria = "Mese"

            titolo = "Andamento mensile dei crimini"

            tipo_grafico = "line"


        dati = risultato.toPandas()


    # =====================================================
    # SISTEMAZIONE ETICHETTE
    # =====================================================

    if tipo_analisi == "Distribuzione arresti":

        dati["Arrest"] = dati["Arrest"].map(
            {
                True: "Arresto effettuato",
                False: "Nessun arresto"
            }
        )


    if tipo_analisi == "Andamento mensile":

        mesi = {
            1: "Gen",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "Mag",
            6: "Giu",
            7: "Lug",
            8: "Ago",
            9: "Set",
            10: "Ott",
            11: "Nov",
            12: "Dic"
        }

        dati["MeseNome"] = dati["Mese"].map(
            mesi
        )

        categoria_grafico = "MeseNome"

    else:

        categoria_grafico = categoria


    # =====================================================
    # SALVATAGGIO CACHE
    # =====================================================

    st.session_state.cache_analisi_chiave = (
        chiave_analisi
    )

    st.session_state.cache_analisi_dati = dati

    st.session_state.cache_analisi_titolo = titolo

    st.session_state.cache_analisi_categoria = (
        categoria_grafico
    )

    st.session_state.cache_analisi_grafico = (
        tipo_grafico
    )


# =========================================================
# RECUPERO CACHE
# =========================================================

cache_valida = (
    st.session_state.cache_analisi_chiave
    == chiave_analisi
    and
    st.session_state.cache_analisi_dati
    is not None
)


if not cache_valida:

    st.info(
        "Seleziona il tipo di analisi e premi "
        "«Esegui analisi»."
    )

    st.stop()


dati = st.session_state.cache_analisi_dati

titolo = st.session_state.cache_analisi_titolo

categoria_grafico = (
    st.session_state.cache_analisi_categoria
)

tipo_grafico = (
    st.session_state.cache_analisi_grafico
)


# =========================================================
# RISULTATI
# =========================================================

st.divider()

st.subheader(titolo)


if dati.empty:

    st.warning(
        "Nessun dato disponibile "
        "con i filtri selezionati."
    )

    st.stop()


# =========================================================
# METRICHE
# =========================================================

totale_rappresentato = int(
    dati["count"].sum()
)


col1, col2 = st.columns(2)


col1.metric(
    "Elementi restituiti",
    len(dati)
)


col2.metric(
    "Crimini rappresentati",
    f"{totale_rappresentato:,}"
)


# =========================================================
# GRAFICO
# =========================================================

st.markdown("### 📈 Visualizzazione")


if tipo_grafico == "line":

    # -----------------------------------------------------
    # ANDAMENTO MENSILE
    # -----------------------------------------------------

    if tipo_analisi == "Andamento mensile":

        ordine_mesi = [
            "Gen",
            "Feb",
            "Mar",
            "Apr",
            "Mag",
            "Giu",
            "Lug",
            "Ago",
            "Set",
            "Ott",
            "Nov",
            "Dic"
        ]

        asse_x = alt.X(
            "MeseNome:N",
            title="Mese",
            sort=ordine_mesi
        )


    # -----------------------------------------------------
    # ANDAMENTO ANNUALE
    # -----------------------------------------------------

    else:

        asse_x = alt.X(
            "Year:O",
            title="Anno"
        )


    grafico = (
        alt.Chart(dati)

        .mark_line(
            point=True,
            strokeWidth=3
        )

        .encode(

            x=asse_x,

            y=alt.Y(
                "count:Q",
                title="Numero di crimini"
            ),

            tooltip=[
                alt.Tooltip(
                    f"{categoria_grafico}:N",
                    title="Periodo"
                ),

                alt.Tooltip(
                    "count:Q",
                    title="Crimini",
                    format=","
                )
            ]
        )

        .properties(
            height=450
        )
    )


else:

    grafico = (
        alt.Chart(dati)

        .mark_bar(
            cornerRadiusTopRight=5,
            cornerRadiusBottomRight=5
        )

        .encode(

            x=alt.X(
                "count:Q",
                title="Numero di crimini"
            ),

            y=alt.Y(
                f"{categoria_grafico}:N",
                sort="-x",
                title=None
            ),

            tooltip=[
                alt.Tooltip(
                    f"{categoria_grafico}:N",
                    title="Categoria"
                ),

                alt.Tooltip(
                    "count:Q",
                    title="Crimini",
                    format=","
                )
            ]
        )

        .properties(
            height=450
        )
    )


st.altair_chart(
    grafico,
    use_container_width=True
)


# =========================================================
# TABELLA
# =========================================================

st.markdown("### 📋 Dati")

st.dataframe(
    dati,
    use_container_width=True,
    hide_index=True
)