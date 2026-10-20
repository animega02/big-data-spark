from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml.feature import VectorAssembler
import math

from pyspark.sql.functions import (
    avg,
    col,
    count,
    desc,
    lit,
    pmod,
    xxhash64
)


# =========================================================
# PREPARAZIONE DATI
# =========================================================

def prepara_dataset_kmeans(
    crimini,
    limite=100000
):

    dati = (
        crimini

        .filter(
            col("ID").isNotNull()
        )

        .filter(
            col("X Coordinate").isNotNull()
        )

        .filter(
            col("Y Coordinate").isNotNull()
        )

        .filter(
            col("Latitude").isNotNull()
        )

        .filter(
            col("Longitude").isNotNull()
        )

        .select(
            "ID",

            col("X Coordinate")
            .cast("double")
            .alias("XCoordinate"),

            col("Y Coordinate")
            .cast("double")
            .alias("YCoordinate"),

            col("Latitude")
            .cast("double")
            .alias("Latitude"),

            col("Longitude")
            .cast("double")
            .alias("Longitude")
        )
    )


    # =====================================================
    # CAMPIONAMENTO DETERMINISTICO
    # =====================================================
    #
    # Evitiamo di prendere semplicemente i primi record.
    # =====================================================

    dati = dati.filter(

        pmod(
            xxhash64(
                col("ID")
            ),
            lit(100)
        )
        <
        10
    )


    dati = dati.limit(
        limite
    )


    return dati


# =========================================================
# K SUGGERITO DALL'ELBOW METHOD
# =========================================================

def trova_k_elbow(risultati_k):

    if len(risultati_k) < 3:
        return None


    # -----------------------------------------------------
    # PUNTO INIZIALE
    # -----------------------------------------------------

    x1 = float(
        risultati_k[0]["K"]
    )

    y1 = float(
        risultati_k[0]["WSS"]
    )


    # -----------------------------------------------------
    # PUNTO FINALE
    # -----------------------------------------------------

    x2 = float(
        risultati_k[-1]["K"]
    )

    y2 = float(
        risultati_k[-1]["WSS"]
    )


    # -----------------------------------------------------
    # DISTANZA DI OGNI PUNTO DALLA RETTA
    # CHE COLLEGA PRIMO E ULTIMO PUNTO
    # -----------------------------------------------------

    denominatore = math.sqrt(
        (y2 - y1) ** 2
        +
        (x2 - x1) ** 2
    )


    if denominatore == 0:
        return int(x1)


    migliore_k = None
    distanza_massima = -1


    for riga in risultati_k[1:-1]:

        x0 = float(
            riga["K"]
        )

        y0 = float(
            riga["WSS"]
        )


        numeratore = abs(
            (y2 - y1) * x0
            -
            (x2 - x1) * y0
            +
            x2 * y1
            -
            y2 * x1
        )


        distanza = (
            numeratore
            /
            denominatore
        )


        if distanza > distanza_massima:

            distanza_massima = distanza

            migliore_k = int(
                riga["K"]
            )


    return migliore_k

# =========================================================
# CLUSTERING
# =========================================================

