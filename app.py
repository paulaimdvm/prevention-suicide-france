"""
Suicide Prevention Dashboard – France
======================================
MVP data visualization project for the Data Visualization course.
Built with Streamlit, Altair, and Plotly.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json

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

    /* ── Metric cards – ensure dark readable text ── */
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
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #333 !important;
    }

    /* ── Prevention boxes ── */
    .prevention-box {
        background: linear-gradient(135deg, #2c5282 0%, #4a90d9 100%);
        padding: 28px;
        border-radius: 14px;
        color: white !important;
        text-align: center;
        margin: 8px 0;
        min-height: 240px;
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
    .insight-box {
        background: #eef6ff;
        border-left: 4px solid #3182bd;
        padding: 12px 18px;
        border-radius: 6px;
        margin: 10px 0;
        color: #1a1a2e !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


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

    # Standardise column names --------------------------------------------------
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
        "Diff régions", "Chapitre", "Situation pro", "Type ménage", "IC 95%",
    ]

    # Ensure numeric columns are truly numeric ---------------------------------
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

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – INTRODUCTION & GLOBAL CONTEXT
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("# 🎗️ Prévention du Suicide – Tableau de Bord Interactif")
st.markdown(
    "#### Comprendre les risques suicidaires en France à travers les données"
)

st.markdown(
    """
