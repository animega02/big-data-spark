import html
from urllib.parse import quote

import streamlit as st


# =========================================================
# TOKEN DESIGN
# =========================================================
#
# Palette "notte di Chicago":
#   void      #05060D  sfondo
#   panel     #0A0E1A  superfici
#   cyan      #00F0FF  colore primario (azioni, dati principali)
#   violet    #7B5CFF  colore di transizione
#   magenta   #FF2BD6  contrasto caldo (secondo dato, evidenze)
#
# Tipografia:
#   Chakra Petch    titoli e numeri (angolare, tecnico)
#   IBM Plex Sans   testo e controlli
#   JetBrains Mono  dati, etichette, chip

PALETTE_GRAFICI = [
    "#00F0FF",
    "#FF2BD6",
    "#7B5CFF",
    "#FFC24B",
    "#2DFFA0",
    "#FF4D6D",
]


# =========================================================
# SKYLINE (decorazione dell'hero)
# =========================================================

def _skyline_data_uri():
    """Genera una skyline stilizzata come SVG incorporato in un data URI."""

    # (larghezza, altezza) di ogni edificio, da sinistra a destra.
    edifici = [
        (38, 34), (26, 52), (44, 40), (30, 70), (36, 48), (24, 86),
        (40, 58), (32, 44), (28, 96), (34, 62), (46, 38), (30, 78),
        (22, 112), (30, 118), (22, 108), (36, 60), (44, 46), (28, 72),
        (34, 90), (26, 64), (42, 42), (30, 80), (36, 54), (24, 100),
        (30, 68), (44, 36), (28, 58), (38, 76), (32, 48), (26, 62),
        (40, 40), (30, 84), (36, 52), (28, 44), (42, 66), (34, 38),
    ]

    larghezza_totale = sum(w for w, _ in edifici)
    altezza_viewbox = 130

    forme = []
    finestre = []

    x = 0

    for indice, (w, h) in enumerate(edifici):

        y = altezza_viewbox - h

        forme.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'fill="#070A16" stroke="#00F0FF" stroke-opacity="0.45" '
            f'stroke-width="1"/>'
        )

        # Antenna sugli edifici più alti.
        if h >= 96:
            cx = x + w / 2
            forme.append(
                f'<line x1="{cx}" y1="{y}" x2="{cx}" y2="{y - 14}" '
                f'stroke="#FF2BD6" stroke-opacity="0.8" stroke-width="1.2"/>'
            )

        # Finestre accese in modo deterministico.
        riga = 0
        yy = y + 8

        while yy < altezza_viewbox - 6:

            colonna = 0
            xx = x + 5

            while xx < x + w - 5:

                seme = (indice * 31 + riga * 17 + colonna * 7) % 11

                if seme in (0, 3, 6):
                    colore = "#FF2BD6" if seme == 6 else "#00F0FF"
                    opacita = 0.75 if seme == 0 else 0.45

                    finestre.append(
                        f'<rect x="{xx}" y="{yy}" width="2.4" height="3" '
                        f'fill="{colore}" fill-opacity="{opacita}"/>'
                    )

                xx += 7
                colonna += 1

            yy += 9
            riga += 1

        x += w

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 -16 {larghezza_totale} {altezza_viewbox + 16}" '
        f'preserveAspectRatio="xMidYMax slice">'
        + "".join(forme)
        + "".join(finestre)
        + "</svg>"
    )

    return "data:image/svg+xml;utf8," + quote(svg)


# =========================================================
# DESIGN SYSTEM
# =========================================================

