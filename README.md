# RedaçãoIA · ENEM

Avaliação inteligente de redações usando IA (Groq + LLM)

## 🎯 Sobre o Projeto

RedaçãoIA é uma aplicação que utiliza IA para avaliar redações no formato ENEM. O sistema analisa 5 competências:

1. Domínio da norma culta
2. Compreensão da proposta
3. Seleção e organização de argumentos
4. Coesão e coerência
5. Proposta de intervenção

A avaliação fornece uma nota estimada de 0 a 1000 pontos, seguindo o modelo oficial do ENEM.

## 🚀 Deploy no Streamlit Cloud

### Passo 1: Preparar o Repositório GitHub

1. Faça fork deste repositório ou crie um novo
2. Clone o repositório localmente:
```bash
git clone https://github.com/seu-usuario/redacao-ia.git
cd redacao-ia
```

3. Verifique se todos os arquivos estão presentes:
   - `app.py` - Aplicação principal
   - `requirements.txt` - Dependências
   - `.gitignore` - Arquivos a ignorar
   - `README.md` - Este arquivo

### Passo 2: Configurar Variáveis de Ambiente

1. Acesse [Streamlit Cloud](https://share.streamlit.io)
2. Conecte sua conta GitHub
3. Clique em "New app"
4. Selecione seu repositório, branch e o arquivo `app.py`
5. Vá em "Advanced settings" → "Secrets"
6. Adicione sua chave API Groq:
```
groq_api_key = "sua_chave_api_aqui"
```

### Passo 3: Deploy

O deploy será realizado automaticamente quando você fizer push para o repositório.

## 💻 Executar Localmente

### Pré-requisitos
- Python 3.8+
- pip

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/redacao-ia.git
cd redacao-ia
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o arquivo de secrets:
```bash
mkdir -p .streamlit
cp secrets.toml.example .streamlit/secrets.toml
```

5. Edite `.streamlit/secrets.toml` e adicione sua chave API Groq:
```toml
groq_api_key = "gsk_sua_chave_aqui"
```

6. Execute a aplicação:
```bash
streamlit run app.py
```

A aplicação abrirá em `http://localhost:8501`

## 🔑 Obter Chave API Groq

1. Acesse [console.groq.com](https://console.groq.com)
2. Crie uma conta ou faça login
3. Vá em "API Keys"
4. Crie uma nova chave
5. Copie e guarde em local seguro

**Importante:** Nunca compartilhe sua chave API! Use variáveis de ambiente ou secrets.

## 📁 Estrutura do Projeto

```
redacao-ia/
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências Python
├── secrets.toml.example   # Template de secrets (exemplo)
├── .gitignore            # Arquivos a ignorar no Git
└── README.md             # Este arquivo
```

## 🎨 Customizações

### Mudar Cores

As cores estão definidas no CSS dentro de `app.py`. Procure por `:root` e modifique as variáveis:

```css
:root {
    --ink: #0f0e0d;        /* Preto principal */
    --paper: #f5f0e8;      /* Fundo */
    --accent: #c8390a;     /* Cor de destaque */
    /* ... mais cores ... */
}
```

### Mudar Modelo de IA

No arquivo `app.py`, procure por `model="llama-3.3-70b-versatile"` e altere para outro modelo disponível na Groq.

## 🐛 Troubleshooting

### Erro: "Configure sua chave API Groq"
- Verifique se adicionou `groq_api_key` nos secrets do Streamlit Cloud
- Para desenvolvimento local, certifique-se de que `.streamlit/secrets.toml` existe e tem a chave

### Erro: "API key not found"
- Regenere sua chave em [console.groq.com](https://console.groq.com)
- Atualize nos secrets do Streamlit Cloud

### Redação não está sendo analisada
- Certifique-se de que tem pelo menos 50 caracteres
- Verifique se a chave API está ativa

## 📝 Licença

Este projeto está disponível sob a MIT License.

## 👥 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas features
- Enviar pull requests

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.

---

**Desenvolvido com ❤️ para estudantes do ENEM**