> **Chaque année, plus de 700 000 personnes meurent par suicide dans le monde** (OMS, 2023).
> Le suicide est la **4ᵉ cause de décès** chez les 15‑29 ans à l'échelle mondiale.
>
> En France, **environ 9 000 décès par suicide** sont enregistrés chaque année,
> soit l'un des taux les plus élevés d'Europe occidentale.
> Ce tableau de bord vise à **sensibiliser et informer** en rendant les données accessibles à tous.
"""
)

# ─── Key metrics ────────────────────────────────────────────────────────────────
df_total = df_france[
    (df_france["Classe_d_age"] == "Tous") & (df_france["Sexe"] == "Hommes et Femmes")
].sort_values("Année")

latest_year = int(df_total["Année"].iloc[-1])
latest_deaths = int(df_total["Nombre de décès"].iloc[-1])
latest_rate = df_total["Taux brut"].iloc[-1]

c1, c2, c3, c4 = st.columns(4)
c1.metric("🌍 Décès mondiaux / an", "~700 000", help="Estimation OMS 2023")
c2.metric(
    f"🇫🇷 Décès en France ({latest_year})",
    f"{latest_deaths:,}".replace(",", " "),
)
c3.metric(
    f"📊 Taux brut ({latest_year})",
    f"{latest_rate:.0f}/100k hab",
    help="Pour 100 000 habitants",
)
c4.metric(
    "📞 Numéro national",
    "3114",
    help="Ligne nationale de prévention du suicide – 24 h/24, 7 j/7",
)

st.markdown("---")

# ─── Chart: Evolution of deaths over time (by sex) ─────────────────────────────
st.markdown("## 📈 Évolution des décès par suicide en France")

df_evol = df_france[df_france["Classe_d_age"] == "Tous"].copy()

if df_evol.dropna(subset=["Nombre de décès"]).empty:
    st.warning("⚠️ Aucune donnée disponible pour le graphique d'évolution des décès.")
else:
  chart_evol = (
    alt.Chart(df_evol)
    .mark_line(point=alt.OverlayMarkDef(size=60), strokeWidth=2.5)
    .encode(
        x=alt.X("Année:O", title="Année", axis=alt.Axis(labelAngle=0)),
        y=alt.Y(
            "Nombre de décès:Q",
            title="Nombre de décès",
            scale=alt.Scale(zero=False),
        ),
        color=alt.Color(
            "Sexe:N",
            scale=alt.Scale(
                domain=["Hommes", "Femmes", "Hommes et Femmes"],
                range=["#3182bd", "#e6550d", "#555555"],
            ),
            legend=alt.Legend(title="Sexe"),
        ),
        tooltip=[
            alt.Tooltip("Année:O"),
            alt.Tooltip("Sexe:N"),
            alt.Tooltip("Nombre de décès:Q", format=",.0f"),
            alt.Tooltip("Taux brut:Q", title="Taux brut (p. 100k)", format=".1f"),
        ],
    )
    .properties(
        height=400,
        title="Nombre de décès par suicide en France (2019–2023)",
    )
    .interactive()
  )

  st.altair_chart(chart_evol, use_container_width=True)
  st.markdown(
    '<p class="source-text">Source : CépiDc–INSERM, traitement Santé publique France</p>',
    unsafe_allow_html=True,
  )

# ─── Chart: Deaths by age and sex (latest year) ────────────────────────────────
st.markdown("### 👥 Décès par tranche d'âge et sexe")

AGE_ORDER = [
    "00-10 ans", "11-14 ans", "15-17 ans", "18-24 ans",
    "25-44 ans", "45-64 ans", "65-84 ans", "85 ans et plus",
]

# ✅ Charger depuis CSV
df_age = pd.read_csv("df_age.csv")

# 1. Préparation des données (toujours s'assurer du type numérique)
df_age["Nombre de décès"] = pd.to_numeric(df_age["Nombre de décès"], errors="coerce")
df_age["Taux brut"] = pd.to_numeric(df_age["Taux brut"], errors="coerce")

# 2. Création du graphique empilé
if df_age.dropna(subset=["Nombre de décès"]).empty:
    st.warning("⚠️ Aucune donnée disponible.")
else:
    chart_age = (
        alt.Chart(df_age)
        .mark_bar()
        .encode(
            x=alt.X("Classe_d_age:N", title="Tranche d'âge", sort=AGE_ORDER),
            y=alt.Y("Nombre de décès:Q", title="Total des décès"),
            # C'est la couleur qui crée la superposition automatique
            color=alt.Color(
                "Sexe:N",
                scale=alt.Scale(domain=["Hommes", "Femmes"], range=["#3182bd", "#e6550d"]),
                legend=alt.Legend(title="Sexe")
            ),
            tooltip=[
                alt.Tooltip("Classe_d_age:N"),
                alt.Tooltip("Sexe:N"),
                alt.Tooltip("Nombre de décès:Q", format=",.0f"),
                alt.Tooltip("Taux brut:Q", format=".1f"),
            ],
        )
        .properties(
            height=450,
            title="Décès par suicide cumulés par tranche d'âge et sexe (2023)"
        )
        .interactive()
    )

    st.altair_chart(chart_age, use_container_width=True)

st.markdown(
    '<div class="insight-box">💡 <strong>Constat :</strong> Les hommes représentent '
    "environ <strong>3 décès sur 4</strong> par suicide, un ratio constant au "
    "fil des années. La tranche 45‑64 ans est la plus touchée en nombre absolu.</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – INDICATEURS DU BAROMÈTRE SANTÉ 2024
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## 📊 Indicateurs du Baromètre Santé 2024")
st.markdown(
    """
