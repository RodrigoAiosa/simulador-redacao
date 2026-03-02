import streamlit as st
from groq import Groq
import json
import re
import os

# ── API Key Configuration ────────────────────────────────────────────────────
# Lê a chave API direto dos secrets do Streamlit Cloud
GROQ_API_KEY = st.secrets["groq_api_key"]

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RedaçãoIA · ENEM",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
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

* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--paper) !important;
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--ink);
}

[data-testid="stAppViewContainer"] {
    background-image:
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 27px,
            rgba(180,160,120,0.12) 27px,
            rgba(180,160,120,0.12) 28px
        );
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

/* ─ Hero Header ─ */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
}
.hero::before {
    content: '';
    display: block;
    width: 60px;
    height: 4px;
    background: var(--accent);
    margin: 0 auto 1.5rem;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.4rem, 6vw, 4rem);
    font-weight: 900;
    letter-spacing: -0.02em;
    color: var(--ink);
    margin: 0 0 0.5rem;
    line-height: 1.05;
}
.hero h1 span { color: var(--accent); }
.hero p {
    font-size: 1rem;
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ─ Section labels ─ */
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

/* ─ Cards ─ */
.card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1rem;
    box-shadow: 2px 3px 0 var(--cream);
}

/* ─ Competência card ─ */
.comp-card {
    background: white;
    border-left: 4px solid var(--border);
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
}
.comp-card.excelente { border-left-color: var(--accent2); }
.comp-card.bom       { border-left-color: var(--gold); }
.comp-card.regular   { border-left-color: #d4820a; }
.comp-card.fraco     { border-left-color: var(--accent); }

.comp-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}
.comp-title {
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--ink);
    flex: 1;
}
.comp-score {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--ink);
    min-width: 60px;
    text-align: right;
}
.comp-score span {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    font-weight: 400;
    color: var(--muted);
}
.comp-feedback {
    font-size: 0.85rem;
    color: var(--muted);
    line-height: 1.5;
}

/* ─ Progress bar ─ */
.prog-bg {
    background: var(--cream);
    height: 6px;
    border-radius: 0;
    margin: 0.5rem 0 0.8rem;
    overflow: hidden;
}
.prog-fill {
    height: 100%;
    transition: width 0.6s ease;
}

/* ─ Total score ─ */
.total-score {
    text-align: center;
    padding: 2rem;
    background: var(--ink);
    color: var(--paper);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.total-score::before {
    content: '"';
    font-family: 'Playfair Display', serif;
    font-size: 12rem;
    position: absolute;
    top: -2rem;
    left: 1rem;
    opacity: 0.05;
    line-height: 1;
}
.total-score .label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-bottom: 0.3rem;
}
.total-score .number {
    font-family: 'Playfair Display', serif;
    font-size: 5rem;
    font-weight: 900;
    line-height: 1;
    color: white;
}
.total-score .max {
    font-size: 1.5rem;
    opacity: 0.4;
}
.total-score .nivel {
    margin-top: 0.5rem;
    font-size: 0.9rem;
    opacity: 0.75;
    font-weight: 300;
}

/* ─ Suggestion pills ─ */
.sugg-list { list-style: none; padding: 0; margin: 0; }
.sugg-list li {
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--cream);
    font-size: 0.88rem;
    color: var(--ink);
    display: flex;
    gap: 0.6rem;
    align-items: flex-start;
    line-height: 1.4;
}
.sugg-list li::before {
    content: '→';
    color: var(--accent);
    font-weight: bold;
    flex-shrink: 0;
    margin-top: 0.05rem;
}
.sugg-list li:last-child { border-bottom: none; }

/* ─ Textarea ─ */
.stTextArea textarea {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.92rem !important;
    line-height: 1.8 !important;
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    color: var(--ink) !important;
    padding: 1rem !important;
    caret-color: var(--accent) !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(200,57,10,0.12) !important;
    outline: none !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(200,57,10,0.12) !important;
    outline: none !important;
}
.stTextInput input {
    caret-color: var(--accent) !important;
    color: #000 !important;
}

/* ─ Button ─ */
.stButton > button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.75rem 2.5rem !important;
    width: 100% !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: background 0.2s !important;
}
.stButton > button:hover {
    background: #a02d07 !important;
}

/* ─ Input fields ─ */
.stTextInput input, .stSelectbox select {
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    background: white !important;
    color: #000 !important;
}

