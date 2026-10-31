from pyspark.ml import Pipeline

from pyspark.ml.classification import (
    GBTClassifier,
    LogisticRegression,
    RandomForestClassifier
)

from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator,
    RegressionEvaluator
)

from pyspark.ml.feature import (
    IndexToString,
    OneHotEncoder,
    StringIndexer,
    VectorAssembler
)

from pyspark.ml.regression import LinearRegression

from pyspark.sql.functions import (
    col,
    dayofweek,
    floor,
    hour,
    lit,
    max as spark_max,
    month,
    pmod,
    to_timestamp,
    when,
    year
)

from pyspark.sql.window import Window
from pyspark.sql.functions import row_number


FORMATO_DATA = "MM/dd/yyyy hh:mm:ss a"


# =========================================================
# PREPARAZIONE DATASET
# =========================================================

def prepara_dataset_arresto(
    crimini,
    frazione=1.0,
    seed=42
):

    dati = (
        crimini

        # -------------------------------------------------
        # DATA
        # -------------------------------------------------

        .withColumn(
            "_data_ml",
            to_timestamp(
                col("Date"),
                FORMATO_DATA
            )
        )

        .withColumn(
            "Mese",
            month(
                col("_data_ml")
            )
        )

        .withColumn(
            "GiornoSettimana",
            dayofweek(
                col("_data_ml")
            )
        )

        .withColumn(
            "Ora",
            hour(
                col("_data_ml")
            )
        )

        # -------------------------------------------------
        # LABEL
        # -------------------------------------------------

        .withColumn(
            "label",
            col("Arrest").cast("double")
        )

        # -------------------------------------------------
        # DOMESTIC
        # -------------------------------------------------

        .withColumn(
            "DomesticNumerico",

            when(
                col("Domestic") == True,
                1.0
            ).otherwise(0.0)
        )

        # -------------------------------------------------
        # DISTRETTO
        # -------------------------------------------------

        .withColumn(
            "DistrictML",
            col("District").cast("string")
        )
    )


    # =====================================================
    # VALORI MANCANTI
    # =====================================================

    dati = dati.fillna(
        {
            "Primary Type": "UNKNOWN",
            "Location Description": "UNKNOWN",
            "DistrictML": "UNKNOWN"
        }
    )


    # =====================================================
    # COLONNE NECESSARIE
    # =====================================================

    dati = dati.select(
        "ID",
        "Primary Type",
        "Location Description",
        "DistrictML",
        "DomesticNumerico",
        "Mese",
        "GiornoSettimana",
        "Ora",
        "label"
    )


    # =====================================================
    # RECORD VALIDI
    # =====================================================

    dati = (
        dati

        .filter(
            col("ID").isNotNull()
        )

        .filter(
            col("label").isNotNull()
        )

        .filter(
            col("Mese").isNotNull()
        )

        .filter(
            col("GiornoSettimana").isNotNull()
        )

        .filter(
            col("Ora").isNotNull()
        )
    )

    if not 0 < float(frazione) <= 1.0:
        raise ValueError("frazione deve essere compresa tra 0 e 1.")

    if frazione < 1.0:
        dati = dati.sample(
            withReplacement=False,
            fraction=float(frazione),
            seed=int(seed)
        )

    return dati


# =========================================================
# TRAIN / TEST DETERMINISTICO
# =========================================================

def crea_train_test(
    dati,
    test_ratio=0.2,
    seed=42
):
    """Suddivide i dati in training e test in modo riproducibile."""

    test_ratio = float(test_ratio)

    if not 0 < test_ratio < 1:
        raise ValueError("test_ratio deve essere compreso tra 0 e 1.")

    train, test = dati.randomSplit(
        [1.0 - test_ratio, test_ratio],
        seed=int(seed)
    )

    return train, test


# =========================================================
# CLASS WEIGHTING
# =========================================================

