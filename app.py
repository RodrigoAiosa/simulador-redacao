import streamlit as st
import json
import re
import requests
import random

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

if "tema_ia" not in st.session_state:
    st.session_state.tema_ia = ""

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

def gerar_tema_ia():
    if not GROQ_API_KEY:
        raise Exception("Configure a API Key.")

    prompt = """
Gere um único tema inédito para redação do ENEM.
Tema atual, relevante, em formato oficial do ENEM.
Apenas o tema.
"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Apenas o tema."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.8
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data['choices'][0]['message']['content'].strip()


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


def get_feedback_prompt(tema, tipo, titulo, redacao):
    return f"""
Você é um professor especialista em redação do ENEM.

TEMA: {tema}
TÍTULO: {titulo}
TIPO: {tipo}

REDAÇÃO:
{redacao}

Avalie nas 5 competências do ENEM.
Responda APENAS com JSON válido no formato:

{{
"nota_total": 0,
"competencias": [
    {{"numero": 1, "nome": "", "nota": 0, "feedback": ""}},
    {{"numero": 2, "nome": "", "nota": 0, "feedback": ""}},
    {{"numero": 3, "nome": "", "nota": 0, "feedback": ""}},
    {{"numero": 4, "nome": "", "nota": 0, "feedback": ""}},
    {{"numero": 5, "nome": "", "nota": 0, "feedback": ""}}
],
"comentario_geral": "",
"pontos_fortes": [],
"sugestoes": []
}}
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

    temas_fixos = [
        "Saúde mental da juventude na era digital",
        "Regulamentação da Inteligência Artificial no Brasil",
        "Mudanças climáticas e justiça social",
        "Inclusão digital como direito fundamental"
    ]

    opcao = st.selectbox(
        "Escolha um tema",
        ["🎯 Gerar tema automaticamente com IA"] + temas_fixos
    )

    if opcao == "🎯 Gerar tema automaticamente com IA":
        if st.button("Gerar Tema IA"):
            with st.spinner("Gerando tema..."):
                tema_gerado = gerar_tema_ia()
                st.session_state.tema_ia = tema_gerado
                st.success("Tema gerado!")

        if st.session_state.tema_ia:
            st.info(st.session_state.tema_ia)
            tema_sugerido = st.session_state.tema_ia
        else:
            tema_sugerido = ""
    else:
        tema_sugerido = opcao

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
