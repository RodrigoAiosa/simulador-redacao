# Contribuindo para RedaçãoIA

Obrigado por se interessar em contribuir! 🎉

## 📋 Antes de Começar

1. Faça um fork do projeto
2. Clone sua cópia:
```bash
git clone https://github.com/seu-usuario/redacao-ia.git
cd redacao-ia
```

3. Crie uma branch para sua feature:
```bash
git checkout -b feature/minha-feature
```

## 🔧 Configuração Local

```bash
# Virtual env
python -m venv venv
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure secrets
mkdir -p .streamlit
cp secrets.toml.example .streamlit/secrets.toml
# Edite e adicione sua chave API
```

## 📝 Tipos de Contribuição

### 🐛 Reportar Bugs

Abra uma issue com:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado
- Comportamento atual
- Screenshots (se aplicável)

### 💡 Sugerir Features

Abra uma issue descrevendo:
- Problema que resolve
- Solução proposta
- Exemplos de uso
- Benefícios

### 💻 Pull Requests

1. Faça suas mudanças
2. Teste localmente
3. Commit com mensagens descritivas:
```bash
git commit -m "feat: adiciona suporte para redações narrativas"
```

4. Push para sua branch:
```bash
git push origin feature/minha-feature
```

5. Abra um Pull Request no repositório original

## 📐 Estilo de Código

- Use Python 3.8+
- Siga PEP 8
- Adicione docstrings para funções
- Mantenha o padrão de nomenclatura

## ✨ Melhorias Bem-Vindas

- [ ] Suporte a mais tipos de redação
- [ ] Exportar relatório em PDF
- [ ] Dashboard com histórico
- [ ] Comparação com redações anteriores
- [ ] Tradução para outros idiomas
- [ ] Suporte a outros modelos LLM
- [ ] Testes automatizados

## 📞 Comunicação

- Issues para bugs e features
- Discussions para perguntas gerais
- Pull Requests para código

## 📜 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a MIT License.

---

**Obrigado por contribuir para melhorar RedaçãoIA!** ❤️