def aggiungi_pesi_classi(
    train
):

    conteggi = (
        train
        .groupBy(
            "label"
        )
        .count()
        .collect()
    )


    conteggio_0 = 0
    conteggio_1 = 0


    for riga in conteggi:

        if float(riga["label"]) == 0.0:

            conteggio_0 = int(
                riga["count"]
            )

        elif float(riga["label"]) == 1.0:

            conteggio_1 = int(
                riga["count"]
            )


    totale = (
        conteggio_0
        +
        conteggio_1
    )


    # =====================================================
    # FORMULA BALANCED
    # =====================================================
    #
    # peso_classe =
    #
    # totale
    # ----------------------------
    # numero_classi * casi_classe
    #
    # =====================================================

    peso_0 = (
        totale
        /
        (2 * conteggio_0)
        if conteggio_0 > 0
        else 1.0
    )


    peso_1 = (
        totale
        /
        (2 * conteggio_1)
        if conteggio_1 > 0
        else 1.0
    )


    train_pesato = train.withColumn(

        "classWeight",

        when(
            col("label") == 1.0,
            lit(peso_1)
        ).otherwise(
            lit(peso_0)
        )
    )


    return (
        train_pesato,
        peso_0,
        peso_1
    )


# =========================================================
# PIPELINE
# =========================================================

def crea_pipeline_arresto(
    tipo_modello,
    bilanciato=False,
    seed=42
):

    # =====================================================
    # STRING INDEXER
    # =====================================================

    index_primary_type = StringIndexer(
        inputCol="Primary Type",
        outputCol="primary_type_index",
        handleInvalid="keep"
    )


    index_location = StringIndexer(
        inputCol="Location Description",
        outputCol="location_index",
        handleInvalid="keep"
    )


    index_district = StringIndexer(
        inputCol="DistrictML",
        outputCol="district_index",
        handleInvalid="keep"
    )


    # =====================================================
    # ONE HOT ENCODER
    # =====================================================

    encoder = OneHotEncoder(

        inputCols=[
            "primary_type_index",
            "location_index",
            "district_index"
        ],

        outputCols=[
            "primary_type_encoded",
            "location_encoded",
            "district_encoded"
        ],

        handleInvalid="keep"
    )


    # =====================================================
    # VECTOR ASSEMBLER
    # =====================================================

    assembler = VectorAssembler(

        inputCols=[
            "primary_type_encoded",
            "location_encoded",
            "district_encoded",
            "DomesticNumerico",
            "Mese",
            "GiornoSettimana",
            "Ora"
        ],

        outputCol="features",

        handleInvalid="keep"
    )


    # =====================================================
    # LOGISTIC REGRESSION
    # =====================================================

    if tipo_modello == "Logistic Regression":

        if bilanciato:

            classificatore = LogisticRegression(
                featuresCol="features",
                labelCol="label",
                predictionCol="prediction",
                probabilityCol="probability",
                rawPredictionCol="rawPrediction",
                weightCol="classWeight",
                maxIter=50
            )

        else:

            classificatore = LogisticRegression(
                featuresCol="features",
                labelCol="label",
                predictionCol="prediction",
                probabilityCol="probability",
                rawPredictionCol="rawPrediction",
                maxIter=50
            )


    # =====================================================
    # RANDOM FOREST
    # =====================================================

    elif tipo_modello == "Random Forest":

        parametri = dict(
            featuresCol="features",
            labelCol="label",
            predictionCol="prediction",
            probabilityCol="probability",
            rawPredictionCol="rawPrediction",
            numTrees=30,
            maxDepth=8,
            featureSubsetStrategy="sqrt",
            seed=int(seed)
        )

        if bilanciato:
            parametri["weightCol"] = "classWeight"

        classificatore = RandomForestClassifier(**parametri)


    # =====================================================
    # GRADIENT-BOOSTED TREES
    # =====================================================

    elif tipo_modello == "GBT":

        parametri = dict(
            featuresCol="features",
            labelCol="label",
            predictionCol="prediction",
            probabilityCol="probability",
            rawPredictionCol="rawPrediction",
            maxIter=50,
            maxDepth=6,
            seed=int(seed)
        )

        if bilanciato:
            parametri["weightCol"] = "classWeight"

        classificatore = GBTClassifier(**parametri)


    else:
        raise ValueError(f"Modello non supportato: {tipo_modello}")


    return Pipeline(
        stages=[
            index_primary_type,
            index_location,
            index_district,
            encoder,
            assembler,
            classificatore
        ]
    )


