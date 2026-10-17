from pyspark.sql.functions import (
    col,
    lit,
    to_date,
    to_timestamp,
    udf
)

from pyspark.sql.types import BooleanType


FORMATO_DATA = "MM/dd/yyyy hh:mm:ss a"


# =========================================================
# SUPPORTO GEOGRAFICO
# =========================================================

def estrai_poligono(area):
    """
    Estrae dal GeoJSON restituito da Folium
    la lista dei vertici del poligono.

    Ogni vertice è:
    [longitudine, latitudine]
    """

    if area is None:
        return None

    geometria = area.get("geometry")

    if geometria is None:
        return None

    tipo = geometria.get("type")
    coordinate = geometria.get("coordinates")

    if not coordinate:
        return None

    if tipo == "Polygon":
        return coordinate[0]

    if tipo == "MultiPolygon":
        return coordinate[0][0]

    return None


def punto_nel_poligono(longitudine, latitudine, poligono):
    """
    Algoritmo ray casting.

    Restituisce True se il punto è contenuto
    all'interno del poligono.
    """

    if longitudine is None or latitudine is None:
        return False

    dentro = False

    j = len(poligono) - 1

    for i in range(len(poligono)):

        xi, yi = poligono[i]
        xj, yj = poligono[j]

        intersezione = (
            (yi > latitudine) != (yj > latitudine)
            and
            longitudine
            <
            (xj - xi)
            * (latitudine - yi)
            / ((yj - yi) + 1e-12)
            + xi
        )

        if intersezione:
            dentro = not dentro

        j = i

    return dentro


# =========================================================
# FILTRO GEOGRAFICO
# =========================================================

def applica_filtro_geografico(crimini, area):

    poligono = estrai_poligono(area)

    if not poligono:
        return crimini


    # -----------------------------------------------------
    # BOUNDING BOX
    # -----------------------------------------------------
    # Prima riduciamo drasticamente i dati usando Spark.

    longitudini = [
        punto[0]
        for punto in poligono
    ]

    latitudini = [
        punto[1]
        for punto in poligono
    ]

    lon_min = min(longitudini)
    lon_max = max(longitudini)

    lat_min = min(latitudini)
    lat_max = max(latitudini)


    risultato = (
        crimini

        .filter(
            col("Latitude").isNotNull()
        )

        .filter(
            col("Longitude").isNotNull()
        )

        .filter(
            (col("Latitude") >= lat_min)
            &
            (col("Latitude") <= lat_max)
            &
            (col("Longitude") >= lon_min)
            &
            (col("Longitude") <= lon_max)
        )
    )


    # -----------------------------------------------------
    # POINT-IN-POLYGON
    # -----------------------------------------------------
    # Il bounding box non basta per un poligono arbitrario.
    # Facciamo quindi il controllo preciso.

    def controlla_punto(longitudine, latitudine):

        return punto_nel_poligono(
            longitudine,
            latitudine,
            poligono
        )


    punto_in_area = udf(
        controlla_punto,
        BooleanType()
    )


    risultato = risultato.filter(
        punto_in_area(
            col("Longitude"),
            col("Latitude")
        )
    )


    return risultato


# =========================================================
# FILTRI GLOBALI
# =========================================================

def applica_filtri_globali(
    crimini,
    data_inizio,
    data_fine,
    tipo_crimine="Tutti",
    distretto="Tutti",
    arresto="Tutti",
    area=None
):

    # -----------------------------------------------------
    # DATA
    # -----------------------------------------------------

    risultato = crimini.withColumn(
        "_data_timestamp",

        to_timestamp(
            col("Date"),
            FORMATO_DATA
        )
    )


    risultato = risultato.withColumn(
        "_data",

        to_date(
            col("_data_timestamp")
        )
    )


    risultato = risultato.filter(
        (
            col("_data")
            >=
            to_date(
                lit(data_inizio.isoformat())
            )
        )
        &
        (
            col("_data")
            <=
            to_date(
                lit(data_fine.isoformat())
            )
        )
    )


    # -----------------------------------------------------
    # TIPO DI CRIMINE
    # -----------------------------------------------------

    if tipo_crimine != "Tutti":

        risultato = risultato.filter(
            col("Primary Type") == tipo_crimine
        )


    # -----------------------------------------------------
    # DISTRETTO
    # -----------------------------------------------------

    if distretto != "Tutti":

        risultato = risultato.filter(
            col("District") == int(distretto)
        )


    # -----------------------------------------------------
    # ARRESTO
    # -----------------------------------------------------

    if arresto == "Sì":

        risultato = risultato.filter(
            col("Arrest") == True
        )


    elif arresto == "No":

        risultato = risultato.filter(
            col("Arrest") == False
        )


    # -----------------------------------------------------
    # AREA GEOGRAFICA
    # -----------------------------------------------------

    if area is not None:

        risultato = applica_filtro_geografico(
            risultato,
            area
        )


    return risultato