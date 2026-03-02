import streamlit as st
import json
import re
import requests

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RedaçãoIA · ENEM",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# API KEY
# ─────────────────────────────────────────────
try:
    GROQ_API_KEY = st.secrets["groq_api_key"]
except Exception:
    GROQ_API_KEY = None

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "titulo" not in st.session_state:
    st.session_state.titulo = ""

if "redacao" not in st.session_state:
    st.session_state.redacao = ""

if "auto_avaliar" not in st.session_state:
    st.session_state.auto_avaliar = False

# ─────────────────────────────────────────────
# CSS PERSONALIZADO
# ─────────────────────────────────────────────
st.markdown("""
<style>

/* Texto branco nas caixas */
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

# ─────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────

def gerar_fallback_erro(mensagem):
    return {
        "nota_total": 0,
        "competencias": [
            {"numero": 1, "nome": "Domínio da Norma Culta", "nota": 0, "feedback": mensagem},
            {"numero": 2, "nome": "Compreensão do Tema", "nota": 0, "feedback": mensagem},
            {"numero": 3, "nome": "Argumentação", "nota": 0, "feedback": mensagem},
            {"numero": 4, "nome": "Coesão e Coerência", "nota": 0, "feedback": mensagem},
            {"numero": 5, "nome": "Proposta de Intervenção", "nota": 0, "feedback": mensagem}
        ],
        "comentario_geral": "Não foi possível analisar automaticamente.",
        "pontos_fortes": [],
        "sugestoes": []
    }

def gerar_redacao_nota_maxima(tema):
    if not GROQ_API_KEY:
        raise Exception("Configure a API Key no secrets.")

    prompt = f"""
Gere uma redação dissertativo-argumentativa modelo ENEM nota 1000.

Tema: {tema}

Estrutura:
- Introdução
- Dois parágrafos de desenvolvimento
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
            {"role": "system", "content": "Responda apenas com o texto da redação."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1800,
        "temperature": 0.7
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()

def get_feedback_prompt(tema, tipo, titulo, redacao):
    return f"""
Você é um professor especialista em correção de redação do ENEM.

TEMA: {tema}
TÍTULO: {titulo}
TIPO: {tipo}

REDAÇÃO:
{redacao}

Avalie nas 5 competências do ENEM (0 a 200 cada).
Retorne apenas JSON no formato:

{{
  "nota_total": 0-1000,
  "competencias": [
    {{"numero": 1, "nome": "", "nota": 0-200, "feedback": ""}},
    {{"numero": 2, "nome": "", "nota": 0-200, "feedback": ""}},
    {{"numero": 3, "nome": "", "nota": 0-200, "feedback": ""}},
    {{"numero": 4, "nome": "", "nota": 0-200, "feedback": ""}},
    {{"numero": 5, "nome": "", "nota": 0-200, "feedback": ""}}
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
            {"role": "system", "content": "Responda apenas com JSON válido."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.2
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    raw = data["choices"][0]["message"]["content"].strip()

    # Extrai apenas o JSON
    match = re.search(r'\{.*\}', raw, re.DOTALL)

    if not match:
        return gerar_fallback_erro("Resposta fora do padrão JSON.")

    json_text = match.group(0)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return gerar_fallback_erro("Erro ao decodificar JSON da IA.")

# ─────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────

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
    redacao = st.text_area("Redação", height=350, value=st.session_state.redacao)

with col_right:

    tipo = st.selectbox("Tipo", ["Dissertativo-Argumentativo (ENEM)"])
    avaliar_btn = st.button("✦ Avaliar Redação")

# ─────────────────────────────────────────────
# RESULTADO
# ─────────────────────────────────────────────

if avaliar_btn or st.session_state.auto_avaliar:

    st.session_state.auto_avaliar = False

    if not redacao or len(redacao.strip()) < 50:
        st.error("Escreva uma redação com pelo menos 50 caracteres.")
    elif not titulo:
        st.error("Informe o título.")
    else:
        with st.spinner("Analisando redação..."):
            resultado = avaliar_redacao(tema_sugerido, tipo, titulo, redacao)

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

        st.subheader("Sugestões de Melhoria")
        for s in resultado.get("sugestoes", []):
            st.write("•", s)
