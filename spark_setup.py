import streamlit as st
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession


@st.cache_resource
def get_spark_context() -> SparkContext:
    """Crea (o riusa) un solo SparkContext per tutta l'app Streamlit.

    Configurazione pensata per un PC Windows con circa 16 GB di RAM:
    4 task Spark concorrenti e 3 GB di heap per il driver.
    """
    conf = (
        SparkConf()
        .setAppName("ChicagoCrimesStreamlit")
        .setMaster("local[4]")
        .set("spark.driver.memory", "3g")
        # In local mode il parametro davvero importante è driver.memory;
        # executor.memory viene lasciato per compatibilità con eventuali
        # esecuzioni non-locali future.
        .set("spark.executor.memory", "3g")
        .set("spark.sql.shuffle.partitions", "16")
        .set("spark.default.parallelism", "8")
    )

    sc = SparkContext.getOrCreate(conf=conf)
    sc.setLogLevel("ERROR")
    return sc


@st.cache_resource
def get_spark_session() -> SparkSession:
    """Restituisce la SparkSession condivisa dall'app."""
    get_spark_context()
    spark = SparkSession.builder.getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def crea_spark() -> SparkSession:
    """Alias retrocompatibile usato dai vecchi file del progetto.

    Alcuni moduli storici importano ancora ``crea_spark``. Tenerlo evita
    ImportError e fa sì che tutti usino comunque la stessa sessione cached.
    """
    return get_spark_session()
