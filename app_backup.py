from pathlib import Path

import altair as alt
import streamlit as st

from spark_setup import crea_spark
from query_crimini import (
    tipi_crimine_piu_frequenti,
    distretti_con_piu_crimini,
    conteggio_arresti,
    luoghi_piu_frequenti,
    crimini_per_anno,
    crimini_per_mese,
    coordinate_crimini
)


# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA
# ---------------------------------------------------------

st.set_page_config(
    page_title="Chicago Crimes Dashboard",
    page_icon="🌃",
    layout="wide"
)


# ---------------------------------------------------------
# STILE GRAFICO
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    [data-testid="stSidebar"] {
        background-color: #161b26;
    }

    .hero {
        padding: 2rem 2.2rem;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #14213d 0%,
            #1d3557 55%,
            #264653 100%
        );
        margin-bottom: 2rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.8rem;
        color: white;
    }

    .hero p {
        margin-top: 0.7rem;
        margin-bottom: 0;
        color: #dce6f2;
        font-size: 1.05rem;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-weight: 600;
    }

    [data-testid="stMetric"] {
        background-color: #171c27;
        border: 1px solid #2b3240;
        padding: 1rem;
        border-radius: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# SPARK
# ---------------------------------------------------------

@st.cache_resource
def ottieni_spark():
    return crea_spark()


@st.cache_resource
def carica_dataset():
    spark = ottieni_spark()

    cartella_data = Path(__file__).resolve().parent / "data"
    percorso_dataset = next(cartella_data.glob("*.csv"))

    crimini = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(str(percorso_dataset))
    )

    return crimini


crimini = carica_dataset()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>🌃 Chicago Crimes Dashboard</h1>
        <p>
            Analisi interattiva dei crimini registrati nella città di Chicago
            tramite Apache Spark.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("⚙️ Parametri")

anno = st.sidebar.number_input(
    "Anno",
    min_value=2001,
    max_value=2026,
    value=2015,
    step=1
)

top_n = st.sidebar.slider(
    "Numero di risultati",
    min_value=5,
    max_value=20,
    value=10
)

tipo_query = st.sidebar.selectbox(
    "Tipo di analisi",
    [
        "Top tipi di crimine",
        "Top distretti",
        "Arresti",
        "Top luoghi",
        "Andamento nel tempo",
        "Andamento mensile",
        "Mappa geografica"

    ]
)
# Compare solo se scegli "Mappa geografica"
tipo_crimine_mappa = None

if tipo_query == "Mappa geografica":

    tipo_crimine_mappa = st.sidebar.selectbox(
        "Tipo di crimine",
        [
            "Tutti",
            "THEFT",
            "BATTERY",
            "CRIMINAL DAMAGE",
            "NARCOTICS",
            "ASSAULT",
            "ROBBERY",
            "BURGLARY",
            "MOTOR VEHICLE THEFT"
        ]
    )

esegui = st.sidebar.button(
    "🔍 Esegui analisi",
    use_container_width=True
)


# ---------------------------------------------------------
# QUERY
# ---------------------------------------------------------

