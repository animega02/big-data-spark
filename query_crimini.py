from pyspark.sql.functions import (
    col,
    count,
    countDistinct,
    date_format,
    dayofweek,
    desc,
    hour,
    month,
    sum as spark_sum,
    to_date,
    to_timestamp,
    when,
    year
)


# =========================================================
# VECCHIE QUERY
# =========================================================
# Le manteniamo per compatibilità con il codice già scritto.
# Più avanti, se non servono più, potremo eliminarle.


def tipi_crimine_piu_frequenti(crimini, anno, top_n=10):

    risultato = (
        crimini
        .filter(crimini["Year"] == anno)
        .groupBy("Primary Type")
        .count()
        .orderBy(desc("count"))
        .limit(top_n)
    )

    return risultato


def distretti_con_piu_crimini(crimini, anno, top_n=10):

    risultato = (
        crimini
        .filter(crimini["Year"] == anno)
        .filter(crimini["District"].isNotNull())
        .groupBy("District")
        .count()
        .orderBy(desc("count"))
        .limit(top_n)
    )

    return risultato


def conteggio_arresti(crimini, anno):

    risultato = (
        crimini
        .filter(crimini["Year"] == anno)
        .groupBy("Arrest")
        .count()
        .orderBy(desc("count"))
    )

    return risultato


def luoghi_piu_frequenti(crimini, anno, top_n=10):

    risultato = (
        crimini
        .filter(crimini["Year"] == anno)
        .filter(crimini["Location Description"].isNotNull())
        .groupBy("Location Description")
        .count()
        .orderBy(desc("count"))
        .limit(top_n)
    )

    return risultato


def crimini_per_anno(crimini):

    risultato = (
        crimini
        .filter(crimini["Year"].isNotNull())
        .groupBy("Year")
        .count()
        .orderBy("Year")
    )

    return risultato


def crimini_per_mese(crimini, anno):

    risultato = (
        crimini
        .filter(crimini["Year"] == anno)
        .withColumn(
            "Data",
            to_timestamp(
                "Date",
                "MM/dd/yyyy hh:mm:ss a"
            )
        )
        .withColumn(
            "Mese",
            month("Data")
        )
        .filter(crimini["Date"].isNotNull())
        .groupBy("Mese")
        .count()
        .orderBy("Mese")
    )

    return risultato


def coordinate_crimini(
    crimini,
    anno,
    tipo_crimine=None,
    limite=3000
):

    risultato = (
        crimini
        .filter(crimini["Year"] == anno)
        .filter(crimini["Latitude"].isNotNull())
        .filter(crimini["Longitude"].isNotNull())
    )

    if tipo_crimine is not None:

        risultato = risultato.filter(
            crimini["Primary Type"] == tipo_crimine
        )

    risultato = (
        risultato
        .select(
            "Latitude",
            "Longitude",
            "Primary Type"
        )
        .limit(limite)
    )

    return risultato


# =========================================================
# NUOVE QUERY
# =========================================================
#
# Queste funzioni ricevono un DataFrame già filtrato da
# applica_filtri_globali().
#
# Il loro compito è quindi solo quello di aggregare i dati.
# =========================================================


# =========================================================
# PANORAMICA GENERALE
# =========================================================

def statistiche_generali(crimini):

    risultato = crimini.agg(

        count("*").alias(
            "Totale"
        ),

        spark_sum(
            when(
                col("Arrest") == True,
                1
            ).otherwise(0)
        ).alias(
            "Arresti"
        ),

        spark_sum(
            when(
                col("Domestic") == True,
                1
            ).otherwise(0)
        ).alias(
            "Domestici"
        ),

        countDistinct(
            "District"
        ).alias(
            "Distretti"
        )
    )

    return risultato


# =========================================================
# TOP TIPI DI CRIMINE
# =========================================================

def top_tipi_crimine(
    crimini,
    top_n=10
):

    risultato = (
        crimini

        .filter(
            col("Primary Type").isNotNull()
        )

        .groupBy(
            "Primary Type"
        )

        .count()

        .orderBy(
            desc("count")
        )

        .limit(
            top_n
        )
    )

    return risultato


# =========================================================
# TOP DISTRETTI
# =========================================================

def top_distretti(
    crimini,
    top_n=10
):

    risultato = (
        crimini

        .filter(
            col("District").isNotNull()
        )

        .groupBy(
            "District"
        )

        .count()

        .orderBy(
            desc("count")
        )

        .limit(
            top_n
        )
    )

    return risultato


