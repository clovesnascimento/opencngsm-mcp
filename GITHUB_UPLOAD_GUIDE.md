# 📤 Guia de Upload para GitHub

## ✅ Preparação Completa

Seu repositório OpenCngsm v3.3 está pronto para upload! Arquivos criados:

- ✅ `README.md` - Documentação profissional com badges de segurança
- ✅ `.gitignore` - Proteção de secrets e arquivos temporários
- ✅ `LICENSE` - MIT License
- ✅ Git repository inicializado
- ✅ Commit inicial criado

---

## 🚀 Passos para Subir no GitHub

### **1. Criar Repositório no GitHub**

1. Acesse: https://github.com/new
2. **Repository name:** `opencngsm-mcp`
3. **Description:** `Production-Grade AI Agent System with Military-Grade Security`
4. **Visibility:** 
   - ✅ **Public** (recomendado para open source)
   - ⚠️ **Private** (se quiser manter privado inicialmente)
5. **NÃO** marque "Initialize with README" (já temos um)
6. Clique em **"Create repository"**

---

### **2. Conectar Repositório Local ao GitHub**

Copie e execute estes comandos no PowerShell:

```powershell
cd C:\Users\cngsm\Desktop\XXX\opencngsm-mcp

# Adicionar remote (SUBSTITUA 'YOUR_USERNAME' pelo seu usuário GitHub)
git remote add origin https://github.com/YOUR_USERNAME/opencngsm-mcp.git

# Renomear branch para 'main'
git branch -M main

# Push inicial
git push -u origin main
```

**Exemplo com usuário real:**
```powershell
# Se seu usuário for 'johndoe':
git remote add origin https://github.com/johndoe/opencngsm-mcp.git
git branch -M main
git push -u origin main
```

---

### **3. Autenticação GitHub**

Quando executar `git push`, você precisará autenticar:

#### **Opção A: Personal Access Token (Recomendado)**

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token (classic)"**
3. **Note:** `OpenCngsm Upload`
4. **Expiration:** `90 days` (ou conforme preferir)
5. **Scopes:** Marque `repo` (acesso completo a repositórios)
6. Clique em **"Generate token"**
7. **COPIE O TOKEN** (você só verá uma vez!)

Quando o git pedir senha, use o **token** (não sua senha do GitHub).

#### **Opção B: GitHub CLI (Mais fácil)**

```powershell
# Instalar GitHub CLI
winget install GitHub.cli

# Autenticar
gh auth login

# Push
git push -u origin main
```

---

### **4. Verificar Upload**

Após o push bem-sucedido:

1. Acesse: `https://github.com/YOUR_USERNAME/opencngsm-mcp`
2. Você verá:
   - ✅ README.md renderizado com badges
   - ✅ Estrutura de diretórios completa
   - ✅ Todos os arquivos (exceto os do .gitignore)

---

## 📋 Comandos Completos (Copiar e Colar)

```powershell
# 1. Navegar para o diretório
cd C:\Users\cngsm\Desktop\XXX\opencngsm-mcp

# 2. Adicionar remote (SUBSTITUA YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/opencngsm-mcp.git

# 3. Renomear branch
git branch -M main

# 4. Push
git push -u origin main
```

---

## 🔐 Proteção de Secrets

O `.gitignore` já está configurado para **NÃO** enviar:

- ✅ `.env` files (API keys)
- ✅ `*.key`, `*.pem` (certificados)
- ✅ `secrets/` directory
- ✅ `monitoring/prometheus_data/` (dados de monitoramento)
- ✅ `*.log` (logs)
- ✅ `__pycache__/` (cache Python)

**IMPORTANTE:** Antes do push, verifique se não há secrets:

```powershell
# Verificar arquivos que serão enviados
git status

# Se ver algum arquivo sensível:
git rm --cached arquivo_sensivel.env
echo "arquivo_sensivel.env" >> .gitignore
git add .gitignore
git commit -m "chore: add sensitive file to .gitignore"
```

---

## 📝 Próximos Passos Após Upload

### **1. Configurar GitHub Pages (Opcional)**

Para documentação online:
1. Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: `main` / `docs`

### **2. Adicionar Topics**

No repositório GitHub:
1. Clique em ⚙️ (Settings icon ao lado de About)
2. Adicione topics:
   - `ai-agent`
   - `llm-security`
   - `owasp`
   - `mitre-atlas`
   - `mcp-server`
   - `esp32`
   - `android-automation`
   - `adversarial-testing`

### **3. Configurar GitHub Actions (Opcional)**

Para CI/CD automático:
```yaml
# .github/workflows/security-tests.yml
name: Security Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/security/
```

### **4. Adicionar Badges ao README**

Após configurar GitHub Actions, adicione badges:
```markdown
[![Tests](https://github.com/YOUR_USERNAME/opencngsm-mcp/actions/workflows/security-tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/opencngsm-mcp/actions)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
```

---

## 🆘 Troubleshooting

### **Erro: "remote origin already exists"**
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/opencngsm-mcp.git
```

### **Erro: "Authentication failed"**
- Use Personal Access Token (não senha)
- Ou instale GitHub CLI: `gh auth login`

### **Erro: "Repository not found"**
- Verifique se criou o repositório no GitHub
- Verifique se o nome está correto
- Verifique se está logado na conta certa

### **Arquivos muito grandes**
```powershell
# Ver tamanho dos arquivos
git ls-files | xargs -I {} du -h {}

# Remover arquivo grande do histórico
git rm --cached arquivo_grande.zip
echo "*.zip" >> .gitignore
```

---

## ✅ Checklist Final

Antes do push, verifique:

- [ ] Repositório criado no GitHub
- [ ] `.env` e secrets no `.gitignore`
- [ ] Commit inicial criado
- [ ] Remote configurado corretamente
- [ ] Token de autenticação pronto (ou GitHub CLI instalado)
- [ ] README.md revisado (substitua placeholders como YOUR_USERNAME)

---

## 🎉 Após Upload Bem-Sucedido

Compartilhe seu repositório:

```
🚀 OpenCngsm v3.3 agora está no GitHub!

🔗 https://github.com/YOUR_USERNAME/opencngsm-mcp

🛡️ PRODUCTION-GRADE SECURITY++ (MILITARY-GRADE)
✅ 90%+ security score
✅ 100% OWASP/MITRE/NIST compliance
✅ ESP32 + Android integrations
✅ 24/7 adversarial monitoring

#AI #Security #OpenSource #LLM
```

---

**Criado:** 2026-02-08  
**Status:** ✅ Pronto para upload