/* ─ Word count badge ─ */
.wc-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    padding: 0.2rem 0.6rem;
    background: var(--cream);
    border: 1px solid var(--border);
    color: var(--muted);
    display: inline-block;
    margin-top: 0.3rem;
}
.wc-badge.ok   { border-color: var(--accent2); color: var(--accent2); }
.wc-badge.warn { border-color: #d4820a; color: #d4820a; }
.wc-badge.bad  { border-color: var(--accent); color: var(--accent); }

/* ─ Divider ─ */
.ornament {
    text-align: center;
    color: var(--border);
    font-size: 1.2rem;
    margin: 1.5rem 0;
    letter-spacing: 0.5rem;
}

/* hide streamlit defaults */
#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Helper functions ──────────────────────────────────────────────────────────

def count_words(text: str) -> int:
    return len(text.split()) if text.strip() else 0

def count_lines(text: str) -> int:
    return len([l for l in text.split('\n') if l.strip()])

def score_color_class(score: int) -> str:
    if score >= 160: return "excelente"
    if score >= 120: return "bom"
    if score >= 80:  return "regular"
    return "fraco"

def score_color_hex(score: int) -> str:
    if score >= 160: return "#1a6b3c"
    if score >= 120: return "#b8922a"
    if score >= 80:  return "#d4820a"
    return "#c8390a"

def nivel_texto(total: int) -> str:
    if total >= 900: return "Excelência — desempenho de elite"
    if total >= 750: return "Muito Bom — acima da média"
    if total >= 600: return "Bom — desempenho sólido"
    if total >= 400: return "Regular — há espaço para crescer"
    return "Iniciante — continue praticando!"

def get_feedback_prompt(tema: str, tipo: str, titulo: str, redacao: str) -> str:
    return f"""Você é um professor especialista em redação do ENEM com 15 anos de experiência corrigindo provas. 
Avalie a redação abaixo com rigor e precisão, como na correção oficial do ENEM.

TEMA: {tema}
TÍTULO DA REDAÇÃO: {titulo}
TIPO DE TEXTO: {tipo}

REDAÇÃO DO ALUNO:
---
{redacao}
---

Avalie nas 5 competências do ENEM. Para cada competência, dê uma nota de 0 a 200 (múltiplos de 40: 0, 40, 80, 120, 160, 200).

Responda APENAS com JSON válido, sem nenhum texto antes ou depois:
{{
  "competencias": [
    {{
      "numero": 1,
      "nome": "Domínio da norma culta",
      "nota": <0-200>,
      "feedback": "<2-3 frases específicas sobre o que o aluno fez bem e o que errou>"
    }},
    {{
      "numero": 2,
      "nome": "Compreensão da proposta",
      "nota": <0-200>,
      "feedback": "<2-3 frases específicas>"
    }},
    {{
      "numero": 3,
      "nome": "Seleção e organização de argumentos",
      "nota": <0-200>,
      "feedback": "<2-3 frases específicas>"
    }},
    {{
      "numero": 4,
      "nome": "Coesão e coerência",
      "nota": <0-200>,
      "feedback": "<2-3 frases específicas>"
    }},
    {{
      "numero": 5,
      "nome": "Proposta de intervenção",
      "nota": <0-200>,
      "feedback": "<2-3 frases específicas sobre a proposta: agente, ação, modo/meio, finalidade, detalhamento>"
    }}
  ],
  "nota_total": <soma das 5 notas>,
  "pontos_fortes": ["<ponto forte 1>", "<ponto forte 2>", "<ponto forte 3>"],
  "sugestoes": ["<sugestão 1>", "<sugestão 2>", "<sugestão 3>", "<sugestão 4>"],
  "comentario_geral": "<parágrafo de 3-4 frases resumindo a redação e o desempenho geral>"
}}"""


def avaliar_redacao(tema: str, tipo: str, titulo: str, redacao: str):
    api_key = GROQ_API_KEY
    
    client = Groq(api_key=api_key)
    prompt = get_feedback_prompt(tema, tipo, titulo, redacao)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1500,
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": "Voce e um corretor especialista em redacoes do ENEM. Responda SEMPRE e SOMENTE com JSON valido, sem markdown e sem texto adicional."
            },
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'^```\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


# ── App layout ────────────────────────────────────────────────────────────────

# Hero
st.markdown("""
<div class="hero">
  <h1>Redação<span>IA</span></h1>
  <p>Avaliação inteligente · 5 competências · Estilo ENEM</p>
</div>
""", unsafe_allow_html=True)