# =========================================================
# DISTRIBUZIONE ARRESTI
# =========================================================

def distribuzione_arresti(
    crimini
):

    risultato = (
        crimini

        .filter(
            col("Arrest").isNotNull()
        )

        .groupBy(
            "Arrest"
        )

        .count()

        .orderBy(
            desc("count")
        )
    )

    return risultato


# =========================================================
# TOP LUOGHI
# =========================================================

def top_luoghi(
    crimini,
    top_n=10
):

    risultato = (
        crimini

        .filter(
            col("Location Description").isNotNull()
        )

        .groupBy(
            "Location Description"
        )

        .count()

        .orderBy(
            desc("count")
        )

        .limit(
            top_n
        )
    )

    return risultato


# =========================================================
# ANDAMENTO TEMPORALE
# =========================================================

def andamento_temporale(
    crimini,
    granularita="mese"
):

    risultato = crimini.filter(
        col("_data_timestamp").isNotNull()
    )


    # -----------------------------------------------------
    # GIORNO
    # -----------------------------------------------------

    if granularita == "giorno":

        risultato = (
            risultato

            .withColumn(
                "Periodo",
                to_date(
                    col("_data_timestamp")
                )
            )

            .groupBy(
                "Periodo"
            )

            .count()

            .orderBy(
                "Periodo"
            )
        )


    # -----------------------------------------------------
    # ANNO
    # -----------------------------------------------------

    elif granularita == "anno":

        risultato = (
            risultato

            .withColumn(
                "Periodo",
                year(
                    col("_data_timestamp")
                )
            )

            .groupBy(
                "Periodo"
            )

            .count()

            .orderBy(
                "Periodo"
            )
        )


    # -----------------------------------------------------
    # MESE
    # -----------------------------------------------------

    else:

        risultato = (
            risultato

            .withColumn(
                "Periodo",
                date_format(
                    col("_data_timestamp"),
                    "yyyy-MM"
                )
            )

            .groupBy(
                "Periodo"
            )

            .count()

            .orderBy(
                "Periodo"
            )
        )


    return risultato


# =========================================================
# GIORNO DELLA SETTIMANA
# =========================================================

def crimini_per_giorno_settimana(
    crimini
):

    risultato = (
        crimini

        .filter(
            col("_data_timestamp").isNotNull()
        )

        .withColumn(
            "GiornoNumero",
            dayofweek(
                col("_data_timestamp")
            )
        )

        # Spark:
        # 1 = domenica
        # 2 = lunedì
        # ...
        # 7 = sabato
        #
        # Creiamo quindi un ordine più naturale:
        # lunedì -> domenica.

        .withColumn(
            "Ordine",

            when(
                col("GiornoNumero") == 2,
                1
            )

            .when(
                col("GiornoNumero") == 3,
                2
            )

            .when(
                col("GiornoNumero") == 4,
                3
            )

            .when(
                col("GiornoNumero") == 5,
                4
            )

            .when(
                col("GiornoNumero") == 6,
                5
            )

            .when(
                col("GiornoNumero") == 7,
                6
            )

            .otherwise(7)
        )

        .groupBy(
            "GiornoNumero",
            "Ordine"
        )

        .count()

        .orderBy(
            "Ordine"
        )
    )

    return risultato


# =========================================================
# FASCIA ORARIA
# =========================================================

def crimini_per_fascia_oraria(
    crimini
):

    risultato = (
        crimini

        .filter(
            col("_data_timestamp").isNotNull()
        )

        .withColumn(
            "Ora",
            hour(
                col("_data_timestamp")
            )
        )

        .withColumn(
            "Fascia",

            when(
                (col("Ora") >= 0)
                &
                (col("Ora") < 6),
                "00:00 - 05:59"
            )

            .when(
                (col("Ora") >= 6)
                &
                (col("Ora") < 12),
                "06:00 - 11:59"
            )

            .when(
                (col("Ora") >= 12)
                &
                (col("Ora") < 18),
                "12:00 - 17:59"
            )

            .otherwise(
                "18:00 - 23:59"
            )
        )

        .withColumn(
            "Ordine",

            when(
                col("Ora") < 6,
                1
            )

            .when(
                col("Ora") < 12,
                2
            )

            .when(
                col("Ora") < 18,
                3
            )

            .otherwise(4)
        )

        .groupBy(
            "Fascia",
            "Ordine"
        )

        .count()

        .orderBy(
            "Ordine"
        )
    )

    return risultato