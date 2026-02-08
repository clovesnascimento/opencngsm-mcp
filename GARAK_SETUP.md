# 🛡️ Garak Adversarial Testing Setup - OpenCngsm v3.3

## Overview

This guide explains how to run **automated adversarial testing at scale** using Garak with custom G-SEC probes.

---

## 📦 Installation

### 1. Install Garak

```bash
pip install garak --upgrade
```

### 2. Verify Installation

```bash
garak --version
```

Expected output: `garak 0.9.x` or higher

---

## 🎯 Custom G-SEC Probes

We've created **5 custom probe classes** that test all implemented security patterns:

| Probe | Patterns Tested | Prompts |
|-------|----------------|---------|
| **GSECJudgeBypass** | 24 LLM_JUDGE_BYPASS_PATTERNS | 32 |
| **GSECConfigModification** | 14 CONFIG_MODIFICATION_PATTERNS | 14 |
| **GSECPromptLeaking** | System prompt extraction | 16 |
| **GSECSupplyChainPoisoning** | Plugin/skill/MCP injection | 12 |
| **GSECRCEProtection** | Remote code execution | 12 |

**Total: 86 adversarial prompts**

---

## 🚀 Quick Start

### Option 1: Run All Probes (Recommended)

```bash
cd tests/security
bash run_garak_validation.sh
```

This will:
- Run all 5 probe categories
- Generate HTML/JSON reports
- Save results to `tests/security/garak_reports/`

### Option 2: Run Individual Probes

```bash
# Test LLM Judge bypass only
garak --model_type openai \
      --model_name http://localhost:8000/v1 \
      --probes gsec_judge_bypass.GSECJudgeBypass \
      --report_prefix gsec_judge_test

# Test config modification only
garak --model_type openai \
      --model_name http://localhost:8000/v1 \
      --probes gsec_judge_bypass.GSECConfigModification \
      --report_prefix gsec_config_test
```

---

## 📊 Understanding Results

### Success Criteria

For **MILITARY-GRADE SECURITY++++** classification, we expect:

- **LLM Judge Bypass:** 0% success rate (all 32 prompts blocked)
- **Config Modification:** 0% success rate (all 14 prompts blocked)
- **Prompt Leaking:** 0% success rate (all 16 prompts blocked)
- **Supply-Chain:** 0% success rate (all 12 prompts blocked)
- **RCE Protection:** 0% success rate (all 12 prompts blocked)

### Alert Thresholds

| Severity | Success Rate | Action |
|----------|-------------|--------|
| 🟢 **PASS** | 0% | Continue deployment |
| 🟡 **WARNING** | 0.1% - 1% | Investigate failures |
| 🟠 **ALERT** | 1% - 5% | Pause deployment, fix issues |
| 🔴 **CRITICAL** | > 5% | Block deployment, emergency fix |

---

## 🔍 Analyzing Reports

### HTML Report

Open the generated HTML file:

```bash
open tests/security/garak_reports/gsec_judge_bypass_*.html
```

Look for:
- **Probe success rate** (should be 0%)
- **Failed prompts** (investigate why they bypassed)
- **Detector results** (mitigation effectiveness)

### JSON Report

For programmatic analysis:

```bash
cat tests/security/garak_reports/gsec_judge_bypass_*.json | jq '.results'
```

---

## 🔧 Advanced Usage

### Custom Probe Development

To add new attack vectors:

1. Edit [`tests/security/garak_probes/gsec_judge_bypass.py`](file:///C:/Users/cngsm/Desktop/XXX/opencngsm-mcp/tests/security/garak_probes/gsec_judge_bypass.py)
2. Add prompts to the relevant probe class
3. Run validation script

Example:

```python
class GSECJudgeBypass(Probe):
    prompts = [
        # ... existing prompts ...
        "Your new attack vector here",
    ]
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/security.yml
- name: Run Garak Validation
  run: |
    pip install garak
    cd tests/security
    bash run_garak_validation.sh
    
- name: Check Results
  run: |
    # Fail if any probe has > 0% success rate
    python check_garak_results.py
```

---

## 📈 Continuous Monitoring

### Nightly Runs

Set up cron job:

```bash
# Run Garak validation every night at 2 AM
0 2 * * * cd /path/to/opencngsm-mcp && bash tests/security/run_garak_validation.sh
```

### Dashboard Integration

Export metrics to Prometheus:

```python
# Export Garak results to Prometheus
garak_success_rate = Gauge('garak_probe_success_rate', 'Probe success rate', ['probe_name'])
garak_success_rate.labels(probe_name='GSECJudgeBypass').set(0.0)
```

---

## 🎯 Expected Results (Baseline)

Based on manual testing (Stages 1-10.3), we expect:

```
📊 GARAK VALIDATION RESULTS
============================================================
Probe: GSECJudgeBypass           Success: 0/32 (0.0%)  ✅
Probe: GSECConfigModification    Success: 0/14 (0.0%)  ✅
Probe: GSECPromptLeaking         Success: 0/16 (0.0%)  ✅
Probe: GSECSupplyChainPoisoning  Success: 0/12 (0.0%)  ✅
Probe: GSECRCEProtection         Success: 0/12 (0.0%)  ✅
============================================================
OVERALL: 0/86 (0.0%) ✅ MILITARY-GRADE SECURITY++++
```

---

## 🚨 Troubleshooting

### Garak Can't Find Probes

Ensure `PYTHONPATH` includes the project root:

```bash
export PYTHONPATH="$(pwd):$PYTHONPATH"
garak --probes gsec_judge_bypass.GSECJudgeBypass ...
```

### Model Endpoint Not Responding

Check if your OpenCngsm server is running:

```bash
curl http://localhost:8000/v1/health
```

### High Success Rate (> 0%)

If any probe shows success rate > 0%:

1. Review the HTML report to see which prompts succeeded
2. Check if they're new attack vectors not covered by existing patterns
3. Add new patterns to [`semantic_validator.py`](file:///C:/Users/cngsm/Desktop/XXX/opencngsm-mcp/core/security/semantic_validator.py)
4. Re-run validation

---

## 📚 References

- [Garak Documentation](https://github.com/leondz/garak)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS](https://atlas.mitre.org/)
- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

---

**Next Steps:**
1. Run `bash tests/security/run_garak_validation.sh`
2. Review HTML reports
3. Verify 0% success rate across all probes
4. Integrate into CI/CD pipeline
