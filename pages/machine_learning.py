import altair as alt
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from dati import carica_dataset
from kmeans_models import trova_cluster_geografici
from ml_models import (
    allena_modello_arresto,
    allena_modello_tipo_crimine,
    previsione_crimini_mensili,
)
from stato_app import inizializza_stato
from ui import applica_stile_grafico, mostra_header_pagina


# =========================================================
# STATO
# =========================================================

inizializza_stato()

for chiave in (
    "ml_risultati_arresto_v4",
    "ml_multiclasse_results_v2",
    "ml_regressione_results_v2",
    "kmeans_risultati_v4",
):
    if chiave not in st.session_state:
        st.session_state[chiave] = {}


# =========================================================
# INTESTAZIONE
# =========================================================

mostra_header_pagina(
    "Laboratorio / Machine Learning",
    "Dai dati ai modelli.",
    "Classificazione, previsioni mensili e clustering geografico: quattro esperimenti per esplorare i pattern dei crimini di Chicago."
)
st.caption("Ogni esperimento utilizza i propri parametri di addestramento; i filtri di Mappa, Records e Analytics non si applicano a questa sezione.")


tab_binaria, tab_multiclasse, tab_regressione, tab_kmeans = st.tabs(
    [
        "Arresto",
        "Tipo di crimine",
        "Previsione mensile",
        "Aree critiche",
    ]
)


# =========================================================
# 1. CLASSIFICAZIONE BINARIA
# =========================================================

with tab_binaria:
    st.header("Predizione dell'arresto")
    st.write(
        "Il primo esperimento prova a stimare se un evento criminale porterà a un "
        "arresto. Il modello viene addestrato su una parte dei dati e valutato su "
        "record separati che non sono stati utilizzati durante il training."
    )
    st.caption(
        "Il modello considera tipologia e luogo del crimine, distretto, evento domestico "
        "e informazioni temporali come mese, giorno della settimana e ora."
    )

    c1, c2, c3 = st.columns([2, 1.1, 1.4])

    with c1:
        tipo_modello = st.selectbox(
            "Algoritmo",
            ["Logistic Regression", "Random Forest", "GBT"],
            key="ml_bin_algo_v5",
        )

    with c2:
        seed = st.number_input(
            "Seed",
            min_value=0,
            max_value=999999,
            value=42,
            step=1,
            key="ml_bin_seed_v5",
            help="Rende riproducibili sampling, split e algoritmi casuali.",
        )

    with c3:
        st.markdown(
            '<div style="height: 1.55rem;"></div>',
            unsafe_allow_html=True,
        )
        bilanciato = st.checkbox(
            "Bilancia le classi",
            value=False,
            key="ml_bin_balance_v5",
            help=(
                "Assegna un peso maggiore alla classe meno frequente "
                "durante il training."
            ),
        )

    p1, p2 = st.columns(2)

    with p1:
        sampling = st.slider(
            "Sampling",
            min_value=0.01,
            max_value=1.00,
            value=0.10,
            step=0.01,
            format="%.2f",
            key="ml_bin_sampling_v5",
            help=(
                "Frazione dell'intero dataset valido utilizzata nell'esperimento. "
                "0.10 corrisponde a circa il 10% dei record disponibili."
            ),
        )

    with p2:
        test_ratio = st.slider(
            "Test ratio",
            min_value=0.10,
            max_value=0.40,
            value=0.20,
            step=0.05,
            format="%.2f",
            key="ml_bin_test_ratio_v5",
            help="Quota del campione riservata alla valutazione del modello.",
        )

    if bilanciato:
        st.caption(
            "Bilanciamento attivo: la classe meno frequente riceve maggiore peso nel training."
        )

    chiave_binaria = (
        tipo_modello,
        int(seed),
        bilanciato,
        round(float(sampling), 2),
        round(float(test_ratio), 2),
    )

    if st.button(
        "Addestra modello binario",
        icon=":material/auto_awesome:",
        type="primary",
        use_container_width=True,
        key="train_binario_v5",
    ):
        crimini = carica_dataset()
        nome = tipo_modello + (" bilanciata" if bilanciato else "")

        with st.spinner(f"Spark sta addestrando {nome}..."):
            _, metriche, matrice = allena_modello_arresto(
                crimini,
                tipo_modello=tipo_modello,
                bilanciato=bilanciato,
                frazione=sampling,
                test_ratio=test_ratio,
                seed=int(seed),
            )

        st.session_state.ml_risultati_arresto_v4[chiave_binaria] = {
            "metriche": metriche,
            "matrice": matrice,
        }

    risultato_binario = st.session_state.ml_risultati_arresto_v4.get(
        chiave_binaria
    )

    if risultato_binario is None:
        st.info("Addestra il modello per visualizzare i risultati.")
    else:
        metriche = risultato_binario["metriche"]
        matrice = risultato_binario["matrice"].copy()

        st.subheader(f"Prestazioni — {metriche['modello']}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Accuracy", f"{metriche['accuracy'] * 100:.2f}%")
        m2.metric(
            "Balanced Accuracy",
            f"{metriche['balanced_accuracy'] * 100:.2f}%",
        )
        m3.metric("F1 arresti", f"{metriche['f1_arresti'] * 100:.2f}%")
        m4.metric("AUC ROC", f"{metriche['auc']:.3f}")

        st.caption(
            f"Training: {metriche['train_count']:,} record · "
            f"Test: {metriche['test_count']:,} record · "
            f"Seed: {metriche['seed']}"
        )

        st.markdown("#### Matrice di confusione")

        matrice["label"] = matrice["label"].map(
            {0.0: "Nessun arresto", 1.0: "Arresto"}
        )
        matrice["prediction"] = matrice["prediction"].map(
            {0.0: "Nessun arresto", 1.0: "Arresto"}
        )

        matrice_pivot = (
            matrice.pivot(
                index="label",
                columns="prediction",
                values="count",
            )
            .fillna(0)
            .astype(int)
            .reindex(
                index=["Nessun arresto", "Arresto"],
                columns=["Nessun arresto", "Arresto"],
                fill_value=0,
            )
        )
        matrice_pivot.index.name = "Valore reale"
        matrice_pivot.columns.name = "Predizione"
        st.dataframe(matrice_pivot, use_container_width=True)


