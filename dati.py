from pathlib import Path

import streamlit as st

from spark_setup import get_spark_session


@st.cache_resource
def ottieni_spark():
    return get_spark_session()


@st.cache_resource
def carica_dataset():
    spark = ottieni_spark()

    cartella_data = Path(__file__).resolve().parent / "data"

    # Preferiamo il nome ufficiale del dataset, ma accettiamo anche un altro
    # CSV presente nella cartella data.
    percorso_preferito = cartella_data / "Crimes_-_2001_to_Present.csv"

    if percorso_preferito.exists():
        percorso_dataset = percorso_preferito
    else:
        csv_disponibili = sorted(cartella_data.glob("*.csv")) if cartella_data.exists() else []

        if not csv_disponibili:
            raise FileNotFoundError(
                "Dataset non trovato. Crea la cartella 'data' nella root del progetto "
                "e inserisci 'Crimes_-_2001_to_Present.csv'."
            )

        percorso_dataset = csv_disponibili[0]

    crimini = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(str(percorso_dataset))
    )

    return crimini