CSS_GLOBALE = """
<style>

@import url("https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap");


/* ==================================================
   TOKEN
   ================================================== */

:root {
    --void: #05060D;
    --panel: #0A0E1A;
    --panel-2: #0E1424;
    --panel-3: #131B30;

    --line: rgba(0, 240, 255, 0.14);
    --line-strong: rgba(0, 240, 255, 0.40);
    --line-neutral: rgba(159, 178, 208, 0.14);

    --cyan: #00F0FF;
    --violet: #7B5CFF;
    --magenta: #FF2BD6;
    --amber: #FFC24B;
    --danger: #FF4D6D;
    --success: #2DFFA0;

    --text: #E8F1FF;
    --text-secondary: #9FB2D0;
    --text-muted: #7387AB;

    --font-display: "Chakra Petch", "IBM Plex Sans", system-ui, sans-serif;
    --font-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
    --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
}


/* ==================================================
   BASE
   ================================================== */

.stApp {
    font-family: var(--font-body);

    color: var(--text);

    background:
        radial-gradient(
            ellipse 60rem 28rem at 12% -6%,
            rgba(0, 240, 255, 0.10),
            transparent 70%
        ),
        radial-gradient(
            ellipse 52rem 30rem at 98% 4%,
            rgba(255, 43, 214, 0.09),
            transparent 70%
        ),
        var(--void);
}


.stApp :is(p, label, li, td, th, summary, small, input, textarea, button) {
    font-family: var(--font-body);
}


.stApp :is(h1, h2, h3, h4, h5, h6) {
    font-family: var(--font-display);

    color: var(--text);

    letter-spacing: -0.01em;
}


.stApp h1 { font-weight: 700 !important; }
.stApp h2 { font-weight: 600 !important; letter-spacing: 0; }
.stApp h3, .stApp h4 { font-weight: 600 !important; letter-spacing: 0; }


.stApp p {
    color: var(--text-secondary);
}


::selection {
    background: rgba(0, 240, 255, 0.28);
    color: #FFFFFF;
}


.block-container {
    max-width: 1540px;

    padding-top: 2.2rem;
    padding-bottom: 5rem;
    padding-left: 2.4rem;
    padding-right: 2.4rem;
}


/* Scrollbar sottile */

* {
    scrollbar-width: thin;
    scrollbar-color: rgba(0, 240, 255, 0.35) transparent;
}


/* Focus da tastiera sempre visibile */

.stApp :is(button, a, input, textarea, [role="tab"], [role="option"]):focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}


/* ==================================================
   HEADER STREAMLIT
   ================================================== */

[data-testid="stHeader"] {
    background: rgba(5, 6, 13, 0.82);

    backdrop-filter: blur(10px);

    border-bottom: 1px solid var(--line);
}


[data-testid="stToolbar"] {
    background: transparent;
}


/* ==================================================
   SIDEBAR
   ================================================== */

[data-testid="stSidebar"] {
    background:
        radial-gradient(
            ellipse 18rem 22rem at 0% 100%,
            rgba(0, 240, 255, 0.30),
            transparent 70%
        ),
        radial-gradient(
            ellipse 18rem 22rem at 100% 100%,
            rgba(255, 43, 214, 0.26),
            transparent 70%
        ),
        linear-gradient(
            180deg,
            #090D19 0%,
            #060810 70%,
            #05060D 100%
        );

    border-right: 1px solid var(--line);
}


[data-testid="stSidebarContent"] {
    padding-top: 1rem;
}


[data-testid="stSidebarNav"] a {
    position: relative;

    border-radius: 6px;

    margin: 3px 8px;

    padding-top: 0.65rem;
    padding-bottom: 0.65rem;

    color: var(--text-secondary);

    border: 1px solid transparent;

    transition:
        background 160ms ease,
        color 160ms ease,
        border-color 160ms ease;
}


[data-testid="stSidebarNav"] a:hover {
    background: rgba(0, 240, 255, 0.07);

    color: var(--text);

    border-color: var(--line);
}


[data-testid="stSidebarNav"] a[aria-current="page"] {
    color: #FFFFFF;

    background:
        linear-gradient(
            90deg,
            rgba(0, 240, 255, 0.16),
            rgba(123, 92, 255, 0.10) 70%,
            transparent
        );

    border-color: rgba(0, 240, 255, 0.30);

    box-shadow:
        inset 3px 0 0 var(--cyan),
        0 0 22px rgba(0, 240, 255, 0.10);
}


[data-testid="stSidebarNav"] a[aria-current="page"] span {
    text-shadow: 0 0 12px rgba(0, 240, 255, 0.55);
}


/* ==================================================
   HERO
   ================================================== */

.crime-hero {
    position: relative;

    overflow: hidden;

    isolation: isolate;

    min-height: 21rem;

    padding: 2.6rem 2.8rem 9rem 2.8rem;

    margin-bottom: 1.8rem;

    border-radius: 8px;

    border: 1px solid rgba(0, 240, 255, 0.28);

    background:
        radial-gradient(
            ellipse 40rem 14rem at 50% 100%,
            rgba(255, 43, 214, 0.22),
            transparent 70%
        ),
        linear-gradient(
            180deg,
            #060916 0%,
            #0A0820 100%
        );

    box-shadow:
        0 0 0 1px rgba(255, 43, 214, 0.06),
        0 30px 80px rgba(0, 0, 0, 0.55),
        0 0 60px rgba(0, 240, 255, 0.08),
        inset 0 0 90px rgba(0, 240, 255, 0.05);
}


/* Pavimento a griglia in prospettiva */

.crime-hero::before {
    content: "";

    position: absolute;

    z-index: -2;

    left: -40%;
    right: -40%;
    bottom: -2px;

    height: 62%;

    background-image:
        linear-gradient(rgba(0, 240, 255, 0.40) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 240, 255, 0.40) 1px, transparent 1px);

    background-size: 52px 52px;

    transform: perspective(360px) rotateX(64deg);
    transform-origin: 50% 100%;

    -webkit-mask-image: linear-gradient(to top, #000 5%, transparent 90%);
            mask-image: linear-gradient(to top, #000 5%, transparent 90%);

    animation: hero-grid 5s linear infinite;
}


/* Linea di scansione */

.crime-hero::after {
    content: "";

    position: absolute;

    z-index: -1;

    left: 0;
    right: 0;
    top: 0;

    height: 2px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(0, 240, 255, 0.95),
            transparent
        );

    box-shadow: 0 0 18px 2px rgba(0, 240, 255, 0.55);

    animation: hero-scan 7s ease-in-out infinite;
}


.crime-hero-skyline {
    position: absolute;

    z-index: 0;

    left: 0;
    right: 0;
    bottom: 0;

    height: 9.2rem;

    background-image: url("__SKYLINE__");
    background-repeat: no-repeat;
    background-position: center bottom;
    background-size: 100% 100%;

    pointer-events: none;
}


@keyframes hero-grid {
    from { background-position: 0 0; }
    to   { background-position: 0 52px; }
}


@keyframes hero-scan {
    0%   { top: 0;    opacity: 0; }
    10%  { opacity: 1; }
    90%  { opacity: 1; }
    100% { top: 100%; opacity: 0; }
}


@keyframes hero-pulse {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.25; }
}


.crime-hero-kicker {
    position: relative;

    z-index: 2;

    display: inline-flex;

    align-items: center;

    gap: 0.55rem;

    padding: 0.32rem 0.75rem;

    margin-bottom: 1.1rem;

    border-radius: 4px;

    border: 1px solid rgba(0, 240, 255, 0.35);

    background: rgba(0, 240, 255, 0.07);

    color: var(--cyan);

    font-family: var(--font-mono);
    font-size: 0.76rem;
    font-weight: 500;
}


.crime-hero-kicker::before {
    content: "";

    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: var(--cyan);

    box-shadow: 0 0 10px var(--cyan);

    animation: hero-pulse 1.8s ease-in-out infinite;
}


.crime-hero-title {
    position: relative;

    z-index: 2;

    margin: 0;

    font-family: var(--font-display);

    font-size: clamp(2.6rem, 5.6vw, 5.4rem);

    line-height: 0.96;

    font-weight: 700;

    color: #FFFFFF;

    letter-spacing: -0.015em;

    text-shadow:
        0 0 22px rgba(0, 240, 255, 0.55),
        0 0 70px rgba(123, 92, 255, 0.40);
}


.crime-hero-subtitle {
    position: relative;

    z-index: 2;

    max-width: 40rem;

    margin-top: 1.1rem;
    margin-bottom: 0;

    color: var(--text-secondary);

    font-size: 1.04rem;

    line-height: 1.7;
}


/* ==================================================
   HEADER PAGINA
   ================================================== */

.crime-page-header {
    position: relative;

    padding: 0.4rem 0 1.5rem 1.2rem;

    margin-bottom: 1.8rem;

    border-bottom: 1px solid var(--line-neutral);
}


.crime-page-header::before {
    content: "";

    position: absolute;

    left: 0;
    top: 0.5rem;
    bottom: 1.6rem;

    width: 3px;

    background:
        linear-gradient(
            180deg,
            var(--cyan),
            var(--magenta)
        );

    box-shadow: 0 0 14px rgba(0, 240, 255, 0.6);
}


.crime-page-kicker {
    color: var(--cyan);

    font-family: var(--font-mono);
    font-weight: 500;
    font-size: 0.8rem;

    margin-bottom: 0.4rem;
}


.crime-page-title {
    margin: 0;

    font-family: var(--font-display);

    font-size: 2.6rem;

    font-weight: 700;

    color: #FFFFFF;

    letter-spacing: -0.01em;

    text-shadow: 0 0 26px rgba(0, 240, 255, 0.28);
}


.crime-page-description {
    max-width: 46rem;

    margin-top: 0.55rem;
    margin-bottom: 0;

    color: var(--text-secondary);
}


/* ==================================================
   PANNELLI
   (container con key che inizia per "panel")
   Angoli a mirino disegnati con i background.
   ================================================== */

[class*="st-key-panel"] {
    --angolo: var(--cyan);

    position: relative;

    border-radius: 6px;

    border: 1px solid var(--line);

    padding: 1.1rem 1.25rem;

    background:
        linear-gradient(var(--angolo), var(--angolo)) top left / 16px 2px no-repeat,
        linear-gradient(var(--angolo), var(--angolo)) top left / 2px 16px no-repeat,
        linear-gradient(var(--angolo), var(--angolo)) top right / 16px 2px no-repeat,
        linear-gradient(var(--angolo), var(--angolo)) top right / 2px 16px no-repeat,
        linear-gradient(var(--angolo), var(--angolo)) bottom left / 16px 2px no-repeat,
        linear-gradient(var(--angolo), var(--angolo)) bottom left / 2px 16px no-repeat,
        linear-gradient(var(--angolo), var(--angolo)) bottom right / 16px 2px no-repeat,
        linear-gradient(var(--angolo), var(--angolo)) bottom right / 2px 16px no-repeat,
        linear-gradient(
            160deg,
            rgba(14, 20, 36, 0.96),
            rgba(8, 11, 22, 0.96)
        );

    transition:
        border-color 180ms ease,
        box-shadow 180ms ease;
}


[class*="st-key-panel"]:hover {
    border-color: var(--line-strong);

    box-shadow:
        0 0 28px rgba(0, 240, 255, 0.10),
        inset 0 0 40px rgba(0, 240, 255, 0.03);
}


[class*="st-key-panel-magenta"] {
    --angolo: var(--magenta);
}


[class*="st-key-panel-magenta"]:hover {
    border-color: rgba(255, 43, 214, 0.45);

    box-shadow:
        0 0 28px rgba(255, 43, 214, 0.12),
        inset 0 0 40px rgba(255, 43, 214, 0.03);
}


[class*="st-key-panel-violet"] {
    --angolo: var(--violet);
}


[class*="st-key-panel-violet"]:hover {
    border-color: rgba(123, 92, 255, 0.55);

    box-shadow:
        0 0 28px rgba(123, 92, 255, 0.16),
        inset 0 0 40px rgba(123, 92, 255, 0.04);
}


/* ==================================================
   KPI / METRICHE
   ================================================== */

[data-testid="stMetric"] {
    height: 100%;

    position: relative;

    padding: 1rem 1.15rem 1rem 1.3rem;

    border-radius: 6px;

    border: 1px solid var(--line-neutral);

    background:
        linear-gradient(
            160deg,
            rgba(14, 20, 36, 0.94),
            rgba(8, 11, 22, 0.96)
        );

    transition:
        border-color 160ms ease,
        box-shadow 160ms ease;
}


[data-testid="stMetric"]::before {
    content: "";

    position: absolute;

    left: 0;
    top: 0.8rem;
    bottom: 0.8rem;

    width: 2px;

    background: var(--cyan);

    box-shadow: 0 0 10px var(--cyan);
}


[data-testid="stMetric"]:hover {
    border-color: var(--line-strong);

    box-shadow: 0 0 26px rgba(0, 240, 255, 0.10);
}


[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: var(--text-secondary);

    font-size: 0.86rem;
}


[data-testid="stMetricValue"] {
    color: #FFFFFF;

    font-family: var(--font-display);

    font-weight: 600;

    letter-spacing: -0.01em;

    text-shadow: 0 0 18px rgba(0, 240, 255, 0.30);
}


/* ==================================================
   BOTTONI
   ================================================== */

div.stButton > button,
div.stFormSubmitButton > button,
div.stDownloadButton > button {
    min-height: 2.9rem;

    border-radius: 6px;

    border: 1px solid rgba(0, 240, 255, 0.35);

    background: rgba(0, 240, 255, 0.05);

    color: var(--text);

    font-weight: 600;

    transition:
        transform 150ms ease,
        box-shadow 150ms ease,
        border-color 150ms ease,
        background 150ms ease;
}


div.stButton > button p,
div.stFormSubmitButton > button p,
div.stDownloadButton > button p {
    color: #FFFFFF !important;
}


div.stButton > button:hover,
div.stFormSubmitButton > button:hover,
div.stDownloadButton > button:hover {
    transform: translateY(-1px);

    border-color: var(--cyan);

    background: rgba(0, 240, 255, 0.12);

    box-shadow:
        0 0 22px rgba(0, 240, 255, 0.28),
        inset 0 0 14px rgba(0, 240, 255, 0.08);
}


div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"] {
    border: 1px solid rgba(255, 255, 255, 0.18);

    background:
        linear-gradient(
            90deg,
            #0891B2,
            #5B3FE0 55%,
            #C026A8
        );

    box-shadow: 0 6px 26px rgba(91, 63, 224, 0.35);
}


div.stButton > button[kind="primary"]:hover,
div.stFormSubmitButton > button[kind="primary"]:hover {
    box-shadow:
        0 8px 34px rgba(91, 63, 224, 0.55),
        0 0 28px rgba(255, 43, 214, 0.28);
}


/* ==================================================
   INPUT
   ================================================== */

[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="base-input"],
[data-baseweb="textarea"] {
    background: var(--panel-2) !important;

    border-color: var(--line-neutral) !important;

    border-radius: 6px !important;

    transition:
        border-color 150ms ease,
        box-shadow 150ms ease;
}


[data-baseweb="input"]:focus-within > div,
[data-baseweb="select"]:focus-within > div,
[data-baseweb="textarea"]:focus-within {
    border-color: var(--cyan) !important;

    box-shadow: 0 0 0 1px var(--cyan), 0 0 18px rgba(0, 240, 255, 0.22) !important;
}


[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    color: #FFFFFF !important;
}


/* Menu a tendina */

[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] ul {
    background: var(--panel-2) !important;

    border: 1px solid var(--line);
}


[data-baseweb="popover"] li:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"] {
    background: rgba(0, 240, 255, 0.12) !important;
}


/* Etichette dei widget */

[data-testid="stWidgetLabel"] p {
    color: var(--text-secondary);

    font-size: 0.86rem;

    font-weight: 500;
}


/* ==================================================
   TAB
   ================================================== */

[data-baseweb="tab-list"] {
    gap: 0.4rem;

    border-bottom: 1px solid var(--line-neutral);
}


[data-baseweb="tab-border"] {
    background: transparent !important;
}


button[data-baseweb="tab"] {
    border-radius: 6px 6px 0 0;

    padding-left: 1.1rem;
    padding-right: 1.1rem;

    transition:
        background 150ms ease;
}


button[data-baseweb="tab"] p {
    color: var(--text-secondary);

    font-weight: 500;
}


button[data-baseweb="tab"]:hover {
    background: rgba(0, 240, 255, 0.06);
}


button[data-baseweb="tab"][aria-selected="true"] {
    background:
        linear-gradient(
            180deg,
            rgba(0, 240, 255, 0.12),
            transparent
        );
}


button[data-baseweb="tab"][aria-selected="true"] p {
    color: #FFFFFF;

    text-shadow: 0 0 12px rgba(0, 240, 255, 0.55);
}


[data-baseweb="tab-highlight"] {
    height: 2px !important;

    background:
        linear-gradient(
            90deg,
            var(--cyan),
            var(--magenta)
        ) !important;

    box-shadow: 0 0 12px rgba(0, 240, 255, 0.7);
}


/* ==================================================
   EXPANDER / POPOVER / ALERT
   ================================================== */

[data-testid="stExpander"] {
    border: 1px solid var(--line-neutral);

    border-radius: 6px;

    background: rgba(10, 14, 26, 0.7);
}


[data-testid="stExpander"] summary:hover {
    color: var(--cyan);
}


[data-testid="stPopover"] button {
    border-radius: 6px;

    border: 1px solid rgba(0, 240, 255, 0.35);

    background: rgba(0, 240, 255, 0.06);
}


[data-testid="stPopover"] button:hover {
    border-color: var(--cyan);

    box-shadow: 0 0 20px rgba(0, 240, 255, 0.22);
}


[data-testid="stAlert"] {
    border-radius: 6px;

    border: 1px solid var(--line);

    background: rgba(10, 14, 26, 0.85);
}


/* ==================================================
   TABELLE E GRAFICI
   ================================================== */

[data-testid="stDataFrame"] {
    border: 1px solid var(--line);

    border-radius: 6px;

    overflow: hidden;

    background: var(--panel);
}


[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"] {
    padding: 1rem;

    background:
        linear-gradient(
            160deg,
            rgba(14, 20, 36, 0.80),
            rgba(8, 11, 22, 0.80)
        );

    border: 1px solid var(--line);

    border-radius: 6px;
}


/* Le mappe vivono in un riquadro con bordo neon */

iframe[title*="streamlit_folium"] {
    border: 1px solid var(--line-strong);

    border-radius: 6px;

    box-shadow: 0 0 34px rgba(0, 240, 255, 0.10);
}


hr {
    border-color: var(--line-neutral) !important;
}


/* ==================================================
   CHIP FILTRI
   ================================================== */

.crime-chips {
    display: flex;

    flex-wrap: wrap;

    gap: 0.5rem;

    margin-top: 0.6rem;
    margin-bottom: 1.2rem;
}


.crime-chip {
    display: inline-flex;

    align-items: baseline;

    gap: 0.5rem;

    padding: 0.38rem 0.7rem;

    border-radius: 4px;

    background: rgba(0, 240, 255, 0.06);

    border: 1px solid rgba(0, 240, 255, 0.26);

    color: var(--text-secondary);

    font-family: var(--font-mono);
    font-size: 0.76rem;

    white-space: nowrap;
}


.crime-chip strong {
    color: #FFFFFF;

    font-weight: 500;
}


/* ==================================================
   ETICHETTA DI SEZIONE
   ================================================== */

.crime-section-label {
    display: flex;

    align-items: center;

    gap: 0.55rem;

    margin-top: 0.6rem;
    margin-bottom: 0.5rem;

    color: var(--text-muted);

    font-family: var(--font-mono);
    font-size: 0.78rem;
}


.crime-section-label::before {
    content: "";

    width: 8px;
    height: 8px;

    background: var(--cyan);

    box-shadow: 0 0 8px var(--cyan);
}


/* ==================================================
   SCHERMI PICCOLI
   ================================================== */

@media (max-width: 900px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .crime-hero {
        padding: 1.8rem 1.4rem 8rem 1.4rem;
    }

    .crime-page-title {
        font-size: 2rem;
    }
}


/* ==================================================
   MOVIMENTO RIDOTTO
   ================================================== */

@media (prefers-reduced-motion: reduce) {

    .crime-hero::before,
    .crime-hero::after,
    .crime-hero-kicker::before {
        animation: none;
    }

    .crime-hero::after {
        display: none;
    }
}



.brand{display:flex;gap:12px;align-items:center;margin:0 0 2.5rem}
.brand-mark{display:grid;place-items:center;width:42px;height:46px;border:1px solid #38bdf855;border-radius:13px;color:#7dd3fc;background:linear-gradient(135deg,#38bdf820,#8b5cf620);font-size:24px}
.brand strong{font-size:17px;line-height:1.3}
.brand small{display:block;font-size:10px;color:#8fa2bc;letter-spacing:.17em;margin-top:4px}

.nav-label{font-size:10px;letter-spacing:.16em;color:#8799b3;margin:1.5rem 0 .65rem;font-weight:650}

.sidebar-note{margin-top:3rem;padding:1rem;border:1px solid #ffffff0c;border-radius:12px;color:#8fa2bc;font-size:12px;line-height:1.8}
.sidebar-note strong{color:#d6e2f2;display:block;font-size:12px}
.sidebar-note span{color:#7dd3fc}

.overview-topline{display:flex;justify-content:space-between;gap:1rem;color:#8c9db6;font-size:10px;letter-spacing:.13em;margin:0 0 1rem}
.overview-topline span:last-child{letter-spacing:.02em}

.workspace-heading h2{margin:0;padding:0!important;font-size:1.4rem!important}
.workspace-heading p{color:#9baac0;font-size:13px;margin:.35rem 0 0}

.workspace-card{position:relative;overflow:hidden;min-height:188px;padding:6px 4px 0;--accent:#38bdf8}
.workspace-card.violet{--accent:#a78bfa}
.workspace-card.blue{--accent:#60a5fa}
.workspace-card.pink{--accent:#e879b9}
.card-eyebrow{font-size:9px;letter-spacing:.15em;font-weight:700;color:var(--accent);margin-bottom:23px}
.workspace-card h3{font-size:1.5rem!important;margin:0;padding:0!important;position:relative;z-index:1}
.card-subtitle{font-size:13px;color:#e0e7f2;margin:.4rem 0 .65rem}
.workspace-card p{font-size:13px;color:#9caec5;max-width:86%;margin:0;line-height:1.7}
.card-art{position:absolute;right:-12px;top:-12px;width:145px;height:80px;color:var(--accent);opacity:.65;pointer-events:none}
.card-art svg{width:100%}

.workspace-footer{display:flex;justify-content:space-between;border-top:1px solid #ffffff10;margin-top:1.5rem;padding-top:1rem;color:#8293ab;font-size:10px;letter-spacing:.06em}
.card-art{width:110px;opacity:.4}
.workspace-card p{max-width:100%}
.overview-topline span:last-child{display:none}
.workspace-card{min-height:170px}
.workspace-footer{gap:1rem;flex-wrap:wrap}
.brand-mark{color:var(--cyan);border-color:var(--line-strong);box-shadow:0 0 18px #00f0ff22}
.brand strong,.workspace-heading h2,.workspace-card h3{font-family:var(--font-display)}
.sidebar-note{border-color:var(--line);background:#0a0e1a99}
.sidebar-note span{color:var(--cyan)}
.workspace-card{min-height:190px;--accent:var(--cyan)}
.workspace-card.violet{--accent:var(--magenta)}
.workspace-card.blue{--accent:var(--violet)}
.workspace-card.pink{--accent:var(--cyan)}
[class*="st-key-panel-"]:has(.workspace-card){padding:1rem 1.15rem;border:1px solid var(--line-strong);border-radius:6px}
.st-key-panel-magenta-analytics:has(.workspace-card){border-color:#ff2bd655}
.st-key-panel-violet-records:has(.workspace-card){border-color:#7b5cff77}
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]{padding:.85rem;border-radius:6px;border:1px solid transparent}
.st-key-nav_active [data-testid="stPageLink-NavLink"]{background:linear-gradient(90deg,#00f0ff22,#7b5cff11)!important;border-color:var(--line-strong)!important;box-shadow:inset 3px 0 var(--cyan),0 0 20px #00f0ff15}
[data-testid="stTabs"] [role="tablist"]{gap:6px;padding:6px;border:1px solid var(--line-strong);border-radius:8px;background:var(--panel)}
[data-testid="stTabs"] [role="tab"]{padding:10px 16px;border-radius:5px;height:auto;border:1px solid transparent}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{border-color:var(--cyan);background:linear-gradient(100deg,#00f0ff20,#7b5cff20);box-shadow:0 0 12px #00f0ff15}
.filter-section-title{display:flex;align-items:center;gap:.65rem;margin:1.15rem 0 .7rem;font-size:1.15rem;font-weight:600;color:var(--text)}
.filter-section-emoji{font-family:"Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif;font-size:1.3rem;line-height:1.4;flex-shrink:0}
@media(max-width:700px){.overview-topline span:last-child{display:none}.workspace-card{min-height:190px}.workspace-footer{flex-wrap:wrap;gap:.5rem}.card-art{width:110px;opacity:.4}}


.block-container{padding-top:4.5rem!important}
.filter-section-emoji{display:inline-flex;color:var(--cyan)}

.home-neon-title{display:flex;align-items:center;gap:.8rem;margin:.3rem 0 .8rem}
.home-neon-icon{display:inline-flex;flex-shrink:0;color:var(--cyan);filter:drop-shadow(0 0 6px #00f0ff99) drop-shadow(0 0 14px #00f0ff55)}
.home-neon-title h3{margin:0!important;padding:0!important}
[class*="st-key-panel-"]:has(.workspace-card):hover .home-neon-icon{filter:drop-shadow(0 0 8px #00f0ff) drop-shadow(0 0 18px #00f0ff99)}
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]{transition:background 160ms ease,color 160ms ease,border-color 160ms ease,box-shadow 160ms ease}
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover{background:rgba(0,240,255,.07);border-color:var(--line);color:var(--text)}
.st-key-nav_active [data-testid="stPageLink-NavLink"]{color:#fff!important;background:linear-gradient(90deg,rgba(0,240,255,.16),rgba(123,92,255,.10) 70%,transparent)!important;border-color:rgba(0,240,255,.30)!important;box-shadow:inset 3px 0 0 var(--cyan),0 0 22px rgba(0,240,255,.10)!important}
.st-key-nav_active [data-testid="stPageLink-NavLink"] span,.st-key-nav_active [data-testid="stPageLink-NavLink"] p{text-shadow:0 0 12px rgba(0,240,255,.55);color:#fff!important}

</style>
"""