# =========================================================
# MATRICE DI CONFUSIONE
# =========================================================

def calcola_matrice_confusione(
    predizioni
):

    matrice = (
        predizioni

        .groupBy(
            "label",
            "prediction"
        )

        .count()

        .orderBy(
            "label",
            "prediction"
        )
    )


    righe = matrice.collect()


    tn = 0
    fp = 0
    fn = 0
    tp = 0


    for riga in righe:

        reale = int(
            riga["label"]
        )

        predetto = int(
            riga["prediction"]
        )

        numero = int(
            riga["count"]
        )


        if reale == 0 and predetto == 0:

            tn = numero


        elif reale == 0 and predetto == 1:

            fp = numero


        elif reale == 1 and predetto == 0:

            fn = numero


        elif reale == 1 and predetto == 1:

            tp = numero


    return (
        matrice,
        tn,
        fp,
        fn,
        tp
    )


# =========================================================
# TRAINING
# =========================================================

def allena_modello_arresto(
    crimini,
    tipo_modello="Logistic Regression",
    bilanciato=False,
    frazione=0.10,
    test_ratio=0.2,
    seed=42
):

    # =====================================================
    # DATASET
    # =====================================================

    dati = prepara_dataset_arresto(
        crimini,
        frazione=frazione,
        seed=seed
    )


    # =====================================================
    # STESSO TRAIN / TEST PER TUTTI
    # =====================================================

    train, test = crea_train_test(
        dati,
        test_ratio=test_ratio,
        seed=seed
    )


    train = train.cache()
    test = test.cache()


    train_count = train.count()
    test_count = test.count()


    # =====================================================
    # CLASS WEIGHTING
    # =====================================================

    peso_0 = 1.0
    peso_1 = 1.0


    if bilanciato:

        (
            train_modello,
            peso_0,
            peso_1
        ) = aggiungi_pesi_classi(
            train
        )


    else:

        train_modello = train


    # =====================================================
    # MODELLO
    # =====================================================

    pipeline = crea_pipeline_arresto(
        tipo_modello,
        bilanciato,
        seed=seed
    )


    modello = pipeline.fit(
        train_modello
    )


    # =====================================================
    # PREDIZIONI
    # =====================================================

    predizioni = modello.transform(
        test
    )


    # =====================================================
    # MATRICE CONFUSIONE
    # =====================================================

    (
        matrice,
        tn,
        fp,
        fn,
        tp
    ) = calcola_matrice_confusione(
        predizioni
    )


    # Piccolissima tabella: possiamo convertirla subito.
    matrice_pandas = matrice.toPandas()


    totale = (
        tn
        +
        fp
        +
        fn
        +
        tp
    )


    # =====================================================
    # ACCURACY
    # =====================================================

    accuracy = (
        (tp + tn)
        /
        totale
        if totale > 0
        else 0
    )


    # =====================================================
    # PRECISION ARRESTI
    # =====================================================

    precision_arresti = (
        tp
        /
        (tp + fp)
        if (tp + fp) > 0
        else 0
    )


    # =====================================================
    # RECALL ARRESTI
    # =====================================================

    recall_arresti = (
        tp
        /
        (tp + fn)
        if (tp + fn) > 0
        else 0
    )


    # =====================================================
    # F1 ARRESTI
    # =====================================================

    if (
        precision_arresti
        +
        recall_arresti
        >
        0
    ):

        f1_arresti = (
            2
            *
            precision_arresti
            *
            recall_arresti
            /
            (
                precision_arresti
                +
                recall_arresti
            )
        )


    else:

        f1_arresti = 0


    # =====================================================
    # SPECIFICITÀ
    # =====================================================

    specificita = (
        tn
        /
        (tn + fp)
        if (tn + fp) > 0
        else 0
    )


    # =====================================================
    # BALANCED ACCURACY
    # =====================================================

    balanced_accuracy = (
        recall_arresti
        +
        specificita
    ) / 2


    # =====================================================
    # AUC ROC
    # =====================================================

    auc_evaluator = (
        BinaryClassificationEvaluator(
            labelCol="label",
            rawPredictionCol="rawPrediction",
            metricName="areaUnderROC"
        )
    )


    auc = auc_evaluator.evaluate(
        predizioni
    )


    # =====================================================
    # DISTRIBUZIONE TEST
    # =====================================================

    arresti_reali = (
        tp
        +
        fn
    )


    non_arresti_reali = (
        tn
        +
        fp
    )


    percentuale_arresti = (
        arresti_reali
        /
        totale
        if totale > 0
        else 0
    )


    # =====================================================
    # BASELINE
    # =====================================================

    baseline_accuracy = (
        max(
            arresti_reali,
            non_arresti_reali
        )
        /
        totale
        if totale > 0
        else 0
    )


    # =====================================================
    # NOME CONFIGURAZIONE
    # =====================================================

    nome_modello = tipo_modello


    if bilanciato:

        nome_modello += " bilanciata"


    # =====================================================
    # METRICHE
    # =====================================================

    metriche = {

        "modello": nome_modello,

        "tipo_modello": tipo_modello,

        "bilanciato": bilanciato,

        "accuracy": accuracy,

        "balanced_accuracy": balanced_accuracy,

        "auc": auc,

        "precision_arresti": precision_arresti,

        "recall_arresti": recall_arresti,

        "f1_arresti": f1_arresti,

        "specificita": specificita,

        "baseline_accuracy": baseline_accuracy,

        "percentuale_arresti": percentuale_arresti,

        "train_count": train_count,

        "test_count": test_count,

        "frazione": float(frazione),

        "test_ratio": float(test_ratio),

        "seed": int(seed),

        "tn": tn,

        "fp": fp,

        "fn": fn,

        "tp": tp,

        "peso_non_arresto": peso_0,

        "peso_arresto": peso_1
    }


    # =====================================================
    # LIBERA CACHE SPARK
    # =====================================================

    train.unpersist()
    test.unpersist()


    return (
        modello,
        metriche,
        matrice_pandas
    )
