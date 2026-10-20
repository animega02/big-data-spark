import html

import streamlit as st



# =========================================================
# DESIGN SYSTEM
# =========================================================

def applica_stile_globale():

    st.markdown(
        """
        <style>

        /* ==================================================
           PALETTE
           ================================================== */

        :root {
            --bg: #080B12;
            --bg-soft: #0B1019;

            --surface: #0F1520;
            --surface-2: #141C2A;
            --surface-3: #182233;

            --border: #223047;
            --border-soft: rgba(148, 163, 184, 0.14);

            --text: #F8FAFC;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;

            --cyan: #38BDF8;
            --blue: #3B82F6;
            --violet: #8B5CF6;
            --magenta: #EC4899;

            --danger: #F43F5E;
            --success: #22C55E;
        }


        /* ==================================================
           APP
           ================================================== */

        html,
        body,
        [class*="css"] {
            font-family:
                Inter,
                ui-sans-serif,
                system-ui,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }


        .stApp {
            background:
                radial-gradient(
                    circle at 18% 0%,
                    rgba(14, 165, 233, 0.10),
                    transparent 28rem
                ),
                radial-gradient(
                    circle at 92% 8%,
                    rgba(139, 92, 246, 0.09),
                    transparent 30rem
                ),
                var(--bg);

            color: var(--text);
        }


        .block-container {
            max-width: 1540px;
            padding-top: 2rem;
            padding-bottom: 5rem;
            padding-left: 2.2rem;
            padding-right: 2.2rem;
        }
        /* ==================================================
           STREAMLIT HEADER
           ================================================== */
        
        [data-testid="stHeader"] {
            background: rgba(8, 11, 18, 0.96);
            border-bottom: 1px solid rgba(148, 163, 184, 0.08);
        }
        
        [data-testid="stToolbar"] {
            background: transparent;
        }
        

        /* ==================================================
           SIDEBAR
           ================================================== */

        [data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #0E1420 0%,
                    #0A0F18 100%
                );

            border-right: 1px solid var(--border-soft);
        }


        [data-testid="stSidebarContent"] {
            padding-top: 1rem;
        }


        [data-testid="stSidebarNav"] a {
            border-radius: 12px;
            margin: 4px 8px;
            padding-top: 0.7rem;
            padding-bottom: 0.7rem;

            color: var(--text-secondary);

            transition:
                background 160ms ease,
                color 160ms ease,
                transform 160ms ease;
        }


        [data-testid="stSidebarNav"] a:hover {
            background: rgba(56, 189, 248, 0.08);
            color: var(--text);

            transform: translateX(2px);
        }


        [data-testid="stSidebarNav"] a[aria-current="page"] {
            color: white;

            background:
                linear-gradient(
                    90deg,
                    rgba(14, 165, 233, 0.18),
                    rgba(139, 92, 246, 0.15)
                );

            border:
                1px solid rgba(56, 189, 248, 0.25);

            box-shadow:
                inset 3px 0 0 #38BDF8,
                0 0 24px rgba(14, 165, 233, 0.08);
        }


        /* ==================================================
           TITOLI STREAMLIT
           ================================================== */

        h1 {
            color: var(--text);
            font-weight: 800 !important;
            letter-spacing: -0.035em;
        }


        h2,
        h3 {
            color: var(--text);
            letter-spacing: -0.02em;
        }


        p {
            color: var(--text-secondary);
        }


        /* ==================================================
           HERO
           ================================================== */

        .crime-hero {
            position: relative;
            overflow: hidden;

            padding: 2rem 2.2rem;

            margin-bottom: 1.6rem;

            border-radius: 24px;

            border:
                1px solid rgba(56, 189, 248, 0.18);

            background:
                linear-gradient(
                    135deg,
                    rgba(20, 28, 42, 0.98),
                    rgba(15, 21, 32, 0.97)
                );

            box-shadow:
                0 18px 60px rgba(0, 0, 0, 0.28);
        }


        .crime-hero::before {
            content: "";

            position: absolute;

            width: 350px;
            height: 350px;

            right: -130px;
            top: -200px;

            background:
                radial-gradient(
                    circle,
                    rgba(56, 189, 248, 0.24),
                    transparent 65%
                );

            pointer-events: none;
        }


        .crime-hero::after {
            content: "";

            position: absolute;

            width: 300px;
            height: 300px;

            left: 45%;
            bottom: -260px;

            background:
                radial-gradient(
                    circle,
                    rgba(139, 92, 246, 0.20),
                    transparent 68%
                );

            pointer-events: none;
        }


        .crime-hero-kicker {
            display: inline-flex;
            align-items: center;

            padding: 0.35rem 0.7rem;

            border-radius: 999px;

            border:
                1px solid rgba(56, 189, 248, 0.26);

            background:
                rgba(56, 189, 248, 0.07);

            color: #7DD3FC;

            font-size: 0.73rem;
            font-weight: 700;

            letter-spacing: 0.09em;
            text-transform: uppercase;

            margin-bottom: 1rem;
        }


        .crime-hero-title {
            position: relative;
            z-index: 2;

            margin: 0;

            font-size: clamp(
                2.3rem,
                4vw,
                4.5rem
            );

            line-height: 1;

            font-weight: 850;

            color: white;

            letter-spacing: -0.055em;
        }


        .crime-hero-title span {
            background:
                linear-gradient(
                    90deg,
                    #38BDF8,
                    #60A5FA,
                    #A78BFA
                );

            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }


        .crime-hero-subtitle {
            position: relative;
            z-index: 2;

            max-width: 820px;

            margin-top: 1rem;
            margin-bottom: 0;

            color: var(--text-secondary);

            font-size: 1.02rem;
            line-height: 1.75;
        }


        /* ==================================================
           PAGE HEADER
           ================================================== */

        .crime-page-header {
            padding: 0.7rem 0 1.4rem 0;

            border-bottom:
                1px solid var(--border-soft);

            margin-bottom: 1.7rem;
        }


        .crime-page-kicker {
            color: #38BDF8;

            font-weight: 700;
            font-size: 0.76rem;

            text-transform: uppercase;
            letter-spacing: 0.08em;

            margin-bottom: 0.45rem;
        }


        .crime-page-title {
            margin: 0;

            font-size: 2.35rem;

            font-weight: 800;

            color: white;

            letter-spacing: -0.045em;
        }


        .crime-page-description {
            margin-top: 0.5rem;
            margin-bottom: 0;

            color: var(--text-secondary);
        }


        /* ==================================================
           KPI / METRICHE
           ================================================== */

        [data-testid="stMetric"] {
            height: 100%;

            background:
                linear-gradient(
                    145deg,
                    rgba(20, 28, 42, 0.94),
                    rgba(13, 18, 28, 0.95)
                );

            border:
                1px solid var(--border-soft);

            border-radius: 18px;

            padding: 1.05rem 1.15rem;

            box-shadow:
                0 10px 28px rgba(0, 0, 0, 0.17);

            transition:
                transform 160ms ease,
                border-color 160ms ease,
                box-shadow 160ms ease;
        }


        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);

            border-color:
                rgba(56, 189, 248, 0.28);

            box-shadow:
                0 16px 36px rgba(0, 0, 0, 0.23),
                0 0 24px rgba(14, 165, 233, 0.04);
        }


        [data-testid="stMetricLabel"] {
            color: var(--text-secondary);
        }


        [data-testid="stMetricValue"] {
            color: white;

            font-weight: 750;

            letter-spacing: -0.035em;
        }


        /* ==================================================
           BUTTON
           ================================================== */

        div.stButton > button,
        div.stFormSubmitButton > button {
            min-height: 3rem;

            border-radius: 12px;

            border:
                1px solid var(--border);

            background: var(--surface-2);

            color: var(--text);

            font-weight: 650;

            transition:
                transform 150ms ease,
                box-shadow 150ms ease,
                border-color 150ms ease;
        }


        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover {
            transform: translateY(-1px);

            border-color:
                rgba(56, 189, 248, 0.5);

            color: white;
        }


        div.stButton > button[kind="primary"],
        div.stFormSubmitButton > button[kind="primary"] {
            border: none;

            color: white;

            background:
                linear-gradient(
                    90deg,
                    #0284C7,
                    #2563EB,
                    #7C3AED
                );

            box-shadow:
                0 8px 24px rgba(37, 99, 235, 0.22);
        }


        div.stButton > button[kind="primary"]:hover,
        div.stFormSubmitButton > button[kind="primary"]:hover {
            box-shadow:
                0 12px 30px rgba(37, 99, 235, 0.32),
                0 0 26px rgba(139, 92, 246, 0.13);
        }


        /* ==================================================
           INPUT
           ================================================== */

        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        [data-baseweb="base-input"] {
            background: #111827 !important;

            border-color:
                rgba(148, 163, 184, 0.16) !important;

            border-radius: 12px !important;
        }


        [data-baseweb="input"] input {
            color: white !important;
        }


        /* ==================================================
           POPOVER
           ================================================== */

        [data-testid="stPopover"] button {
            border-radius: 12px;

            border:
                1px solid rgba(56, 189, 248, 0.22);

            background:
                rgba(20, 28, 42, 0.82);
        }


        /* ==================================================
           ALERT
           ================================================== */

        [data-testid="stAlert"] {
            border-radius: 14px;

            border:
                1px solid var(--border-soft);

            background:
                rgba(20, 28, 42, 0.76);
        }


        /* ==================================================
           DATAFRAME / CHART
           ================================================== */

        [data-testid="stDataFrame"] {
            border:
                1px solid var(--border-soft);

            border-radius: 16px;

            overflow: hidden;

            background: var(--surface);
        }


        [data-testid="stVegaLiteChart"] {
            padding: 1rem;

            background:
                rgba(15, 21, 32, 0.60);

            border:
                1px solid var(--border-soft);

            border-radius: 18px;
        }


        /* ==================================================
           DIVIDER
           ================================================== */

        hr {
            border-color:
                rgba(148, 163, 184, 0.12) !important;
        }


        /* ==================================================
           FILTER CHIPS
           ================================================== */

        .crime-chips {
            display: flex;
            flex-wrap: wrap;

            gap: 0.55rem;

            margin-top: 0.7rem;
            margin-bottom: 1.2rem;
        }


        .crime-chip {
            display: inline-flex;
            align-items: center;

            padding:
                0.4rem
                0.72rem;

            border-radius: 999px;

            background:
                rgba(15, 23, 42, 0.88);

            border:
                1px solid rgba(148, 163, 184, 0.18);

            color: #CBD5E1;

            font-size: 0.78rem;

            white-space: nowrap;
        }


        .crime-chip strong {
            color: white;
            margin-left: 0.3rem;
        }


        .crime-chip-accent {
            border-color:
                rgba(56, 189, 248, 0.28);

            background:
                rgba(14, 165, 233, 0.08);
        }


        /* ==================================================
           SECTION LABEL
           ================================================== */

        .crime-section-label {
            margin-top: 0.6rem;

            margin-bottom: 0.2rem;

            color: #64748B;

            font-size: 0.73rem;

            font-weight: 700;

            text-transform: uppercase;

            letter-spacing: 0.09em;
        }


        /* ==================================================
           SMALL SCREENS
           ================================================== */

        @media (
            max-width: 900px
        ) {

            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .crime-hero {
                padding: 1.6rem;
            }
        }      

        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HERO HOME
# =========================================================
def mostra_hero():

    contenuto = (
        '<section class="crime-hero">'
        '<div class="crime-hero-kicker">'
        'Apache Spark · Crime Intelligence'
        '</div>'
        '<h1 class="crime-hero-title">'
        'Chicago <span>Crime Explorer</span>'
        '</h1>'
        '<p class="crime-hero-subtitle">'
        'Esplora milioni di eventi criminali, '
        'analizza pattern geografici e temporali '
        'e sperimenta modelli di Machine Learning '
        'attraverso una dashboard interattiva '
        'costruita su Apache Spark.'
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

        .configure_view(
            stroke=None
        )

        .configure_axis(
            gridColor="#1E293B",
            gridOpacity=0.65,

            domainColor="#334155",
            domainOpacity=0.8,

            tickColor="#334155",

            labelColor="#CBD5E1",
            labelFontSize=12,

            titleColor="#94A3B8",
            titleFontSize=12,

            titlePadding=14
        )

        .configure_legend(
            labelColor="#CBD5E1",
            labelFontSize=12,

            titleColor="#94A3B8",
            titleFontSize=12
        )
    )