"""
Suicide Prevention  – France
======================================
Une visualisation pédagogique sur la prévention du suicide en France.
Structuré comme une enquête progressive pour identifier les facteurs de risque.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json

# ─── Color Constants (Consistent throughout) ──────────────────────────────────
COLOR_MEN = "#2196F3"      # Blue for men
COLOR_WOMEN = "#E91E63"    # Pink for women
COLOR_ALL = "#757575"      # Grey for all

# ─── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prévention du Suicide en France",
    page_icon="🎗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .block-container { padding-top: 1rem; max-width: 1200px; }

    /* ── Metric cards ── */
    div[data-testid="stMetric"] {
        background: #f0f4fa !important;
        padding: 18px 22px;
        border-radius: 12px;
        border-left: 5px solid #3182bd;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #1e3a5f !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1a1a2e !important;
        font-weight: 700 !important;
    }

    /* ── Prevention boxes ── */
    .prevention-box {
        background: linear-gradient(135deg, #2c5282 0%, #4a90d9 100%);
        padding: 28px;
        border-radius: 14px;
        color: white !important;
        text-align: center;
        margin: 8px 0;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .prevention-box h2 { color: white !important; margin-bottom: 4px; }
    .prevention-box p  { color: #e8f0fe !important; margin: 4px 0; }
    .prevention-box a  { color: #ffd700 !important; text-decoration: underline; }

    /* ── Typography ── */
    h1 { color: #1e3a5f !important; }
    h2, h3 { color: #2c5282 !important; }
    .source-text { font-size: 0.78em; color: #888; font-style: italic; }

    /* ── Insight boxes ── */
    .insight-box {
        background: #eef6ff;
        border-left: 4px solid #3182bd;
        padding: 12px 18px;
        border-radius: 6px;
        margin: 10px 0;
        color: #1a1a2e !important;
    }

    /* ── Question headers ── */
    .question-header {
        background: linear-gradient(90deg, #f8f9fa 0%, #ffffff 100%);
        padding: 20px 25px;
        border-radius: 12px;
        margin: 30px 0 20px 0;
        border-left: 5px solid #2c5282;
    }
    .question-header h2 {
        margin: 0 !important;
        font-size: 1.5em !important;
        color: #1e3a5f !important;
    }
    .question-header p {
        margin: 8px 0 0 0 !important;
        color: #666 !important;
        font-size: 1em;
    }

    /* ── Intro warning box ── */
    .intro-warning {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border: 2px solid #ff9800;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    .intro-warning h3 { color: #e65100 !important; margin-top: 0; }
    .intro-warning p { color: #333 !important; margin-bottom: 0; }

    /* ── Gender legend ── */
    .gender-legend {
        display: flex;
        gap: 25px;
        margin: 15px 0;
        font-size: 0.95em;
        justify-content: center;
        background: #f5f5f5;
        padding: 12px 20px;
        border-radius: 8px;
        color: #333 !important;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .legend-item span {
        color: #333 !important;
    }
    .legend-color {
        width: 20px;
        height: 20px;
        border-radius: 4px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ─── Helper Functions ─────────────────────────────────────────────────────────
def get_color_scale(selected_genders):
    """Return color scale based on selected genders."""
    domain = []
    colors = []
    if "Hommes" in selected_genders:
        domain.append("Hommes")
        colors.append(COLOR_MEN)
    if "Femmes" in selected_genders:
        domain.append("Femmes")
        colors.append(COLOR_WOMEN)
    if "Hommes et Femmes" in selected_genders or "Tous" in selected_genders:
        domain.append("Tous" if "Tous" in selected_genders else "Hommes et Femmes")
        colors.append(COLOR_ALL)
    return domain, colors


def gender_checkboxes(key_prefix, include_all=True, default_men=True, default_women=True, default_all=False):
    """Create gender filter checkboxes."""
    if include_all:
        cols = st.columns(3)
        with cols[0]:
            show_men = st.checkbox("👨 Hommes", value=default_men, key=f"{key_prefix}_men")
        with cols[1]:
            show_women = st.checkbox("👩 Femmes", value=default_women, key=f"{key_prefix}_women")
        with cols[2]:
            show_all = st.checkbox("👥 Tous", value=default_all, key=f"{key_prefix}_all")
    else:
        cols = st.columns(2)
        with cols[0]:
            show_men = st.checkbox("👨 Hommes", value=default_men, key=f"{key_prefix}_men")
        with cols[1]:
            show_women = st.checkbox("👩 Femmes", value=default_women, key=f"{key_prefix}_women")
        show_all = False

    selected = []
    if show_men:
        selected.append("Hommes")
    if show_women:
        selected.append("Femmes")
    if show_all:
        selected.append("Tous")
    return selected


# ─── Data Loading ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df_sante = pd.read_excel(
        "sante-mentale-pensees-suicidaires-et-tentatives-de-suicide_fra.xlsx"
    )
    df_baro = pd.read_excel(
        "conduites-sucidaires-indicateurs-du-barometre-2024.xlsx"
    )
    df_france = pd.read_excel("suicides-deces-france.xlsx")
    df_dept = pd.read_excel("suicides-deces-departement.xlsx")

    # Standardise column names
    df_france.columns = [
        "Année", "Sexe", "Classe_d_age",
        "Nombre de décès", "Taux brut", "Taux standardisé",
    ]
    df_dept.columns = [
        "Année", "Code", "Département", "Classe_d_age",
        "Sexe", "Nombre de décès", "Taux brut", "Taux standardisé",
    ]
    df_sante.columns = [
        "Année", "Sexe",
        "Taux pensées suicidaires", "PS ic_inf", "PS ic_sup",
        "Taux tentatives 12 mois", "TS12 ic_inf", "TS12 ic_sup",
        "Taux tentatives vie", "TSV ic_inf", "TSV ic_sup",
    ]
    df_baro.columns = [
        "Indicateur", "Année", "Sexe", "Classe_d_age", "Diplôme",
        "Région", "PCS", "Situation financière perçue",
        "Estimation", "ic_inf", "ic_sup", "Effectif",
        "Diff régions", "Chapitre", "Situation professionelle", "Type de ménage", "IC 95%",
    ]

    # Ensure numeric columns
    for col in ["Estimation", "ic_inf", "ic_sup", "Effectif"]:
        df_baro[col] = pd.to_numeric(df_baro[col], errors="coerce")
    for col in ["Nombre de décès", "Taux brut", "Taux standardisé"]:
        df_france[col] = pd.to_numeric(df_france[col], errors="coerce")
        df_dept[col] = pd.to_numeric(df_dept[col], errors="coerce")

    return df_sante, df_baro, df_france, df_dept


@st.cache_data
def load_geojson():
    """Fetch France departments GeoJSON from GitHub."""
    import urllib.request
    url = (
        "https://raw.githubusercontent.com/gregoiredavid/"
        "france-geojson/master/departements.geojson"
    )
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode())


df_sante, df_baro, df_france, df_dept = load_data()

# Load CSV data
df_age_csv = pd.read_csv("df_age.csv")
df_age_csv["Nombre de décès"] = pd.to_numeric(df_age_csv["Nombre de décès"], errors="coerce")
df_age_csv["Taux brut"] = pd.to_numeric(df_age_csv["Taux brut"], errors="coerce")

df_attempt_csv = pd.read_csv("df_attempt_age_sex.csv")
df_attempt_csv["Estimation"] = pd.to_numeric(df_attempt_csv["Estimation"], errors="coerce")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – INTRODUCTION
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("# 🎗️ Prévention du Suicide en France")
st.markdown("### Une analyse des facteurs de risque à travers les données")

st.markdown(
    """