# =========================================================
# CLASSIFICAZIONE MULTICLASSE DEL TIPO DI CRIMINE
# =========================================================

def prepara_dataset_tipo_crimine(
    crimini,
    frazione=1.0,
    seed=42
):
    """Prepara un dataset Spark per prevedere Primary Type."""

    dati = (
        crimini
        .withColumn(
            "_data_ml",
            to_timestamp(col("Date"), FORMATO_DATA)
        )
        .withColumn("Mese", month(col("_data_ml")))
        .withColumn("GiornoSettimana", dayofweek(col("_data_ml")))
        .withColumn("Ora", hour(col("_data_ml")))
        .withColumn(
            "DomesticNumerico",
            when(col("Domestic") == True, 1.0).otherwise(0.0)
        )
        .withColumn("DistrictML", col("District").cast("string"))
        .filter(col("ID").isNotNull())
        .filter(col("Primary Type").isNotNull())
        .filter(col("Mese").isNotNull())
        .filter(col("GiornoSettimana").isNotNull())
        .filter(col("Ora").isNotNull())
        .fillna(
            {
                "Location Description": "UNKNOWN",
                "DistrictML": "UNKNOWN"
            }
        )
        .select(
            "ID",
            "Primary Type",
            "Location Description",
            "DistrictML",
            "DomesticNumerico",
            "Mese",
            "GiornoSettimana",
            "Ora"
        )
    )

    if not 0 < float(frazione) <= 1.0:
        raise ValueError("frazione deve essere compresa tra 0 e 1.")

    if frazione < 1.0:
        dati = dati.sample(
            withReplacement=False,
            fraction=float(frazione),
            seed=int(seed)
        )

    return dati