Les graphiques ci‑dessous proviennent du **Baromètre de Santé publique France 2024**
et portent sur les pensées suicidaires et les tentatives de suicide déclarées
dans la population française de 18 à 85 ans.
"""
)

# ─── Chart 1: Suicide attempt rate by age AND sex (scatter / bubble) ────────────
st.markdown("### 🔴 Taux de tentatives de suicide par tranche d'âge et sexe")

BARO_AGE_ORDER = [
    "18-29 ans", "30-39 ans", "40-49 ans",
    "50-59 ans", "60-69 ans", "70-79 ans",
]

# ✅ Charger depuis CSV
df_attempt_age_sex = pd.read_csv("df_attempt_age_sex.csv")
df_attempt_age_sex["Estimation"] = pd.to_numeric(df_attempt_age_sex["Estimation"], errors="coerce")
df_attempt_age_sex = df_attempt_age_sex.dropna(subset=["Estimation"])

if df_attempt_age_sex.empty:
    st.warning("⚠️ Aucune donnée disponible pour le graphique des tentatives par âge et sexe.")
else:
    chart_attempt = (
        alt.Chart(df_attempt_age_sex)
        .mark_point(filled=True, size=200, opacity=0.85)
        .encode(
            x=alt.X("Classe_d_age:N", title="Tranche d'âge", sort=BARO_AGE_ORDER,
                     axis=alt.Axis(labelAngle=0)),
            y=alt.Y(
                "Estimation:Q",
                title="Taux de tentative de suicide (%)",
                scale=alt.Scale(zero=True),
            ),
            color=alt.Color(
                "Sexe:N",
                scale=alt.Scale(
                    domain=["Hommes", "Femmes"], range=["#3182bd", "#e6550d"]
                ),
                legend=alt.Legend(title="Sexe"),
            ),
            tooltip=[
                alt.Tooltip("Classe_d_age:N", title="Tranche d'âge"),
                alt.Tooltip("Sexe:N"),
                alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f"),
            ],
        )
        .properties(
            height=420,
            title="Tentatives de suicide au cours de la vie – par tranche d'âge et sexe (2024)",
        )
        .interactive()
    )
    st.altair_chart(chart_attempt, use_container_width=True)

st.markdown(
    '<div class="insight-box">💡 <strong>Constat :</strong> Les femmes déclarent un taux de '
    "tentative de suicide <strong>systématiquement supérieur</strong> à celui des hommes, "
    "en particulier chez les <strong>18‑29 ans</strong>.</div>",
    unsafe_allow_html=True,
)

# ─── Chart: Suicidal thoughts by age ────────────────────────────────────────────
st.markdown("### 💭 Pensées suicidaires par tranche d'âge")

# ✅ Charger depuis CSV
df_age_baro = pd.read_csv("df_age_baro.csv")
df_age_baro["Estimation"] = pd.to_numeric(df_age_baro["Estimation"], errors="coerce")
df_age_baro = df_age_baro.dropna(subset=["Estimation"])

if df_age_baro.empty:
    st.warning("⚠️ Aucune donnée disponible pour le graphique des pensées suicidaires par âge.")
else:
    chart_age_baro = (
        alt.Chart(df_age_baro)
        .mark_bar()
        .encode(
            x=alt.X("Classe_d_age:N", title="Tranche d'âge", sort=BARO_AGE_ORDER,
                     axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Estimation:Q", title="Taux (%)", scale=alt.Scale(zero=True)),
            color=alt.Color(
                "Classe_d_age:N",
                scale=alt.Scale(scheme="blues"),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Classe_d_age:N"),
                alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f"),
            ],
        )
        .properties(
            height=420,
            title="Pensées suicidaires (12 derniers mois) par tranche d'âge (2024)",
        )
        .interactive()
    )
    st.altair_chart(chart_age_baro, use_container_width=True)

st.markdown(
    '<div class="insight-box">💡 <strong>Constat :</strong> Les jeunes de '
    "<strong>18‑29 ans</strong> présentent le taux de pensées suicidaires le "
    "plus élevé, soulignant l'importance de la prévention en milieu étudiant.</div>",
    unsafe_allow_html=True,
)

# ─── Chart 2: Suicidal thoughts by financial situation ──────────────────────────
st.markdown("### 💰 Pensées suicidaires selon la Situation financière perçue")

df_fin = df_baro[
    (df_baro["Indicateur"] == "Pensées suicidaires au cours des 12 derniers mois")
    & (df_baro["Situation financière perçue"] != "Tous")
    & (df_baro["Sexe"] == "Tous")
    & ((df_baro["Classe_d_age"] == "Tous") | (df_baro["Classe_d_age"].isna()))
    & (df_baro["Diplôme"] == "Tous")
].copy()
df_fin = df_fin.dropna(subset=["Estimation"])

# Shorten labels for readability – match dynamically to avoid Unicode issues
LABEL_MAP_FIN = {}
for v in df_fin["Situation financière perçue"].unique():
    s = str(v).lower()
    if "difficilement" in s:
        LABEL_MAP_FIN[v] = "Difficulté financière"
    elif "aise" in s:
        LABEL_MAP_FIN[v] = "À l'aise"
    elif "juste" in s:
        LABEL_MAP_FIN[v] = "C'est juste"
    elif "va" in s:
        LABEL_MAP_FIN[v] = "Ça va"

# Ordre logique : de la pire à la meilleure situation financière
LABEL_FIN_ORDER = [
    "Difficulté financière", "C'est juste", "Ça va", "À l'aise",
]

df_fin["Situation (court)"] = (
    df_fin["Situation financière perçue"]
    .map(LABEL_MAP_FIN)
    .fillna(df_fin["Situation financière perçue"])
)

if df_fin.empty:
    st.warning("⚠️ Aucune donnée disponible pour le graphique par Situation financière perçue.")
else:
  chart_fin = (
    alt.Chart(df_fin)
    .mark_bar()
    .encode(
        x=alt.X(
            "Situation (court):N",
            title="Situation financière perçue",
            sort=LABEL_FIN_ORDER,
            axis=alt.Axis(labelAngle=0, labelLimit=160),
        ),
        y=alt.Y(
            "Estimation:Q",
            title="Taux de pensées suicidaires (%)",
            scale=alt.Scale(zero=True),
        ),
        color=alt.Color(
            "Estimation:Q",
            scale=alt.Scale(scheme="orangered"),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("Situation (court):N", title="Situation"),
            alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f"),
            alt.Tooltip("IC 95%:N", title="IC 95 %"),
            alt.Tooltip("Effectif:Q", title="Effectif", format=","),
        ],
    )
    .properties(
        height=420,
        title="Pensées suicidaires selon la Situation financière perçue (2024)",
    )
    .interactive()
  )

  st.altair_chart(chart_fin, use_container_width=True)

st.markdown(
    '<div class="insight-box">💡 <strong>Constat :</strong> Les personnes déclarant '
    "des difficultés financières ont un taux de pensées suicidaires "
    "<strong>nettement supérieur</strong> à celles qui se disent à l'aise.</div>",
    unsafe_allow_html=True,
)

# ─── Chart 3: Suicide attempts by education level  (bubble chart) ───────────────
st.markdown("### 🎓 Tentatives de suicide selon le niveau de diplôme")

EDU_ORDER_SHORT = ["< Bac", "Bac", "> Bac"]

df_edu = df_baro[
    (df_baro["Indicateur"] == "Tentative de suicide au cours de la vie")
    & (df_baro["Diplôme"] != "Tous")
    & (df_baro["Sexe"] == "Tous")
    & ((df_baro["Classe_d_age"] == "Tous") | (df_baro["Classe_d_age"].isna()))
    & (df_baro["Situation financière perçue"] == "Tous")
].copy()
df_edu = df_edu.dropna(subset=["Estimation"])

EDU_SHORT_MAP = {
    "Aucun diplôme ou inférieur au Bac": "< Bac",
    "Bac": "Bac",
    "Supérieur au Bac": "> Bac",
}
df_edu["Diplôme (court)"] = df_edu["Diplôme"].map(EDU_SHORT_MAP).fillna(df_edu["Diplôme"])

if df_edu.empty:
    st.warning("⚠️ Aucune donnée disponible pour le graphique par niveau de diplôme.")
else:
  chart_edu = (
    alt.Chart(df_edu)
    .mark_circle(opacity=0.8)
    .encode(
        x=alt.X(
            "Diplôme (court):N",
            title="Niveau de diplôme",
            sort=EDU_ORDER_SHORT,
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y(
            "Estimation:Q",
            title="Taux de tentatives de suicide (%)",
            scale=alt.Scale(zero=True),
        ),
        size=alt.Size(
            "Effectif:Q",
            scale=alt.Scale(range=[600, 4000]),
            legend=alt.Legend(title="Effectif"),
        ),
        color=alt.Color(
            "Diplôme (court):N",
            scale=alt.Scale(
                domain=EDU_ORDER_SHORT,
                range=["#e74c3c", "#f39c12", "#27ae60"],
            ),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("Diplôme:N", title="Diplôme"),
            alt.Tooltip("Estimation:Q", title="Taux (%)", format=".1f"),
            alt.Tooltip("IC 95%:N", title="IC 95 %"),
            alt.Tooltip("Effectif:Q", title="Effectif", format=","),
        ],
    )
    .properties(
        height=420,
        title="Tentatives de suicide au cours de la vie selon le diplôme (2024)",
    )
    .interactive()
  )

  st.altair_chart(chart_edu, use_container_width=True)

st.markdown(
    '<div class="insight-box">💡 <strong>Constat :</strong> La taille des bulles représente '
    "le nombre de répondants. Le taux de tentative est légèrement plus élevé chez les "
    "titulaires du <strong>Bac</strong> que chez les diplômés du supérieur.</div>",
    unsafe_allow_html=True,
)

# ─── Chart: Historical indicators (sante-mentale dataset) ──────────────────────
st.markdown("### 📉 Évolution des indicateurs suicidaires (2005–2021)")

df_hf = df_sante[df_sante["Sexe"] == "Hommes et Femmes"].copy()

df_melt = df_hf.melt(
    id_vars=["Année", "Sexe"],
    value_vars=[
        "Taux pensées suicidaires",
        "Taux tentatives 12 mois",
        "Taux tentatives vie",
    ],
    var_name="Indicateur",
    value_name="Taux (%)",
)
df_melt = df_melt.dropna(subset=["Taux (%)"])

IND_LABELS = {
    "Taux pensées suicidaires": "Pensées suicidaires (12 mois)",
    "Taux tentatives 12 mois": "Tentatives de suicide (12 mois)",
    "Taux tentatives vie": "Tentatives de suicide (vie entière)",
}
df_melt["Indicateur"] = df_melt["Indicateur"].map(IND_LABELS)

if df_melt.empty:
    st.warning("⚠️ Aucune donnée disponible pour le graphique d'évolution historique.")
else:
  chart_hist = (
    alt.Chart(df_melt)
    .mark_line(point=alt.OverlayMarkDef(size=60), strokeWidth=2.5)
    .encode(
        x=alt.X("Année:O", title="Année", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Taux (%):Q", title="Taux (%)"),
        color=alt.Color(
            "Indicateur:N",
            scale=alt.Scale(
                domain=list(IND_LABELS.values()),
                range=["#e74c3c", "#f39c12", "#3498db"],
            ),
        ),
        tooltip=[
            alt.Tooltip("Année:O"),
            alt.Tooltip("Indicateur:N"),
            alt.Tooltip("Taux (%):Q", format=".2f"),
        ],
    )
    .properties(
        height=400,
        title="Évolution des indicateurs suicidaires – population générale",
    )
    .interactive()
  )

  st.altair_chart(chart_hist, use_container_width=True)

  st.markdown(
    '<p class="source-text">Source : Baromètres de Santé publique France 2005, 2010, 2014, 2017, 2021, 2024</p>',
    unsafe_allow_html=True,
  )

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – INTERACTIVE MAP BY DEPARTMENT  (Plotly choropleth)
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## 🗺️ Carte interactive des décès par suicide par département")
st.markdown(
    """
