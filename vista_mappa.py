"""Conserva la vista Leaflet nel browser, senza eventi Streamlit di pan/zoom."""
from branca.element import MacroElement, Template


class VistaMappaPersistente(MacroElement):
    """La chiave di sessione evita di riusare la vista di una nuova sessione."""

    _template = Template("""
    {% macro script(this, kwargs) %}
    (function () {
        const map = {{ this._parent.get_name() }};
        const key = {{ this.storage_key | tojson }};
        function saveView() {
            const center = map.getCenter();
            try {
                sessionStorage.setItem(key, JSON.stringify({
                    lat: center.lat, lng: center.lng, zoom: map.getZoom()
                }));
            } catch (_) { /* La mappa resta utilizzabile se lo storage è bloccato. */ }
        }
        try {
            const view = JSON.parse(sessionStorage.getItem(key));
            if (view && Number.isFinite(view.lat) && Number.isFinite(view.lng)
                && Number.isFinite(view.zoom) && Math.abs(view.lat) <= 90
                && view.zoom >= 0 && view.zoom <= 22) {
                map.setView([view.lat, view.lng], view.zoom, {animate: false});
            }
        } catch (_) { /* Nessuna vista valida: usa la vista iniziale. */ }
        map.on('moveend zoomend', saveView);
        map.on('draw:created draw:edited draw:deleted', saveView);
        saveView();
    })();
    {% endmacro %}
    """)

    def __init__(self, session_id):
        super().__init__()
        self._name = "VistaMappaPersistente"
        self.storage_key = "chicago-crime-map-view:" + session_id
