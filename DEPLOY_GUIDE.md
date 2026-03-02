# 🚀 Guia Rápido: Deploy RedaçãoIA no Streamlit Cloud

## ⚡ 5 Passos para Deploy

### 1️⃣ Prepare seu GitHub
```bash
# Clone ou crie seu repositório
git clone https://github.com/seu-usuario/redacao-ia.git
cd redacao-ia

# Se for repositório novo:
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/seu-usuario/redacao-ia.git
git push -u origin main
```

### 2️⃣ Obtenha sua Chave Groq
1. Vá para https://console.groq.com
2. Login/Register
3. Clique em "API Keys"
4. Crie uma nova chave (gsk_...)
5. **Copie e guarde em local seguro**

### 3️⃣ Acesse Streamlit Cloud
1. Vá para https://share.streamlit.io
2. Login com sua conta GitHub
3. Clique em "New app"

### 4️⃣ Configure o Deployment
1. **Repository:** selecione seu repositório
2. **Branch:** main (ou a branch que quer)
3. **Main file path:** app.py
4. Clique em "Deploy!"

### 5️⃣ Configure os Secrets
1. Aguarde o app carregar
2. Clique no **⋮** (três pontos) → Settings
3. Vá em "Secrets" 
4. Cole:
```
groq_api_key = "gsk_sua_chave_aqui"
```
5. Salve e o app vai recarregar automaticamente

## ✅ Pronto!

Seu app está no ar! A URL será algo como:
```
https://seu-usuario-redacao-ia.streamlit.app
```

## 🔄 Atualizar o App

Toda vez que você fizer push no GitHub:
```bash
git add .
git commit -m "Descrição da mudança"
git push origin main
```

O Streamlit Cloud detecta a mudança automaticamente e faz redeploy!

## 🛠️ Para Desenvolvimento Local

```bash
# 1. Crie virtual env
python -m venv venv
source venv/bin/activate  # ou: venv\Scripts\activate (Windows)

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure secrets
mkdir -p .streamlit
cp secrets.toml.example .streamlit/secrets.toml
# Edite o arquivo e adicione sua chave

# 4. Execute
streamlit run app.py
```

## ⚠️ Segurança

- **NUNCA** coloque a chave API no código
- **NUNCA** commit `.streamlit/secrets.toml`
- Sempre use variáveis de ambiente ou secrets do Streamlit
- A chave em `app.py` é carregada automaticamente dos secrets

## 📱 Tecnologias

- **Streamlit** - Framework web
- **Groq API** - LLM (Llama 3.3 70B)
- **Python** - Linguagem

## 🎓 Modelo Educacional

O app avalia 5 competências do ENEM:
1. Domínio da norma culta
2. Compreensão da proposta
3. Seleção e organização de argumentos
4. Coesão e coerência
5. Proposta de intervenção

Nota: 0-1000 pontos (como no ENEM real)

---

Dúvidas? Abra uma issue no GitHub! 🤓