if esegui:

    with st.spinner("Spark sta elaborando i dati..."):


        if tipo_query == "Top tipi di crimine":

            risultato = tipi_crimine_piu_frequenti(
                crimini,
                anno,
                top_n
            )

            titolo = "Tipi di crimine più frequenti"
            colonna_categoria = "Primary Type"


        elif tipo_query == "Top distretti":

            risultato = distretti_con_piu_crimini(
                crimini,
                anno,
                top_n
            )

            titolo = "Distretti con più crimini"
            colonna_categoria = "District"


        elif tipo_query == "Arresti":

            risultato = conteggio_arresti(
                crimini,
                anno
            )

            titolo = "Crimini con e senza arresto"
            colonna_categoria = "Arrest"


        elif tipo_query == "Top luoghi":

            risultato = luoghi_piu_frequenti(
                crimini,
                anno,
                top_n
            )

            titolo = "Luoghi con più crimini"
            colonna_categoria = "Location Description"

        elif tipo_query == "Andamento nel tempo":

            risultato = crimini_per_anno(
                crimini
            )

            titolo = "Andamento dei crimini nel tempo"
            colonna_categoria = "Year"

        elif tipo_query == "Andamento mensile":

            risultato = crimini_per_mese(
                crimini,
                anno
            )

            titolo = "Andamento mensile dei crimini"
            colonna_categoria = "Mese"

        elif tipo_query == "Mappa geografica":

            tipo_selezionato = (
                None
                if tipo_crimine_mappa == "Tutti"
                else tipo_crimine_mappa
            )

            risultato = coordinate_crimini(
                crimini,
                anno,
                tipo_selezionato,
                3000
            )

            titolo = "Distribuzione geografica dei crimini"
            colonna_categoria = "Primary Type"


        risultato_pandas = risultato.toPandas()


    # -----------------------------------------------------
    # SISTEMAZIONE ETICHETTE
    # -----------------------------------------------------

    if tipo_query == "Arresti":

        risultato_pandas["Arrest"] = risultato_pandas["Arrest"].map(
            {
                True: "Arresto effettuato",
                False: "Nessun arresto"
            }
        )

    if tipo_query == "Andamento mensile":
        nomi_mesi = {
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

        risultato_pandas["MeseNome"] = risultato_pandas["Mese"].map(nomi_mesi)


    # -----------------------------------------------------
    # TITOLO RISULTATI
    # -----------------------------------------------------

    if tipo_query == "Andamento nel tempo":
        st.subheader(titolo)
    else:
        st.subheader(f"{titolo} — {anno}")


    # -----------------------------------------------------
    # METRICHE
    # -----------------------------------------------------

    # -----------------------------------------------------
    # METRICHE
    # -----------------------------------------------------
    col1, col2, col3 = st.columns(3)

    if tipo_query == "Mappa geografica":

        col1.metric(
            "Anno analizzato",
            anno
        )

        col2.metric(
            "Tipo di crimine",
            tipo_crimine_mappa
        )

        col3.metric(
            "Punti visualizzati",
            len(risultato_pandas)
        )

    elif tipo_query == "Andamento mensile":

        totale_crimini = int(
            risultato_pandas["count"].sum()
        )

        indice_massimo = risultato_pandas["count"].idxmax()

        mese_massimo = risultato_pandas.loc[
            indice_massimo,
            "MeseNome"
        ]

        crimini_mese_massimo = int(
            risultato_pandas.loc[indice_massimo, "count"]
        )

        media_mensile = risultato_pandas["count"].mean()

        col1.metric(
            "Crimini totali",
            f"{totale_crimini:,}"
        )

        col2.metric(
            "Mese con più crimini",
            mese_massimo,
            f"{crimini_mese_massimo:,} casi"
        )

        col3.metric(
            "Media mensile",
            f"{media_mensile:,.0f}"
        )

    else:

        col1.metric(
            "Anno analizzato",
            anno
        )

        col2.metric(
            "Risultati mostrati",
            len(risultato_pandas)
        )

        if len(risultato_pandas) > 0:
            prima_categoria = str(
                risultato_pandas.iloc[0][colonna_categoria]
            )

            primo_valore = int(
                risultato_pandas.iloc[0]["count"]
            )

            col3.metric(
                "Valore più frequente",
                prima_categoria,
                f"{primo_valore:,} casi"
            )
    # -----------------------------------------------------
    # GRAFICO
    # -----------------------------------------------------

    st.markdown("### 📊 Visualizzazione")

    if tipo_query == "Mappa geografica":

        dati_mappa = risultato_pandas.rename(
            columns={
                "Latitude": "lat",
                "Longitude": "lon"
            }
        )

        st.map(
            dati_mappa,
            latitude="lat",
            longitude="lon",
            size=8
        )

    ##elif tipo_query == "Andamento nel tempo":

    if tipo_query == "Andamento nel tempo":

        grafico = (
            alt.Chart(risultato_pandas)
            .mark_line(
                point=True,
                strokeWidth=3
            )
            .encode(

                x=alt.X(
                    "Year:O",
                    title="Anno"
                ),

                y=alt.Y(
                    "count:Q",
                    title="Numero di crimini"
                ),

                tooltip=[
                    alt.Tooltip(
                        "Year:O",
                        title="Anno"
                    ),
                    alt.Tooltip(
                        "count:Q",
                        title="Crimini",
                        format=","
                    )
                ]
            )
            .properties(
                height=430
            )
        )



    elif tipo_query == "Andamento mensile":

        grafico = (

            alt.Chart(risultato_pandas)

            .mark_line(

                point=True,

                strokeWidth=3

            )

            .encode(

                x=alt.X(

                    "MeseNome:N",

                    title="Mese",

                    sort=[

                        "Gen", "Feb", "Mar", "Apr",

                        "Mag", "Giu", "Lug", "Ago",

                        "Set", "Ott", "Nov", "Dic"

                    ]

                ),

                y=alt.Y(

                    "count:Q",

                    title="Numero di crimini"

                ),

                tooltip=[

                    alt.Tooltip(

                        "MeseNome:N",

                        title="Mese"

                    ),

                    alt.Tooltip(

                        "count:Q",

                        title="Crimini",

                        format=","

                    )

                ]

            )

            .properties(height=430)

        )


    else:

        grafico = (
            alt.Chart(risultato_pandas)
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
                    f"{colonna_categoria}:N",
                    sort="-x",
                    title=None
                ),

                tooltip=[
                    alt.Tooltip(
                        f"{colonna_categoria}:N",
                        title="Categoria"
                    ),
                    alt.Tooltip(
                        "count:Q",
                        title="Numero",
                        format=","
                    )
                ]
            )
            .properties(
                height=430
            )
        )

    if tipo_query != "Mappa geografica":
        st.altair_chart(
            grafico,
            use_container_width=True
        )


    # -----------------------------------------------------
    # TABELLA
    # -----------------------------------------------------

    st.markdown("### 📋 Dati")

    st.dataframe(
        risultato_pandas,
        use_container_width=True,
        hide_index=True
    )