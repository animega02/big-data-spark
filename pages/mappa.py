from uuid import uuid4
import folium
import streamlit as st

from branca.element import MacroElement, Template
from folium.plugins import Draw
from pyspark.sql.functions import col, rand
from streamlit_folium import st_folium
from vista_mappa import VistaMappaPersistente

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

# Confine amministrativo ufficiale della City of Chicago.
CHICAGO_BOUNDARY_URL = (
    "https://data.cityofchicago.org/api/v3/views/qqq8-j68g/"
    "query.geojson?accessType=DOWNLOAD"
)


# =========================================================
# STATO
# =========================================================

inizializza_stato()

# Identifica la vista locale per questa sessione, senza inviare pan/zoom a Python.
if "mappa_vista_id" not in st.session_state:
    st.session_state.mappa_vista_id = uuid4().hex


if "punti_mappa" not in st.session_state:
    st.session_state.punti_mappa = None


if "numero_totale_mappa" not in st.session_state:
    st.session_state.numero_totale_mappa = 0


if "modalita_ricerca_mappa" not in st.session_state:
    st.session_state.modalita_ricerca_mappa = None


# =========================================================
# CONFINE DI CHICAGO
# =========================================================

class ConfineChicagoClient(MacroElement):
    """Carica il confine nel browser senza bloccare Streamlit."""

    _template = Template("""
    {% macro script(this, kwargs) %}
    (function () {
        const map = {{ this._parent.get_name() }};
        const url = {{ this.boundary_url | tojson }};

        // Pane dedicato: il contorno resta sopra le tile ma sotto marker/disegni.
        if (!map.getPane('chicagoBoundaryPane')) {
            map.createPane('chicagoBoundaryPane');
            map.getPane('chicagoBoundaryPane').style.zIndex = 390;
            map.getPane('chicagoBoundaryPane').style.pointerEvents = 'none';
        }

        fetch(url, { mode: 'cors' })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                // Bordo scuro esterno per mantenere contrasto sulle tile.
                L.geoJSON(data, {
                    pane: 'chicagoBoundaryPane',
                    interactive: false,
                    style: function () {
                        return {
                            color: '#07111F',
                            weight: 6,
                            opacity: 0.78,
                            fill: false
                        };
                    }
                }).addTo(map);

                // Tratto neon coerente con il frontend.
                L.geoJSON(data, {
                    pane: 'chicagoBoundaryPane',
                    interactive: false,
                    style: function () {
                        return {
                            color: '#38BDF8',
                            weight: 3,
                            opacity: 0.98,
                            fill: false
                        };
                    }
                }).addTo(map);
            })
            .catch(function (error) {
                // Il fallimento del contorno non deve mai impedire la mappa.
                console.warn('Confine di Chicago non disponibile:', error);
            });
    })();
    {% endmacro %}
    """)

    def __init__(self, boundary_url):
        super().__init__()
        self._name = "ConfineChicagoClient"
        self.boundary_url = boundary_url


# =========================================================
# QUERY PER LA MAPPA
# =========================================================

def cerca_crimini_mappa(area=None):
    """
    Restituisce un campione rappresentativo dei crimini filtrati.

    Importante: non prendiamo piu' semplicemente i primi 1.000 record del
    dataset. Se i risultati sono piu' di MAX_PUNTI_MAPPA, eseguiamo prima
    un campionamento casuale sull'intero insieme filtrato e solo dopo
    scegliamo i punti da visualizzare. In questo modo intervalli temporali
    differenti producono campioni realmente riferiti a tutto il periodo.
    """

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
        .filter(col("Latitude").isNotNull())
        .filter(col("Longitude").isNotNull())
        .select(
            "Latitude",
            "Longitude",
            "Primary Type",
            "Location Description",
            "District",
            "Date"
        )
    )

    # Numero reale di crimini compatibili con i filtri correnti.
    numero_totale = risultato.count()

    if numero_totale > MAX_PUNTI_MAPPA:
        # Campioniamo sull'INTERO risultato filtrato.
        # L'oversampling (4x) mantiene piccolo lo shuffle successivo ma rende
        # estremamente improbabile ottenere meno di 1.000 righe.
        frazione = min(
            1.0,
            (MAX_PUNTI_MAPPA * 4.0) / float(numero_totale)
        )

        risultato_mappa = (
            risultato
            .sample(
                withReplacement=False,
                fraction=frazione,
                seed=42
            )
            # Mischiamo soltanto il campione ridotto, non milioni di righe.
            .orderBy(rand(42))
            .limit(MAX_PUNTI_MAPPA)
        )
    else:
        risultato_mappa = risultato

    dati = risultato_mappa.toPandas()

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

    return dati, numero_totale


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
        type="primary",
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

        (
            st.session_state.punti_mappa,
            st.session_state.numero_totale_mappa
        ) = cerca_crimini_mappa()


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

        (
            st.session_state.punti_mappa,
            st.session_state.numero_totale_mappa
        ) = cerca_crimini_mappa(
            st.session_state.area_disegnata
        )


        st.session_state.modalita_ricerca_mappa = (
            "area"
        )


# =========================================================
# PULISCI MAPPA
# =========================================================

if pulisci:

    st.session_state.punti_mappa = None

    st.session_state.numero_totale_mappa = 0

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

    numero_visualizzato = len(
        st.session_state.punti_mappa
    )
    numero_totale = st.session_state.numero_totale_mappa

    totale_formattato = f"{numero_totale:,}".replace(",", ".")
    visualizzati_formattato = f"{numero_visualizzato:,}".replace(",", ".")

    if (
        st.session_state.modalita_ricerca_mappa
        == "area"
    ):

        st.success(
            f"📐 {totale_formattato} crimini trovati nell'area selezionata · "
            f"{visualizzati_formattato} visualizzati sulla mappa."
        )


    else:

        st.success(
            f"{totale_formattato} crimini trovati · "
            f"{visualizzati_formattato} visualizzati sulla mappa."
        )


    if numero_totale > MAX_PUNTI_MAPPA:

        st.caption(
            f"La mappa mostra un campione di massimo "
            f"{MAX_PUNTI_MAPPA:,} punti estratto dall'intero insieme filtrato, "
            "così il periodo selezionato è rappresentato nel suo complesso. "
            "Records e Analytics continuano a lavorare su tutti i risultati."
        )


# =========================================================
# CREAZIONE MAPPA
# =========================================================

mappa = folium.Map(

    location=[41.8781, -87.6298],

    zoom_start=10,

    tiles="OpenStreetMap",

    control_scale=True,

    # Migliora le prestazioni con molti CircleMarker.
    prefer_canvas=True
)


# =========================================================
# CONFINE AMMINISTRATIVO DI CHICAGO
# =========================================================

# Il caricamento avviene nel browser: la mappa viene mostrata subito e
# un eventuale problema di rete può far mancare solo il contorno.
ConfineChicagoClient(CHICAGO_BOUNDARY_URL).add_to(mappa)


# =========================================================
# AREA SALVATA
# =========================================================

if st.session_state.area_disegnata is not None:

    folium.GeoJson(

        st.session_state.area_disegnata,

        style_function=lambda feature: {

            "color": "#00F0FF",

            "weight": 3,

            "fillColor": "#00F0FF",

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

            color="#FF2BD6",

            fill=True,

            fill_color="#FF2BD6",

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

# Ripristina la vista anche quando il disegno o i risultati ricreano la mappa.
VistaMappaPersistente(st.session_state.mappa_vista_id).add_to(mappa)

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
            st.session_state.numero_totale_mappa = 0

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
            st.session_state.numero_totale_mappa = 0

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