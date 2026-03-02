import streamlit as st
import json
import re
import requests

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RedaçãoIA · ENEM",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── API KEY ──────────────────────────────────────────────────────────────────
try:
    GROQ_API_KEY = st.secrets["groq_api_key"]
except (KeyError, FileNotFoundError):
    GROQ_API_KEY = None

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --ink: #0f0e0d;
    --paper: #f5f0e8;
    --cream: #ede7d5;
    --accent: #c8390a;
    --accent2: #1a6b3c;
    --gold: #b8922a;
    --muted: #6b6457;
    --border: #d4cabb;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--paper) !important;
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--ink);
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.4rem, 6vw, 4rem);
    font-weight: 900;
    color: var(--ink);
    margin: 0;
}
.hero h1 span { color: var(--accent); }
.hero p {
    font-size: 1rem;
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.4rem;
    display: block;
}

.card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1rem;
    box-shadow: 2px 3px 0 var(--cream);
}

.comp-card {
    background: white;
    border-left: 4px solid var(--border);
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
}
.comp-card.excelente { border-left-color: var(--accent2); }
.comp-card.bom { border-left-color: var(--gold); }
.comp-card.regular { border-left-color: #d4820a; }
.comp-card.fraco { border-left-color: var(--accent); }

.comp-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}
.comp-title {
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--ink);
}
.comp-score {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--ink);
}

.prog-bg {
    background: var(--cream);
    height: 6px;
    margin: 0.5rem 0 0.8rem;
    overflow: hidden;
}
.prog-fill {
    height: 100%;
    transition: width 0.6s ease;
}

.total-score {
    text-align: center;
    padding: 2rem;
    background: var(--ink);
    color: var(--paper);
    margin-bottom: 1.5rem;
}
.total-score .number {
    font-family: 'Playfair Display', serif;
    font-size: 5rem;
    font-weight: 900;
    line-height: 1;
    color: white;
}

/* INPUTS COM TEXTO BRANCO */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    color: white !important;
    background-color: #1a1a1a !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: rgba(255,255,255,0.7) !important;
}

.stButton > button {
    background: var(--accent) !important;
    color: white !important;
}
.stButton > button:hover {
    background: #a02d07 !important;
}

#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────

def count_words(text):
    return len(text.split()) if text.strip() else 0

def count_lines(text):
    return len([l for l in text.split('\n') if l.strip()])

def score_color(score):
    if score >= 160: return ("#1a6b3c", "excelente")
    if score >= 120: return ("#b8922a", "bom")
    if score >= 80: return ("#d4820a", "regular")
    return ("#c8390a", "fraco")

def nivel_texto(total):
    if total >= 900: return "Excelência — desempenho de elite"
    if total >= 750: return "Muito Bom — acima da média"
    if total >= 600: return "Bom — desempenho sólido"
    if total >= 400: return "Regular — há espaço para crescer"
    return "Iniciante — continue praticando!"

def gerar_redacao_nota_maxima(tema):
    if not GROQ_API_KEY:
        raise Exception("Configure a API Key.")

    prompt = f"""
Gere uma redação dissertativo-argumentativa estilo ENEM nota 1000.

Tema: {tema}

Estrutura:
- Introdução
- 2 desenvolvimentos
- Conclusão com proposta de intervenção completa

Apenas o texto.
"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Apenas texto da redação."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1800,
        "temperature": 0.7
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data['choices'][0]['message']['content'].strip()

# ── APP ───────────────────────────────────────────────────────────────────────

st.markdown('<div class="hero"><h1>Redação<span>IA</span></h1><p>Avaliação inteligente · 5 competências · Estilo ENEM</p></div>', unsafe_allow_html=True)

col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown('<span class="section-label">Tema Sugerido</span>', unsafe_allow_html=True)

    tema_sugerido = st.selectbox(
        "Escolha um tema",
        [
            "Saúde mental da juventude na era digital",
            "Regulamentação da Inteligência Artificial no Brasil",
            "Mudanças climáticas e justiça social",
            "Inclusão digital como direito fundamental",
            "Desinformação e democracia no Brasil",
            "Segurança nas escolas e cultura de paz",
            "Desafios da educação pública na redução das desigualdades"
        ],
        label_visibility="collapsed"
    )

    gerar_btn = st.button("✦ Gerar Redação Modelo (Nota Alta)")

    if gerar_btn:
        with st.spinner("Gerando redação..."):
            texto = gerar_redacao_nota_maxima(tema_sugerido)
            st.session_state["titulo"] = tema_sugerido
            st.session_state["redacao"] = texto
            st.session_state["auto_avaliar"] = True
            st.rerun()

    st.markdown('<span class="section-label">01 — Título</span>', unsafe_allow_html=True)
    titulo = st.text_input("Título", value=st.session_state.get("titulo",""), label_visibility="collapsed")

    st.markdown('<span class="section-label" style="margin-top:1rem;">02 — Redação</span>', unsafe_allow_html=True)
    redacao = st.text_area("Redação", value=st.session_state.get("redacao",""), height=320, label_visibility="collapsed")

    if redacao:
        wc = count_words(redacao)
        lc = count_lines(redacao)
        st.caption(f"{wc} palavras · {lc} linhas")

with col_right:
    st.markdown('<span class="section-label">03 — Tipo</span>', unsafe_allow_html=True)
    tipo = st.selectbox("Tipo", ["Dissertativo-Argumentativo (ENEM)"], label_visibility="collapsed")

    avaliar_btn = st.button("✦ Avaliar Redação", use_container_width=True)

# ── AUTO AVALIAÇÃO ───────────────────────────────────────────────────────────

if avaliar_btn or st.session_state.get("auto_avaliar"):
    st.session_state["auto_avaliar"] = False
    st.success("Avaliação iniciada automaticamente.")