Explorez les données de mortalité par suicide à l'échelle départementale.
Utilisez les contrôles ci‑dessous pour sélectionner l'année, le sexe et l'indicateur.
"""
)

# ─── Controls ────────────────────────────────────────────────────────────────────
col_y, col_s, col_i = st.columns(3)
with col_y:
    year_map = st.slider("Année", min_value=2019, max_value=2023, value=2023, step=1)
with col_s:
    sex_map = st.selectbox("Sexe", ["Hommes et Femmes", "Hommes", "Femmes"])
with col_i:
    indicator_label = st.selectbox(
        "Indicateur",
        ["Taux brut (pour 100 000)", "Nombre de décès"],
    )

indicator_col = "Taux brut" if "Taux" in indicator_label else "Nombre de décès"

# ─── Filter data ─────────────────────────────────────────────────────────────────
df_map = df_dept[
    (df_dept["Année"] == year_map)
    & (df_dept["Classe_d_age"] == "Tous")
    & (df_dept["Sexe"] == sex_map)
].copy()
df_map = df_map.dropna(subset=[indicator_col])

# ─── Load GeoJSON ────────────────────────────────────────────────────────────────
geojson = load_geojson()

# ─── Build Plotly choropleth ─────────────────────────────────────────────────────
if not df_map.empty:
    fig_map = px.choropleth(
        df_map,
        geojson=geojson,
        locations="Code",
        featureidkey="properties.code",
        color=indicator_col,
        hover_name="Département",
        hover_data={
            "Code": True,
            "Taux brut": ":.1f",
            "Nombre de décès": ":.1f",
            "Taux standardisé": ":.1f",
            "Année": True,
        },
        color_continuous_scale="Reds",
        labels={
            "Taux brut": "Taux brut (p. 100k)",
            "Nombre de décès": "Nb décès",
            "Taux standardisé": "Taux std.",
        },
        title=f"{indicator_label} par département – {sex_map} ({year_map})",
    )
    fig_map.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)",
    )
    fig_map.update_layout(
        height=620,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title=indicator_label,
            thickness=15,
            len=0.6,
        ),
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Aucune donnée disponible pour cette sélection.")

st.markdown(
    '<p class="source-text">Source : CépiDc–INSERM, traitement Santé publique France</p>',
    unsafe_allow_html=True,
)

# ─── Top / Bottom departments ───────────────────────────────────────────────────
if not df_map.empty:
    col_top, col_bot = st.columns(2)
    with col_top:
        st.markdown("#### 🔴 Départements les plus touchés")
        top10 = (
            df_map.nlargest(10, indicator_col)[
                ["Département", "Code", "Nombre de décès", "Taux brut"]
            ]
            .reset_index(drop=True)
        )
        top10.index = top10.index + 1
        st.dataframe(top10, use_container_width=True)
    with col_bot:
        st.markdown("#### 🟢 Départements les moins touchés")
        bot10 = (
            df_map[df_map[indicator_col] > 0]
            .nsmallest(10, indicator_col)[
                ["Département", "Code", "Nombre de décès", "Taux brut"]
            ]
            .reset_index(drop=True)
        )
        bot10.index = bot10.index + 1
        st.dataframe(bot10, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3bis – ÉVOLUTION PAR DÉPARTEMENT (JEUNES 10‑28 ANS)
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## 📊 Évolution des décès par suicide chez les jeunes – par département")
st.markdown(
    """
