import pandas as pd
import streamlit as st

from dati import carica_dataset
from ml_models import (
    allena_modello_arresto,
    ottimizza_soglia_logistica
)

import folium

from streamlit_folium import st_folium

from kmeans_models import trova_cluster_geografici

from stato_app import inizializza_stato
import altair as alt


# =========================================================
# STATO
# =========================================================

inizializza_stato()


# Usiamo una nuova chiave per non mischiare
# risultati creati dalla vecchia versione del codice.

if "ml_risultati_arresto_v2" not in st.session_state:

    st.session_state.ml_risultati_arresto_v2 = {}


# =========================================================
# TITOLO
# =========================================================

st.title("🤖 Machine Learning")

st.caption(
    "Classificazione dell'arresto tramite Apache Spark MLlib."
)


# =========================================================
# INTRODUZIONE
# =========================================================

st.subheader("Predizione dell'arresto")

st.write(
    """
    L'obiettivo è prevedere se un evento criminale
    porterà o meno a un arresto.
    """
)


st.markdown(
    """
    **Feature utilizzate**

    - Tipo di crimine
    - Luogo del crimine
    - Distretto
    - Evento domestico
    - Mese
    - Giorno della settimana
    - Ora
    """
)


st.info(
    "Il dataset presenta uno sbilanciamento tra "
    "crimini con e senza arresto. Possiamo quindi "
    "confrontare la versione normale del modello "
    "con una versione che assegna pesi diversi alle classi."
)


# =========================================================
# CONFIGURAZIONE
# =========================================================

st.divider()

st.subheader("Configurazione esperimento")


col1, col2, col3 = st.columns(
    [2, 1.4, 1.4]
)


with col1:

    tipo_modello = st.selectbox(
        "Algoritmo",
        [
            "Logistic Regression",
            "Random Forest"
        ]
    )


with col2:

    bilanciato = st.checkbox(
        "Bilancia le classi",
        value=False
    )


with col3:

    limite = st.selectbox(
        "Numero record",
        [
            50000,
            100000,
            200000
        ],
        index=2
    )


# =========================================================
# DESCRIZIONE BILANCIAMENTO
# =========================================================

if bilanciato:

    st.caption(
        "La classe meno frequente riceverà un peso maggiore "
        "durante il training. Il test set rimane invariato."
    )


else:

    st.caption(
        "Il modello viene addestrato sulla distribuzione "
        "originale delle classi."
    )


# =========================================================
# CHIAVE RISULTATO
# =========================================================

chiave_risultato = (
    tipo_modello,
    bilanciato,
    limite
)


# =========================================================
# TRAINING
# =========================================================

allena = st.button(
    "🧠 Addestra modello",
    type="primary",
    use_container_width=True
)


if allena:

    crimini = carica_dataset()


    nome = tipo_modello

    if bilanciato:
        nome += " bilanciata"


    with st.spinner(
        f"Spark sta addestrando {nome}..."
    ):

        (
            modello,
            metriche,
            matrice
        ) = allena_modello_arresto(
            crimini,
            tipo_modello,
            bilanciato,
            limite
        )


        st.session_state.ml_risultati_arresto_v2[
            chiave_risultato
        ] = {

            "metriche": metriche,

            "matrice": matrice
        }


# =========================================================
# NESSUN RISULTATO
# =========================================================

if (
    chiave_risultato
    not in
    st.session_state.ml_risultati_arresto_v2
):

    st.info(
        "Addestra questa configurazione "
        "per visualizzarne i risultati."
    )

    st.stop()


# =========================================================
# RISULTATO
# =========================================================

risultati = (
    st.session_state.ml_risultati_arresto_v2[
        chiave_risultato
    ]
)


metriche = risultati[
    "metriche"
]


# =========================================================
# NOME MODELLO
# =========================================================

st.divider()

st.subheader(
    f"Prestazioni — {metriche['modello']}"
)


