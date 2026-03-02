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
    border-radius: 0;
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

.stTextInput input {
    color: #000 !important;
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

# ── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

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

def get_feedback_prompt(tema, tipo, titulo, redacao):
    return f"""Você é um professor especialista em redação do ENEM com 15 anos de experiência.
Avalie a redação abaixo com rigor, como na correção oficial do ENEM.

TEMA: {tema}
TÍTULO: {titulo}
TIPO: {tipo}

REDAÇÃO:
---
{redacao}
---

Avalie nas 5 competências do ENEM. Para cada uma, dê nota de 0 a 200 (múltiplos de 40).

Responda APENAS com JSON válido:
{{
  "competencias": [
    {{"numero": 1, "nome": "Domínio da norma culta", "nota": <0-200>, "feedback": "<feedback curto>"}},
    {{"numero": 2, "nome": "Compreensão da proposta", "nota": <0-200>, "feedback": "<feedback curto>"}},
    {{"numero": 3, "nome": "Seleção e organização", "nota": <0-200>, "feedback": "<feedback curto>"}},
    {{"numero": 4, "nome": "Coesão e coerência", "nota": <0-200>, "feedback": "<feedback curto>"}},
    {{"numero": 5, "nome": "Proposta de intervenção", "nota": <0-200>, "feedback": "<feedback curto>"}}
  ],
  "nota_total": <soma>,
  "pontos_fortes": ["<forte1>", "<forte2>", "<forte3>"],
  "sugestoes": ["<sugestão1>", "<sugestão2>", "<sugestão3>", "<sugestão4>"],
  "comentario_geral": "<comentário>"
}}"""

def avaliar_redacao(tema, tipo, titulo, redacao):
    if not GROQ_API_KEY:
        raise Exception("🔑 CONFIGURE SUA CHAVE API!\n\n1. Acesse: https://share.streamlit.io\n2. Seu app → ⋮ → Settings → Secrets\n3. Cole: groq_api_key = \"gsk_sua_chave_aqui\"\n4. Save\n\nDepois tente novamente!")
    
    try:
        prompt = get_feedback_prompt(tema, tipo, titulo, redacao)
        
        # Usar API HTTP do Groq ao invés do SDK (evita erro de proxies)
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Responda APENAS com JSON válido, sem markdown."},
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
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Erro na conexão: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("❌ Erro ao processar resposta. Tente novamente.")
    except Exception as e:
        raise Exception(f"❌ Erro: {str(e)}")

# ── APP LAYOUT ───────────────────────────────────────────────────────────────

st.markdown('<div class="hero"><h1>Redação<span>IA</span></h1><p>Avaliação inteligente · 5 competências · Estilo ENEM</p></div>', unsafe_allow_html=True)

col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown('<span class="section-label" style="color: white;">01 — Título</span>', unsafe_allow_html=True)
    titulo = st.text_input("Título", placeholder="Ex: IA na educação brasileira", label_visibility="collapsed")
    
    st.markdown('<span class="section-label" style="margin-top:1rem;display:block;">02 — Redação</span>', unsafe_allow_html=True)
    redacao = st.text_area("Redação", placeholder="Escreva sua redação aqui...", height=320, label_visibility="collapsed")
    
    if redacao:
        wc = count_words(redacao)
        lc = count_lines(redacao)
        status = "✓" if lc >= 7 else ("~" if lc >= 4 else "!")
        st.caption(f"{status} {wc} palavras · {lc} linhas")

with col_right:
    st.markdown('<span class="section-label">03 — Tipo</span>', unsafe_allow_html=True)
    tipo = st.selectbox("Tipo", ["Dissertativo-Argumentativo (ENEM)", "Narrativo", "Descritivo"], label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
      <span class="section-label">Como funciona</span>
      <ul style="list-style: none; padding: 0; margin: 0;">
        <li>→ Informe o título</li>
        <li>→ Escreva a redação</li>
        <li>→ Escolha o tipo</li>
        <li>→ Clique em Avaliar</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)
    
    avaliar_btn = st.button("✦ Avaliar Redação", use_container_width=True)

# ── RESULTS ──────────────────────────────────────────────────────────────────

if avaliar_btn:
    if not redacao or len(redacao.strip()) < 50:
        st.error("Escreva uma redação com pelo menos 50 caracteres")
    elif not titulo:
        st.error("Informe o título")
    else:
        with st.spinner("Analisando..."):
            try:
                resultado = avaliar_redacao(titulo, tipo, titulo, redacao)
            except Exception as e:
                st.error(f"Erro ao analisar: {e}")
                st.stop()
        
        total = resultado.get("nota_total", 0)
        nivel = nivel_texto(total)
        
        st.markdown(f'<div class="total-score"><div style="font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; opacity: 0.6; margin-bottom: 0.3rem;">Nota Estimada ENEM</div><div class="number">{total}<span style="font-size: 1.5rem; opacity: 0.4;">/1000</span></div><div style="margin-top: 0.5rem; font-size: 0.9rem; opacity: 0.75;">{nivel}</div></div>', unsafe_allow_html=True)
        
        res_left, res_right = st.columns([3, 2], gap="large")
        
        with res_left:
            st.markdown('<span class="section-label">Avaliação</span>', unsafe_allow_html=True)
            for comp in resultado.get("competencias", []):
                nota = comp["nota"]
                cor, classe = score_color(nota)
                pct = int((nota / 200) * 100)
                
                st.markdown(f"""
                <div class="comp-card {classe}">
                  <div class="comp-header">
                    <div class="comp-title">C{comp['numero']} · {comp['nome']}</div>
                    <div class="comp-score">{nota}<span style="font-size: 0.75rem; font-weight: 400; color: #6b6457;">/200</span></div>
                  </div>
                  <div class="prog-bg">
                    <div class="prog-fill" style="width:{pct}%; background:{cor};"></div>
                  </div>
                  <div style="font-size: 0.85rem; color: #6b6457; line-height: 1.5;">{comp['feedback']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with res_right:
            st.markdown('<span class="section-label">Comentário</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="card"><p style="font-size:0.88rem; line-height:1.7; margin:0;">{resultado.get("comentario_geral", "")}</p></div>', unsafe_allow_html=True)
            
            st.markdown('<span class="section-label" style="margin-top:1rem;display:block;">Pontos Fortes</span>', unsafe_allow_html=True)
            fortes = resultado.get("pontos_fortes", [])
            st.markdown(f'<div class="card">{"".join([f"<div style=\"padding:0.5rem 0; border-bottom:1px solid var(--cream);\">→ {p}</div>" for p in fortes])}</div>', unsafe_allow_html=True)
            
            st.markdown('<span class="section-label" style="margin-top:1rem;display:block;">Melhorar</span>', unsafe_allow_html=True)
            sugg = resultado.get("sugestoes", [])
            st.markdown(f'<div class="card">{"".join([f"<div style=\"padding:0.5rem 0; border-bottom:1px solid var(--cream);\">→ {s}</div>" for s in sugg])}</div>', unsafe_allow_html=True)