Sélectionnez un ou plusieurs départements pour visualiser l'évolution du nombre
de décès par suicide chez les **jeunes (0‑24 ans)** entre 2019 et 2023,
détaillée par sexe.  
*(Les tranches d'âge 0‑17 ans et 18‑24 ans sont combinées pour approcher la population jeune.)*
"""
)

# Build dataset for young people (combine 00-17 and 18-24 age groups)
YOUNG_AGES = ["00-17 ans", "18-24 ans"]
df_young = df_dept[
    (df_dept["Classe_d_age"].isin(YOUNG_AGES))
    & (df_dept["Sexe"] != "Hommes et Femmes")
].copy()
df_young["Nombre de décès"] = pd.to_numeric(df_young["Nombre de décès"], errors="coerce")
df_young = df_young.dropna(subset=["Nombre de décès"])

# Aggregate across the two age groups per (Année, Département, Sexe)
df_young_agg = (
    df_young.groupby(["Année", "Code", "Département", "Sexe"], as_index=False)["Nombre de décès"]
    .sum()
)

# Department selector
dept_list = sorted(df_young_agg["Département"].unique())
selected_depts = st.multiselect(
    "🔍 Choisissez un ou plusieurs départements :",
    options=dept_list,
    default=dept_list[:3] if len(dept_list) >= 3 else dept_list,
)

df_young_sel = df_young_agg[df_young_agg["Département"].isin(selected_depts)]

if df_young_sel.empty:
    st.warning("⚠️ Aucune donnée disponible pour la sélection. Essayez d'autres départements.")
else:
    # Create a combined label for color encoding: "Département – Sexe"
    df_young_sel = df_young_sel.copy()
    df_young_sel["Dept – Sexe"] = df_young_sel["Département"] + " – " + df_young_sel["Sexe"]

    # Build line chart
    chart_young = (
        alt.Chart(df_young_sel)
        .mark_line(point=alt.OverlayMarkDef(size=50), strokeWidth=2)
        .encode(
            x=alt.X("Année:O", title="Année", axis=alt.Axis(labelAngle=0)),
            y=alt.Y(
                "Nombre de décès:Q",
                title="Nombre de décès (0‑24 ans)",
                scale=alt.Scale(zero=True),
            ),
            color=alt.Color("Dept – Sexe:N", legend=alt.Legend(title="Département – Sexe")),
            strokeDash=alt.StrokeDash(
                "Sexe:N",
                scale=alt.Scale(domain=["Hommes", "Femmes"], range=[[1, 0], [5, 5]]),
                legend=alt.Legend(title="Sexe"),
            ),
            tooltip=[
                alt.Tooltip("Année:O"),
                alt.Tooltip("Département:N"),
                alt.Tooltip("Sexe:N"),
                alt.Tooltip("Nombre de décès:Q", format=",.0f"),
            ],
        )
        .properties(
            height=450,
            title="Évolution des décès par suicide chez les jeunes (0‑24 ans) par département et sexe",
        )
        .interactive()
    )

    st.altair_chart(chart_young, use_container_width=True)

    st.markdown(
        '<div class="insight-box">💡 <strong>Constat :</strong> Les lignes continues représentent '
        "les <strong>hommes</strong> et les lignes pointillées les <strong>femmes</strong>. "
        "Cela permet de comparer l'évolution entre départements et entre sexes.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="source-text">Source : CépiDc–INSERM, traitement Santé publique France '
        "– tranches d'âge 0‑17 ans et 18‑24 ans combinées</p>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – PREVENTION & HELP RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("## 🤝 Prévention et ressources d'aide")
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
        <p>Gratuit · Confidentiel · 24 h/24 · 7 j/7</p>
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
        <p>Écoute anonyme et gratuite<br/>pour les 12‑25 ans</p>
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
        <p>Par et pour les étudiant·es<br/>Gratuit et confidentiel</p>
        <p><a href="https://www.nightline.fr" target="_blank">nightline.fr</a></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("")
st.markdown(
    """
### Autres ressources

| Service | Contact | Description |
|---------|---------|-------------|
| **SOS Amitié** | 09 72 39 40 50 | Écoute 24 h/24 pour les personnes en détresse |
| **SOS Médecins** | 3624 | Consultation médicale d'urgence |
| **Suicide Écoute** | 01 45 39 40 00 | Écoute anonyme et confidentielle |
| **En parler** | [enparler.org](https://enparler.org) | Chat en ligne anonyme |
"""
)

st.markdown("---")
st.markdown(
    """
### ⚠️ Avertissement

> Ce tableau de bord est un **projet pédagogique** réalisé dans le cadre d'un cours
> de Data Visualization (Master MDS / SDI).
> Les données présentées sont issues de sources publiques
> (Santé publique France, CépiDc–INSERM, OMS).
>
> **Pour toute situation d'urgence, contactez le 3114 ou le 15 (SAMU).**
"""
)

st.markdown(
    """
<div style="text-align:center; color:#666; padding:24px 0 12px 0; font-size:0.85em;">
    Projet Data Visualization – Master MDS / SDI · Données : Santé publique France,
    CépiDc–INSERM, OMS
</div>
""",
    unsafe_allow_html=True,
)
