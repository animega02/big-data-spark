import streamlit as st

st.title("🌃 Chicago Crime Explorer")

st.write(
    """
    Esplora e analizza i crimini registrati nella città di Chicago
    attraverso Apache Spark.
    """
)

st.markdown(
    """
    ### 🗺️ Mappa
    Esplora geograficamente gli eventi e seleziona aree personalizzate.

    ### 📋 Crimini
    Consulta gli eventi corrispondenti ai filtri selezionati.

    ### 📊 Analisi
    Visualizza statistiche, classifiche e andamento temporale.

    ### ⚙️ Filtri
    Configura filtri avanzati condivisi tra le diverse sezioni.
    """
)