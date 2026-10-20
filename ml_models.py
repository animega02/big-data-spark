from pyspark.ml import Pipeline

from pyspark.ml.functions import vector_to_array

from pyspark.ml.classification import (
    LogisticRegression,
    RandomForestClassifier
)

from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator
)

from pyspark.ml.feature import (
    OneHotEncoder,
    StringIndexer,
    VectorAssembler
)

from pyspark.sql.functions import (
    col,
    dayofweek,
    hour,
    lit,
    month,
    pmod,
    sum as spark_sum,
    to_timestamp,
    when,
    xxhash64
)


FORMATO_DATA = "MM/dd/yyyy hh:mm:ss a"


# =========================================================
# PREPARAZIONE DATASET
# =========================================================

def prepara_dataset_arresto(
    crimini,
    limite=200000
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

        .limit(
            limite
        )
    )


    return dati


# =========================================================
# TRAIN / TEST DETERMINISTICO
# =========================================================

def crea_train_test(
    dati
):

    # =====================================================
    # IMPORTANTE
    # =====================================================
    #
    # Non usiamo più randomSplit().
    #
    # Calcoliamo invece un bucket deterministico
    # a partire dall'ID del crimine.
    #
    # Bucket:
    # 0-7 -> training
    # 8-9 -> test
    #
    # In questo modo Logistic Regression e Random Forest
    # vedono ESATTAMENTE gli stessi record.
    # =====================================================

    dati = dati.withColumn(
        "_split_bucket",

        pmod(
            xxhash64(
                col("ID")
            ),
            lit(10)
        )
    )


    train = (
        dati
        .filter(
            col("_split_bucket") < 8
        )
        .drop(
            "_split_bucket"
        )
    )


    test = (
        dati
        .filter(
            col("_split_bucket") >= 8
        )
        .drop(
            "_split_bucket"
        )
    )


    return (
        train,
        test
    )


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
    bilanciato=False
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

    else:

        if bilanciato:

            classificatore = RandomForestClassifier(
                featuresCol="features",
                labelCol="label",
                predictionCol="prediction",
                probabilityCol="probability",
                rawPredictionCol="rawPrediction",
                weightCol="classWeight",
                numTrees=30,
                maxDepth=8,
                featureSubsetStrategy="sqrt",
                seed=42
            )

        else:

            classificatore = RandomForestClassifier(
                featuresCol="features",
                labelCol="label",
                predictionCol="prediction",
                probabilityCol="probability",
                rawPredictionCol="rawPrediction",
                numTrees=30,
                maxDepth=8,
                featureSubsetStrategy="sqrt",
                seed=42
            )


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
    limite=200000
):

    # =====================================================
    # DATASET
    # =====================================================

    dati = prepara_dataset_arresto(
        crimini,
        limite
    )


    # =====================================================
    # STESSO TRAIN / TEST PER TUTTI
    # =====================================================

    train, test = crea_train_test(
        dati
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
        bilanciato
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
# TRAIN / VALIDATION / TEST
# PER THRESHOLD TUNING
# =========================================================

def crea_train_validation_test(dati):

    dati = dati.withColumn(
        "_split_bucket",

        pmod(
            xxhash64(
                col("ID")
            ),
            lit(10)
        )
    )


    # 0 - 6 -> 70%
    train = (
        dati
        .filter(
            col("_split_bucket") < 7
        )
        .drop(
            "_split_bucket"
        )
    )


    # 7 -> 10%
    validation = (
        dati
        .filter(
            col("_split_bucket") == 7
        )
        .drop(
            "_split_bucket"
        )
    )


    # 8 - 9 -> 20%
    test = (
        dati
        .filter(
            col("_split_bucket") >= 8
        )
        .drop(
            "_split_bucket"
        )
    )


    return (
        train,
        validation,
        test
    )


# =========================================================
# METRICHE PER UNA SOGLIA
# =========================================================

def calcola_metriche_soglia(
    predizioni,
    soglia
):

    dati = predizioni.withColumn(
        "_predizione_soglia",

        when(
            col("prob_arresto") >= soglia,
            1.0
        ).otherwise(0.0)
    )


    riga = (
        dati

        .agg(

            spark_sum(
                when(
                    (col("label") == 0)
                    &
                    (col("_predizione_soglia") == 0),
                    1
                ).otherwise(0)
            ).alias("tn"),


            spark_sum(
                when(
                    (col("label") == 0)
                    &
                    (col("_predizione_soglia") == 1),
                    1
                ).otherwise(0)
            ).alias("fp"),


            spark_sum(
                when(
                    (col("label") == 1)
                    &
                    (col("_predizione_soglia") == 0),
                    1
                ).otherwise(0)
            ).alias("fn"),


            spark_sum(
                when(
                    (col("label") == 1)
                    &
                    (col("_predizione_soglia") == 1),
                    1
                ).otherwise(0)
            ).alias("tp")
        )

        .first()
    )


    tn = int(riga["tn"] or 0)
    fp = int(riga["fp"] or 0)
    fn = int(riga["fn"] or 0)
    tp = int(riga["tp"] or 0)


    totale = (
        tn + fp + fn + tp
    )


    accuracy = (
        (tp + tn) / totale
        if totale > 0
        else 0
    )


    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0
        else 0
    )


    recall = (
        tp / (tp + fn)
        if (tp + fn) > 0
        else 0
    )


    specificita = (
        tn / (tn + fp)
        if (tn + fp) > 0
        else 0
    )


    if precision + recall > 0:

        f1 = (
            2
            *
            precision
            *
            recall
            /
            (
                precision
                +
                recall
            )
        )

    else:

        f1 = 0


    balanced_accuracy = (
        recall
        +
        specificita
    ) / 2


    return {
        "Soglia": soglia,

        "Accuracy": accuracy,

        "Precision": precision,

        "Recall": recall,

        "F1": f1,

        "Specificita": specificita,

        "Balanced Accuracy":
            balanced_accuracy,

        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp
    }


