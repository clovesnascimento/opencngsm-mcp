# 🤖 OpenCngsm v3.3 - Segregated Agents

## Arquitetura de Agentes Segregados

### **Objetivo:**
Separar agentes de leitura e execução para prevenir privilege escalation via prompt injection.

---

## 📁 Componentes

```
core/agents/
├── models.py                    # Modelos de dados (Action, ActionPlan, etc.)
├── reader_agent.py              # Reader Agent (baixo privilégio)
├── executor_agent.py            # Executor Agent (alto privilégio)
├── approval_gateway.py          # Approval Gateway
└── examples/
    └── segregated_agents_example.py  # Exemplos de uso
```

---

## 🤖 1. Reader Agent (Baixo Privilégio)

**Responsabilidades:**
- ✅ Processar inputs do usuário
- ✅ Ler documentos
- ✅ Gerar planos de ação

**Restrições:**
- ❌ NÃO pode executar comandos
- ❌ NÃO pode modificar arquivos
- ❌ NÃO pode acessar credenciais

**Uso:**
```python
from core.agents.reader_agent import ReaderAgent

reader = ReaderAgent(workspace_path)
plan = await reader.process_input(user_input)
```

---

## ⚙️ 2. Executor Agent (Alto Privilégio)

**Responsabilidades:**
- ✅ Executar planos aprovados
- ✅ Acessar credenciais
- ✅ Executar skills

**Restrições:**
- ❌ NÃO processa inputs diretos do usuário

**Uso:**
```python
from core.agents.executor_agent import ExecutorAgent

executor = ExecutorAgent(config_dir, workspace_path)
result = await executor.execute_plan(plan, approved=True, password="xxx")
```

---

## 🔐 3. Approval Gateway

**Responsabilidades:**
- Validar planos de ação
- Determinar se requer aprovação
- Solicitar aprovação do usuário

**Uso:**
```python
from core.agents.approval_gateway import ApprovalGateway

gateway = ApprovalGateway(auto_approve_low_risk=True)

if gateway.requires_approval(plan):
    approved = await gateway.request_approval(plan)
else:
    approved = True
```

---

## 🔄 Fluxo Completo

```
User Input
    ↓
[Prompt Injection Filter]
    ↓
Reader Agent (LOW PRIVILEGE)
    ↓
Action Plan
    ↓
Approval Gateway
    ↓
[User Approval?]
    ↓
Executor Agent (HIGH PRIVILEGE)
    ↓
Result
```

---

## 🧪 Exemplos

```bash
cd core/agents/examples
python segregated_agents_example.py
```

---

**OpenCngsm v3.3 - Agentes Segregados Implementados! 🤖**
