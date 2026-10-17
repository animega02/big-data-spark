from pathlib import Path

import streamlit as st

from spark_setup import crea_spark


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