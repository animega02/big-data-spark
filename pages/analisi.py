import altair as alt
import streamlit as st

from componenti_filtri import mostra_filtri_globali
from dati import carica_dataset
from filtri_crimini import applica_filtri_globali
from stato_app import inizializza_stato
from ui import (
    mostra_header_pagina,
    mostra_chip_filtri,
    applica_stile_grafico
)

from query_crimini import (
    statistiche_generali,
    top_tipi_crimine,
    top_distretti,
    distribuzione_arresti,
    top_luoghi,
    andamento_temporale,
    crimini_per_giorno_settimana,
    crimini_per_fascia_oraria
)


# =========================================================
# STATO
# =========================================================

inizializza_stato()


# =========================================================
# CACHE PANORAMICA
# =========================================================

if "cache_panoramica_versione" not in st.session_state:
    st.session_state.cache_panoramica_versione = None

if "cache_panoramica_dati" not in st.session_state:
    st.session_state.cache_panoramica_dati = None


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

if "cache_analisi_granularita" not in st.session_state:
    st.session_state.cache_analisi_granularita = None


# =========================================================
# FUNZIONI DI SUPPORTO
# =========================================================

def ottieni_area_attiva():

    if (
        st.session_state.area_filtro_attiva
        and
        st.session_state.area_disegnata is not None
    ):

        return st.session_state.area_disegnata

    return None


def dataframe_con_filtri_globali():

    crimini = carica_dataset()

    return applica_filtri_globali(
        crimini,
        st.session_state.data_inizio,
        st.session_state.data_fine,
        st.session_state.tipo_crimine,
        st.session_state.distretto,
        st.session_state.arresto,
        ottieni_area_attiva()
    )


def dataframe_per_analisi(
    tipo_analisi
):

    crimini = carica_dataset()


    tipo_crimine = (
        st.session_state.tipo_crimine
    )

    distretto = (
        st.session_state.distretto
    )

    arresto = (
        st.session_state.arresto
    )


    # =====================================================
    # FILTRI CONTESTUALI
    # =====================================================
    #
    # Quando analizziamo una certa dimensione,
    # non ha senso filtrare proprio quella dimensione.
    #
    # Esempio:
    #
    # Tipo = ROBBERY
    # Analisi = Tipi più frequenti
    #
    # Se mantenessimo il filtro Tipo, otterremmo soltanto
    # ROBBERY.
    # =====================================================

    if (
        tipo_analisi
        == "Tipi di crimine più frequenti"
    ):

        tipo_crimine = "Tutti"


    elif (
        tipo_analisi
        == "Distretti con più crimini"
    ):

        distretto = "Tutti"


    elif (
        tipo_analisi
        == "Distribuzione arresti"
    ):

        arresto = "Tutti"


    return applica_filtri_globali(
        crimini,
        st.session_state.data_inizio,
        st.session_state.data_fine,
        tipo_crimine,
        distretto,
        arresto,
        ottieni_area_attiva()
    )


def determina_granularita():

    giorni = (
        st.session_state.data_fine
        -
        st.session_state.data_inizio
    ).days + 1


    if giorni <= 90:
        return "giorno"

    elif giorni <= 730:
        return "mese"

    else:
        return "anno"


# =========================================================
# TITOLO
# =========================================================

# =========================================================
# HEADER
# =========================================================

mostra_header_pagina(
    "◫ Crime Intelligence",
    "Analytics",
    "Esplora pattern, distribuzioni e trend temporali "
    "degli eventi criminali registrati a Chicago."
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
        "Imposta i filtri desiderati tramite "
        "il pannello ⚙ Filtri per iniziare l'analisi."
    )

    st.stop()

# =========================================================
# CACHE PANORAMICA
# =========================================================

