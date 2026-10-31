from datetime import datetime, date

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    LongType,
    DoubleType,
    BooleanType,
    DateType,
)


# =========================================================
# QUERY BASATE ESPLICITAMENTE SU RDD
# =========================================================
#
# Tutte le funzioni di questo file ricevono un DataFrame
# Spark, lo convertono ESPLICITAMENTE in RDD tramite .rdd e
# svolgono l'elaborazione con trasformazioni/azioni RDD come:
#
#   map, filter, flatMap, reduceByKey, distinct,
#   sortByKey, takeOrdered, count, collect
#
# Alla fine il risultato viene riconvertito in DataFrame solo
# per mantenere compatibile la GUI Streamlit già esistente
# (che usa .first(), .show() e .toPandas()).
# =========================================================


# =========================================================
# FUNZIONI DI SUPPORTO
# =========================================================


def _spark(crimini):
    return crimini.sparkSession


def _safe_int(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_string(value):
    if value is None:
        return ""
    return str(value)


def _parse_timestamp(value):
    """Converte Date/_data_timestamp in datetime quando possibile."""

    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())

    testo = str(value).strip()

    if not testo:
        return None

    formati = (
        "%m/%d/%Y %I:%M:%S %p",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    )

    for formato in formati:
        try:
            return datetime.strptime(testo, formato)
        except ValueError:
            pass

    return None


def _df_da_righe(crimini, righe, schema):
    """Riconverte un piccolo risultato RDD/lista in DataFrame per la GUI."""
    return _spark(crimini).createDataFrame(righe, schema=schema)


# =========================================================
# SCHEMI DI OUTPUT
# =========================================================

SCHEMA_TIPO_COUNT = StructType([
    StructField("Primary Type", StringType(), True),
    StructField("count", LongType(), False),
])

SCHEMA_DISTRETTO_COUNT = StructType([
    StructField("District", StringType(), True),
    StructField("count", LongType(), False),
])

SCHEMA_ARRESTO_COUNT = StructType([
    StructField("Arrest", BooleanType(), True),
    StructField("count", LongType(), False),
])

SCHEMA_LUOGO_COUNT = StructType([
    StructField("Location Description", StringType(), True),
    StructField("count", LongType(), False),
])

SCHEMA_ANNO_COUNT = StructType([
    StructField("Year", IntegerType(), True),
    StructField("count", LongType(), False),
])

SCHEMA_MESE_COUNT = StructType([
    StructField("Mese", IntegerType(), True),
    StructField("count", LongType(), False),
])

SCHEMA_COORDINATE = StructType([
    StructField("Latitude", DoubleType(), True),
    StructField("Longitude", DoubleType(), True),
    StructField("Primary Type", StringType(), True),
])

SCHEMA_STATISTICHE = StructType([
    StructField("Totale", LongType(), False),
    StructField("Arresti", LongType(), False),
    StructField("Domestici", LongType(), False),
    StructField("Distretti", LongType(), False),
])

SCHEMA_GIORNO_SETTIMANA = StructType([
    StructField("GiornoNumero", IntegerType(), False),
    StructField("Ordine", IntegerType(), False),
    StructField("count", LongType(), False),
])

SCHEMA_FASCIA = StructType([
    StructField("Fascia", StringType(), False),
    StructField("Ordine", IntegerType(), False),
    StructField("count", LongType(), False),
])


# =========================================================
# VECCHIE QUERY - ORA IMPLEMENTATE CON RDD
# =========================================================


def tipi_crimine_piu_frequenti(crimini, anno, top_n=10):
    # DataFrame -> RDD ESPLICITO
    righe = crimini.rdd

    risultato = (
        righe
        .filter(lambda r: _safe_int(r["Year"]) == int(anno))
        .map(lambda r: (_safe_string(r["Primary Type"]), 1))
        .filter(lambda coppia: coppia[0] != "")
        .reduceByKey(lambda a, b: a + b)
        .takeOrdered(top_n, key=lambda coppia: -coppia[1])
    )

    return _df_da_righe(crimini, risultato, SCHEMA_TIPO_COUNT)



def distretti_con_piu_crimini(crimini, anno, top_n=10):
    righe = crimini.rdd

    risultato = (
        righe
        .filter(lambda r: _safe_int(r["Year"]) == int(anno))
        .map(lambda r: (_safe_string(r["District"]), 1))
        .filter(lambda coppia: coppia[0] != "")
        .reduceByKey(lambda a, b: a + b)
        .takeOrdered(top_n, key=lambda coppia: -coppia[1])
    )

    return _df_da_righe(crimini, risultato, SCHEMA_DISTRETTO_COUNT)



def conteggio_arresti(crimini, anno):
    righe = crimini.rdd

    risultato = (
        righe
        .filter(lambda r: _safe_int(r["Year"]) == int(anno))
        .map(lambda r: r["Arrest"])
        .filter(lambda valore: valore is not None)
        .map(lambda valore: (bool(valore), 1))
        .reduceByKey(lambda a, b: a + b)
        .sortBy(lambda coppia: -coppia[1])
        .collect()
    )

    return _df_da_righe(crimini, risultato, SCHEMA_ARRESTO_COUNT)



