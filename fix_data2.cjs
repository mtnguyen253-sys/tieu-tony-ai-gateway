const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const correctHeader = `export interface FileNode {
  path: string;
  name: string;
  type: 'file' | 'folder';
  content?: string;
  description: string;
  children?: FileNode[];
}

export const FILE_TREE: FileNode[] = [
  { path: 'AGENTS.md', name: 'AGENTS.md', type: 'file', description: PROJECT_FILES['AGENTS.md'].desc },
  { path: 'ROADMAP.md', name: 'ROADMAP.md', type: 'file', description: PROJECT_FILES['ROADMAP.md'].desc },
  { path: 'TECH_DEBT.md', name: 'TECH_DEBT.md', type: 'file', description: PROJECT_FILES['TECH_DEBT.md'].desc },
  { path: 'REPORT_SPRINT_15.md', name: 'REPORT_SPRINT_15.md', type: 'file', description: PROJECT_FILES['REPORT_SPRINT_15.md'].desc },
  { path: 'REPORT_SPRINT_16.md', name: 'REPORT_SPRINT_16.md', type: 'file', description: PROJECT_FILES['REPORT_SPRINT_16.md'].desc },
  { path: 'ai_gateway/core/circuit_breaker.py', name: 'circuit_breaker.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/circuit_breaker.py'].desc },
  { path: 'ai_gateway/core/executor.py', name: 'executor.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/executor.py'].desc },
  { path: 'ai_gateway/tests/test_circuit_breaker.py', name: 'test_circuit_breaker.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_circuit_breaker.py'].desc },
  { path: 'ai_gateway/tests/test_executor.py', name: 'test_executor.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_executor.py'].desc }
];

export const PROJECT_FILES: Record<string, { content: string; desc: string }> = {`;

const projectFilesIndex = data.indexOf("export const PROJECT_FILES: Record<string, { content: string; desc: string }> = {");
if (projectFilesIndex !== -1) {
    data = correctHeader + data.substring(projectFilesIndex + 81);
}

fs.writeFileSync('src/data.ts', data);
