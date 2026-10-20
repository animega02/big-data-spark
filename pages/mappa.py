import folium
import streamlit as st

from folium.plugins import Draw
from pyspark.sql.functions import col
from streamlit_folium import st_folium

from componenti_filtri import mostra_filtri_globali
from dati import carica_dataset
from filtri_crimini import applica_filtri_globali
from stato_app import inizializza_stato

from componenti_filtri import mostra_filtri_globali

from ui import (
    mostra_header_pagina,
    mostra_chip_filtri
)


# =========================================================
# CONFIGURAZIONE
# =========================================================

MAX_PUNTI_MAPPA = 1000


# =========================================================
# STATO
# =========================================================

inizializza_stato()


if "punti_mappa" not in st.session_state:
    st.session_state.punti_mappa = None


if "modalita_ricerca_mappa" not in st.session_state:
    st.session_state.modalita_ricerca_mappa = None


# =========================================================
# QUERY PER LA MAPPA
# =========================================================

def cerca_crimini_mappa(area=None):

    crimini = carica_dataset()

    risultato = applica_filtri_globali(
        crimini,
        st.session_state.data_inizio,
        st.session_state.data_fine,
        st.session_state.tipo_crimine,
        st.session_state.distretto,
        st.session_state.arresto,
        area
    )


    risultato = (
        risultato

        .filter(
            col("Latitude").isNotNull()
        )

        .filter(
            col("Longitude").isNotNull()
        )

        .select(
            "Latitude",
            "Longitude",
            "Primary Type",
            "Location Description",
            "District",
            "Date"
        )

        .limit(
            MAX_PUNTI_MAPPA
        )
    )


    dati = risultato.toPandas()


    dati = dati.rename(
        columns={
            "Latitude": "lat",
            "Longitude": "lon",
            "Primary Type": "tipo",
            "Location Description": "luogo",
            "District": "distretto",
            "Date": "data"
        }
    )


    return dati


# =========================================================
# TITOLO
# =========================================================
# =========================================================
# HEADER PAGINA
# =========================================================

mostra_header_pagina(
    "Spatial Intelligence",
    "Crime Map",
    "Esplora la distribuzione geografica degli eventi criminali "
    "e seleziona aree personalizzate sulla mappa."
)


# =========================================================
# TOOLBAR SUPERIORE
# =========================================================

col_filtri_attivi, col_pannello_filtri = st.columns(
    [5, 1.3],
    vertical_alignment="center"
)


with col_filtri_attivi:

    mostra_chip_filtri()


with col_pannello_filtri:

    mostra_filtri_globali()


# =========================================================
# AZIONI MAPPA
# =========================================================

st.markdown(
    """
    <div class="crime-section-label">
        Map controls
    </div>
    """,
    unsafe_allow_html=True
)


col_cerca, col_area, col_pulisci = st.columns(
    [2.2, 2.2, 1]
)


with col_cerca:

    cerca = st.button(
        "Cerca crimini",
        type="primary",
        use_container_width=True
    )


with col_area:

    cerca_area = st.button(
        "Cerca nell'area selezionata",
        use_container_width=True,

        disabled=(
            st.session_state.area_disegnata
            is None
        )
    )


with col_pulisci:

    pulisci = st.button(
        "Pulisci",
        use_container_width=True
    )

# =========================================================
# RICERCA GENERALE
# =========================================================

if cerca:

    # La ricerca generale NON usa l'area geografica.
    st.session_state.area_filtro_attiva = False

    st.session_state.filtri_applicati = True


    with st.spinner(
        "Spark sta cercando i crimini..."
    ):

        st.session_state.punti_mappa = (
            cerca_crimini_mappa()
        )


        st.session_state.modalita_ricerca_mappa = (
            "generale"
        )


# =========================================================
# RICERCA NELL'AREA
# =========================================================

if cerca_area:

    st.session_state.area_filtro_attiva = True

    st.session_state.filtri_applicati = True


    with st.spinner(
        "Spark sta cercando i crimini "
        "nell'area selezionata..."
    ):

        st.session_state.punti_mappa = (
            cerca_crimini_mappa(
                st.session_state.area_disegnata
            )
        )


        st.session_state.modalita_ricerca_mappa = (
            "area"
        )


# =========================================================
# PULISCI MAPPA
# =========================================================

if pulisci:

    st.session_state.punti_mappa = None

    st.session_state.area_disegnata = None

    st.session_state.area_filtro_attiva = False

    st.session_state.modalita_ricerca_mappa = None

    st.rerun()


# =========================================================
# MESSAGGI RISULTATI
# =========================================================

if st.session_state.punti_mappa is None:

    st.info(
        "La mappa è pronta. "
        "Premi «Cerca crimini» oppure "
        "disegna un'area geografica."
    )