if (
    st.session_state.cache_panoramica_versione
    !=
    st.session_state.versione_filtri
):

    with st.spinner(
        "Calcolo della panoramica..."
    ):

        crimini_panoramica = (
            dataframe_con_filtri_globali()
        )

        riga = (
            statistiche_generali(
                crimini_panoramica
            )
            .first()
        )


        if riga is None:

            panoramica = {
                "Totale": 0,
                "Arresti": 0,
                "Domestici": 0,
                "Distretti": 0
            }


        else:

            panoramica = {
                "Totale": int(
                    riga["Totale"] or 0
                ),

                "Arresti": int(
                    riga["Arresti"] or 0
                ),

                "Domestici": int(
                    riga["Domestici"] or 0
                ),

                "Distretti": int(
                    riga["Distretti"] or 0
                )
            }


        st.session_state.cache_panoramica_dati = (
            panoramica
        )

        st.session_state.cache_panoramica_versione = (
            st.session_state.versione_filtri
        )


panoramica = (
    st.session_state.cache_panoramica_dati
)


totale = panoramica["Totale"]
arresti = panoramica["Arresti"]
domestici = panoramica["Domestici"]
distretti = panoramica["Distretti"]


if totale > 0:

    percentuale_arresti = (
        arresti
        /
        totale
        *
        100
    )

    percentuale_domestici = (
        domestici
        /
        totale
        *
        100
    )


else:

    percentuale_arresti = 0
    percentuale_domestici = 0


# =========================================================
# METRICHE PANORAMICA
# =========================================================

# =========================================================
# KPI PANORAMICA
# =========================================================

