import json
from pathlib import Path


FILE_STATO = (
    Path(__file__).resolve().parent
    / ".stato_filtri.json"
)


def salva_filtri(stato):

    dati = {
        "data_inizio": stato.data_inizio.isoformat(),
        "data_fine": stato.data_fine.isoformat(),

        "tipo_crimine": stato.tipo_crimine,
        "distretto": stato.distretto,
        "arresto": stato.arresto,

        "area_disegnata": stato.area_disegnata,
        "area_filtro_attiva": stato.area_filtro_attiva,

        "filtri_applicati": stato.filtri_applicati
    }

    with open(
        FILE_STATO,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            dati,
            file,
            ensure_ascii=False,
            indent=2
        )


def carica_filtri():

    if not FILE_STATO.exists():
        return None

    try:

        with open(
            FILE_STATO,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):

        return None