def crea_pipeline_tipo_crimine(tipo_modello, seed=42):
    """Crea la Pipeline Spark ML per la classificazione multiclasse."""

    label_indexer = StringIndexer(
        inputCol="Primary Type",
        outputCol="label",
        handleInvalid="skip"
    )

    index_location = StringIndexer(
        inputCol="Location Description",
        outputCol="location_index",
        handleInvalid="keep"
    )

    index_district = StringIndexer(
        inputCol="DistrictML",
        outputCol="district_index",
        handleInvalid="keep"
    )

    encoder = OneHotEncoder(
        inputCols=["location_index", "district_index"],
        outputCols=["location_encoded", "district_encoded"],
        handleInvalid="keep"
    )

    assembler = VectorAssembler(
        inputCols=[
            "location_encoded",
            "district_encoded",
            "DomesticNumerico",
            "Mese",
            "GiornoSettimana",
            "Ora"
        ],
        outputCol="features",
        handleInvalid="keep"
    )

    if tipo_modello == "Random Forest":
        classificatore = RandomForestClassifier(
            featuresCol="features",
            labelCol="label",
            predictionCol="prediction",
            numTrees=60,
            maxDepth=10,
            featureSubsetStrategy="sqrt",
            seed=int(seed)
        )

    elif tipo_modello == "Logistic Regression":
        classificatore = LogisticRegression(
            featuresCol="features",
            labelCol="label",
            predictionCol="prediction",
            probabilityCol="probability",
            rawPredictionCol="rawPrediction",
            family="multinomial",
            maxIter=30,
            regParam=0.05
        )

    else:
        raise ValueError(f"Modello multiclasse non supportato: {tipo_modello}")

    return Pipeline(
        stages=[
            label_indexer,
            index_location,
            index_district,
            encoder,
            assembler,
            classificatore
        ]
    )


def allena_modello_tipo_crimine(
    crimini,
    tipo_modello="Random Forest",
    frazione=0.10,
    test_ratio=0.2,
    seed=42
):
    """Addestra un classificatore Spark ML multiclasse su Primary Type."""

    dati = prepara_dataset_tipo_crimine(
        crimini,
        frazione=frazione,
        seed=seed
    )
    train, test = crea_train_test(
        dati,
        test_ratio=test_ratio,
        seed=seed
    )

    train = train.cache()
    test = test.cache()

    train_count = train.count()
    test_count = test.count()

    pipeline = crea_pipeline_tipo_crimine(tipo_modello, seed=seed)
    modello = pipeline.fit(train)
    predizioni = modello.transform(test)

    accuracy_eval = MulticlassClassificationEvaluator(
        labelCol="label",
        predictionCol="prediction",
        metricName="accuracy"
    )

    f1_eval = MulticlassClassificationEvaluator(
        labelCol="label",
        predictionCol="prediction",
        metricName="f1"
    )

    precision_eval = MulticlassClassificationEvaluator(
        labelCol="label",
        predictionCol="prediction",
        metricName="weightedPrecision"
    )

    recall_eval = MulticlassClassificationEvaluator(
        labelCol="label",
        predictionCol="prediction",
        metricName="weightedRecall"
    )

    label_model = modello.stages[0]
    etichette = list(label_model.labels)

    reale_decoder = IndexToString(
        inputCol="label",
        outputCol="Tipo reale",
        labels=etichette
    )

    pred_decoder = IndexToString(
        inputCol="prediction",
        outputCol="Tipo predetto",
        labels=etichette
    )

    predizioni_leggibili = pred_decoder.transform(
        reale_decoder.transform(predizioni)
    )

    esempio = (
        predizioni_leggibili
        .select(
            "Tipo reale",
            "Tipo predetto",
            "Location Description",
            "DistrictML"
        )
        .limit(100)
        .toPandas()
    )

    metriche = {
        "modello": tipo_modello,
        "accuracy": accuracy_eval.evaluate(predizioni),
        "weighted_f1": f1_eval.evaluate(predizioni),
        "weighted_precision": precision_eval.evaluate(predizioni),
        "weighted_recall": recall_eval.evaluate(predizioni),
        "numero_classi": len(etichette),
        "train_count": train_count,
        "test_count": test_count,
        "frazione": float(frazione),
        "test_ratio": float(test_ratio),
        "seed": int(seed)
    }

    train.unpersist()
    test.unpersist()

    return modello, metriche, esempio