# =========================================================
# METRICHE PRINCIPALI
# =========================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Accuracy",
        f"{metriche['accuracy'] * 100:.2f}%"
    )


with col2:

    st.metric(
        "Balanced Accuracy",
        f"{metriche['balanced_accuracy'] * 100:.2f}%"
    )


with col3:

    st.metric(
        "AUC ROC",
        f"{metriche['auc']:.3f}"
    )


# =========================================================
# CLASSE ARRESTO
# =========================================================

st.markdown(
    "### Prestazioni sulla classe Arresto"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Precision arresti",
        f"{metriche['precision_arresti'] * 100:.2f}%"
    )


with col2:

    st.metric(
        "Recall arresti",
        f"{metriche['recall_arresti'] * 100:.2f}%"
    )


with col3:

    st.metric(
        "F1 arresti",
        f"{metriche['f1_arresti'] * 100:.2f}%"
    )


# =========================================================
# SPECIFICITÀ
# =========================================================

st.metric(
    "Specificità",
    f"{metriche['specificita'] * 100:.2f}%"
)


# =========================================================
# PESI
# =========================================================

if metriche["bilanciato"]:

    st.markdown(
        "### Pesi delle classi"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Peso Nessun arresto",
            f"{metriche['peso_non_arresto']:.3f}"
        )


    with col2:

        st.metric(
            "Peso Arresto",
            f"{metriche['peso_arresto']:.3f}"
        )


    st.caption(
        "Gli arresti ricevono un peso maggiore perché "
        "rappresentano la classe meno frequente nel training set."
    )


# =========================================================
# BASELINE
# =========================================================

st.markdown(
    "### Confronto con la baseline"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Accuracy modello",
        f"{metriche['accuracy'] * 100:.2f}%"
    )


with col2:

    st.metric(
        "Baseline",
        f"{metriche['baseline_accuracy'] * 100:.2f}%"
    )


with col3:

    miglioramento = (
        metriche["accuracy"]
        -
        metriche["baseline_accuracy"]
    )

    st.metric(
        "Differenza",
        f"{miglioramento * 100:+.2f} punti %"
    )


st.caption(
    "La baseline predice sempre la classe più frequente."
)


# =========================================================
# DATASET
# =========================================================

st.markdown(
    "### Dataset utilizzato"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Training set",
        f"{metriche['train_count']:,}"
    )


with col2:

    st.metric(
        "Test set",
        f"{metriche['test_count']:,}"
    )


with col3:

    st.metric(
        "Arresti nel test",
        f"{metriche['percentuale_arresti'] * 100:.1f}%"
    )


st.caption(
    "La suddivisione train/test è deterministica: "
    "tutti i modelli vengono valutati sugli stessi record."
)


# =========================================================
# MATRICE DI CONFUSIONE
# =========================================================

st.markdown(
    "### Matrice di confusione"
)


matrice = risultati[
    "matrice"
].copy()


matrice["label"] = (
    matrice["label"]
    .map(
        {
            0.0: "Nessun arresto",
            1.0: "Arresto"
        }
    )
)


matrice["prediction"] = (
    matrice["prediction"]
    .map(
        {
            0.0: "Nessun arresto",
            1.0: "Arresto"
        }
    )
)


matrice = matrice.rename(
    columns={
        "label": "Valore reale",
        "prediction": "Predizione",
        "count": "Numero casi"
    }
)


matrice_pivot = (
    matrice

    .pivot(
        index="Valore reale",
        columns="Predizione",
        values="Numero casi"
    )

    .fillna(0)

    .astype(int)
)


matrice_pivot = matrice_pivot.reindex(

    index=[
        "Nessun arresto",
        "Arresto"
    ],

    columns=[
        "Nessun arresto",
        "Arresto"
    ],

    fill_value=0
)


st.dataframe(
    matrice_pivot,
    use_container_width=True
)