def luoghi_piu_frequenti(crimini, anno, top_n=10):
    righe = crimini.rdd

    risultato = (
        righe
        .filter(lambda r: _safe_int(r["Year"]) == int(anno))
        .map(lambda r: (_safe_string(r["Location Description"]), 1))
        .filter(lambda coppia: coppia[0] != "")
        .reduceByKey(lambda a, b: a + b)
        .takeOrdered(top_n, key=lambda coppia: -coppia[1])
    )

    return _df_da_righe(crimini, risultato, SCHEMA_LUOGO_COUNT)



def crimini_per_anno(crimini):
    righe = crimini.rdd

    risultato = (
        righe
        .map(lambda r: _safe_int(r["Year"]))
        .filter(lambda anno: anno is not None)
        .map(lambda anno: (anno, 1))
        .reduceByKey(lambda a, b: a + b)
        .sortByKey(ascending=True)
        .collect()
    )

    return _df_da_righe(crimini, risultato, SCHEMA_ANNO_COUNT)



def crimini_per_mese(crimini, anno):
    righe = crimini.rdd

    risultato = (
        righe
        .filter(lambda r: _safe_int(r["Year"]) == int(anno))
        .map(lambda r: _parse_timestamp(r["Date"]))
        .filter(lambda ts: ts is not None)
        .map(lambda ts: (int(ts.month), 1))
        .reduceByKey(lambda a, b: a + b)
        .sortByKey(ascending=True)
        .collect()
    )

    return _df_da_righe(crimini, risultato, SCHEMA_MESE_COUNT)



def coordinate_crimini(
    crimini,
    anno,
    tipo_crimine=None,
    limite=3000
):
    righe = crimini.rdd

    risultato = (
        righe
        .filter(lambda r: _safe_int(r["Year"]) == int(anno))
        .filter(
            lambda r:
            _safe_float(r["Latitude"]) is not None
            and _safe_float(r["Longitude"]) is not None
        )
    )

    if tipo_crimine is not None:
        risultato = risultato.filter(
            lambda r: _safe_string(r["Primary Type"]) == str(tipo_crimine)
        )

    risultato = (
        risultato
        .map(
            lambda r: (
                _safe_float(r["Latitude"]),
                _safe_float(r["Longitude"]),
                _safe_string(r["Primary Type"]),
            )
        )
        .take(limite)
    )

    return _df_da_righe(crimini, risultato, SCHEMA_COORDINATE)


# =========================================================
# NUOVE QUERY - RDD ESPLICITI
# =========================================================
# Queste funzioni ricevono un DataFrame già filtrato da
# applica_filtri_globali(), ma l'aggregazione viene svolta
# usando l'API RDD.
# =========================================================


# =========================================================
# PANORAMICA GENERALE
# =========================================================


def statistiche_generali(crimini):
    # Conversione esplicita DataFrame -> RDD
    righe = crimini.rdd

    # Una sola passata distribuita. Ogni riga diventa:
    # (totale, arresti, domestici, insieme_distretti)
    parziali = righe.map(
        lambda r: (
            1,
            1 if r["Arrest"] is True else 0,
            1 if r["Domestic"] is True else 0,
            {_safe_string(r["District"])} if _safe_string(r["District"]) != "" else set(),
        )
    )

    zero = (0, 0, 0, set())

    def somma_partizionale(acc, valore):
        return (
            acc[0] + valore[0],
            acc[1] + valore[1],
            acc[2] + valore[2],
            acc[3] | valore[3],
        )

    def combina_partizioni(a, b):
        return (
            a[0] + b[0],
            a[1] + b[1],
            a[2] + b[2],
            a[3] | b[3],
        )

    totale, arresti, domestici, distretti = parziali.aggregate(
        zero,
        somma_partizionale,
        combina_partizioni,
    )

    risultato = [(
        int(totale),
        int(arresti),
        int(domestici),
        int(len(distretti)),
    )]

    return _df_da_righe(crimini, risultato, SCHEMA_STATISTICHE)


# =========================================================
# TOP TIPI DI CRIMINE
# =========================================================


def top_tipi_crimine(crimini, top_n=10):
    righe = crimini.rdd

    risultato = (
        righe
        .map(lambda r: (_safe_string(r["Primary Type"]), 1))
        .filter(lambda coppia: coppia[0] != "")
        .reduceByKey(lambda a, b: a + b)
        .takeOrdered(top_n, key=lambda coppia: -coppia[1])
    )

    return _df_da_righe(crimini, risultato, SCHEMA_TIPO_COUNT)


# =========================================================
# TOP DISTRETTI
# =========================================================


