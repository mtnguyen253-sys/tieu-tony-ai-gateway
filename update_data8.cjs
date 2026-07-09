const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const agentsMd = fs.readFileSync('AGENTS.md', 'utf8');
const architectureMd = fs.readFileSync('ARCHITECTURE.md', 'utf8');
const workflowMd = fs.readFileSync('DEVELOPMENT_WORKFLOW.md', 'utf8');
const roadmapMd = fs.readFileSync('ROADMAP.md', 'utf8');
const techDebtMd = fs.readFileSync('TECH_DEBT.md', 'utf8');
const decisionsMd = fs.readFileSync('DECISIONS.md', 'utf8');

const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

const newFiles = `
  'AGENTS.md': {
    content: \`${esc(agentsMd)}\`,
    desc: 'Hiến pháp Dự án AI Gateway'
  },
  'ARCHITECTURE.md': {
    content: \`${esc(architectureMd)}\`,
    desc: 'Kiến trúc Dự án'
  },
  'DEVELOPMENT_WORKFLOW.md': {
    content: \`${esc(workflowMd)}\`,
    desc: 'Quy trình Phát triển chuẩn'
  },
  'ROADMAP.md': {
    content: \`${esc(roadmapMd)}\`,
    desc: 'Lộ trình các Sprint'
  },
  'DECISIONS.md': {
    content: \`${esc(decisionsMd)}\`,
    desc: 'Architecture Decision Records'
  },
`;

// TECH_DEBT.md already exists in data.ts, we need to replace its content
data = data.replace(
  /'TECH_DEBT\.md': \{\s+content: `[\s\S]*?`,\s+desc: 'Technical Debt Log'\s+\},/g,
  `'TECH_DEBT.md': {\n    content: \`${esc(techDebtMd)}\`,\n    desc: 'Technical Debt Log'\n  },`
);

if (!data.includes('AGENTS.md')) {
  data = data.replace(/};\n\nexport const FILE_TREE/, newFiles + '\n};\n\nexport const FILE_TREE');

  data = data.replace(
    /\];\n/,
    `  { path: 'AGENTS.md', name: 'AGENTS.md', type: 'file', description: PROJECT_FILES['AGENTS.md'].desc },
  { path: 'ARCHITECTURE.md', name: 'ARCHITECTURE.md', type: 'file', description: PROJECT_FILES['ARCHITECTURE.md'].desc },
  { path: 'DEVELOPMENT_WORKFLOW.md', name: 'DEVELOPMENT_WORKFLOW.md', type: 'file', description: PROJECT_FILES['DEVELOPMENT_WORKFLOW.md'].desc },
  { path: 'ROADMAP.md', name: 'ROADMAP.md', type: 'file', description: PROJECT_FILES['ROADMAP.md'].desc },
  { path: 'DECISIONS.md', name: 'DECISIONS.md', type: 'file', description: PROJECT_FILES['DECISIONS.md'].desc }\n];\n`
  );

  fs.writeFileSync('src/data.ts', data);
  console.log('Successfully updated src/data.ts');
}