# =========================================================
# REGRESSIONE SUL TREND MENSILE
# =========================================================

def prepara_crimini_mensili(crimini):
    """Aggrega i crimini per mese e crea una feature temporale numerica t."""

    mensili = (
        crimini
        .select("Date")
        .filter(col("Date").isNotNull())
        .withColumn(
            "_data_ml",
            to_timestamp(col("Date"), FORMATO_DATA)
        )
        .filter(col("_data_ml").isNotNull())
        .withColumn("Anno", year(col("_data_ml")))
        .withColumn("Mese", month(col("_data_ml")))
        .groupBy("Anno", "Mese")
        .count()
        .withColumnRenamed("count", "Crimini")
        .withColumn(
            "t",
            col("Anno") * lit(12) + col("Mese")
        )
        .orderBy("t")
    )

    return mensili


def crea_split_temporale(mensili, test_ratio=0.2):
    """Usa gli ultimi mesi come test set, evitando leakage temporale."""

    totale = mensili.count()

    if totale < 5:
        raise ValueError(
            "Servono almeno 5 mesi validi per addestrare la regressione."
        )

    test_count = max(1, int(round(totale * test_ratio)))
    train_count = totale - test_count

    finestra = Window.orderBy("t")
    numerati = mensili.withColumn(
        "_riga_temporale",
        row_number().over(finestra)
    )

    train = (
        numerati
        .filter(col("_riga_temporale") <= train_count)
        .drop("_riga_temporale")
    )

    test = (
        numerati
        .filter(col("_riga_temporale") > train_count)
        .drop("_riga_temporale")
    )

    return train, test


def previsione_crimini_mensili(
    crimini,
    future_months=6,
    test_ratio=0.2
):
    """Regressione lineare Spark ML del trend mensile e previsione futura."""

    mensili = prepara_crimini_mensili(crimini).cache()
    train, test = crea_split_temporale(mensili, test_ratio)

    assembler = VectorAssembler(
        inputCols=["t"],
        outputCol="features"
    )

    regressore = LinearRegression(
        featuresCol="features",
        labelCol="Crimini",
        predictionCol="prediction"
    )

    pipeline = Pipeline(stages=[assembler, regressore])
    modello = pipeline.fit(train)
    predizioni_test = modello.transform(test)

    rmse = RegressionEvaluator(
        labelCol="Crimini",
        predictionCol="prediction",
        metricName="rmse"
    ).evaluate(predizioni_test)

    mae = RegressionEvaluator(
        labelCol="Crimini",
        predictionCol="prediction",
        metricName="mae"
    ).evaluate(predizioni_test)

    r2 = RegressionEvaluator(
        labelCol="Crimini",
        predictionCol="prediction",
        metricName="r2"
    ).evaluate(predizioni_test)

    ultimo_t = int(
        mensili.agg(spark_max("t").alias("max_t")).first()["max_t"]
    )

    spark = crimini.sparkSession
    futuri = [
        (ultimo_t + i,)
        for i in range(1, future_months + 1)
    ]

    future_df = spark.createDataFrame(futuri, ["t"])

    future_pred = (
        modello
        .transform(future_df)
        .withColumn(
            "Anno",
            floor((col("t") - lit(1)) / lit(12)).cast("int")
        )
        .withColumn(
            "Mese",
            (pmod(col("t") - lit(1), lit(12)) + lit(1)).cast("int")
        )
        .withColumn(
            "prediction",
            when(col("prediction") < 0, 0.0).otherwise(col("prediction"))
        )
        .select("Anno", "Mese", "t", "prediction")
        .orderBy("t")
    )

    metriche = {
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
        "train_count": train.count(),
        "test_count": test.count(),
        "mesi_totali": mensili.count(),
        "future_months": future_months
    }

    mensili.unpersist()

    return modello, metriche, prepara_crimini_mensili(crimini), predizioni_test, future_pred
