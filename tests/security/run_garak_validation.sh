#!/bin/bash
# G-SEC Garak Validation Script
# Runs comprehensive adversarial testing using custom probes

set -e

echo "🛡️ G-SEC GARAK VALIDATION - AUTOMATED ADVERSARIAL TESTING"
echo "=========================================================="

# Check if Garak is installed
if ! command -v garak &> /dev/null; then
    echo "❌ Garak not found. Installing..."
    pip install garak --upgrade
fi

# Set up environment
export PYTHONPATH="$(pwd):$PYTHONPATH"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="tests/security/garak_reports"
mkdir -p "$REPORT_DIR"

echo ""
echo "📊 Running G-SEC Custom Probes..."
echo "Report directory: $REPORT_DIR"
echo ""

# Run each probe category
echo "1️⃣ Testing LLM Judge Bypass Protection..."
garak --model_type openai \
      --model_name http://localhost:8000/v1 \
      --probes gsec_judge_bypass.GSECJudgeBypass \
      --report_prefix "$REPORT_DIR/gsec_judge_bypass_$TIMESTAMP" \
      --verbose

echo ""
echo "2️⃣ Testing Config Modification Protection..."
garak --model_type openai \
      --model_name http://localhost:8000/v1 \
      --probes gsec_judge_bypass.GSECConfigModification \
      --report_prefix "$REPORT_DIR/gsec_config_mod_$TIMESTAMP" \
      --verbose

echo ""
echo "3️⃣ Testing Prompt Leaking Protection..."
garak --model_type openai \
      --model_name http://localhost:8000/v1 \
      --probes gsec_judge_bypass.GSECPromptLeaking \
      --report_prefix "$REPORT_DIR/gsec_prompt_leak_$TIMESTAMP" \
      --verbose

echo ""
echo "4️⃣ Testing Supply-Chain Poisoning Protection..."
garak --model_type openai \
      --model_name http://localhost:8000/v1 \
      --probes gsec_judge_bypass.GSECSupplyChainPoisoning \
      --report_prefix "$REPORT_DIR/gsec_supply_chain_$TIMESTAMP" \
      --verbose

echo ""
echo "5️⃣ Testing RCE Protection..."
garak --model_type openai \
      --model_name http://localhost:8000/v1 \
      --probes gsec_judge_bypass.GSECRCEProtection \
      --report_prefix "$REPORT_DIR/gsec_rce_$TIMESTAMP" \
      --verbose

echo ""
echo "=========================================================="
echo "✅ Garak validation complete!"
echo "📊 Reports saved to: $REPORT_DIR"
echo ""
echo "To view HTML report:"
echo "  open $REPORT_DIR/gsec_*_$TIMESTAMP.html"
echo ""
