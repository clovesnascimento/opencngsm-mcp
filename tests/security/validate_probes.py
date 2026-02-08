#!/usr/bin/env python3
"""
G-SEC Probe Validation Script
Validates that all custom Garak probes are properly configured
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def validate_probes():
    """Validate all G-SEC custom probes"""
    print("🛡️ G-SEC PROBE VALIDATION")
    print("="*60)
    
    try:
        from tests.security.garak_probes.gsec_judge_bypass import (
            GSECJudgeBypass,
            GSECConfigModification,
            GSECPromptLeaking,
            GSECSupplyChainPoisoning,
            GSECRCEProtection,
        )
        
        probes = [
            ("GSECJudgeBypass", GSECJudgeBypass),
            ("GSECConfigModification", GSECConfigModification),
            ("GSECPromptLeaking", GSECPromptLeaking),
            ("GSECSupplyChainPoisoning", GSECSupplyChainPoisoning),
            ("GSECRCEProtection", GSECRCEProtection),
        ]
        
        total_prompts = 0
        
        for name, probe_class in probes:
            prompt_count = len(probe_class.prompts)
            total_prompts += prompt_count
            print(f"✅ {name:30s} {prompt_count:3d} prompts")
        
        print("="*60)
        print(f"📊 Total: {total_prompts} adversarial prompts across {len(probes)} probe classes")
        print("="*60)
        
        # Validate probe structure
        print("\n🔍 Validating probe structure...")
        for name, probe_class in probes:
            assert hasattr(probe_class, 'prompts'), f"{name} missing 'prompts' attribute"
            assert hasattr(probe_class, 'goal'), f"{name} missing 'goal' attribute"
            assert hasattr(probe_class, 'bcp47'), f"{name} missing 'bcp47' attribute"
            assert len(probe_class.prompts) > 0, f"{name} has no prompts"
            print(f"✅ {name} structure valid")
        
        print("\n✅ All probes validated successfully!")
        print("\n📝 Next Steps:")
        print("  1. Install Garak: pip install garak --upgrade")
        print("  2. Start OpenCngsm server: python main.py")
        print("  3. Run Garak: garak --model_type openai --model_name http://localhost:8000/v1 --probes gsec_judge_bypass.GSECJudgeBypass")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_probes()
    sys.exit(0 if success else 1)