# =========================================================
# 2. CLASSIFICAZIONE MULTICLASSE
# =========================================================

with tab_multiclasse:
    st.header("Classificazione del tipo di crimine")
    st.write(
        "In questo esperimento il modello non deve scegliere tra due sole classi, "
        "ma deve riconoscere la categoria del crimine. L'obiettivo è prevedere il "
        "Primary Type utilizzando il contesto geografico e temporale dell'evento."
    )
    st.caption(
        "Le informazioni utilizzate comprendono luogo, distretto, evento domestico, "
        "mese, giorno della settimana e ora."
    )

    c1, c2 = st.columns([2, 1])

    with c1:
        modello_multi = st.selectbox(
            "Algoritmo",
            ["Random Forest", "Logistic Regression"],
            key="ml_multi_algo_v3",
        )

    with c2:
        seed_multi = st.number_input(
            "Seed",
            min_value=0,
            max_value=999999,
            value=42,
            step=1,
            key="ml_multi_seed_v3",
            help="Rende riproducibili sampling, split e algoritmi casuali.",
        )

    p1, p2 = st.columns(2)

    with p1:
        sampling_multi = st.slider(
            "Sampling",
            min_value=0.01,
            max_value=1.00,
            value=0.10,
            step=0.01,
            format="%.2f",
            key="ml_multi_sampling_v3",
            help=(
                "Frazione dell'intero dataset valido utilizzata nell'esperimento. "
                "0.10 corrisponde a circa il 10% dei record disponibili."
            ),
        )

    with p2:
        test_ratio_multi = st.slider(
            "Test ratio",
            min_value=0.10,
            max_value=0.40,
            value=0.20,
            step=0.05,
            format="%.2f",
            key="ml_multi_test_ratio_v3",
        )

    chiave_multi = (
        modello_multi,
        int(seed_multi),
        round(float(sampling_multi), 2),
        round(float(test_ratio_multi), 2),
    )

    if st.button(
        "Addestra modello multiclasse",
        icon=":material/auto_awesome:",
        type="primary",
        use_container_width=True,
        key="train_multiclasse_v3",
    ):
        crimini = carica_dataset()

        with st.spinner(
            f"Spark sta addestrando {modello_multi} multiclasse..."
        ):
            _, metriche_multi, _ = allena_modello_tipo_crimine(
                crimini,
                tipo_modello=modello_multi,
                frazione=sampling_multi,
                test_ratio=test_ratio_multi,
                seed=int(seed_multi),
            )

        st.session_state.ml_multiclasse_results_v2[chiave_multi] = metriche_multi

    m = st.session_state.ml_multiclasse_results_v2.get(chiave_multi)

    if m is None:
        st.info("Addestra il modello per visualizzare i risultati.")
    else:
        st.subheader(f"Prestazioni — {m['modello']}")
        m1, m2 = st.columns(2)
        m1.metric("Accuracy", f"{m['accuracy'] * 100:.2f}%")
        m2.metric("Weighted F1", f"{m['weighted_f1'] * 100:.2f}%")

        st.caption(
            f"Classi: {m['numero_classi']} · "
            f"Training: {m['train_count']:,} record · "
            f"Test: {m['test_count']:,} record · "
            f"Seed: {m['seed']}"
        )


