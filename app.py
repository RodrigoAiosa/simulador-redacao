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

# ── SESSION STATE ────────────────────────────────────────────────────────────
if "titulo" not in st.session_state:
    st.session_state.titulo = ""

if "redacao" not in st.session_state:
    st.session_state.redacao = ""

if "auto_avaliar" not in st.session_state:
    st.session_state.auto_avaliar = False

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>

/* INPUTS TEXTO BRANCO */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    color: white !important;
    background-color: #1a1a1a !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: rgba(255,255,255,0.6) !important;
}

</style>
""", unsafe_allow_html=True)

# ── FUNÇÕES ───────────────────────────────────────────────────────────────────

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

# ── GERAR REDAÇÃO ────────────────────────────────────────────────────────────
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

# ── AVALIAÇÃO (ORIGINAL) ─────────────────────────────────────────────────────
def get_feedback_prompt(tema, tipo, titulo, redacao):
    return f"""
Você é um professor especialista em redação do ENEM.

TEMA: {tema}
TÍTULO: {titulo}
TIPO: {tipo}

REDAÇÃO:
{redacao}

Avalie nas 5 competências do ENEM.
Responda APENAS com JSON válido.
"""

def avaliar_redacao(tema, tipo, titulo, redacao):
    if not GROQ_API_KEY:
        raise Exception("Configure sua API Key.")

    prompt = get_feedback_prompt(tema, tipo, titulo, redacao)

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Responda APENAS com JSON válido."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.3
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    raw = data['choices'][0]['message']['content'].strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)

    return json.loads(raw)

# ── LAYOUT ───────────────────────────────────────────────────────────────────

st.title("RedaçãoIA")

col_left, col_right = st.columns([3,2])

with col_left:

    st.subheader("Tema Sugerido")

    tema_sugerido = st.selectbox(
        "Escolha um tema",
        [
            "Saúde mental da juventude na era digital",
            "Regulamentação da Inteligência Artificial no Brasil",
            "Mudanças climáticas e justiça social",
            "Inclusão digital como direito fundamental"
        ]
    )

    if st.button("✦ Gerar Redação Modelo"):
        with st.spinner("Gerando redação..."):
            texto = gerar_redacao_nota_maxima(tema_sugerido)
            st.session_state.titulo = tema_sugerido
            st.session_state.redacao = texto
            st.session_state.auto_avaliar = True
            st.rerun()

    st.subheader("Título")
    titulo = st.text_input("Título", value=st.session_state.titulo)

    st.subheader("Redação")
    redacao = st.text_area("Redação", height=300, value=st.session_state.redacao)

with col_right:

    tipo = st.selectbox("Tipo", ["Dissertativo-Argumentativo (ENEM)"])

    avaliar_btn = st.button("✦ Avaliar Redação")

# ── RESULTADOS ───────────────────────────────────────────────────────────────

if avaliar_btn or st.session_state.auto_avaliar:

    st.session_state.auto_avaliar = False

    if not redacao or len(redacao.strip()) < 50:
        st.error("Escreva uma redação com pelo menos 50 caracteres.")
    elif not titulo:
        st.error("Informe o título.")
    else:
        with st.spinner("Analisando..."):
            resultado = avaliar_redacao(titulo, tipo, titulo, redacao)

        total = resultado.get("nota_total", 0)
        st.success(f"Nota estimada: {total}/1000")

        for comp in resultado.get("competencias", []):
            st.write(f"C{comp['numero']} - {comp['nome']}: {comp['nota']}/200")
            st.caption(comp["feedback"])

        st.subheader("Comentário Geral")
        st.write(resultado.get("comentario_geral", ""))

        st.subheader("Pontos Fortes")
        for p in resultado.get("pontos_fortes", []):
            st.write("•", p)

        st.subheader("Melhorar")
        for s in resultado.get("sugestoes", []):
            st.write("•", s)
