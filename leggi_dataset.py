from pyspark.sql import SparkSession

# Avvio di Spark
spark = (
    SparkSession.builder
    .appName("ChicagoCrimes")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

# Percorso del dataset
percorso_dataset = "data/Crimes_-_2001_to_Present.csv"

# Lettura del CSV con Spark
crimini = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(percorso_dataset)
)

print("\n==============================")
print("DATASET CARICATO CORRETTAMENTE")
print("==============================\n")

print("Colonne presenti nel dataset:")
print(crimini.columns)

print("\nPrime 5 righe:")
crimini.show(5, truncate=False)

print("\nStruttura del dataset:")
crimini.printSchema()

spark.stop()