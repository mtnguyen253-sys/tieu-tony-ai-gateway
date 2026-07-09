import os
import re

def esc(s):
    return s.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

# List of files we need
files = [
    'AGENTS.md', 'ROADMAP.md', 'TECH_DEBT.md', 
    'REPORT_SPRINT_15.md', 'REPORT_SPRINT_16.md', 'REPORT_SPRINT_17.md',
    'ai_gateway/core/__init__.py', 'ai_gateway/core/config.py', 'ai_gateway/core/router.py', 
    'ai_gateway/core/circuit_breaker.py', 'ai_gateway/core/executor.py', 'ai_gateway/core/orchestrator.py',
    'ai_gateway/core/fallback.py', 'ai_gateway/core/retry.py', 'ai_gateway/core/state.py', 'ai_gateway/core/compressor.py',
    'ai_gateway/adapters/__init__.py', 'ai_gateway/adapters/base.py', 'ai_gateway/adapters/gemini.py',
    'ai_gateway/protocols/__init__.py', 'ai_gateway/protocols/cap.py',
    'ai_gateway/registry/__init__.py', 'ai_gateway/registry/capability.py',
    'ai_gateway/api/__init__.py', 'ai_gateway/api/schemas.py', 'ai_gateway/api/app.py',
    'ai_gateway/main.py',
    'ai_gateway/tests/__init__.py', 'ai_gateway/tests/test_router.py', 'ai_gateway/tests/test_circuit_breaker.py',
    'ai_gateway/tests/test_executor.py', 'ai_gateway/tests/test_orchestrator.py', 'ai_gateway/tests/test_fallback.py',
    'ai_gateway/tests/test_retry.py', 'ai_gateway/tests/test_state.py', 'ai_gateway/tests/test_compressor.py',
    'ai_gateway/tests/test_api.py'
]

# Provide fallback descriptions
desc_map = {
    'ai_gateway/api/__init__.py': 'Module khởi tạo API layer.',
    'ai_gateway/api/schemas.py': 'Chứa các schema Pydantic tương thích OpenAI API (ChatCompletion).',
    'ai_gateway/api/app.py': 'Module chính của FastAPI, định nghĩa các endpoints REST API v1 tương thích OpenAI.',
    'ai_gateway/tests/test_api.py': 'File test mock cho API layer, kiểm tra validation, response và schema mapping.',
    'REPORT_SPRINT_17.md': 'Báo cáo Sprint 17 về Public REST API v1.'
}

# Try to extract existing descriptions from src/data.ts
try:
    with open("src/data.ts", "r") as f:
        content = f.read()
        matches = re.finditer(r"'([^']+)':\s*\{\s*content:.*?desc:\s*'([^']+)'", content, re.DOTALL)
        for m in matches:
            if m.group(1) not in desc_map:
                desc_map[m.group(1)] = m.group(2)
except:
    pass

new_content = """export interface FileNode {
  path: string;
  name: string;
  type: 'file' | 'folder';
  content?: string;
  description: string;
  children?: FileNode[];
}

export const PROJECT_FILES: Record<string, { content: string; desc: string }> = {
"""

for i, filepath in enumerate(files):
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, "r") as f:
        file_content = f.read()
        
    desc = desc_map.get(filepath, "File " + filepath)
    
    new_content += f"  '{filepath}': {{\n"
    new_content += f"    content: `{esc(file_content)}`,\n"
    new_content += f"    desc: '{desc}'\n"
    new_content += "  }"
    if i < len(files) - 1:
        new_content += ",\n"
    else:
        new_content += "\n"
        
new_content += "};\n\n"

new_content += "export const FILE_TREE: FileNode[] = [\n"
for i, filepath in enumerate(files):
    if not os.path.exists(filepath):
        continue
    name = os.path.basename(filepath)
    new_content += f"  {{ path: '{filepath}', name: '{name}', type: 'file', description: PROJECT_FILES['{filepath}'].desc }}"
    if i < len(files) - 1:
        new_content += ",\n"
    else:
        new_content += "\n"
new_content += "];\n"

with open("src/data.ts", "w") as f:
    f.write(new_content)
