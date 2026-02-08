# 🧪 OpenCngsm v3.3 - Penetration Testing

## Framework de Testes de Segurança

### **Objetivo:**
Validação contínua de segurança através de testes automatizados.

---

## 📁 Estrutura

```
tests/security/
├── test_prompt_injection.py      # Testes de prompt injection
├── test_rate_limiting.py          # Testes de rate limiting
├── test_credential_security.py    # Testes de credenciais
├── test_sandbox_isolation.py      # Testes de sandbox
└── run_pentest.py                 # Executar todos os testes

core/security/
└── pentest_framework.py           # Framework de testes
```

---

## 🧪 Testes Implementados

### **1. Prompt Injection Tests**
- 17 vetores de ataque
- Testa jailbreak, exfiltração, reconhecimento
- Valida sanitização

### **2. Rate Limiting Tests**
- Aplicação de limites
- Isolamento entre usuários
- Janela de tempo

### **3. Credential Security Tests**
- Criptografia AES-256
- Sem vazamento de dados
- Permissões de arquivo

### **4. Sandbox Isolation Tests**
- Network isolation
- Workspace access
- Resource limits

---

## 🚀 Executar Testes

### **Todos os testes:**
```bash
cd tests/security
python run_pentest.py
```

### **Testes individuais:**
```bash
python test_prompt_injection.py
python test_rate_limiting.py
python test_credential_security.py
python test_sandbox_isolation.py
```

---

## 📊 Relatórios

### **Formato Texto:**
```
/tmp/opencngsm_pentest/pentest_report_YYYYMMDD_HHMMSS.txt
```

### **Formato JSON:**
```
/tmp/opencngsm_pentest/pentest_report_YYYYMMDD_HHMMSS.json
```

---

## 🎯 Taxa de Sucesso

- **≥95%:** ✅ EXCELENTE
- **≥80%:** ⚠️ BOM
- **≥60%:** ⚠️ ATENÇÃO
- **<60%:** ❌ CRÍTICO

---

**OpenCngsm v3.3 - Penetration Testing Implementado! 🧪**