def applica_stile_globale():
    st.markdown(
        CSS_GLOBALE.replace(
            "__SKYLINE__",
            _skyline_data_uri()
        ),
        unsafe_allow_html=True
    )


# =========================================================
# HERO HOME
# =========================================================

def mostra_hero():
    contenuto = (
        '<section class="crime-hero">'

        '<div class="crime-hero-skyline"></div>'

        '<div class="crime-hero-kicker">'
        'CHICAGO · CRIME INTELLIGENCE'
        '</div>'

        '<h1 class="crime-hero-title">'
        'La città, vista<br>attraverso i dati.'
        '</h1>'

        '<p class="crime-hero-subtitle">'
        'Esplora i crimini di Chicago. Collega luoghi, scopri tendenze e trasforma i dati in nuove prospettive.'
        '</p>'

        '</section>'
    )

    st.markdown(
        contenuto,
        unsafe_allow_html=True
    )


# =========================================================
# HEADER PAGINA
# =========================================================

def mostra_header_pagina(
        sezione,
        titolo,
        descrizione
):
    contenuto = (
        '<div class="crime-page-header">'

        '<div class="crime-page-kicker">'
        f'{html.escape(sezione)}'
        '</div>'

        '<h1 class="crime-page-title">'
        f'{html.escape(titolo)}'
        '</h1>'

        '<p class="crime-page-description">'
        f'{html.escape(descrizione)}'
        '</p>'

        '</div>'
    )

    st.markdown(
        contenuto,
        unsafe_allow_html=True
    )