st.markdown(
    """
    <div class="crime-section-label">
        ◈ Overview
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("## Panoramica")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Eventi totali",
        f"{totale:,}"
    )


with col2:

    st.metric(
        "Tasso di arresto",
        f"{percentuale_arresti:.1f}%"
    )


with col3:

    st.metric(
        "Crimini domestici",
        f"{percentuale_domestici:.1f}%"
    )


with col4:

    st.metric(
        "Distretti coinvolti",
        f"{distretti:,}"
    )
# =========================================================
# SELEZIONE ANALISI
# =========================================================

TIPI_ANALISI = [
    "Tipi di crimine più frequenti",
    "Distretti con più crimini",
    "Distribuzione arresti",
    "Luoghi più frequenti",
    "Andamento nel tempo",
    "Crimini per giorno della settimana",
    "Crimini per fascia oraria"
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
# RIPRISTINO ULTIMA ANALISI
# =========================================================

analisi_predefinita = TIPI_ANALISI[0]
top_predefinito = 10


if (
    st.session_state.cache_analisi_chiave
    is not None
):

    chiave_vecchia = (
        st.session_state.cache_analisi_chiave
    )


    if (
        chiave_vecchia[0]
        ==
        st.session_state.versione_filtri
    ):

        analisi_vecchia = (
            chiave_vecchia[1]
        )

        top_vecchio = (
            chiave_vecchia[2]
        )


        if analisi_vecchia in TIPI_ANALISI:

            analisi_predefinita = (
                analisi_vecchia
            )


        if top_vecchio in OPZIONI_TOP:

            top_predefinito = (
                top_vecchio
            )

# =========================================================
# QUERY LAB
# =========================================================

st.divider()


st.markdown(
    """
    <div class="crime-section-label">
        ⌁ Query Lab
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("## Costruisci l'analisi")


with st.container(
    border=True,
    key="panel-cyan-analisi"
):

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


    # =====================================================
    # INFORMAZIONI CONTESTUALI
    # =====================================================

    if (
        tipo_analisi
        ==
        "Tipi di crimine più frequenti"
        and
        st.session_state.tipo_crimine != "Tutti"
    ):

        st.info(
            "Per confrontare i diversi tipi di crimine, "
            "il filtro «Tipo di crimine» viene ignorato "
            "in questa analisi."
        )


    elif (
        tipo_analisi
        ==
        "Distretti con più crimini"
        and
        st.session_state.distretto != "Tutti"
    ):

        st.info(
            "Per confrontare i distretti, "
            "il filtro «Distretto» viene ignorato "
            "in questa analisi."
        )


    elif (
        tipo_analisi
        ==
        "Distribuzione arresti"
        and
        st.session_state.arresto != "Tutti"
    ):

        st.info(
            "Per confrontare crimini con e senza arresto, "
            "il filtro «Arresto» viene ignorato "
            "in questa analisi."
        )


    # =====================================================
    # GRANULARITÀ
    # =====================================================

    granularita = None


    if tipo_analisi == "Andamento nel tempo":

        granularita = determina_granularita()


        nomi_granularita = {
            "giorno": "giornaliera",
            "mese": "mensile",
            "anno": "annuale"
        }


        st.caption(
            "Granularità temporale: "
            f"**{nomi_granularita[granularita]}**"
        )


    # =====================================================
    # BOTTONE
    # =====================================================

    esegui = st.button(
        "Esegui analisi →",
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
    top_cache,
    granularita
)


# =========================================================
# ESECUZIONE
# =========================================================

if esegui:

    with st.spinner(
        "Spark sta elaborando l'analisi..."
    ):

        crimini_filtrati = (
            dataframe_per_analisi(
                tipo_analisi
            )
        )


        # =================================================
        # TIPI
        # =================================================

        if (
            tipo_analisi
            == "Tipi di crimine più frequenti"
        ):

            risultato = top_tipi_crimine(
                crimini_filtrati,
                top_n
            )

            titolo = (
                "Tipi di crimine più frequenti"
            )

            categoria = "Primary Type"

            tipo_grafico = "bar"


        # =================================================
        # DISTRETTI
        # =================================================

        elif (
            tipo_analisi
            == "Distretti con più crimini"
        ):

            risultato = top_distretti(
                crimini_filtrati,
                top_n
            )

            titolo = (
                "Distretti con più crimini"
            )

            categoria = "District"

            tipo_grafico = "bar"


        # =================================================
        # ARRESTI
        # =================================================

        elif (
            tipo_analisi
            == "Distribuzione arresti"
        ):

            risultato = distribuzione_arresti(
                crimini_filtrati
            )

            titolo = (
                "Distribuzione degli arresti"
            )

            categoria = "Arrest"

            tipo_grafico = "bar"


        # =================================================
        # LUOGHI
        # =================================================

        elif (
            tipo_analisi
            == "Luoghi più frequenti"
        ):

            risultato = top_luoghi(
                crimini_filtrati,
                top_n
            )

            titolo = (
                "Luoghi più frequenti"
            )

            categoria = "Location Description"

            tipo_grafico = "bar"


        # =================================================
        # ANDAMENTO TEMPORALE
        # =================================================

        elif (
            tipo_analisi
            == "Andamento nel tempo"
        ):

            risultato = andamento_temporale(
                crimini_filtrati,
                granularita
            )

            titolo = (
                "Andamento dei crimini nel tempo"
            )

            categoria = "Periodo"

            tipo_grafico = "line"


        # =================================================
        # GIORNO SETTIMANA
        # =================================================

        elif (
            tipo_analisi
            == "Crimini per giorno della settimana"
        ):

            risultato = (
                crimini_per_giorno_settimana(
                    crimini_filtrati
                )
            )

            titolo = (
                "Crimini per giorno della settimana"
            )

            categoria = "Giorno"

            tipo_grafico = "bar"


        # =================================================
        # FASCIA ORARIA
        # =================================================

        else:

            risultato = (
                crimini_per_fascia_oraria(
                    crimini_filtrati
                )
            )

            titolo = (
                "Crimini per fascia oraria"
            )

            categoria = "Fascia"

            tipo_grafico = "bar"


        dati = risultato.toPandas()


    # =====================================================
    # SISTEMAZIONE DATI
    # =====================================================

    if (
        tipo_analisi
        == "Distribuzione arresti"
    ):

        dati["Arrest"] = dati["Arrest"].map(
            {
                True: "Arresto effettuato",
                False: "Nessun arresto"
            }
        )


    elif (
        tipo_analisi
        == "Andamento nel tempo"
    ):

        dati["Periodo"] = (
            dati["Periodo"]
            .astype(str)
        )


    elif (
        tipo_analisi
        == "Crimini per giorno della settimana"
    ):

        nomi_giorni = {
            1: "Domenica",
            2: "Lunedì",
            3: "Martedì",
            4: "Mercoledì",
            5: "Giovedì",
            6: "Venerdì",
            7: "Sabato"
        }


        dati["Giorno"] = (
            dati["GiornoNumero"]
            .map(
                nomi_giorni
            )
        )


        dati = dati[
            [
                "Giorno",
                "count"
            ]
        ]


    elif (
        tipo_analisi
        == "Crimini per fascia oraria"
    ):

        dati = dati[
            [
                "Fascia",
                "count"
            ]
        ]


    # =====================================================
    # CACHE
    # =====================================================

    st.session_state.cache_analisi_chiave = (
        chiave_analisi
    )

    st.session_state.cache_analisi_dati = (
        dati
    )

    st.session_state.cache_analisi_titolo = (
        titolo
    )

    st.session_state.cache_analisi_categoria = (
        categoria
    )

    st.session_state.cache_analisi_grafico = (
        tipo_grafico
    )

    st.session_state.cache_analisi_granularita = (
        granularita
    )


# =========================================================
# RECUPERO CACHE
# =========================================================

cache_valida = (
    st.session_state.cache_analisi_chiave
    ==
    chiave_analisi
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


dati = (
    st.session_state.cache_analisi_dati
)

titolo = (
    st.session_state.cache_analisi_titolo
)

categoria = (
    st.session_state.cache_analisi_categoria
)

tipo_grafico = (
    st.session_state.cache_analisi_grafico
)


# =========================================================
# RISULTATI
# =========================================================

st.divider()


st.markdown(
    """
    <div class="crime-section-label">
        ◫ Result
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(
    f"## {titolo}"
)

if dati.empty:

    st.warning(
        "Nessun dato disponibile "
        "con i filtri selezionati."
    )

    st.stop()


# =========================================================
# METRICHE RISULTATO
# =========================================================

totale_rappresentato = int(
    dati["count"].sum()
)


indice_picco = (
    dati["count"].idxmax()
)


categoria_picco = str(
    dati.loc[
        indice_picco,
        categoria
    ]
)


valore_picco = int(
    dati.loc[
        indice_picco,
        "count"
    ]
)


# =========================================================
# METRICHE RISULTATO
# =========================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Eventi rappresentati",
        f"{totale_rappresentato:,}"
    )


with col2:

    st.metric(
        "Categorie",
        f"{len(dati):,}"
    )


with col3:

    st.metric(
        "Valore principale",
        categoria_picco
    )

    st.caption(
        f"{valore_picco:,} eventi"
    )

# =========================================================
# GRAFICO
# =========================================================


st.markdown(
    "### Visualizzazione"
)


# =========================================================
# ANDAMENTO NEL TEMPO -> LINEA
# =========================================================

if tipo_grafico == "line":

    grafico = (
        alt.Chart(dati)

        .mark_line(
            color="#00F0FF",
            point={
                "filled": True,
                "fill": "#00F0FF",
                "size": 65
            },
            strokeWidth=3
        )

        .encode(

            x=alt.X(
                "Periodo:N",
                title="Periodo",
                sort=None
            ),

            y=alt.Y(
                "count:Q",
                title="Numero di crimini"
            ),

            tooltip=[
                alt.Tooltip(
                    "Periodo:N",
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
            height=420
        )
    )


# =========================================================
# DISTRETTI -> BARRE VERTICALI
# =========================================================

elif tipo_analisi == "Distretti con più crimini":

    grafico = (
        alt.Chart(dati)

        .mark_bar(
            color="#7B5CFF",
            cornerRadiusTopLeft=6,
            cornerRadiusTopRight=6
        )

        .encode(

            x=alt.X(
                "District:N",
                title="Distretto",
                sort="-y",
                axis=alt.Axis(
                    labelAngle=0
                )
            ),

            y=alt.Y(
                "count:Q",
                title="Numero di crimini"
            ),

            tooltip=[
                alt.Tooltip(
                    "District:N",
                    title="Distretto"
                ),

                alt.Tooltip(
                    "count:Q",
                    title="Crimini",
                    format=","
                )
            ]
        )

        .properties(
            height=400
        )
    )


# =========================================================
# ARRESTI -> BARRE VERTICALI
# =========================================================

elif tipo_analisi == "Distribuzione arresti":

    ordine_arresti = [
        "Nessun arresto",
        "Arresto effettuato"
    ]

    grafico = (
        alt.Chart(dati)

        .mark_bar(
            color="#FF2BD6",
            size=42,
            cornerRadiusTopRight=7,
            cornerRadiusBottomRight=7
        )

        .encode(

            x=alt.X(
                "count:Q",
                title="Numero di crimini"
            ),

            y=alt.Y(
                "Arrest:N",
                title=None,
                sort=ordine_arresti,
                axis=alt.Axis(
                    labelLimit=220
                )
            ),

            tooltip=[
                alt.Tooltip(
                    "Arrest:N",
                    title="Stato"
                ),
                alt.Tooltip(
                    "count:Q",
                    title="Crimini",
                    format=","
                )
            ]
        )

        .properties(
            height=180
        )
    )

# =========================================================
# GIORNI DELLA SETTIMANA -> BARRE VERTICALI
# =========================================================

elif tipo_analisi == "Crimini per giorno della settimana":

    ordine_giorni = [
        "Lunedì",
        "Martedì",
        "Mercoledì",
        "Giovedì",
        "Venerdì",
        "Sabato",
        "Domenica"
    ]

    grafico = (
        alt.Chart(dati)

        .mark_bar(
            color="#00F0FF",
            cornerRadiusTopLeft=6,
            cornerRadiusTopRight=6
        )

        .encode(

            x=alt.X(
                "Giorno:N",
                title=None,
                sort=ordine_giorni,
                axis=alt.Axis(
                    labelAngle=0
                )
            ),

            y=alt.Y(
                "count:Q",
                title="Numero di crimini"
            ),

            tooltip=[
                alt.Tooltip(
                    "Giorno:N",
                    title="Giorno"
                ),

                alt.Tooltip(
                    "count:Q",
                    title="Crimini",
                    format=","
                )
            ]
        )

        .properties(
            height=380
        )
    )


# =========================================================
# FASCE ORARIE -> BARRE VERTICALI
# =========================================================

elif tipo_analisi == "Crimini per fascia oraria":

    ordine_fasce = [
        "00:00 - 05:59",
        "06:00 - 11:59",
        "12:00 - 17:59",
        "18:00 - 23:59"
    ]

    grafico = (
        alt.Chart(dati)

        .mark_bar(
            color="#FF2BD6",
            cornerRadiusTopLeft=6,
            cornerRadiusTopRight=6
        )

        .encode(

            x=alt.X(
                "Fascia:N",
                title="Fascia oraria",
                sort=ordine_fasce,
                axis=alt.Axis(
                    labelAngle=0
                )
            ),

            y=alt.Y(
                "count:Q",
                title="Numero di crimini"
            ),

            tooltip=[
                alt.Tooltip(
                    "Fascia:N",
                    title="Fascia"
                ),

                alt.Tooltip(
                    "count:Q",
                    title="Crimini",
                    format=","
                )
            ]
        )

        .properties(
            height=380
        )
    )


# =========================================================
# TIPI / LUOGHI -> BARRE ORIZZONTALI
# =========================================================

else:

    grafico = (
        alt.Chart(dati)

        .mark_bar(
            color="#7B5CFF",
            cornerRadiusTopRight=6,
            cornerRadiusBottomRight=6
        )

        .encode(

            x=alt.X(
                "count:Q",
                title="Numero di crimini"
            ),

            y=alt.Y(
                f"{categoria}:N",
                sort="-x",
                title=None,

                axis=alt.Axis(
                    labelLimit=0
                )
            ),

            tooltip=[
                alt.Tooltip(
                    f"{categoria}:N",
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

# =========================================================
# STILE GRAFICO
# =========================================================

grafico = applica_stile_grafico(
    grafico
)


# =========================================================
# VISUALIZZAZIONE
# =========================================================


st.altair_chart(
    grafico,
    use_container_width=True
)

# =========================================================
# TABELLA
# =========================================================

st.markdown(
    "### ▤ Dati"
)


st.dataframe(
    dati,
    use_container_width=True,
    hide_index=True
)