def top_distretti(crimini, top_n=10):
    righe = crimini.rdd

    risultato = (
        righe
        .map(lambda r: (_safe_string(r["District"]), 1))
        .filter(lambda coppia: coppia[0] != "")
        .reduceByKey(lambda a, b: a + b)
        .takeOrdered(top_n, key=lambda coppia: -coppia[1])
    )

    return _df_da_righe(crimini, risultato, SCHEMA_DISTRETTO_COUNT)


# =========================================================
# DISTRIBUZIONE ARRESTI
# =========================================================


def distribuzione_arresti(crimini):
    righe = crimini.rdd

    risultato = (
        righe
        .map(lambda r: r["Arrest"])
        .filter(lambda valore: valore is not None)
        .map(lambda valore: (bool(valore), 1))
        .reduceByKey(lambda a, b: a + b)
        .sortBy(lambda coppia: -coppia[1])
        .collect()
    )

    return _df_da_righe(crimini, risultato, SCHEMA_ARRESTO_COUNT)


# =========================================================
# TOP LUOGHI
# =========================================================


def top_luoghi(crimini, top_n=10):
    righe = crimini.rdd

    risultato = (
        righe
        .map(lambda r: (_safe_string(r["Location Description"]), 1))
        .filter(lambda coppia: coppia[0] != "")
        .reduceByKey(lambda a, b: a + b)
        .takeOrdered(top_n, key=lambda coppia: -coppia[1])
    )

    return _df_da_righe(crimini, risultato, SCHEMA_LUOGO_COUNT)


# =========================================================
# ANDAMENTO TEMPORALE
# =========================================================


def andamento_temporale(crimini, granularita="mese"):
    righe = crimini.rdd

    timestamp_rdd = (
        righe
        .map(lambda r: _parse_timestamp(r["_data_timestamp"]))
        .filter(lambda ts: ts is not None)
    )

    if granularita == "giorno":
        # chiave = data Python; ordinamento cronologico naturale
        risultato = (
            timestamp_rdd
            .map(lambda ts: (ts.date(), 1))
            .reduceByKey(lambda a, b: a + b)
            .sortByKey(ascending=True)
            .collect()
        )

        schema = StructType([
            StructField("Periodo", DateType(), False),
            StructField("count", LongType(), False),
        ])

    elif granularita == "anno":
        risultato = (
            timestamp_rdd
            .map(lambda ts: (int(ts.year), 1))
            .reduceByKey(lambda a, b: a + b)
            .sortByKey(ascending=True)
            .collect()
        )

        schema = StructType([
            StructField("Periodo", IntegerType(), False),
            StructField("count", LongType(), False),
        ])

    else:
        risultato = (
            timestamp_rdd
            .map(lambda ts: (f"{ts.year:04d}-{ts.month:02d}", 1))
            .reduceByKey(lambda a, b: a + b)
            .sortByKey(ascending=True)
            .collect()
        )

        schema = StructType([
            StructField("Periodo", StringType(), False),
            StructField("count", LongType(), False),
        ])

    return _df_da_righe(crimini, risultato, schema)


# =========================================================
# GIORNO DELLA SETTIMANA
# =========================================================


def crimini_per_giorno_settimana(crimini):
    righe = crimini.rdd

    # Python weekday(): lun=0 ... dom=6
    # Spark dayofweek(): dom=1, lun=2 ... sab=7
    risultato = (
        righe
        .map(lambda r: _parse_timestamp(r["_data_timestamp"]))
        .filter(lambda ts: ts is not None)
        .map(
            lambda ts: (
                (
                    ((ts.weekday() + 1) % 7) + 1,  # GiornoNumero stile Spark
                    ts.weekday() + 1,              # Ordine lunedi -> domenica
                ),
                1,
            )
        )
        .reduceByKey(lambda a, b: a + b)
        .map(lambda coppia: (coppia[0][1], (coppia[0][0], coppia[0][1], coppia[1])))
        .sortByKey(ascending=True)
        .values()
        .collect()
    )

    return _df_da_righe(crimini, risultato, SCHEMA_GIORNO_SETTIMANA)


# =========================================================
# FASCIA ORARIA
# =========================================================


def crimini_per_fascia_oraria(crimini):
    righe = crimini.rdd

    def fascia_da_ora(ora):
        if ora < 6:
            return "00:00 - 05:59", 1
        if ora < 12:
            return "06:00 - 11:59", 2
        if ora < 18:
            return "12:00 - 17:59", 3
        return "18:00 - 23:59", 4

    risultato = (
        righe
        .map(lambda r: _parse_timestamp(r["_data_timestamp"]))
        .filter(lambda ts: ts is not None)
        .map(lambda ts: (fascia_da_ora(ts.hour), 1))
        .reduceByKey(lambda a, b: a + b)
        .map(lambda coppia: (coppia[0][1], (coppia[0][0], coppia[0][1], coppia[1])))
        .sortByKey(ascending=True)
        .values()
        .collect()
    )

    return _df_da_righe(crimini, risultato, SCHEMA_FASCIA)