else:

    numero = len(
        st.session_state.punti_mappa
    )


    if (
        st.session_state.modalita_ricerca_mappa
        == "area"
    ):

        st.success(
            f"📐 Visualizzati {numero:,} eventi "
            "nell'area selezionata."
        )


    else:

        st.success(
            f"Visualizzati {numero:,} eventi "
            "con i filtri selezionati."
        )


    if numero >= MAX_PUNTI_MAPPA:

        st.caption(
            f"La mappa mostra al massimo "
            f"{MAX_PUNTI_MAPPA:,} punti per mantenere "
            "la visualizzazione fluida. "
            "Crimini e Analisi continuano invece "
            "a lavorare sull'intero insieme filtrato."
        )


# =========================================================
# CREAZIONE MAPPA
# =========================================================

mappa = folium.Map(

    location=[
        41.8781,
        -87.6298
    ],

    zoom_start=10,

    tiles="OpenStreetMap",

    control_scale=True,

    # Migliora le prestazioni con molti CircleMarker.
    prefer_canvas=True
)


# =========================================================
# AREA SALVATA
# =========================================================

if st.session_state.area_disegnata is not None:

    folium.GeoJson(

        st.session_state.area_disegnata,

        style_function=lambda feature: {

            "color": "#2563eb",

            "weight": 3,

            "fillColor": "#2563eb",

            "fillOpacity": 0.12
        }

    ).add_to(
        mappa
    )


# =========================================================
# PUNTI
# =========================================================

if st.session_state.punti_mappa is not None:

    for _, riga in (
        st.session_state.punti_mappa.iterrows()
    ):

        folium.CircleMarker(

            location=[
                riga["lat"],
                riga["lon"]
            ],

            radius=3,

            color="#dc2626",

            fill=True,

            fill_color="#dc2626",

            fill_opacity=0.95,

            weight=0,

            tooltip=(
                f"<b>{riga['tipo']}</b><br>"
                f"Data: {riga['data']}<br>"
                f"Luogo: {riga['luogo']}<br>"
                f"Distretto: {riga['distretto']}"
            )

        ).add_to(
            mappa
        )


# =========================================================
# DISEGNO AREA
# =========================================================

Draw(

    export=False,

    position="topleft",

    draw_options={

        "polyline": False,

        "circle": False,

        "circlemarker": False,

        "marker": False,

        "polygon": {
            "allowIntersection": False,
            "showArea": True
        },

        "rectangle": True
    },

    edit_options={

        "edit": True,

        "remove": True
    }

).add_to(
    mappa
)


# =========================================================
# VISUALIZZAZIONE
# =========================================================

evento_mappa = st_folium(

    mappa,

    height=650,

    use_container_width=True,

    key="mappa_crimini",

    returned_objects=[
        "all_drawings",
        "last_active_drawing"
    ]
)


# =========================================================
# AREA DISEGNATA
# =========================================================

disegni = evento_mappa.get(
    "all_drawings"
)


# ---------------------------------------------------------
# AREA CREATA O MODIFICATA
# ---------------------------------------------------------

if disegni:

    nuova_area = disegni[-1]


    if (
        nuova_area
        !=
        st.session_state.area_disegnata
    ):

        st.session_state.area_disegnata = (
            nuova_area
        )


        # Disegnare un'area non significa ancora
        # applicarla come filtro.
        st.session_state.area_filtro_attiva = False


        # Se prima stavamo visualizzando una vecchia
        # ricerca geografica, la invalidiamo.
        if (
            st.session_state.modalita_ricerca_mappa
            == "area"
        ):

            st.session_state.punti_mappa = None

            st.session_state.modalita_ricerca_mappa = (
                None
            )


        st.rerun()


# ---------------------------------------------------------
# AREA ELIMINATA
# ---------------------------------------------------------

elif disegni == []:

    if (
        st.session_state.area_disegnata
        is not None
    ):

        st.session_state.area_disegnata = None

        st.session_state.area_filtro_attiva = False


        if (
            st.session_state.modalita_ricerca_mappa
            == "area"
        ):

            st.session_state.punti_mappa = None

            st.session_state.modalita_ricerca_mappa = (
                None
            )


        st.rerun()


# =========================================================
# STATO AREA
# =========================================================

if st.session_state.area_disegnata is not None:

    if st.session_state.area_filtro_attiva:

        st.success(
            "📐 Il filtro geografico è attivo. "
            "Anche Crimini e Analisi utilizzeranno "
            "questa area."
        )


    else:

        st.info(
            "📐 Area selezionata. "
            "Premi «Cerca nell'area selezionata» "
            "per applicarla come filtro globale."
        )