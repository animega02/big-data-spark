from pyspark.sql import SparkSession

# Creiamo una sessione Spark
spark = (
    SparkSession.builder
    .appName("PrimoTestSpark")
    .master("local[*]")
    .getOrCreate()
)

# Riduciamo i messaggi di log di Spark
spark.sparkContext.setLogLevel("ERROR")

print("================================")
print("SPARK FUNZIONA!")
print("Versione Spark:", spark.version)
print("================================")

# Creiamo dei dati di prova
dati = [
    ("THEFT", 10),
    ("BATTERY", 7),
    ("ROBBERY", 3)
]

df = spark.createDataFrame(
    dati,
    ["TipoCrimine", "Numero"]
)

df.show()

# Chiudiamo Spark
spark.stop()