def trova_cluster_geografici(
    crimini,
    limite=100000,
    k_min=2,
    k_max=8,
    k_manual=None,
    max_punti_mappa=1000
):

    # =====================================================
    # PREPARAZIONE DATASET
    # =====================================================

    dati = prepara_dataset_kmeans(
        crimini,
        limite
    )


    # =====================================================
    # FEATURES
    # =====================================================

    assembler = VectorAssembler(

        inputCols=[
            "XCoordinate",
            "YCoordinate"
        ],

        outputCol="features"
    )


    dati_features = (
        assembler
        .transform(
            dati
        )
        .cache()
    )


    numero_record = (
        dati_features.count()
    )


    if numero_record == 0:

        dati_features.unpersist()

        raise ValueError(
            "Non sono disponibili record con coordinate valide."
        )


    if numero_record < k_max:

        dati_features.unpersist()

        raise ValueError(
            "Il numero di record disponibili è inferiore "
            "al numero massimo di cluster richiesto."
        )


    # =====================================================
    # EVALUATOR SILHOUETTE
    # =====================================================

    evaluator = ClusteringEvaluator(

        featuresCol="features",

        predictionCol="prediction",

        metricName="silhouette",

        distanceMeasure="squaredEuclidean"
    )


    # =====================================================
    # CONFRONTO VALORI DI K
    # =====================================================

    risultati_k = []

    modello_migliore = None

    modello_manuale = None

    silhouette_migliore = -1

    k_migliore = None


    for k in range(
        k_min,
        k_max + 1
    ):


        # -------------------------------------------------
        # MODELLO
        # -------------------------------------------------

        kmeans = KMeans(

            featuresCol="features",

            predictionCol="prediction",

            k=k,

            seed=42,

            maxIter=40
        )


        modello = kmeans.fit(
            dati_features
        )


        # -------------------------------------------------
        # PREDIZIONI
        # -------------------------------------------------

        predizioni = modello.transform(
            dati_features
        )


        # -------------------------------------------------
        # SILHOUETTE
        # -------------------------------------------------

        silhouette = evaluator.evaluate(
            predizioni
        )


        # -------------------------------------------------
        # WSS / TRAINING COST
        # -------------------------------------------------
        #
        # Somma delle distanze quadratiche dei punti
        # dal centroide del proprio cluster.
        #
        # Più è basso, più i cluster sono compatti.
        # -------------------------------------------------

        wss = float(
            modello.summary.trainingCost
        )


        risultati_k.append(
            {
                "K": k,
                "Silhouette": silhouette,
                "WSS": wss
            }
        )


        # -------------------------------------------------
        # MIGLIORE SILHOUETTE
        # -------------------------------------------------

        if silhouette > silhouette_migliore:

            silhouette_migliore = silhouette

            k_migliore = k

            modello_migliore = modello


        # -------------------------------------------------
        # EVENTUALE K MANUALE
        # -------------------------------------------------

        if (
            k_manual is not None
            and
            k == k_manual
        ):

            modello_manuale = modello

    # =========================================================
    # K SUGGERITO DALL'ELBOW METHOD
    # =========================================================

    k_elbow = trova_k_elbow(
        risultati_k
    )


    # =====================================================
    # SCELTA DEL MODELLO FINALE
    # =====================================================

    if k_manual is not None:

        if modello_manuale is None:

            dati_features.unpersist()

            raise ValueError(
                "Il valore K manuale non è compreso "
                "nell'intervallo analizzato."
            )


        modello_finale = (
            modello_manuale
        )

        k_finale = (
            k_manual
        )


        riga_finale = next(

            riga

            for riga in risultati_k

            if riga["K"] == k_manual
        )


        silhouette_finale = (
            riga_finale["Silhouette"]
        )

        wss_finale = (
            riga_finale["WSS"]
        )


        modalita = "manuale"


    else:

        modello_finale = (
            modello_migliore
        )

        k_finale = (
            k_migliore
        )


        riga_finale = next(

            riga

            for riga in risultati_k

            if riga["K"] == k_migliore
        )


        silhouette_finale = (
            riga_finale["Silhouette"]
        )

        wss_finale = (
            riga_finale["WSS"]
        )


        modalita = "automatica"


    # =====================================================
    # PREDIZIONI FINALI
    # =====================================================

    predizioni_finali = (
        modello_finale
        .transform(
            dati_features
        )
        .cache()
    )


    # =====================================================
    # RIEPILOGO CLUSTER
    # =====================================================

    riepilogo_cluster = (
        predizioni_finali

        .groupBy(
            "prediction"
        )

        .agg(

            count("*").alias(
                "Crimini"
            ),

            avg(
                "Latitude"
            ).alias(
                "Latitudine"
            ),

            avg(
                "Longitude"
            ).alias(
                "Longitudine"
            ),

            avg(
                "XCoordinate"
            ).alias(
                "X centro"
            ),

            avg(
                "YCoordinate"
            ).alias(
                "Y centro"
            )
        )

        .orderBy(
            desc("Crimini")
        )
    )


    riepilogo_pandas = (
        riepilogo_cluster
        .toPandas()
    )


    riepilogo_pandas["Cluster"] = (
        riepilogo_pandas["prediction"]
        +
        1
    )


    riepilogo_pandas = riepilogo_pandas[
        [
            "Cluster",
            "Crimini",
            "Latitudine",
            "Longitudine",
            "X centro",
            "Y centro"
        ]
    ]


    # =====================================================
    # PUNTI PER LA MAPPA
    # =====================================================

    punti_mappa = (
        predizioni_finali

        .select(
            "Latitude",
            "Longitude",
            "prediction"
        )

        .limit(
            max_punti_mappa
        )

        .toPandas()
    )


    punti_mappa["Cluster"] = (
        punti_mappa["prediction"]
        +
        1
    )


    # =====================================================
    # PULIZIA
    # =====================================================

    predizioni_finali.unpersist()

    dati_features.unpersist()


    # =====================================================
    # RISULTATO
    # =====================================================

    return {

        "modalita":
            modalita,

        "k_migliore_automatico":
            k_migliore,

        "k_elbow":
            k_elbow,

        "silhouette_migliore_automatica":
            silhouette_migliore,

        "k_finale":
            k_finale,

        "silhouette_finale":
            silhouette_finale,

        "wss_finale":
            wss_finale,

        "numero_record":
            numero_record,

        "valutazioni":
            risultati_k,

        "cluster":
            riepilogo_pandas,

        "punti_mappa":
            punti_mappa
    }