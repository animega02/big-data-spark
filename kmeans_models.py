from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import Window
from pyspark.sql.functions import (
    avg,
    col,
    count,
    lit,
    row_number,
    xxhash64,
)


# =========================================================
# PREPARAZIONE DATI
# =========================================================

def prepara_dataset_kmeans(crimini, frazione=0.10, seed=42):
    """Seleziona e campiona i record con coordinate valide usati dal clustering."""

    frazione = float(frazione)
    seed = int(seed)

    if not 0 < frazione <= 1.0:
        raise ValueError("frazione deve essere compresa tra 0 e 1.")

    dati = (
        crimini
        .filter(col("ID").isNotNull())
        .filter(col("X Coordinate").isNotNull())
        .filter(col("Y Coordinate").isNotNull())
        .filter(col("Latitude").isNotNull())
        .filter(col("Longitude").isNotNull())
        .select(
            "ID",
            col("X Coordinate").cast("double").alias("XCoordinate"),
            col("Y Coordinate").cast("double").alias("YCoordinate"),
            col("Latitude").cast("double").alias("Latitude"),
            col("Longitude").cast("double").alias("Longitude"),
        )
    )

    if frazione < 1.0:
        dati = dati.sample(
            withReplacement=False,
            fraction=frazione,
            seed=seed,
        )

    return dati


# =========================================================
# CLUSTERING
# =========================================================

def trova_cluster_geografici(
    crimini,
    frazione=0.10,
    k=6,
    seed=42,
    max_punti_mappa=1000,
):
    """
    Esegue un singolo K-Means con il valore K scelto dall'utente.

    Non viene più cercato automaticamente un K alternativo: se k=8,
    Spark addestra direttamente KMeans(k=8).
    """

    k = int(k)
    seed = int(seed)

    if k < 2:
        raise ValueError("K deve essere almeno 2.")

    dati = prepara_dataset_kmeans(
        crimini,
        frazione=frazione,
        seed=seed,
    )

    assembler = VectorAssembler(
        inputCols=["XCoordinate", "YCoordinate"],
        outputCol="features",
    )

    dati_features = assembler.transform(dati).cache()
    numero_record = dati_features.count()

    if numero_record == 0:
        dati_features.unpersist()
        raise ValueError("Non sono disponibili record con coordinate valide.")

    if numero_record < k:
        dati_features.unpersist()
        raise ValueError(
            "Il numero di record disponibili è inferiore al numero di cluster richiesto."
        )

    kmeans = KMeans(
        featuresCol="features",
        predictionCol="prediction",
        k=k,
        seed=seed,
        maxIter=40,
    )

    modello = kmeans.fit(dati_features)
    predizioni = modello.transform(dati_features).cache()

    evaluator = ClusteringEvaluator(
        featuresCol="features",
        predictionCol="prediction",
        metricName="silhouette",
        distanceMeasure="squaredEuclidean",
    )

    silhouette = float(evaluator.evaluate(predizioni))
    wss = float(modello.summary.trainingCost)

    # -----------------------------------------------------
    # RIEPILOGO CLUSTER
    # -----------------------------------------------------
    riepilogo_cluster = (
        predizioni
        .groupBy("prediction")
        .agg(
            count("*").alias("Crimini"),
            avg("Latitude").alias("Latitudine"),
            avg("Longitude").alias("Longitudine"),
            avg("XCoordinate").alias("X centro"),
            avg("YCoordinate").alias("Y centro"),
        )
        .orderBy("prediction")
    )

    riepilogo_pandas = riepilogo_cluster.toPandas()
    cluster_effettivi = len(riepilogo_pandas)

    riepilogo_pandas["Cluster"] = riepilogo_pandas["prediction"] + 1
    riepilogo_pandas = riepilogo_pandas[
        [
            "Cluster",
            "Crimini",
            "Latitudine",
            "Longitudine",
            "X centro",
            "Y centro",
        ]
    ]

    # -----------------------------------------------------
    # PUNTI PER LA MAPPA
    # -----------------------------------------------------
    # Non prendiamo semplicemente i primi 1000 record: in quel caso la mappa
    # può mostrare solo alcuni cluster. Prendiamo invece punti da OGNI cluster.
    punti_per_cluster = max(1, int(max_punti_mappa) // max(k, 1))

    finestra_cluster = Window.partitionBy("prediction").orderBy(
        xxhash64(col("ID"), lit(seed))
    )

    punti_mappa = (
        predizioni
        .withColumn("_ordine_cluster", row_number().over(finestra_cluster))
        .filter(col("_ordine_cluster") <= punti_per_cluster)
        .select("Latitude", "Longitude", "prediction")
        .toPandas()
    )

    punti_mappa["Cluster"] = punti_mappa["prediction"] + 1

    predizioni.unpersist()
    dati_features.unpersist()

    return {
        "k_finale": k,
        "cluster_effettivi": cluster_effettivi,
        "silhouette_finale": silhouette,
        "wss_finale": wss,
        "numero_record": numero_record,
        "frazione": float(frazione),
        "seed": seed,
        "cluster": riepilogo_pandas,
        "punti_mappa": punti_mappa,
    }