# =========================================================
# 3. REGRESSIONE / PREVISIONE MENSILE
# =========================================================

with tab_regressione:
    st.header("Previsione del trend mensile")
    st.write(
        "I crimini vengono aggregati mese per mese e una Linear Regression di Spark "
        "viene utilizzata per stimare l'andamento temporale. Gli ultimi mesi vengono "
        "tenuti separati come test set, mentre il modello può proiettare il trend nei "
        "mesi successivi."
    )
    st.caption(
        "Si tratta di una regressione sul trend temporale, non di un modello specialistico "
        "per serie storiche come ARIMA o SARIMA."
    )

    c1, c2 = st.columns(2)

    with c1:
        mesi_futuri = st.slider(
            "Mesi futuri da stimare",
            min_value=1,
            max_value=24,
            value=6,
            step=1,
            key="reg_mesi_futuri_v2",
        )

    with c2:
        test_ratio_reg = st.slider(
            "Test ratio temporale",
            min_value=0.10,
            max_value=0.40,
            value=0.20,
            step=0.05,
            format="%.2f",
            key="reg_test_ratio_v2",
            help="Gli ultimi mesi, in ordine cronologico, vengono utilizzati come test.",
        )

    chiave_regressione = (
        int(mesi_futuri),
        round(float(test_ratio_reg), 2),
    )

    if st.button(
        "Addestra previsione mensile",
        icon=":material/trending_up:",
        type="primary",
        use_container_width=True,
        key="train_regressione_v2",
    ):
        crimini = carica_dataset()

        with st.spinner("Spark sta addestrando la Linear Regression..."):
            (
                _,
                metriche_reg,
                storico_spark,
                _,
                futuro_spark,
            ) = previsione_crimini_mensili(
                crimini,
                future_months=mesi_futuri,
                test_ratio=test_ratio_reg,
            )

            storico = storico_spark.toPandas()
            futuro = futuro_spark.toPandas()

        st.session_state.ml_regressione_results_v2[chiave_regressione] = {
            "metriche": metriche_reg,
            "storico": storico,
            "futuro": futuro,
        }

    risultato_reg = st.session_state.ml_regressione_results_v2.get(
        chiave_regressione
    )

    if risultato_reg is None:
        st.info("Addestra il modello per visualizzare il trend e la previsione.")
    else:
        m = risultato_reg["metriche"]

        m1, m2 = st.columns(2)
        m1.metric("RMSE", f"{m['rmse']:,.1f}")
        m2.metric("R²", f"{m['r2']:.3f}")

        st.caption(
            f"Mesi training: {m['train_count']} · "
            f"Mesi test: {m['test_count']} · "
            f"Mesi totali: {m['mesi_totali']}"
        )

        storico = risultato_reg["storico"].copy()
        futuro = risultato_reg["futuro"].copy()

        storico["Periodo"] = pd.to_datetime(
            dict(year=storico["Anno"], month=storico["Mese"], day=1)
        )
        futuro["Periodo"] = pd.to_datetime(
            dict(year=futuro["Anno"], month=futuro["Mese"], day=1)
        )

        storico_plot = storico[["Periodo", "Crimini"]].copy()
        storico_plot["Serie"] = "Crimini reali"
        storico_plot = storico_plot.rename(columns={"Crimini": "Valore"})

        futuro_plot = futuro[["Periodo", "prediction"]].copy()
        futuro_plot["Serie"] = "Previsione futura"
        futuro_plot = futuro_plot.rename(columns={"prediction": "Valore"})

        dati_plot = pd.concat(
            [storico_plot, futuro_plot],
            ignore_index=True,
        )

        st.markdown("#### Andamento temporale")
        grafico_reg = (
            alt.Chart(dati_plot)
            .mark_line(point=False)
            .encode(
                x=alt.X("Periodo:T", title="Periodo"),
                y=alt.Y("Valore:Q", title="Numero di crimini"),
                color=alt.Color("Serie:N", title="Serie"),
                tooltip=[
                    alt.Tooltip("Periodo:T", title="Periodo"),
                    alt.Tooltip("Serie:N", title="Serie"),
                    alt.Tooltip("Valore:Q", format=",.0f"),
                ],
            )
            .properties(height=430)
        )
        st.altair_chart(
            applica_stile_grafico(grafico_reg),
            use_container_width=True,
        )

        st.markdown("#### Mesi futuri")
        futuro_tabella = futuro.rename(
            columns={"prediction": "Crimini previsti"}
        ).copy()
        futuro_tabella["Crimini previsti"] = (
            futuro_tabella["Crimini previsti"].round().astype(int)
        )
        st.dataframe(
            futuro_tabella[["Anno", "Mese", "Crimini previsti"]],
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# 4. K-MEANS
# =========================================================

with tab_kmeans:
    st.header("Aree critiche con K-Means")
    st.write(
        "K-Means divide gli eventi criminali in aree geografiche con caratteristiche "
        "spaziali simili. Il numero di aree non viene scelto automaticamente: K indica "
        "direttamente quanti cluster Spark deve cercare."
    )
    st.caption(
        "Il clustering utilizza le coordinate X e Y del dataset; latitudine e longitudine "
        "servono per rappresentare il risultato sulla mappa."
    )

    c1, c2 = st.columns(2)

    with c1:
        sampling_kmeans = st.slider(
            "Sampling",
            min_value=0.01,
            max_value=1.00,
            value=0.10,
            step=0.01,
            format="%.2f",
            key="kmeans_sampling_v5",
            help=(
                "Frazione dei record con coordinate valide utilizzata dal clustering. "
                "0.10 corrisponde a circa il 10% dei record disponibili."
            ),
        )

    with c2:
        k_scelto = st.slider(
            "Numero di cluster K",
            min_value=3,
            max_value=10,
            value=6,
            step=1,
            key="kmeans_k_v5",
        )

    st.caption(
        "Il seed del K-Means è fissato a 42 per rendere il risultato riproducibile."
    )

    chiave_kmeans = (round(float(sampling_kmeans), 2), int(k_scelto))

    if st.button(
        "Esegui clustering",
        icon=":material/hub:",
        type="primary",
        use_container_width=True,
        key="run_kmeans_v5",
    ):
        crimini = carica_dataset()

        with st.spinner(f"Spark sta calcolando {k_scelto} cluster..."):
            try:
                risultato_kmeans = trova_cluster_geografici(
                    crimini,
                    frazione=sampling_kmeans,
                    k=int(k_scelto),
                    seed=42,
                    max_punti_mappa=1200,
                )
                st.session_state.kmeans_risultati_v4[
                    chiave_kmeans
                ] = risultato_kmeans
            except ValueError as errore:
                st.error(str(errore))

    risultato_kmeans = st.session_state.kmeans_risultati_v4.get(
        chiave_kmeans
    )

    if risultato_kmeans is None:
        st.info("Esegui il clustering per visualizzare le aree individuate.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Cluster K", risultato_kmeans["k_finale"])
        m2.metric(
            "Silhouette Score",
            f"{risultato_kmeans['silhouette_finale']:.3f}",
        )
        m3.metric(
            "Record analizzati",
            f"{risultato_kmeans['numero_record']:,}",
        )

        if risultato_kmeans["cluster_effettivi"] != risultato_kmeans["k_finale"]:
            st.warning(
                f"Sono stati richiesti {risultato_kmeans['k_finale']} cluster, ma "
                f"nei dati risultano {risultato_kmeans['cluster_effettivi']} cluster "
                "con almeno un punto assegnato."
            )

        with st.expander("Riepilogo dei cluster"):
            st.dataframe(
                risultato_kmeans["cluster"],
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("#### Distribuzione geografica")
        st.caption(
            "La mappa mostra un campione bilanciato di punti provenienti da tutti i cluster, "
            "in modo che le diverse aree siano sempre rappresentate."
        )

        mappa_kmeans = folium.Map(
            location=[41.8781, -87.6298],
            zoom_start=10,
            tiles="OpenStreetMap",
            prefer_canvas=True,
            control_scale=True,
        )

        colori_cluster = [
            "#FF2BD6",
            "#00F0FF",
            "#7B5CFF",
            "#FFC24B",
            "#2DFFA0",
            "#FF4D6D",
            "#4DA3FF",
            "#B8FF3D",
            "#FF8A3D",
            "#C77DFF",
        ]

        for _, riga in risultato_kmeans["punti_mappa"].iterrows():
            cluster_numero = int(riga["Cluster"])
            colore = colori_cluster[
                (cluster_numero - 1) % len(colori_cluster)
            ]

            folium.CircleMarker(
                location=[riga["Latitude"], riga["Longitude"]],
                radius=3,
                color=colore,
                fill=True,
                fill_color=colore,
                fill_opacity=0.72,
                weight=0,
                tooltip=f"Cluster {cluster_numero}",
            ).add_to(mappa_kmeans)

        for _, riga in risultato_kmeans["cluster"].iterrows():
            cluster_numero = int(riga["Cluster"])
            colore = colori_cluster[
                (cluster_numero - 1) % len(colori_cluster)
            ]

            folium.CircleMarker(
                location=[riga["Latitudine"], riga["Longitudine"]],
                radius=10,
                color=colore,
                fill=True,
                fill_color=colore,
                fill_opacity=1,
                weight=3,
                tooltip=(
                    f"Centro Cluster {cluster_numero} — "
                    f"{int(riga['Crimini']):,} eventi"
                ),
            ).add_to(mappa_kmeans)

        st_folium(
            mappa_kmeans,
            height=650,
            use_container_width=True,
            key=(
                f"kmeans_map_v5_{sampling_kmeans:.2f}_{k_scelto}_"
                f"{risultato_kmeans['cluster_effettivi']}"
            ),
            returned_objects=[],
        )

