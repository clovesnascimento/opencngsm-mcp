# 🔐 OpenCngsm v3.2 - Security Package

## Phase 1: Critical Security (✅ IMPLEMENTADO)

### 1. **Prompt Injection Filter** (`prompt_filter.py`)
### 2. **Credential Manager** (`credential_manager.py`)
### 3. **Enhanced Docker Sandbox** (`../sandbox/docker_runner.py`)

## Phase 2: High Priority Security (✅ IMPLEMENTADO)

### 4. **Rate Limiter** (`rate_limiter.py`)
Previne abuso de requisições (10 req/min padrão).

### 5. **Input Validator** (`input_validator.py`)
Sanitiza HTML/JavaScript, valida URLs/API keys/e-mails.

### 6. **Audit Logger** (`audit_logger.py`)
Logging seguro com mascaramento automático de credenciais.

---

## 📚 Documentação Completa

Veja `security_implementation_plan.md` para detalhes completos.

## 🧪 Exemplos

- **Phase 1:** `examples/security_examples.py`
- **Phase 2:** `examples/phase2_examples.py`

## 📦 Dependências

```bash
pip install cryptography docker
```

**OpenCngsm v3.2 - Segurança Enterprise! 🔐**
