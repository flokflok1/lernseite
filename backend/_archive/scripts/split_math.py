#!/usr/bin/env python3
"""
Split math_toolkit.py into 4 focused modules based on functionality.

Analysis of math_toolkit.py (511 lines, 20 functions):
- Categories (2 funcs): get_categories, ...
- Patterns (3 funcs): get_patterns, get_pattern, ...
- Formulas (4 funcs): get_formulas, toggle_formula_favorite, use_formula, ...
- Calculator (3 funcs): evaluate_expression, get_calculator_history, save_calculator_entry
- Sessions (5 funcs): start_session, get_session, end_session, get_session_steps, save_session_step
- Progress (2 funcs): get_user_progress, update_user_progress
- Hints (1 func): get_hint
- Tasks (3 funcs): get_tasks, check_task_answer, ...
- Admin (1 func): create_pattern

Structure:
- reference.py: Categories, Patterns, Formulas (read-only data, ~150 LOC)
- calculator.py: Calculator operations (~120 LOC)
- sessions.py: Session management and steps (~130 LOC)
- interactive.py: Progress, hints, tasks, admin (~130 LOC)
"""
from pathlib import Path

# Read original file
math_original = Path("app/api/math_toolkit.py.original").read_text()
lines = math_original.splitlines(keepends=True)

# Common header (lines 0-28)
header = "".join(lines[0:29])

# Find all section starts by looking for function definitions
funcs = []
for i, line in enumerate(lines):
    if line.strip().startswith("def "):
        func_name = line.strip().split("(")[0].replace("def ", "")
        funcs.append((i, func_name))

# Group functions by category
reference_funcs = ["get_categories", "get_patterns", "get_pattern", "get_formulas",
                   "toggle_formula_favorite", "use_formula"]
calculator_funcs = ["evaluate_expression", "get_calculator_history", "save_calculator_entry"]
sessions_funcs = ["start_session", "get_session", "end_session", "get_session_steps", "save_session_step"]
interactive_funcs = ["get_user_progress", "update_user_progress", "get_hint", "get_tasks",
                     "check_task_answer", "create_pattern"]

# Build content for each module
def extract_function_range(func_name, next_func_line=None):
    """Extract lines for a specific function."""
    start = None
    for i, (line_num, fname) in enumerate(funcs):
        if fname == func_name:
            start = line_num
            # Find decorator line (@api_v1.route)
            while start > 0 and (lines[start-1].strip().startswith("@") or lines[start-1].strip() == ""):
                start -= 1
            # Find end (next function or EOF)
            if i + 1 < len(funcs):
                end = funcs[i+1][0]
            else:
                end = len(lines)
            return lines[start:end]
    return []

# reference.py
reference_content = header + """

# =============================================================================
# MATH REFERENCE DATA - Categories, Patterns, Formulas
# =============================================================================

"""
for func_name in reference_funcs:
    reference_content += "".join(extract_function_range(func_name))

# calculator.py
calculator_content = header + """

# =============================================================================
# CALCULATOR OPERATIONS
# =============================================================================

"""
for func_name in calculator_funcs:
    calculator_content += "".join(extract_function_range(func_name))

# sessions.py
sessions_content = header + """

# =============================================================================
# MATH SESSION MANAGEMENT
# =============================================================================

"""
for func_name in sessions_funcs:
    sessions_content += "".join(extract_function_range(func_name))

# interactive.py
interactive_content = header + """

# =============================================================================
# INTERACTIVE MATH TOOLS - Progress, Hints, Tasks
# =============================================================================

"""
for func_name in interactive_funcs:
    interactive_content += "".join(extract_function_range(func_name))

# Write split files
Path("app/api/math/reference.py").write_text(reference_content)
Path("app/api/math/calculator.py").write_text(calculator_content)
Path("app/api/math/sessions.py").write_text(sessions_content)
Path("app/api/math/interactive.py").write_text(interactive_content)

print("✅ math_toolkit.py split into 4 files:")
print(f"   - reference.py ({len(reference_content.splitlines())} lines)")
print(f"   - calculator.py ({len(calculator_content.splitlines())} lines)")
print(f"   - sessions.py ({len(sessions_content.splitlines())} lines)")
print(f"   - interactive.py ({len(interactive_content.splitlines())} lines)")