<div class="intro-warning">
    <h3>📞 Besoin d'aide ?</h3>
    <p>Si vous ou une personne de votre entourage traverse une période difficile,
    appelez le <strong>3114</strong> (numéro national de prévention du suicide)
    – gratuit, confidentiel, 24h/24.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
**Objectif de ce dashboard :** Explorer les données publiques sur le suicide en France
pour identifier les facteurs qui peuvent rendre certaines personnes plus vulnérables.

**Question centrale :** *Existe-t-il des facteurs (sexe, âge, situation économique,
territoire) qui rendent certaines personnes plus susceptibles d'avoir des pensées
suicidaires ou de passer à l'acte ?*

Ce dashboard est conçu comme une **enquête progressive** qui vous guidera à travers
les données étape par étape.
"""
)


# Key metrics
df_total = df_france[
    (df_france["Classe_d_age"] == "Tous") & (df_france["Sexe"] == "Hommes et Femmes")
].sort_values("Année")
latest_year = int(df_total["Année"].iloc[-1])
latest_deaths = int(df_total["Nombre de décès"].iloc[-1])

c1, c2, c3 = st.columns(3)
c1.metric("🇫🇷 Décès par suicide en France", f"{latest_deaths:,}".replace(",", " "), f"Année {latest_year}")
c2.metric("🌍 Décès mondiaux / an", "~700 000", "Estimation OMS 2023")
c3.metric("📊 Rang mondial", "4ᵉ cause", "de décès chez les 15-29 ans")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – DIFFERENCES BY SEX
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
<div class="question-header">
    <h2>❓ Le sexe influence-t-il le risque suicidaire ?</h2>
    <p>Commençons par examiner s'il existe une différence significative entre les hommes et les femmes.</p>
</div>
""",
    unsafe_allow_html=True,
)

# Indicator selector for sex analysis
indicator_sex = st.radio(
    "📊 Choisissez l'indicateur à analyser :",
    ["Décès par suicide", "Tentatives de suicide", "Pensées suicidaires"],
    horizontal=True,
    key="indicator_sex"
)

st.markdown("**Filtrer par sexe :**")
selected_sex = gender_checkboxes("sex", include_all=True, default_all=True)

if not selected_sex:
    st.warning("⚠️ Veuillez sélectionner au moins un sexe.")