# =========================================================
# THRESHOLD TUNING
# =========================================================

def ottimizza_soglia_logistica(
    crimini,
    bilanciato=False,
    limite=200000,
    criterio="F1 arresti"
):

    # =====================================================
    # DATASET
    # =====================================================

    dati = prepara_dataset_arresto(
        crimini,
        limite
    )


    (
        train,
        validation,
        test
    ) = crea_train_validation_test(
        dati
    )


    train = train.cache()
    validation = validation.cache()
    test = test.cache()


    train_count = train.count()
    validation_count = validation.count()
    test_count = test.count()


    # =====================================================
    # BILANCIAMENTO
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
    # TRAINING LOGISTIC REGRESSION
    # =====================================================

    pipeline = crea_pipeline_arresto(
        "Logistic Regression",
        bilanciato
    )


    modello = pipeline.fit(
        train_modello
    )


    # =====================================================
    # VALIDATION
    # =====================================================

    predizioni_validation = (
        modello

        .transform(
            validation
        )

        .withColumn(
            "prob_arresto",

            vector_to_array(
                col("probability")
            )[1]
        )

        .select(
            "label",
            "prob_arresto"
        )

        .cache()
    )


    # =====================================================
    # SOGLIE DA PROVARE
    # =====================================================

    soglie = [
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80
    ]


    risultati_soglie = []


    for soglia in soglie:

        metriche = calcola_metriche_soglia(
            predizioni_validation,
            soglia
        )

        risultati_soglie.append(
            metriche
        )


    # =====================================================
    # MIGLIORE SOGLIA
    # =====================================================

    if criterio == "Balanced Accuracy":

        chiave_criterio = (
            "Balanced Accuracy"
        )

    else:

        chiave_criterio = "F1"


    migliore = max(
        risultati_soglie,
        key=lambda x: x[
            chiave_criterio
        ]
    )


    soglia_migliore = (
        migliore["Soglia"]
    )


    # =====================================================
    # TEST SET
    # =====================================================

    predizioni_test = (
        modello

        .transform(
            test
        )

        .withColumn(
            "prob_arresto",

            vector_to_array(
                col("probability")
            )[1]
        )

        .select(
            "label",
            "prob_arresto"
        )

        .cache()
    )


    # =====================================================
    # RISULTATO CON SOGLIA 0.50
    # =====================================================

    metriche_default = (
        calcola_metriche_soglia(
            predizioni_test,
            0.50
        )
    )


    # =====================================================
    # RISULTATO CON SOGLIA OTTIMIZZATA
    # =====================================================

    metriche_ottimizzate = (
        calcola_metriche_soglia(
            predizioni_test,
            soglia_migliore
        )
    )


    # =====================================================
    # PULIZIA
    # =====================================================

    predizioni_validation.unpersist()

    predizioni_test.unpersist()

    train.unpersist()

    validation.unpersist()

    test.unpersist()


    return {

        "soglia_migliore":
            soglia_migliore,

        "criterio":
            criterio,

        "risultati_soglie":
            risultati_soglie,

        "metriche_default":
            metriche_default,

        "metriche_ottimizzate":
            metriche_ottimizzate,

        "train_count":
            train_count,

        "validation_count":
            validation_count,

        "test_count":
            test_count,

        "peso_non_arresto":
            peso_0,

        "peso_arresto":
            peso_1
    }