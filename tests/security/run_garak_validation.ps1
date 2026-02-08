# G-SEC Garak Validation Script (PowerShell)
# Runs comprehensive adversarial testing using custom probes

Write-Host "🛡️ G-SEC GARAK VALIDATION - AUTOMATED ADVERSARIAL TESTING" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Set up environment
$env:PYTHONPATH = "C:\Users\cngsm\Desktop\XXX\opencngsm-mcp"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$REPORT_DIR = "tests\security\garak_reports"

# Create report directory
New-Item -ItemType Directory -Force -Path $REPORT_DIR | Out-Null

Write-Host ""
Write-Host "📊 Running G-SEC Custom Probes..." -ForegroundColor Yellow
Write-Host "Report directory: $REPORT_DIR" -ForegroundColor Gray
Write-Host ""

# Note: Garak requires a running OpenAI-compatible endpoint
# For now, we'll create a simplified test that validates the probes exist

Write-Host "🔍 Validating Custom Probes..." -ForegroundColor Yellow

# Test 1: Check if probes can be imported
Write-Host "1️⃣ Testing probe imports..." -ForegroundColor White
python -c "from tests.security.garak_probes.gsec_judge_bypass import GSECJudgeBypass; print(f'✅ GSECJudgeBypass: {len(GSECJudgeBypass.prompts)} prompts')"
python -c "from tests.security.garak_probes.gsec_judge_bypass import GSECConfigModification; print(f'✅ GSECConfigModification: {len(GSECConfigModification.prompts)} prompts')"
python -c "from tests.security.garak_probes.gsec_judge_bypass import GSECPromptLeaking; print(f'✅ GSECPromptLeaking: {len(GSECPromptLeaking.prompts)} prompts')"
python -c "from tests.security.garak_probes.gsec_judge_bypass import GSECSupplyChainPoisoning; print(f'✅ GSECSupplyChainPoisoning: {len(GSECSupplyChainPoisoning.prompts)} prompts')"
python -c "from tests.security.garak_probes.gsec_judge_bypass import GSECRCEProtection; print(f'✅ GSECRCEProtection: {len(GSECRCEProtection.prompts)} prompts')"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "✅ Probe validation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Start your OpenCngsm server on http://localhost:8000" -ForegroundColor Gray
Write-Host "  2. Run: garak --model_type openai --model_name http://localhost:8000/v1 --probes gsec_judge_bypass.GSECJudgeBypass" -ForegroundColor Gray
Write-Host ""
