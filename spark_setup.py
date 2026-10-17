from pyspark.sql import SparkSession


def crea_spark():
    spark = (
        SparkSession.builder
        .appName("ChicagoCrimes")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    return spark