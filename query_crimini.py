from pyspark.sql.functions import desc, to_timestamp, month


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
# Queste ricevono già un DataFrame filtrato da
# applica_filtri_globali().
#
# Quindi NON filtrano nuovamente per anno.
# Sono quelle che useremo nella nuova pagina Analisi.
# =========================================================


def top_tipi_crimine(crimini, top_n=10):

    risultato = (
        crimini
        .filter(crimini["Primary Type"].isNotNull())
        .groupBy("Primary Type")
        .count()
        .orderBy(desc("count"))
        .limit(top_n)
    )

    return risultato


def top_distretti(crimini, top_n=10):

    risultato = (
        crimini
        .filter(crimini["District"].isNotNull())
        .groupBy("District")
        .count()
        .orderBy(desc("count"))
        .limit(top_n)
    )

    return risultato


def distribuzione_arresti(crimini):

    risultato = (
        crimini
        .filter(crimini["Arrest"].isNotNull())
        .groupBy("Arrest")
        .count()
        .orderBy(desc("count"))
    )

    return risultato


def top_luoghi(crimini, top_n=10):

    risultato = (
        crimini
        .filter(crimini["Location Description"].isNotNull())
        .groupBy("Location Description")
        .count()
        .orderBy(desc("count"))
        .limit(top_n)
    )

    return risultato


def andamento_annuale(crimini):

    risultato = (
        crimini
        .filter(crimini["Year"].isNotNull())
        .groupBy("Year")
        .count()
        .orderBy("Year")
    )

    return risultato


def andamento_mensile(crimini):

    risultato = (
        crimini
        .withColumn(
            "_data_analisi",
            to_timestamp(
                "Date",
                "MM/dd/yyyy hh:mm:ss a"
            )
        )
        .withColumn(
            "Mese",
            month("_data_analisi")
        )
        .filter(crimini["Date"].isNotNull())
        .groupBy("Mese")
        .count()
        .orderBy("Mese")
    )

    return risultato