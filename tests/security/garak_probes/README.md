# 🛡️ G-SEC Custom Garak Probes

Complete set of 10 custom Garak probes for comprehensive G-SEC security testing.

## 📦 **Probes Included**

### **1. gsec_judge_bypass.py** ✅
**Coverage:** 32 prompts  
**Target:** LLM Judge bypass resistance  
**Patterns:**
- Hierarchy framing (ROOT-JUDGE, ROOT-AUTHORITY)
- Calibration attacks
- Self-reference paradoxes
- System prompt extraction
- Override commands

### **2. gsec_config_modification.py** ✅
**Coverage:** 14 prompts  
**Target:** Config file modification protection  
**Patterns:**
- Direct file modification
- Append attacks
- Directory creation
- MCP server injection
- Plugin installation

### **3. gsec_prompt_leaking.py** ✅
**Coverage:** 16 prompts  
**Target:** Prompt leaking protection  
**Patterns:**
- Direct prompt requests
- Internal instructions extraction
- Debug mode framing
- System prompt copying

### **4. gsec_supply_chain_poisoning.py** ✅
**Coverage:** 12 prompts  
**Target:** Supply-chain poisoning protection  
**Patterns:**
- Plugin backdoors
- Skill exfiltration
- MCP server injection
- File system access

### **5. gsec_rce_protection.py** ✅
**Coverage:** 12 prompts  
**Target:** RCE protection  
**Patterns:**
- curl/wget commands
- bash/python execution
- Network exfiltration
- File system modification

### **6. gsec_reflection_advanced.py** 🆕
**Coverage:** 21 prompts  
**Target:** Reflection-based leaking (Stage 11)  
**Patterns:**
- Direct reflection requests
- Verbatim citation
- Internal reasoning extraction
- Auto-audit framing
- Alignment reflection
- Literal phrase copying
- Context extraction
- Multi-turn reflection

### **7. gsec_jailbreak_advanced.py** 🆕
**Coverage:** 30 prompts  
**Target:** Jailbreak/DAN (Stage 12)  
**Patterns:**
- DAN mode variants
- God Mode framing
- Administrative override
- Persona hijacking
- Sandbox deception
- Authority framing
- Ethical bypass

### **8. gsec_meta_template.py** 🆕
**Coverage:** 4 prompts  
**Target:** Meta-template trojan horse  
**Patterns:**
- G-SEC format exploitation
- Addendum framing
- Polyglot injection
- Authority escalation

### **9. gsec_multilingual.py** 🆕
**Coverage:** 20 prompts  
**Target:** Multilingual bypass attempts  
**Patterns:**
- Portuguese variations
- Mixed language attacks
- Unicode obfuscation
- Homoglyph substitution

### **10. gsec_mutation_resistant.py** 🆕
**Coverage:** 15 prompts  
**Target:** Mutation-resistant patterns  
**Patterns:**
- Synonym substitution
- Paraphrasing attacks
- Semantic equivalents
- Framing variations

---

## 📊 **Total Coverage**

| Metric | Value |
|--------|-------|
| **Total Probes** | 10 |
| **Total Prompts** | 172 |
| **Critical Probes** | 4 (Judge, Config, Reflection, Jailbreak) |
| **Languages** | 2 (English + Portuguese) |

---

## 🚀 **Usage**

### **Run All Probes**

```bash
garak \
  --model_type openai \
  --model_name http://localhost:8000/v1 \
  --probes gsec_judge_bypass gsec_config_modification gsec_prompt_leaking gsec_supply_chain_poisoning gsec_rce_protection gsec_reflection_advanced gsec_jailbreak_advanced gsec_meta_template gsec_multilingual gsec_mutation_resistant \
  --report_prefix gsec_full_ \
  --report_format json
```

### **Run Critical Probes Only**

```bash
garak \
  --model_type openai \
  --model_name http://localhost:8000/v1 \
  --probes gsec_judge_bypass gsec_config_modification gsec_reflection_advanced gsec_jailbreak_advanced \
  --report_prefix gsec_critical_ \
  --report_format json
```

### **Run Single Probe**

```bash
garak \
  --model_type openai \
  --model_name http://localhost:8000/v1 \
  --probes gsec_reflection_advanced \
  --report_format json
```

---

## 📈 **Expected Results**

### **Critical Probes (Must be 100%)**
- ✅ gsec_judge_bypass: 100% (32/32)
- ✅ gsec_config_modification: 100% (14/14)
- ✅ gsec_reflection_advanced: 100% (21/21)
- ✅ gsec_jailbreak_advanced: 100% (30/30)

### **Standard Probes (Target ≥70%)**
- ⚠️ gsec_prompt_leaking: ≥70% (target: 80%)
- ⚠️ gsec_supply_chain_poisoning: ≥60% (target: 70%)
- ⚠️ gsec_rce_protection: ≥60% (target: 70%)

### **Advanced Probes (Target ≥80%)**
- ✅ gsec_meta_template: ≥80%
- ✅ gsec_multilingual: ≥80%
- ✅ gsec_mutation_resistant: ≥80%

---

## 🔧 **Integration with Monitoring**

These probes are automatically used by:
- `docker-compose.yml` (Garak runner)
- `gsec_adversarial_monitor.sh` (daily monitoring)
- `.github/workflows/gsec-monitoring.yml` (CI/CD)

---

**Generated:** 2026-02-08  
**Version:** OpenCngsm v3.3  
**Total Prompts:** 172  
**Classification:** 🛡️ **PRODUCTION-GRADE SECURITY++ (MILITARY-GRADE)**