st.caption(
    f"Veri negativi: {metriche['tn']:,}  •  "
    f"Falsi positivi: {metriche['fp']:,}  •  "
    f"Falsi negativi: {metriche['fn']:,}  •  "
    f"Veri positivi: {metriche['tp']:,}"
)


# =========================================================
# CONFRONTO CONFIGURAZIONI
# =========================================================

risultati_stesso_dataset = []


for chiave, risultato in (
    st.session_state
    .ml_risultati_arresto_v2
    .items()
):

    algoritmo_cache, bilanciato_cache, limite_cache = (
        chiave
    )


    if limite_cache != limite:
        continue


    m = risultato[
        "metriche"
    ]


    risultati_stesso_dataset.append(
        {
            "Modello": m["modello"],

            "Accuracy": (
                m["accuracy"] * 100
            ),

            "Balanced Accuracy": (
                m["balanced_accuracy"] * 100
            ),

            "AUC ROC": (
                m["auc"]
            ),

            "Precision arresti": (
                m["precision_arresti"] * 100
            ),

            "Recall arresti": (
                m["recall_arresti"] * 100
            ),

            "F1 arresti": (
                m["f1_arresti"] * 100
            )
        }
    )


if len(
    risultati_stesso_dataset
) >= 2:

    st.divider()

    st.subheader(
        "Confronto configurazioni"
    )


    confronto = pd.DataFrame(
        risultati_stesso_dataset
    )


    st.dataframe(

        confronto,

        use_container_width=True,

        hide_index=True,

        column_config={

            "Accuracy":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),

            "Balanced Accuracy":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),

            "AUC ROC":
                st.column_config.NumberColumn(
                    format="%.3f"
                ),

            "Precision arresti":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),

            "Recall arresti":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),

            "F1 arresti":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                )
        }
    )

# =========================================================
# THRESHOLD TUNING
# =========================================================

st.divider()

st.subheader(
    "🎯 Ottimizzazione della soglia"
)


st.write(
    """
    La Logistic Regression assegna a ogni evento una
    probabilità di arresto.

    Normalmente viene utilizzata una soglia pari a **0.50**:
    se la probabilità è almeno 50%, viene predetto
    un arresto.

    Possiamo modificare questa soglia per trovare
    un compromesso migliore tra Precision e Recall.
    """
)


# =========================================================
# SOLO LOGISTIC REGRESSION
# =========================================================

if tipo_modello != "Logistic Regression":

    st.info(
        "Il threshold tuning viene eseguito sulla "
        "Logistic Regression. Selezionala come algoritmo "
        "per avviare l'esperimento."
    )


