#!/usr/bin/env python3
"""
Script para adicionar método _detect_framing ao prompt_filter.py
"""

import sys

# Read the file
with open(r'C:\Users\cngsm\Desktop\XXX\opencngsm-mcp\core\security\prompt_filter.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line after _detect_config_modification
insert_index = None
for i, line in enumerate(lines):
    if 'def _detect_config_modification' in line:
        # Find the end of this method (next method or class end)
        for j in range(i+1, len(lines)):
            if lines[j].strip().startswith('def ') or (lines[j].strip() and not lines[j].startswith(' ')):
                insert_index = j
                break
        break

if insert_index is None:
    print("ERROR: Could not find insertion point")
    sys.exit(1)

# Method to insert
new_method = """    
    def _detect_framing(self, text: str) -> bool:
        \"\"\"Detecta padrões de framing malicioso\"\"\"
        for pattern in self.FRAMING_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"🚨 Framing pattern detected: {pattern}")
                return True
        return False
    
"""

# Insert the method
lines.insert(insert_index, new_method)

# Write back
with open(r'C:\Users\cngsm\Desktop\XXX\opencngsm-mcp\core\security\prompt_filter.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"✅ Method _detect_framing added successfully at line {insert_index}")