else:
    if indicator_sex == "Décès par suicide":
        # Deaths by sex over time
        map_sex = {"Hommes": "Hommes", "Femmes": "Femmes", "Tous": "Hommes et Femmes"}
        filter_sex = [map_sex.get(s, s) for s in selected_sex]

        df_plot = df_france[
            (df_france["Classe_d_age"] == "Tous") &
            (df_france["Sexe"].isin(filter_sex))
        ].copy()

        if not df_plot.empty:
            domain, colors = get_color_scale(filter_sex)

            chart = (
                alt.Chart(df_plot)
                .mark_line(point=alt.OverlayMarkDef(size=60), strokeWidth=2.5)
                .encode(
                    x=alt.X("Année:O", title="Année"),
                    y=alt.Y("Nombre de décès:Q", title="Nombre de décès", scale=alt.Scale(zero=True)),
                    color=alt.Color("Sexe:N", scale=alt.Scale(domain=domain, range=colors), legend=alt.Legend(title="Sexe")),
                    tooltip=["Année:O", "Sexe:N", alt.Tooltip("Nombre de décès:Q", format=",")]
                )
                .properties(height=400, title="Évolution du nombre de décès par suicide (2019-2023)")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown(
                '<div class="insight-box">💡 <strong>Observation :</strong> Les hommes représentent '
                'environ <strong>75% des décès</strong> par suicide, soit 3 hommes pour 1 femme. '
                'Ce ratio est stable dans le temps.</div>',
                unsafe_allow_html=True,
            )

    elif indicator_sex == "Tentatives de suicide":
        # Suicide attempts by sex (aggregated) - only take "Tous" for all other columns
        df_attempt_sex = df_baro[
            (df_baro["Indicateur"] == "Tentative de suicide au cours de la vie")
            & ((df_baro["Classe_d_age"] == "Tous") | df_baro["Classe_d_age"].isna())
            & (df_baro["Diplôme"] == "Tous")
            & (df_baro["Situation financière perçue"] == "Tous")
            & ((df_baro["Région"] == "Tous") | df_baro["Région"].isna())
            & ((df_baro["PCS"] == "Tous") | df_baro["PCS"].isna())
            & (df_baro["Sexe"].isin(selected_sex))
            & (df_baro["Situation professionelle"] == "Tous")
            & (df_baro["Type de ménage"] == "Tous")
            
        ].copy()

        if not df_attempt_sex.empty:
            domain, colors = get_color_scale(selected_sex)

            chart = (
                alt.Chart(df_attempt_sex)
                .mark_bar()
                .encode(
                    x=alt.X("Sexe:N", title="Sexe", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Estimation:Q", title="Taux de tentative (%)", scale=alt.Scale(zero=True)),
                    color=alt.Color("Sexe:N", scale=alt.Scale(domain=domain, range=colors), legend=None),
                    tooltip=["Sexe:N", alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f")]
                )
                .properties(height=400, title="Taux de tentatives de suicide au cours de la vie (2024)")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown(
                '<div class="insight-box">💡 <strong>Paradoxe du suicide :</strong> Les femmes déclarent '
                '<strong>plus de tentatives</strong> que les hommes, mais les hommes <strong>décèdent plus</strong>. '
                'Cela s\'explique par l\'utilisation de méthodes plus létales chez les hommes.</div>',
                unsafe_allow_html=True,
            )

    else:  # Pensées suicidaires
        df_thoughts_sex = df_baro[
            (df_baro["Indicateur"] == "Pensées suicidaires au cours des 12 derniers mois")
            & ((df_baro["Classe_d_age"] == "Tous") | df_baro["Classe_d_age"].isna())
            & (df_baro["Diplôme"] == "Tous")
            & (df_baro["Situation financière perçue"] == "Tous")
            & ((df_baro["Région"] == "Tous") | df_baro["Région"].isna())
            & ((df_baro["PCS"] == "Tous") | df_baro["PCS"].isna())
            & (df_baro["Sexe"].isin(selected_sex))
            & (df_baro["Situation professionelle"] == "Tous")
            & (df_baro["Type de ménage"] == "Tous")
            
        ].copy()

        if not df_thoughts_sex.empty:
            domain, colors = get_color_scale(selected_sex)

            chart = (
                alt.Chart(df_thoughts_sex)
                .mark_bar()
                .encode(
                    x=alt.X("Sexe:N", title="Sexe", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Estimation:Q", title="Taux de pensées suicidaires (%)", scale=alt.Scale(zero=True)),
                    color=alt.Color("Sexe:N", scale=alt.Scale(domain=domain, range=colors), legend=None),
                    tooltip=["Sexe:N", alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f")]
                )
                .properties(height=400, title="Taux de pensées suicidaires dans les 12 derniers mois (2024)")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown(
                '<div class="insight-box">💡 <strong>Observation :</strong> Les pensées suicidaires sont '
                'légèrement plus fréquentes chez les femmes, mais la différence est moins marquée que pour les tentatives.</div>',
                unsafe_allow_html=True,
            )

st.markdown('<p class="source-text">Sources : CépiDc–INSERM, Baromètre Santé publique France 2024</p>', unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – DIFFERENCES BY AGE
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
<div class="question-header">
    <h2>❓ L'âge est-il un facteur de risque ?</h2>
    <p>Certaines tranches d'âge sont-elles plus vulnérables que d'autres ?</p>
</div>
""",
    unsafe_allow_html=True,
)

# Note about age ranges
st.info(
    "⚠️ **Note sur les tranches d'âge :** Les données de décès (CépiDc) et les données "
    "d'enquête (Baromètre) utilisent des tranches d'âge différentes. Nous les présentons "
    "telles quelles pour respecter les sources."
)

# Indicator selector for age analysis
indicator_age = st.radio(
    "📊 Choisissez l'indicateur à analyser :",
    ["Décès par suicide", "Tentatives de suicide", "Pensées suicidaires"],
    horizontal=True,
    key="indicator_age"
)

st.markdown("**Filtrer par sexe :**")
selected_age_sex = gender_checkboxes("age", include_all=False)

if not selected_age_sex:
    st.warning("⚠️ Veuillez sélectionner au moins un sexe.")
else:
    if indicator_age == "Décès par suicide":
        AGE_ORDER = ["00-10 ans", "11-14 ans", "15-17 ans", "18-24 ans", "25-44 ans", "45-64 ans", "65-84 ans", "85 ans et plus"]

        df_plot = df_age_csv[df_age_csv["Sexe"].isin(selected_age_sex)].copy()

        if not df_plot.empty:
            domain, colors = get_color_scale(selected_age_sex)

            # Stacked bar chart for deaths
            chart = (
                alt.Chart(df_plot)
                .mark_bar()
                .encode(
                    x=alt.X("Classe_d_age:N", title="Tranche d'âge", sort=AGE_ORDER),
                    y=alt.Y("Nombre de décès:Q", title="Nombre de décès", scale=alt.Scale(zero=True), stack=True),
                    color=alt.Color("Sexe:N", scale=alt.Scale(domain=domain, range=colors), legend=alt.Legend(title="Sexe")),
                    order=alt.Order("Sexe:N", sort="descending"),
                    tooltip=["Classe_d_age:N", "Sexe:N", alt.Tooltip("Nombre de décès:Q", format=","), alt.Tooltip("Taux brut:Q", format=".1f")]
                )
                .properties(height=450, title="Décès par suicide par tranche d'âge (2023)")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown(
                '<div class="insight-box">💡 <strong>Observation :</strong> En nombre absolu, la tranche '
                '<strong>45-64 ans</strong> est la plus touchée. Cependant, le <strong>taux brut</strong> '
                '(pour 100 000 habitants) est particulièrement élevé chez les hommes de 85 ans et plus (75,8/100k).</div>',
                unsafe_allow_html=True,
            )

    elif indicator_age == "Tentatives de suicide":
        BARO_AGE_ORDER = ["18-29 ans", "30-39 ans", "40-49 ans", "50-59 ans", "60-69 ans", "70-79 ans"]

        df_plot = df_attempt_csv[df_attempt_csv["Sexe"].isin(selected_age_sex)].copy()

        if not df_plot.empty:
            domain, colors = get_color_scale(selected_age_sex)

            chart = (
                alt.Chart(df_plot)
                .mark_point(filled=True, size=150)
                .encode(
                    x=alt.X("Classe_d_age:N", title="Tranche d'âge", sort=BARO_AGE_ORDER),
                    y=alt.Y("Estimation:Q", title="Taux de tentative (%)", scale=alt.Scale(zero=True)),
                    color=alt.Color("Sexe:N", scale=alt.Scale(domain=domain, range=colors), legend=alt.Legend(title="Sexe")),
                    tooltip=["Classe_d_age:N", "Sexe:N", alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f")]
                )
                .properties(height=450, title="Tentatives de suicide au cours de la vie par tranche d'âge (2024)")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown(
                '<div class="insight-box">💡 <strong>Observation :</strong> Les <strong>jeunes femmes (18-29 ans)</strong> '
                'présentent le taux de tentative le plus élevé (9,3%). Les femmes ont un taux supérieur aux hommes '
                'dans toutes les tranches d\'âge.</div>',
                unsafe_allow_html=True,
            )

    else:  # Pensées suicidaires
        BARO_AGE_ORDER = ["18-29 ans", "30-39 ans", "40-49 ans", "50-59 ans", "60-69 ans", "70-79 ans"]

        df_thoughts = df_baro[
            (df_baro["Indicateur"] == "Pensées suicidaires au cours des 12 derniers mois")
            & (df_baro["Classe_d_age"].isin(BARO_AGE_ORDER))
            & (df_baro["Diplôme"] == "Tous")
            & (df_baro["Situation financière perçue"] == "Tous")
            & ((df_baro["Région"] == "Tous") | df_baro["Région"].isna())
            & ((df_baro["PCS"] == "Tous") | df_baro["PCS"].isna())
            & (df_baro["Sexe"].isin(selected_age_sex))
        ].copy()

        if not df_thoughts.empty:
            domain, colors = get_color_scale(selected_age_sex)

            # Point chart for suicidal thoughts
            chart = (
                alt.Chart(df_thoughts)
                .mark_point(filled=True, size=150)
                .encode(
                    x=alt.X("Classe_d_age:N", title="Tranche d'âge", sort=BARO_AGE_ORDER),
                    y=alt.Y("Estimation:Q", title="Taux (%)", scale=alt.Scale(zero=True)),
                    color=alt.Color("Sexe:N", scale=alt.Scale(domain=domain, range=colors), legend=alt.Legend(title="Sexe")),
                    tooltip=["Classe_d_age:N", "Sexe:N", alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f")]
                )
                .properties(height=450, title="Pensées suicidaires (12 derniers mois) par tranche d'âge (2024)")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown(
                '<div class="insight-box">💡 <strong>Observation :</strong> Les <strong>18-29 ans</strong> '
                'présentent le taux de pensées suicidaires le plus élevé. Cela souligne l\'importance '
                'de la prévention en milieu étudiant et jeune.</div>',
                unsafe_allow_html=True,
            )

st.markdown('<p class="source-text">Sources : CépiDc–INSERM (décès), Baromètre Santé publique France 2024 (enquête)</p>', unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – SOCIO-ECONOMIC FACTORS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
<div class="question-header">
    <h2>❓ Les facteurs socio-économiques jouent-ils un rôle ?</h2>
    <p>Le niveau d'études, la situation financière et professionnelle influencent-ils le risque suicidaire ?</p>
</div>
""",
    unsafe_allow_html=True,
)

# Factor selector
factor_socio = st.radio(
    "📊 Choisissez le facteur à analyser :",
    ["Niveau de diplôme", "Situation financière", "Type de ménage", "Situation professionnelle", "Type de métiers (PCS)"],
    horizontal=True,
    key="factor_socio"
)

# Indicator selector
indicator_socio = st.radio(
    "📈 Choisissez l'indicateur :",
    ["Tentatives de suicide", "Pensées suicidaires"],
    horizontal=True,
    key="indicator_socio"
)

st.markdown("**Filtrer par sexe :**")
selected_socio_sex = gender_checkboxes("socio", include_all=True, default_all=True, default_men=False, default_women=False)

indicator_name = "Tentative de suicide au cours de la vie" if indicator_socio == "Tentatives de suicide" else "Pensées suicidaires au cours des 12 derniers mois"

if not selected_socio_sex:
    st.warning("⚠️ Veuillez sélectionner au moins un sexe.")
else:
    if factor_socio == "Niveau de diplôme":
        EDU_ORDER = ["< Bac", "Bac", "> Bac"]
        EDU_MAP = {
            "Aucun diplôme ou inférieur au Bac": "< Bac",
            "Bac": "Bac",
            "Supérieur au Bac": "> Bac",
        }

        df_edu = df_baro[
            (df_baro["Indicateur"] == indicator_name)
            & (df_baro["Diplôme"] != "Tous")
            & ((df_baro["Classe_d_age"] == "Tous") | df_baro["Classe_d_age"].isna())
            & (df_baro["Situation financière perçue"] == "Tous")
            & (df_baro["Sexe"].isin(selected_socio_sex))
        ].copy()
        df_edu["Diplôme (court)"] = df_edu["Diplôme"].map(EDU_MAP).fillna(df_edu["Diplôme"])

        if not df_edu.empty:
            domain, colors = get_color_scale(selected_socio_sex)

            chart = (
                alt.Chart(df_edu)
                .mark_bar()
                .encode(
                    x=alt.X("Diplôme (court):N", title="Niveau de diplôme", sort=EDU_ORDER),
                    y=alt.Y("Estimation:Q", title="Taux (%)", scale=alt.Scale(zero=True)),
                    color=alt.Color("Sexe:N", scale=alt.Scale(domain=domain, range=colors), legend=alt.Legend(title="Sexe")),
                    xOffset="Sexe:N",
                    tooltip=["Diplôme:N", "Sexe:N", alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f")]
                )
                .properties(height=420, title=f"{indicator_socio} selon le niveau de diplôme (2024)")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown(
                '<div class="insight-box">💡 <strong>Observation :</strong> Les personnes avec un niveau '
                'd\'études <strong>inférieur au Bac</strong> présentent généralement des taux plus élevés. '
                'L\'éducation semble jouer un rôle protecteur.</div>',
                unsafe_allow_html=True,
            )

    elif factor_socio == "Situation financière":
        FIN_ORDER = ["Difficulté", "C'est juste", "Ça va", "À l'aise"]

        df_fin = df_baro[
            (df_baro["Indicateur"] == indicator_name)
            & (df_baro["Situation financière perçue"] != "Tous")
            & ((df_baro["Classe_d_age"] == "Tous") | df_baro["Classe_d_age"].isna())
            & (df_baro["Diplôme"] == "Tous")
            & (df_baro["Sexe"].isin(selected_socio_sex))
        ].copy()

        # Shorten labels
        FIN_MAP = {}
        for v in df_fin["Situation financière perçue"].unique():
            s = str(v).lower()
            if "difficilement" in s:
                FIN_MAP[v] = "Difficulté"
            elif "aise" in s:
                FIN_MAP[v] = "À l'aise"
            elif "juste" in s:
                FIN_MAP[v] = "C'est juste"
            elif "va" in s:
                FIN_MAP[v] = "Ça va"

        df_fin["Situation (court)"] = df_fin["Situation financière perçue"].map(FIN_MAP).fillna(df_fin["Situation financière perçue"])

        if not df_fin.empty:
            domain, colors = get_color_scale(selected_socio_sex)

            chart = (
                alt.Chart(df_fin)
                .mark_bar()
                .encode(
                    x=alt.X("Situation (court):N", title="Situation financière", sort=FIN_ORDER),
                    y=alt.Y("Estimation:Q", title="Taux (%)", scale=alt.Scale(zero=True)),
                    color=alt.Color("Sexe:N", scale=alt.Scale(domain=domain, range=colors), legend=alt.Legend(title="Sexe")),
                    xOffset="Sexe:N",
                    tooltip=["Situation (court):N", "Sexe:N", alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f")]
                )
                .properties(height=420, title=f"{indicator_socio} selon la situation financière (2024)")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown(
                '<div class="insight-box">💡 <strong>Observation :</strong> Les personnes en '
                '<strong>difficulté financière</strong> ont un taux <strong>3 à 4 fois plus élevé</strong> '
                'que ceux qui sont à l\'aise. La précarité économique est un facteur de risque majeur.</div>',
                unsafe_allow_html=True,
            )

    elif factor_socio == "Type de ménage":
        df_menage = df_baro[
            (df_baro["Indicateur"] == indicator_name)
            & (df_baro["Type de ménage"] != "Tous")
            & ((df_baro["Classe_d_age"] == "Tous") | df_baro["Classe_d_age"].isna())
            & (df_baro["Diplôme"] == "Tous")
            & (df_baro["Situation financière perçue"] == "Tous")
            & (df_baro["Sexe"].isin(selected_socio_sex))
        ].copy()

        if not df_menage.empty:
            domain, colors = get_color_scale(selected_socio_sex)

            chart = (
                alt.Chart(df_menage)
                .mark_bar()
                .encode(
                    x=alt.X("Type de ménage:N", title="Type de ménage", axis=alt.Axis(labelAngle=-30)),
                    y=alt.Y("Estimation:Q", title="Taux (%)", scale=alt.Scale(zero=True)),
                    color=alt.Color("Sexe:N", scale=alt.Scale(domain=domain, range=colors), legend=alt.Legend(title="Sexe")),
                    xOffset="Sexe:N",
                    tooltip=["Type de ménage:N", "Sexe:N", alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f")]
                )
                .properties(height=420, title=f"{indicator_socio} selon le type de ménage (2024)")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown(
                '<div class="insight-box">💡 <strong>Observation :</strong> Le type de ménage peut influencer '
                'le risque suicidaire. Les personnes vivant seules présentent souvent des taux plus élevés.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning("⚠️ Aucune donnée disponible pour cette sélection.")

    elif factor_socio == "Situation professionnelle":
        df_pro = df_baro[
            (df_baro["Indicateur"] == indicator_name)
            & (df_baro["Situation professionelle"] != "Tous")
            & ((df_baro["Classe_d_age"] == "Tous") | df_baro["Classe_d_age"].isna())
            & (df_baro["Diplôme"] == "Tous")
            & (df_baro["Situation financière perçue"] == "Tous")
            & (df_baro["Sexe"].isin(selected_socio_sex))
        ].copy()

        if not df_pro.empty:
            domain, colors = get_color_scale(selected_socio_sex)

            chart = (
                alt.Chart(df_pro)
                .mark_bar()
                .encode(
                    x=alt.X("Situation professionelle:N", title="Situation professionnelle", axis=alt.Axis(labelAngle=-30)),
                    y=alt.Y("Estimation:Q", title="Taux (%)", scale=alt.Scale(zero=True)),
                    color=alt.Color("Sexe:N", scale=alt.Scale(domain=domain, range=colors), legend=alt.Legend(title="Sexe")),
                    xOffset="Sexe:N",
                    tooltip=["Situation professionelle:N", "Sexe:N", alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f")]
                )
                .properties(height=420, title=f"{indicator_socio} selon la situation professionnelle (2024)")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown(
                '<div class="insight-box">💡 <strong>Observation :</strong> La situation professionnelle '
                'a un impact sur le risque suicidaire. Le chômage est souvent associé à des taux plus élevés. Cependant les femmes en étude sont souvent plus vulnérables (tau très élevé).</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning("⚠️ Aucune donnée disponible pour cette sélection.")

    else:  # Type de métiers (PCS)
        df_pcs = df_baro[
            (df_baro["Indicateur"] == indicator_name)
            & (df_baro["PCS"] != "Tous")
            & ((df_baro["Classe_d_age"] == "Tous") | df_baro["Classe_d_age"].isna())
            & (df_baro["Diplôme"] == "Tous")
            & (df_baro["Situation financière perçue"] == "Tous")
            & (df_baro["Sexe"].isin(selected_socio_sex))
        ].copy()

        if not df_pcs.empty:
            domain, colors = get_color_scale(selected_socio_sex)

            chart = (
                alt.Chart(df_pcs)
                .mark_bar()
                .encode(
                    x=alt.X("PCS:N", title="Type de métiers (PCS)", axis=alt.Axis(labelAngle=-45, labelLimit=150)),
                    y=alt.Y("Estimation:Q", title="Taux (%)", scale=alt.Scale(zero=True)),
                    color=alt.Color("Sexe:N", scale=alt.Scale(domain=domain, range=colors), legend=alt.Legend(title="Sexe")),
                    xOffset="Sexe:N",
                    tooltip=["PCS:N", "Sexe:N", alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f")]
                )
                .properties(height=450, title=f"{indicator_socio} selon le type de métiers - PCS (2024)")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            st.markdown(
                '<div class="insight-box">💡 <strong>Observation :</strong> Les catégories socio-professionnelles '
                'présentent des taux variables. Certains métiers peuvent être associés à des risques plus élevés tels que les employés ou ouvriers.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning("⚠️ Aucune donnée disponible pour cette sélection.")

st.markdown('<p class="source-text">Source : Baromètre Santé publique France 2024</p>', unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 – GEOGRAPHIC ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
<div class="question-header">
    <h2>❓ Certains territoires sont-ils plus touchés ?</h2>
    <p>Existe-t-il des disparités géographiques dans les taux de suicide ?</p>
</div>
""",
    unsafe_allow_html=True,
)

# Map controls
col_y, col_s, col_i = st.columns(3)
with col_y:
    year_map = st.slider("Année", min_value=2019, max_value=2023, value=2023, step=1)
with col_s:
    sex_map = st.selectbox("Sexe", ["Hommes et Femmes", "Hommes", "Femmes"])
with col_i:
    indicator_map = st.selectbox("Indicateur", ["Taux brut (pour 100 000)", "Nombre de décès"])

indicator_col = "Taux brut" if "Taux" in indicator_map else "Nombre de décès"

df_map = df_dept[
    (df_dept["Année"] == year_map)
    & (df_dept["Classe_d_age"] == "Tous")
    & (df_dept["Sexe"] == sex_map)
].copy()
df_map = df_map.dropna(subset=[indicator_col])

geojson = load_geojson()

# Color scale based on sex
if sex_map == "Hommes":
    color_scale = "Reds"
elif sex_map == "Femmes":
    color_scale = "Reds"
else:
    color_scale = "Reds"

if not df_map.empty:
    fig_map = px.choropleth(
        df_map,
        geojson=geojson,
        locations="Code",
        featureidkey="properties.code",
        color=indicator_col,
        hover_name="Département",
        hover_data={"Code": True, "Taux brut": ":.1f", "Nombre de décès": True},
        color_continuous_scale=color_scale,
        labels={"Taux brut": "Taux brut (p. 100k)", "Nombre de décès": "Nb décès"},
        title=f"{indicator_map} – {sex_map} ({year_map})",
    )
    fig_map.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig_map.update_layout(
        height=550,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title=indicator_map, thickness=15, len=0.6),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Top/Bottom departments
    col_top, col_bot = st.columns(2)
    with col_top:
        st.markdown("#### 🔴 Départements les plus touchés")
        top5 = df_map.nlargest(5, indicator_col)[["Département", "Taux brut", "Nombre de décès"]].reset_index(drop=True)
        top5.index = top5.index + 1
        st.dataframe(top5, use_container_width=True)
    with col_bot:
        st.markdown("#### 🟢 Départements les moins touchés")
        bot5 = df_map[df_map[indicator_col] > 0].nsmallest(5, indicator_col)[["Département", "Taux brut", "Nombre de décès"]].reset_index(drop=True)
        bot5.index = bot5.index + 1
        st.dataframe(bot5, use_container_width=True)

    st.markdown(
        '<div class="insight-box">💡 <strong>Observation :</strong> On observe de fortes disparités régionales. '
        'Le <strong>Nord et la Bretagne</strong> présentent des taux plus élevés, tandis que '
        'l\'<strong>Île-de-France</strong> affiche des taux plus bas. Ces écarts peuvent s\'expliquer par '
        'des facteurs socio-économiques, culturels et d\'accès aux soins.</div>',
        unsafe_allow_html=True,
    )
else:
    st.warning("Aucune donnée disponible pour cette sélection.")

st.markdown('<p class="source-text">Source : CépiDc–INSERM, traitement Santé publique France</p>', unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 – REGIONAL EVOLUTION
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
<div class="question-header">
    <h2>📈 Analyse détaillée : Évolution par département</h2>
    <p>Comment les taux ont-ils évolué dans différents territoires ?</p>
</div>
""",
    unsafe_allow_html=True,
)

# Department selector
dept_list = sorted(df_dept["Département"].dropna().unique())
selected_depts = st.multiselect(
    "🔍 Sélectionnez les départements à comparer (max 3) :",
    options=dept_list,
    default=["Paris", "Nord", "Finistère"] if all(d in dept_list for d in ["Paris", "Nord", "Finistère"]) else dept_list[:3],
    max_selections=3
)

st.markdown("**Filtrer par sexe :**")
selected_region_sex = gender_checkboxes("region", include_all=False)

if not selected_depts or not selected_region_sex:
    st.warning("⚠️ Veuillez sélectionner au moins un département et un sexe.")
else:
    df_region = df_dept[
        (df_dept["Département"].isin(selected_depts))
        & (df_dept["Classe_d_age"] == "Tous")
        & (df_dept["Sexe"].isin(selected_region_sex))
    ].copy()
    df_region = df_region.dropna(subset=["Taux brut"])

    if not df_region.empty:
        selected_dept_list = list(df_region["Département"].unique())
        dept_dash_values = [[1, 0], [4, 4], [2, 2]]

        # 1. Base commune
        base = alt.Chart(df_region).encode(
            x=alt.X("Année:O", title="Année"),
            y=alt.Y("Taux brut:Q", title="Taux brut (pour 100 000)", scale=alt.Scale(zero=True)),
            color=alt.Color(
                "Sexe:N",
                scale=alt.Scale(domain=["Hommes", "Femmes"], range=[COLOR_MEN, COLOR_WOMEN]),
                legend=alt.Legend(title="Sexe (couleur)")
            )
        )

        # 2. Couche des Lignes (gère le style de trait et la légende des départements)
        lines = base.mark_line(strokeWidth=2.5).encode(
            strokeDash=alt.StrokeDash(
                "Département:N",
                scale=alt.Scale(
                    domain=selected_dept_list[:3],
                    range=dept_dash_values[:len(selected_dept_list)]
                ),
                legend=alt.Legend(
                    title="Département (trait)",
                    symbolType="stroke",     # Force l'affichage d'un trait
                    symbolStrokeColor="#DDD", # Gris clair/blanc pour être visible
                    symbolSize=500,           # Longueur du trait
                    symbolStrokeWidth=2
                )
            )
        )

        # 3. Couche des Points (pour la lecture, sans légende redondante)
        points = base.mark_point(size=50, filled=True).encode(
            # On ne remet pas de strokeDash ici pour ne pas polluer la légende
            tooltip=["Année:O", "Département:N", "Sexe:N", alt.Tooltip("Taux brut:Q", format=".1f")]
        )

        # Fusion des couches
        chart = (lines + points).properties(
            height=450, 
            title="Évolution du taux de suicide par département (2019-2023)"
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

        st.markdown(
            '<div class="insight-box">💡 <strong>Lecture :</strong> La <strong>couleur</strong> indique le sexe '
            '(bleu = hommes, rose = femmes). Le <strong>style de ligne</strong> différencie les départements. '
            'Cela permet de comparer les évolutions entre territoires et entre sexes.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("Aucune donnée disponible pour cette sélection.")

st.markdown('<p class="source-text">Source : CépiDc–INSERM, traitement Santé publique France</p>', unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 – PREVENTION RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## 🤝 Ressources d'aide et de prévention")

st.markdown(
    """
> **Le suicide n'est pas une fatalité.** La prévention est possible et chacun peut agir.
> Si vous ou une personne de votre entourage traverse une période difficile,
> **n'hésitez pas à demander de l'aide**.
"""
)

ca, cb, cc = st.columns(3)
with ca:
    st.markdown(
        """
    <div class="prevention-box">
        <h2>📞 3114</h2>
        <p><strong>Numéro national de prévention du suicide</strong></p>
        <p>Gratuit · Confidentiel · 24h/24 · 7j/7</p>
        <p><a href="https://3114.fr" target="_blank">3114.fr</a></p>
    </div>
    """,
        unsafe_allow_html=True,
    )
with cb:
    st.markdown(
        """
    <div class="prevention-box">
        <h2>💬 Fil Santé Jeunes</h2>
        <p><strong>0 800 235 236</strong></p>
        <p>Écoute anonyme et gratuite pour les 12-25 ans</p>
        <p><a href="https://www.filsantejeunes.com" target="_blank">filsantejeunes.com</a></p>
    </div>
    """,
        unsafe_allow_html=True,
    )
with cc:
    st.markdown(
        """
    <div class="prevention-box">
        <h2>🎓 Nightline</h2>
        <p><strong>Service d'écoute étudiant</strong></p>
        <p>Par et pour les étudiant·es · Gratuit</p>
        <p><a href="https://www.nightline.fr" target="_blank">nightline.fr</a></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
### Autres ressources

| Service | Contact | Description |
|---------|---------|-------------|
| **SOS Amitié** | 09 72 39 40 50 | Écoute 24h/24 pour les personnes en détresse |
| **Suicide Écoute** | 01 45 39 40 00 | Écoute anonyme et confidentielle |
| **En parler** | [enparler.org](https://enparler.org) | Chat en ligne anonyme |
"""
)

st.markdown("---")

st.markdown(
    """
### ⚠️ Avertissement

> Ce dashboard est un **projet pédagogique** réalisé dans le cadre d'un cours
> de Data Visualization (Master MDS / SDI). Les données sont issues de sources
> publiques (Santé publique France, CépiDc–INSERM, OMS).
>
> **Pour toute situation d'urgence, appelez le 3114 ou le 15 (SAMU).**
"""
)

st.markdown(
    """
<div style="text-align:center; color:#666; padding:24px 0 12px 0; font-size:0.85em;">
    Projet Data Visualization – Master MDS / SDI · Données : Santé publique France, CépiDc–INSERM, OMS
</div>
""",
    unsafe_allow_html=True,
)