else:

    col1, col2 = st.columns(2)


    with col1:

        criterio_threshold = st.selectbox(
            "Criterio di ottimizzazione",
            [
                "F1 arresti",
                "Balanced Accuracy"
            ]
        )


    with col2:

        st.write("")

        st.write("")

        ottimizza = st.button(
            "🎯 Ottimizza soglia",
            use_container_width=True
        )


    # =====================================================
    # CACHE
    # =====================================================

    if "ml_threshold_results" not in st.session_state:

        st.session_state.ml_threshold_results = {}


    chiave_threshold = (
        bilanciato,
        limite,
        criterio_threshold
    )


    # =====================================================
    # ESECUZIONE
    # =====================================================

    if ottimizza:

        crimini = carica_dataset()


        with st.spinner(
            "Spark sta cercando la soglia migliore..."
        ):

            risultato_threshold = (
                ottimizza_soglia_logistica(
                    crimini,
                    bilanciato,
                    limite,
                    criterio_threshold
                )
            )


            st.session_state.ml_threshold_results[
                chiave_threshold
            ] = risultato_threshold


    # =====================================================
    # RISULTATI
    # =====================================================

    if (
        chiave_threshold
        in st.session_state.ml_threshold_results
    ):

        risultato_threshold = (
            st.session_state
            .ml_threshold_results[
                chiave_threshold
            ]
        )


        # =================================================
        # SOGLIA MIGLIORE
        # =================================================

        st.markdown(
            "### Soglia selezionata"
        )


        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "Soglia standard",
                "0.50"
            )


        with col2:

            st.metric(
                "Soglia ottimizzata",
                f"{risultato_threshold['soglia_migliore']:.2f}"
            )


        st.caption(
            "La soglia è stata scelta utilizzando "
            "esclusivamente il validation set."
        )


        # =================================================
        # DATASET
        # =================================================

        st.markdown(
            "### Suddivisione dataset"
        )


        col1, col2, col3 = st.columns(3)


        col1.metric(
            "Training",
            f"{risultato_threshold['train_count']:,}"
        )


        col2.metric(
            "Validation",
            f"{risultato_threshold['validation_count']:,}"
        )


        col3.metric(
            "Test",
            f"{risultato_threshold['test_count']:,}"
        )


        # =================================================
        # CURVE DELLE SOGLIE
        # =================================================

        dati_soglie = pd.DataFrame(
            risultato_threshold[
                "risultati_soglie"
            ]
        )


        dati_grafico = (
            dati_soglie[
                [
                    "Soglia",
                    "Precision",
                    "Recall",
                    "F1",
                    "Balanced Accuracy"
                ]
            ]

            .melt(
                id_vars="Soglia",
                var_name="Metrica",
                value_name="Valore"
            )
        )


        st.markdown(
            "### Effetto della soglia"
        )


        grafico_threshold = (

            alt.Chart(
                dati_grafico
            )

            .mark_line(
                point=True
            )

            .encode(

                x=alt.X(
                    "Soglia:Q",
                    title="Soglia"
                ),

                y=alt.Y(
                    "Valore:Q",
                    title="Valore",
                    scale=alt.Scale(
                        domain=[
                            0,
                            1
                        ]
                    )
                ),

                color=alt.Color(
                    "Metrica:N",
                    title="Metrica"
                ),

                tooltip=[
                    alt.Tooltip(
                        "Soglia:Q",
                        format=".2f"
                    ),

                    alt.Tooltip(
                        "Metrica:N"
                    ),

                    alt.Tooltip(
                        "Valore:Q",
                        format=".3f"
                    )
                ]
            )

            .properties(
                height=430
            )
        )


        st.altair_chart(
            grafico_threshold,
            use_container_width=True
        )


        # =================================================
        # DEFAULT VS OTTIMIZZATA
        # =================================================

        st.markdown(
            "### Confronto sul test set"
        )


        default = (
            risultato_threshold[
                "metriche_default"
            ]
        )


        ottimizzata = (
            risultato_threshold[
                "metriche_ottimizzate"
            ]
        )


        confronto_threshold = pd.DataFrame(
            [
                {
                    "Configurazione":
                        "Soglia 0.50",

                    "Accuracy":
                        default["Accuracy"] * 100,

                    "Precision arresti":
                        default["Precision"] * 100,

                    "Recall arresti":
                        default["Recall"] * 100,

                    "F1 arresti":
                        default["F1"] * 100,

                    "Balanced Accuracy":
                        default[
                            "Balanced Accuracy"
                        ] * 100
                },

                {
                    "Configurazione":
                        (
                            "Soglia "
                            f"{risultato_threshold['soglia_migliore']:.2f}"
                        ),

                    "Accuracy":
                        ottimizzata["Accuracy"] * 100,

                    "Precision arresti":
                        ottimizzata["Precision"] * 100,

                    "Recall arresti":
                        ottimizzata["Recall"] * 100,

                    "F1 arresti":
                        ottimizzata["F1"] * 100,

                    "Balanced Accuracy":
                        ottimizzata[
                            "Balanced Accuracy"
                        ] * 100
                }
            ]
        )


        st.dataframe(

            confronto_threshold,

            use_container_width=True,

            hide_index=True,

            column_config={

                "Accuracy":
                    st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),

                "Precision arresti":
                    st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),

                "Recall arresti":
                    st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),

                "F1 arresti":
                    st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),

                "Balanced Accuracy":
                    st.column_config.NumberColumn(
                        format="%.2f%%"
                    )
            }
        )