# ── Input section ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown('<span class="section-label">01 — Título da Redação</span>', unsafe_allow_html=True)

    titulo = st.text_input(
        label="titulo",
        placeholder="Ex: A inteligência artificial e os desafios da educação brasileira",
        label_visibility="collapsed",
        key="titulo_input"
    )

    st.markdown('<span class="section-label" style="margin-top:1rem;display:block;">02 — Sua Redação</span>', unsafe_allow_html=True)

    redacao = st.text_area(
        label="redacao",
        placeholder="Escreva ou cole sua redação aqui...\n\nLembre-se: a redação dissertativo-argumentativa do ENEM deve ter entre 7 e 30 linhas, com introdução, desenvolvimento (2 parágrafos) e conclusão com proposta de intervenção.",
        height=380,
        label_visibility="collapsed",
        key="redacao_input"
    )

    # Word/line count
    if redacao:
        wc = count_words(redacao)
        lc = count_lines(redacao)
        if lc >= 7:
            badge_class = "ok"
            badge_icon = "✓"
        elif lc >= 4:
            badge_class = "warn"
            badge_icon = "~"
        else:
            badge_class = "bad"
            badge_icon = "!"
        st.markdown(
            f'<span class="wc-badge {badge_class}">{badge_icon} {wc} palavras · {lc} linhas</span>',
            unsafe_allow_html=True
        )

with col_right:
    st.markdown('<span class="section-label">03 — Tipo de Texto</span>', unsafe_allow_html=True)

    tipo = st.selectbox(
        "Tipo de texto",
        ["Dissertativo-Argumentativo (ENEM)", "Narrativo", "Descritivo", "Expositivo"],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-bottom:1rem;">
      <span class="section-label" style="margin-bottom:0.8rem;">Como funciona</span>
      <ul class="sugg-list">
        <li>Informe o título da sua redação</li>
        <li>Escreva sua redação na caixa ao lado</li>
        <li>A IA avalia nas 5 competências do ENEM</li>
        <li>Receba nota estimada e sugestões detalhadas</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    avaliar = st.button("✦ Avaliar Redação")


# ── Result section ────────────────────────────────────────────────────────────

if avaliar:
    if not redacao or len(redacao.strip()) < 50:
        st.error("Por favor, escreva uma redação antes de avaliar.")
    elif not titulo:
        st.error("Informe o título da redação.")
    else:
        st.markdown('<div class="ornament">· · · ·</div>', unsafe_allow_html=True)

        with st.spinner("Analisando sua redação nas 5 competências..."):
            try:
                resultado = avaliar_redacao(titulo, tipo, titulo, redacao)
            except Exception as e:
                st.error(f"❌ Erro ao analisar: {e}")
                st.stop()

        total = resultado.get("nota_total", 0)
        nivel = nivel_texto(total)

        # Total score
        st.markdown(f"""
        <div class="total-score">
          <div class="label">Nota Estimada ENEM</div>
          <div class="number">{total}<span class="max">/1000</span></div>
          <div class="nivel">{nivel}</div>
        </div>
        """, unsafe_allow_html=True)

        # Two columns for results
        res_left, res_right = st.columns([3, 2], gap="large")

        with res_left:
            st.markdown('<span class="section-label">Avaliação por Competência</span>', unsafe_allow_html=True)

            for comp in resultado.get("competencias", []):
                nota = comp["nota"]
                pct = int((nota / 200) * 100)
                cor = score_color_hex(nota)
                css_class = score_color_class(nota)

                st.markdown(f"""
                <div class="comp-card {css_class}">
                  <div class="comp-header">
                    <div class="comp-title">C{comp['numero']} · {comp['nome']}</div>
                    <div class="comp-score">{nota}<span>/200</span></div>
                  </div>
                  <div class="prog-bg">
                    <div class="prog-fill" style="width:{pct}%; background:{cor};"></div>
                  </div>
                  <div class="comp-feedback">{comp['feedback']}</div>
                </div>
                """, unsafe_allow_html=True)

        with res_right:
            # Comentário geral
            st.markdown('<span class="section-label">Comentário Geral</span>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card">
              <p style="font-size:0.88rem; line-height:1.7; color:#3a3530; margin:0;">
                {resultado.get("comentario_geral", "")}
              </p>
            </div>
            """, unsafe_allow_html=True)

            # Pontos fortes
            st.markdown('<span class="section-label" style="margin-top:1rem;display:block;">Pontos Fortes</span>', unsafe_allow_html=True)
            fortes_html = "".join([f"<li>{p}</li>" for p in resultado.get("pontos_fortes", [])])
            st.markdown(f'<div class="card"><ul class="sugg-list">{fortes_html}</ul></div>', unsafe_allow_html=True)

            # Sugestões
            st.markdown('<span class="section-label" style="margin-top:1rem;display:block;">Como Melhorar</span>', unsafe_allow_html=True)
            sugg_html = "".join([f"<li>{s}</li>" for s in resultado.get("sugestoes", [])])
            st.markdown(f'<div class="card"><ul class="sugg-list">{sugg_html}</ul></div>', unsafe_allow_html=True)

        st.markdown('<div class="ornament">✦</div>', unsafe_allow_html=True)
