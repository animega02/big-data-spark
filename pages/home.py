"""Overview: navigation and current scope; no expensive Spark job on entry."""
import streamlit as st
from stato_app import inizializza_stato
from componenti_filtri import mostra_filtri_globali
from ui import mostra_hero, mostra_chip_filtri, icona_neon

inizializza_stato()
st.markdown('<div class="overview-topline"><span>WORKSPACE / OVERVIEW</span><span>Chicago Crime Explorer</span></div>', unsafe_allow_html=True)
mostra_hero()
left, right = st.columns([4, 1])
with left:
    st.markdown('<div class="workspace-heading"><h2>Da dove vuoi iniziare?</h2><p>Quattro modi per esplorare lo stesso territorio.</p></div>', unsafe_allow_html=True)
with right:
    mostra_filtri_globali()
mostra_chip_filtri()

cards = [
    ("map", "01 / ESPLORA", "Crime Map", "Ogni evento ha un luogo.", "Esplora la mappa e disegna un’area per concentrare la ricerca sul territorio che ti interessa.", "Apri la mappa", "pages/mappa.py", "cyan"),
    ("chart", "02 / COMPRENDI", "Analytics", "Trova il filo tra i numeri.", "Confronta categorie e distretti, osserva i trend nel tempo e approfondisci la distribuzione degli arresti.", "Esplora le analisi", "pages/analisi.py", "violet"),
    ("table", "03 / APPROFONDISCI", "Records", "Dal quadro generale al dettaglio.", "Consulta i singoli eventi, cerca nel dataset e leggi i risultati corrispondenti ai filtri applicati.", "Consulta i record", "pages/crimini.py", "blue"),
    ("nodes", "04 / SPERIMENTA", "Machine Learning", "Dai pattern alle previsioni.", "Sperimenta classificazione, trend mensili e clustering geografico con i modelli di Apache Spark.", "Apri il laboratorio", "pages/machine_learning.py", "pink"),
]
for row in (cards[:2], cards[2:]):
    columns = st.columns(2, gap="medium")
    for column, (art, eyebrow, title, subtitle, description, label, page, color) in zip(columns, row):
        with column, st.container(border=True, key={"map":"panel-cyan-mappa", "chart":"panel-magenta-analytics", "table":"panel-violet-records", "nodes":"panel-cyan-ml"}[art]):
            st.markdown(f'<div class="workspace-card {color}"><div class="card-eyebrow">{eyebrow}</div><div class="home-neon-title"><span class="home-neon-icon">{icona_neon(art)}</span><h3>{title}</h3></div><div class="card-subtitle">{subtitle}</div><p>{description}</p></div>', unsafe_allow_html=True)
            if st.button(label + " →", key="home_" + art, use_container_width=True):
                st.switch_page(page)
st.markdown('<div class="workspace-footer"><span>CHICAGO CRIME EXPLORER</span><span>Un territorio. Molte prospettive.</span></div>', unsafe_allow_html=True)
