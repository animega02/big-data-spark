from spark_setup import crea_spark

from query_crimini import (
    tipi_crimine_piu_frequenti,
    distretti_con_piu_crimini,
    conteggio_arresti,
    luoghi_piu_frequenti,
    crimini_per_anno
)

spark = crea_spark()

percorso_dataset = "data/Crimes_-_2001_to_Present.csv"

crimini = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(percorso_dataset)
)

anno = 2015
top_n = 10


# Prima query
risultato_tipi = tipi_crimine_piu_frequenti(
    crimini,
    anno,
    top_n
)

print(f"\nTOP {top_n} TIPI DI CRIMINE NEL {anno}\n")

risultato_tipi.show(truncate=False)


# Seconda query
risultato_distretti = distretti_con_piu_crimini(
    crimini,
    anno,
    top_n
)

print(f"\nTOP {top_n} DISTRETTI CON PIÙ CRIMINI NEL {anno}\n")

risultato_distretti.show(truncate=False)

# Terza query
risultato_arresti = conteggio_arresti(
    crimini,
    anno
)

print(f"\nARRESTI NEL {anno}\n")

risultato_arresti.show(truncate=False)

# Quarta query
risultato_luoghi = luoghi_piu_frequenti(
    crimini,
    anno,
    top_n
)

print(f"\nTOP {top_n} LUOGHI CON PIÙ CRIMINI NEL {anno}\n")

risultato_luoghi.show(truncate=False)



spark.stop()