# =========================================================
# K-MEANS
# =========================================================

st.divider()

st.header(
    "🗺️ Clustering geografico K-Means"
)


st.write(
    """
    K-Means suddivide gli eventi criminali in gruppi
    geografici sulla base della distanza tra le coordinate.

    Si tratta di un algoritmo di **Machine Learning non
    supervisionato**: non esiste una variabile target da
    prevedere.
    """
)


st.info(
    "Il clustering viene calcolato utilizzando "
    "X Coordinate e Y Coordinate. "
    "Latitude e Longitude vengono utilizzate soltanto "
    "per la visualizzazione sulla mappa."
)


# =========================================================
# PARAMETRI
# =========================================================

st.subheader(
    "Configurazione clustering"
)


col1, col2 = st.columns(2)


with col1:

    record_kmeans = st.selectbox(
        "Numero massimo di record",
        [
            50000,
            100000,
            200000
        ],
        index=1,
        key="kmeans_record"
    )


with col2:

    k_massimo = st.slider(
        "K massimo da analizzare",
        min_value=3,
        max_value=10,
        value=8,
        step=1
    )


# =========================================================
# MODALITÀ K
# =========================================================

modalita_k = st.radio(

    "Scelta del numero di cluster",

    [
        "Automatico",
        "Manuale"
    ],

    horizontal=True
)


# =========================================================
# K MANUALE
# =========================================================

k_manual = None


if modalita_k == "Manuale":

    k_manual = st.slider(

        "Numero di cluster K",

        min_value=2,

        max_value=k_massimo,

        value=min(
            7,
            k_massimo
        ),

        step=1
    )


    st.caption(
        "Il valore scelto verrà utilizzato per il clustering, "
        "ma verranno comunque calcolati Silhouette e WSS "
        "per tutti i valori di K."
    )


else:

    st.caption(
        "Il valore di K verrà scelto automaticamente "
        "massimizzando il Silhouette Score."
    )


# =========================================================
# CACHE
# =========================================================

if "kmeans_risultati_v2" not in st.session_state:

    st.session_state.kmeans_risultati_v2 = {}


chiave_kmeans = (

    record_kmeans,

    k_massimo,

    modalita_k,

    k_manual
)


# =========================================================
# ESECUZIONE
# =========================================================

esegui_kmeans = st.button(

    "🧭 Esegui clustering",

    type="primary",

    use_container_width=True
)


if esegui_kmeans:

    crimini = carica_dataset()


    with st.spinner(
        "Spark sta confrontando le configurazioni K-Means..."
    ):

        try:

            risultato_kmeans = (
                trova_cluster_geografici(

                    crimini,

                    limite=record_kmeans,

                    k_min=2,

                    k_max=k_massimo,

                    k_manual=k_manual,

                    max_punti_mappa=1000
                )
            )


            st.session_state.kmeans_risultati_v2[
                chiave_kmeans
            ] = risultato_kmeans


        except ValueError as errore:

            st.error(
                str(errore)
            )


# =========================================================
# RISULTATI
# =========================================================

