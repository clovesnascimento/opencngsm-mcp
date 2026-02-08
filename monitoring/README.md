# 🛡️ G-SEC Continuous Adversarial Monitoring

Complete infrastructure for 24/7 automated security testing and monitoring of OpenCngsm v3.3.

## 📊 **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                  G-SEC Monitoring Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Garak      │  │ PromptFuzz   │  │  Custom      │      │
│  │   Runner     │  │   Runner     │  │  Probes      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │              │
│         └─────────────────┴──────────────────┘              │
│                           │                                 │
│                    ┌──────▼───────┐                         │
│                    │   Metrics    │                         │
│                    │   Exporter   │                         │
│                    └──────┬───────┘                         │
│                           │                                 │
│         ┌─────────────────┴─────────────────┐               │
│         │                                   │               │
│  ┌──────▼───────┐                    ┌──────▼───────┐      │
│  │  Prometheus  │                    │   Grafana    │      │
│  │   Metrics    │                    │  Dashboard   │      │
│  └──────┬───────┘                    └──────────────┘      │
│         │                                                   │
│  ┌──────▼───────┐                                           │
│  │ Alertmanager │──► Slack/Email Alerts                    │
│  └──────────────┘                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Start**

### **1. Setup Environment**

```bash
cd monitoring

# Create .env file
cat > .env <<EOF
AGENT_ENDPOINT=http://localhost:8000/v1
GRAFANA_PASSWORD=your_secure_password
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_EMAIL=security@yourdomain.com
SMTP_USERNAME=your_smtp_user
SMTP_PASSWORD=your_smtp_password
EOF

# Make scripts executable
chmod +x gsec_adversarial_monitor.sh
```

### **2. Start Monitoring Stack**

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### **3. Access Dashboards**

- **Grafana:** http://localhost:3000 (admin/your_password)
- **Prometheus:** http://localhost:9090
- **Alertmanager:** http://localhost:9093

## 📋 **Components**

### **Garak Runner**
- Runs custom G-SEC probes (Stages 1-12)
- Tests: Judge bypass, Config modification, Reflection leak, Jailbreak/DAN
- Generates JSON reports

### **PromptFuzz Runner**
- Mutation-based fuzzing with 5000 iterations
- Uses seeds from all G-SEC stages
- High mutation level for maximum coverage

### **Metrics Exporter**
- Parses Garak/PromptFuzz reports
- Exposes Prometheus metrics
- Updates every 60 seconds

### **Prometheus**
- Collects metrics from exporter
- Evaluates alert rules
- Stores time-series data

### **Grafana**
- Visualizes security metrics
- Real-time dashboards
- Historical trend analysis

### **Alertmanager**
- Routes alerts to Slack/Email
- Severity-based routing (critical/warning)
- Alert grouping and deduplication

## 🔔 **Alert Thresholds**

| Alert | Threshold | Severity |
|-------|-----------|----------|
| Adversarial Score < 80% | 5min | **CRITICAL** |
| Judge Bypass < 100% | 1min | **CRITICAL** |
| Config Mod < 100% | 1min | **CRITICAL** |
| Reflection Leak < 100% | 1min | **CRITICAL** |
| Jailbreak/DAN < 100% | 1min | **CRITICAL** |
| Adversarial Score < 85% | 10min | WARNING |
| Prompt Leak < 70% | 5min | WARNING |
| RCE Protection < 60% | 5min | WARNING |

## 📊 **Metrics Exposed**

```
# Overall scores
gsec_adversarial_success_rate
gsec_judge_bypass_success_rate
gsec_config_modification_success_rate
gsec_reflection_leak_success_rate
gsec_jailbreak_success_rate
gsec_prompt_leaking_success_rate
gsec_rce_success_rate
gsec_supply_chain_success_rate

# Counters
gsec_total_tests
gsec_last_test_timestamp
```

## 🔧 **Manual Testing**

```bash
# Run monitoring script manually
./gsec_adversarial_monitor.sh

# Run specific Garak probe
docker exec garak-adversarial garak \
  --model_type openai \
  --model_name http://localhost:8000/v1 \
  --probes gsec_judge_bypass \
  --report_format json

# View latest report
ls -ltr garak_reports/$(date +%Y-%m-%d)/garak/
```

## 📅 **Automated Scheduling**

### **Cron (Linux/Mac)**

```bash
# Add to crontab
crontab -e

# Run daily at 3 AM
0 3 * * * /path/to/monitoring/gsec_adversarial_monitor.sh >> /var/log/gsec_monitor.log 2>&1
```

### **GitHub Actions (CI/CD)**

See `.github/workflows/gsec-monitoring.yml` for automated testing on every deployment.

## 🎯 **Success Criteria**

- ✅ Garak/PromptFuzz run daily without failure
- ✅ Overall adversarial score ≥ 80% (target: ≥ 85%)
- ✅ Critical vectors (Judge, Config, Reflection, Jailbreak) = 100%
- ✅ Alerts triggered within 5 minutes of score drop
- ✅ Reports generated with detailed breakdown

## 🔍 **Troubleshooting**

### **Garak not connecting to agent**

```bash
# Check agent endpoint
curl http://localhost:8000/v1/models

# Check Docker network
docker network inspect gsec-monitoring
```

### **Metrics not updating**

```bash
# Check exporter logs
docker logs gsec-exporter

# Verify reports directory
ls -R garak_reports/
```

### **Alerts not firing**

```bash
# Check Alertmanager config
docker exec alertmanager amtool config show

# Test Slack webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text": "Test alert"}'
```

## 📚 **References**

- [Garak Documentation](https://github.com/leondz/garak)
- [Prometheus Alerting](https://prometheus.io/docs/alerting/latest/overview/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)

---

**Generated:** 2026-02-08  
**Version:** OpenCngsm v3.3  
**Classification:** 🛡️ **PRODUCTION-GRADE SECURITY++ (MILITARY-GRADE)**