# =========================================================
# CHIP FILTRI
# =========================================================

def mostra_chip_filtri():

    if not st.session_state.get(
            "filtri_applicati",
            False
    ):
        return

    chips = []

    chips.append(
        (
            "Periodo",
            (
                f"{st.session_state.data_inizio:%d/%m/%Y}"
                " → "
                f"{st.session_state.data_fine:%d/%m/%Y}"
            )
        )
    )

    if (
            st.session_state.tipo_crimine
            !=
            "Tutti"
    ):
        chips.append(
            (
                "Crimine",
                st.session_state.tipo_crimine
            )
        )

    if (
            st.session_state.distretto
            !=
            "Tutti"
    ):
        chips.append(
            (
                "Distretto",
                str(
                    st.session_state.distretto
                )
            )
        )

    if (
            st.session_state.arresto
            !=
            "Tutti"
    ):
        chips.append(
            (
                "Arresto",
                st.session_state.arresto
            )
        )

    if st.session_state.get(
            "area_filtro_attiva",
            False
    ):
        chips.append(
            (
                "Area",
                "Selezione mappa"
            )
        )

    contenuto = ""

    for nome, valore in chips:
        contenuto += (
            '<span class="crime-chip">'
            f'{html.escape(nome)}'
            '<strong>'
            f'{html.escape(valore)}'
            '</strong>'
            '</span>'
        )

    st.markdown(
        f"""
        <div class="crime-section-label">
            Filtri attivi
        </div>

        <div class="crime-chips">
            {contenuto}
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# STILE GRAFICI ALTAIR
# =========================================================

def applica_stile_grafico(grafico):

    return (
        grafico

        .configure(
            background="transparent",
            font="IBM Plex Sans"
        )

        .configure_view(
            stroke=None
        )

        .configure_axis(
            gridColor="#12304A",
            gridOpacity=0.8,

            domainColor="#1F4E6B",
            domainOpacity=0.9,

            tickColor="#1F4E6B",

            labelColor="#B7C7E2",
            labelFontSize=12,

            titleColor="#7387AB",
            titleFontSize=12,
            titleFontWeight="normal",

            titlePadding=14
        )

        .configure_legend(
            labelColor="#B7C7E2",
            labelFontSize=12,

            titleColor="#7387AB",
            titleFontSize=12
        )

        .configure_range(
            category=PALETTE_GRAFICI
        )
    )


def illustrazione(tipo):
    """Decorative inline SVGs, never presented as dataset results."""
    paths = {
        "map": '<path d="M0 30H260M0 65H260M0 100H260M40 0V130M90 0V130M145 0V130M205 0V130" stroke="currentColor" opacity=".18"/><path d="M180 0L165 42 190 85 178 130H260V0Z" fill="currentColor" opacity=".12"/><path d="M40 100L90 65 145 65 165 42" stroke="currentColor" stroke-width="2" stroke-dasharray="5 5"/><g fill="currentColor"><circle cx="40" cy="100" r="5"/><circle cx="90" cy="65" r="5"/><circle cx="145" cy="65" r="5"/><circle cx="165" cy="42" r="5"/></g>',
        "chart": '<path d="M10 30H250M10 65H250M10 100H250" stroke="currentColor" opacity=".12"/><path d="M12 100L48 78 85 88 120 48 156 60 195 20 246 32V120H12Z" fill="currentColor" opacity=".08"/><path d="M12 100L48 78 85 88 120 48 156 60 195 20 246 32" stroke="currentColor" stroke-width="3"/><circle cx="195" cy="20" r="5" fill="currentColor"/>',
        "table": '<g stroke="currentColor" opacity=".25"><rect x="15" y="15" width="230" height="100" rx="9"/><path d="M15 42H245M15 68H245M15 92H245M60 15V115M172 15V115"/></g><g fill="currentColor" opacity=".7"><rect x="28" y="27" width="18" height="4" rx="2"/><rect x="75" y="27" width="70" height="4" rx="2"/><rect x="186" y="27" width="42" height="4" rx="2"/></g><path d="M75 55H130M75 80H147M75 104H119" stroke="currentColor" stroke-width="4" opacity=".4"/>',
        "nodes": '<g stroke="currentColor" opacity=".4"><path d="M35 30L110 65 35 105M110 65L185 25 225 70 185 110 110 65M185 25L185 110M35 30L185 25M35 105L185 110"/></g><g fill="currentColor"><circle cx="35" cy="30" r="6"/><circle cx="35" cy="105" r="6"/><circle cx="110" cy="65" r="10"/><circle cx="185" cy="25" r="6"/><circle cx="225" cy="70" r="6"/><circle cx="185" cy="110" r="6"/></g><circle cx="110" cy="65" r="24" stroke="currentColor" opacity=".25"/>',
    }
    if tipo == "city":
        return ('<svg viewBox="0 0 460 290" fill="none" xmlns="http://www.w3.org/2000/svg">'
                '<defs><linearGradient id="city-glow" x2="1" y2="1"><stop stop-color="#38BDF8"/><stop offset="1" stop-color="#8B5CF6"/></linearGradient></defs>'
                '<g stroke="#38BDF8" opacity=".12"><path d="M0 240L230 130 460 240 230 350Z M0 205L230 95 460 205M60 270L290 160M120 300L350 190M170 160L400 270M110 190L340 300"/></g>'
                '<g stroke="url(#city-glow)" stroke-width="1.5" fill="#101c30">'
                '<path d="M65 230V160H105V230M112 230V125H151V230M160 230V80H177V48H192V80H209V230M219 230V111H259V230M270 230V67H285V25H289V67H308V230M319 230V140H355V230M365 230V176H400V230"/>'
                '<path d="M55 231H413"/></g><g stroke="#7DD3FC" opacity=".5" stroke-dasharray="3 9" stroke-width="3">'
                '<path d="M125 143V222M139 143V222M173 94V222M195 94V222M233 129V222M246 129V222M283 84V222M297 84V222M332 153V222M345 153V222"/></g>'
                '<circle cx="289" cy="25" r="5" fill="#38BDF8"/><circle cx="289" cy="25" r="14" stroke="#38BDF8" opacity=".25"/></svg>')
    return '<svg viewBox="0 0 260 130" fill="none" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">' + paths[tipo] + '</svg>'


def icona_neon(tipo):
    forme = {
        "map": '<path d="M3 5l6-2 6 2 6-2v16l-6 2-6-2-6 2Z M9 3v16M15 5v16"/>',
        "chart": '<path d="M4 20V11h3v9ZM11 20V4h3v16ZM18 20v-6h3v6Z" fill="currentColor" stroke="none"/>',
        "table": '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M3 9h18M3 15h18"/>',
        "nodes": '<path d="M9 6l2 5 5 2-5 2-2 5-2-5-5-2 5-2ZM18 2l1.2 3.2L22 6l-2.8 1.2L18 10l-1.2-2.8L14 6l2.8-.8ZM19 16l1 2 2 1-2 1-1 2-1-2-2-1 2-1Z"/>',
    }
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            'width="28" height="28" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + forme[tipo] + '</svg>')
