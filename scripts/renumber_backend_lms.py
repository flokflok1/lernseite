#!/usr/bin/env python3
"""
Renumber Backend Learning Method Mapping: lm00-lm25 → lm00-lm18

Maps old IDs (with gaps) to new continuous IDs:
    Old: 0,1,2,3,6,8,12,13,14,15,17,18,19,20,21,22,23,24,25
    New: 0,1,2,3,4,5,6, 7, 8, 9, 10,11,12,13,14,15,16,17,18
"""

import re
from pathlib import Path

# Renumbering mapping
LM_RENUMBER_MAP = {
    0: 0,   # lm00 → lm00
    1: 1,   # lm01 → lm01
    2: 2,   # lm02 → lm02
    3: 3,   # lm03 → lm03
    6: 4,   # lm06 → lm04
    8: 5,   # lm08 → lm05
    12: 6,  # lm12 → lm06
    13: 7,  # lm13 → lm07
    14: 8,  # lm14 → lm08
    15: 9,  # lm15 → lm09
    17: 10, # lm17 → lm10
    18: 11, # lm18 → lm11
    19: 12, # lm19 → lm12
    20: 13, # lm20 → lm13
    21: 14, # lm21 → lm14
    22: 15, # lm22 → lm15
    23: 16, # lm23 → lm16
    24: 17, # lm24 → lm17
    25: 18, # lm25 → lm18
}

BASE_DIR = Path('/home/pascal/Lernsystem')
MAPPING_FILE = BASE_DIR / 'backend/app/ki/learning_method_mapping.py'

def update_mapping_file():
    """Update learning_method_mapping.py with new LM IDs"""
    content = MAPPING_FILE.read_text(encoding='utf-8')
    original_content = content
    changes = []

    # Update header comments
    content = content.replace(
        '- A: Erklärend (LM00-LM03, LM06) - 5 Methoden',
        '- A: Erklärend (LM00-LM04) - 5 Methoden'
    )
    content = content.replace(
        '- B: Praxis (LM08, LM12-LM15, LM17) - 6 Methoden',
        '- B: Praxis (LM05-LM10) - 6 Methoden'
    )
    content = content.replace(
        '- C: Prüfung (LM18-LM25) - 8 Methoden',
        '- C: Prüfung (LM11-LM18) - 8 Methoden'
    )
    content = content.replace(
        '    lm_id: int                          # 0-25 (mit Lücken bei 4, 5, 7, 9-11, 16)',
        '    lm_id: int                          # 0-18 (durchgehend, 19 Content-LMs)'
    )

    # Update LEARNING_METHODS dictionary keys
    for old_id in sorted(LM_RENUMBER_MAP.keys(), reverse=True):  # Start from highest
        new_id = LM_RENUMBER_MAP[old_id]

        if old_id == new_id:
            continue  # No change needed

        # Pattern: "    6: LearningMethodDefinition("
        pattern = rf'^(\s+){old_id}:\s+LearningMethodDefinition\('
        replacement = rf'\g<1>{new_id}: LearningMethodDefinition('

        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        # Pattern: "lm_id=6,"
        pattern = rf'lm_id={old_id},'
        replacement = f'lm_id={new_id},'

        content = content.replace(pattern, replacement)

        changes.append(f"Renamed LM{old_id:02d} → LM{new_id:02d}")

    # Update ACTIVE_LEARNING_METHODS list
    new_active_lms = '[' + ', '.join(str(i) for i in range(19)) + ']'
    content = re.sub(
        r'ACTIVE_LEARNING_METHODS\s*=\s*\[[^\]]+\]',
        f'ACTIVE_LEARNING_METHODS = {new_active_lms}',
        content
    )

    # Update constraint check in docstrings/comments
    content = content.replace('0-31', '0-18')
    content = content.replace('0-25', '0-18')

    if content != original_content:
        MAPPING_FILE.write_text(content, encoding='utf-8')
        print(f"✓ Updated {MAPPING_FILE}")
        for change in changes:
            print(f"  {change}")
        return len(changes)
    else:
        print("→ No changes needed")
        return 0


def main():
    print("=" * 80)
    print("🔧 RENUMBERING BACKEND LEARNING METHOD MAPPING")
    print("=" * 80)
    print(f"\nFile: {MAPPING_FILE}\n")

    changes = update_mapping_file()

    print("\n" + "=" * 80)
    print("✅ BACKEND LM RENUMBERING COMPLETE!")
    print("=" * 80)
    print(f"\nChanges made: {changes}")
    print("\nNext: Update migration 011_learning_methods.sql")


if __name__ == '__main__':
    main()