if (
    chiave_kmeans
    in st.session_state.kmeans_risultati_v2
):

    risultato_kmeans = (
        st.session_state
        .kmeans_risultati_v2[
            chiave_kmeans
        ]
    )


    # =====================================================
    # METRICHE
    # =====================================================

    st.divider()

    st.subheader(
        "Risultato del clustering"
    )


    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "K utilizzato",
            risultato_kmeans[
                "k_finale"
            ]
        )

    with col2:

        st.metric(
            "K Silhouette",
            risultato_kmeans[
                "k_migliore_automatico"
            ]
        )

    with col3:

        st.metric(
            "K Elbow",
            risultato_kmeans[
                "k_elbow"
            ]
        )

    with col4:

        st.metric(
            "Silhouette Score",
            f"{risultato_kmeans['silhouette_finale']:.3f}"
        )

    with col5:

        st.metric(
            "Record analizzati",
            f"{risultato_kmeans['numero_record']:,}"
        )

    # =====================================================
    # INTERPRETAZIONE DEI CRITERI
    # =====================================================

    k_silhouette = (
        risultato_kmeans[
            "k_migliore_automatico"
        ]
    )

    k_elbow = (
        risultato_kmeans[
            "k_elbow"
        ]
    )

    if k_silhouette == k_elbow:

        st.success(
            f"Silhouette Score ed Elbow Method "
            f"concordano su K = {k_silhouette}."
        )

    else:

        st.info(
            f"Il Silhouette Score suggerisce K = "
            f"{k_silhouette}, mentre l'Elbow Method "
            f"suggerisce K = {k_elbow}. "
            f"I due criteri valutano aspetti diversi "
            f"della qualità del clustering."
        )

    # =====================================================
    # INFORMAZIONE AUTOMATICO / MANUALE
    # =====================================================

    if (
            risultato_kmeans["modalita"]
            ==
            "automatica"
    ):

        st.success(
            "Il valore di K utilizzato è stato selezionato "
            "automaticamente massimizzando il Silhouette Score."
        )

    else:

        st.info(
            f"È stata scelta manualmente la configurazione "
            f"K = {risultato_kmeans['k_finale']}."
        )

    # =====================================================
    # DATAFRAME VALUTAZIONI
    # =====================================================

    dati_k = pd.DataFrame(
        risultato_kmeans[
            "valutazioni"
        ]
    )


    # =====================================================
    # SILHOUETTE
    # =====================================================

    st.markdown(
        "### Silhouette Score"
    )


    st.caption(
        "Valori più alti indicano cluster "
        "più compatti e meglio separati."
    )


    grafico_silhouette = (

        alt.Chart(
            dati_k
        )

        .mark_line(
            point=True,
            strokeWidth=3
        )

        .encode(

            x=alt.X(
                "K:O",
                title="Numero di cluster K"
            ),

            y=alt.Y(
                "Silhouette:Q",
                title="Silhouette Score"
            ),

            tooltip=[
                alt.Tooltip(
                    "K:O",
                    title="K"
                ),

                alt.Tooltip(
                    "Silhouette:Q",
                    title="Silhouette",
                    format=".4f"
                )
            ]
        )

        .properties(
            height=380
        )
    )


    st.altair_chart(
        grafico_silhouette,
        use_container_width=True
    )


    # =====================================================
    # ELBOW METHOD / WSS
    # =====================================================

    st.markdown(
        "### Elbow Method"
    )


    st.caption(
        "Il WSS misura la dispersione interna dei cluster. "
        "Aumentando K tende sempre a diminuire. "
        "Si cerca un punto oltre il quale aggiungere cluster "
        "porta benefici sempre più piccoli."
    )


    grafico_wss = (

        alt.Chart(
            dati_k
        )

        .mark_line(
            point=True,
            strokeWidth=3
        )

        .encode(

            x=alt.X(
                "K:O",
                title="Numero di cluster K"
            ),

            y=alt.Y(
                "WSS:Q",
                title="Within-Cluster Sum of Squares"
            ),

            tooltip=[
                alt.Tooltip(
                    "K:O",
                    title="K"
                ),

                alt.Tooltip(
                    "WSS:Q",
                    title="WSS",
                    format=",.0f"
                )
            ]
        )

        .properties(
            height=380
        )
    )


    st.altair_chart(
        grafico_wss,
        use_container_width=True
    )


    # =====================================================
    # TABELLA CONFRONTO
    # =====================================================

    st.markdown(
        "### Confronto dei valori di K"
    )


    st.dataframe(

        dati_k,

        use_container_width=True,

        hide_index=True,

        column_config={

            "Silhouette":
                st.column_config.NumberColumn(
                    format="%.4f"
                ),

            "WSS":
                st.column_config.NumberColumn(
                    format="%.0f"
                )
        }
    )


    # =====================================================
    # CLUSTER
    # =====================================================

    st.markdown(
        "### Cluster individuati"
    )


    cluster = (
        risultato_kmeans[
            "cluster"
        ]
    )


    st.dataframe(

        cluster,

        use_container_width=True,

        hide_index=True,

        column_config={

            "Latitudine":
                st.column_config.NumberColumn(
                    format="%.5f"
                ),

            "Longitudine":
                st.column_config.NumberColumn(
                    format="%.5f"
                ),

            "X centro":
                st.column_config.NumberColumn(
                    format="%.0f"
                ),

            "Y centro":
                st.column_config.NumberColumn(
                    format="%.0f"
                )
        }
    )


    # =====================================================
    # MAPPA
    # =====================================================

    st.markdown(
        "### Distribuzione geografica dei cluster"
    )


    st.caption(
        "La mappa visualizza al massimo 1.000 eventi. "
        "Il clustering viene comunque calcolato "
        "sull'intero campione selezionato."
    )


    mappa_kmeans = folium.Map(

        location=[
            41.8781,
            -87.6298
        ],

        zoom_start=10,

        tiles="OpenStreetMap",

        prefer_canvas=True,

        control_scale=True
    )


    # =====================================================
    # COLORI
    # =====================================================

    colori_cluster = [
        "#e6194b",
        "#3cb44b",
        "#4363d8",
        "#f58231",
        "#911eb4",
        "#42d4f4",
        "#f032e6",
        "#bfef45",
        "#fabed4",
        "#469990"
    ]


    # =====================================================
    # PUNTI
    # =====================================================

    punti = (
        risultato_kmeans[
            "punti_mappa"
        ]
    )


    for _, riga in punti.iterrows():

        cluster_numero = int(
            riga["Cluster"]
        )


        colore = colori_cluster[
            (cluster_numero - 1)
            %
            len(colori_cluster)
        ]


        folium.CircleMarker(

            location=[
                riga["Latitude"],
                riga["Longitude"]
            ],

            radius=3,

            color=colore,

            fill=True,

            fill_color=colore,

            fill_opacity=0.75,

            weight=0,

            tooltip=(
                f"Cluster {cluster_numero}"
            )

        ).add_to(
            mappa_kmeans
        )


    # =====================================================
    # CENTROIDI
    # =====================================================

    for _, riga in cluster.iterrows():

        cluster_numero = int(
            riga["Cluster"]
        )


        colore = colori_cluster[
            (cluster_numero - 1)
            %
            len(colori_cluster)
        ]


        folium.CircleMarker(

            location=[
                riga["Latitudine"],
                riga["Longitudine"]
            ],

            radius=10,

            color=colore,

            fill=True,

            fill_color=colore,

            fill_opacity=1,

            weight=3,

            tooltip=(
                f"Centro Cluster {cluster_numero} "
                f"— {int(riga['Crimini']):,} eventi"
            )

        ).add_to(
            mappa_kmeans
        )


    # =====================================================
    # MOSTRA MAPPA
    # =====================================================

    st_folium(

        mappa_kmeans,

        height=650,

        use_container_width=True,

        key=(
            f"kmeans_map_"
            f"{record_kmeans}_"
            f"{k_massimo}_"
            f"{modalita_k}_"
            f"{k_manual}_"
            f"{risultato_kmeans['k_finale']}"
        ),

        returned_objects=[]
    )