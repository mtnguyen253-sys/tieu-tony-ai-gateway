const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const agentsMd = fs.readFileSync('AGENTS.md', 'utf8');
const roadmapMd = fs.readFileSync('ROADMAP.md', 'utf8');
const techDebtMd = fs.readFileSync('TECH_DEBT.md', 'utf8');

const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

// Update contents for existing items in PROJECT_FILES
data = data.replace(
  /'AGENTS\.md':\s*\{\s*content:\s*`[\s\S]*?`,\s*desc:\s*'[^']*'\s*\}/,
  `'AGENTS.md': {\n    content: \`${esc(agentsMd)}\`,\n    desc: 'Project Governance'\n  }`
);
data = data.replace(
  /'ROADMAP\.md':\s*\{\s*content:\s*`[\s\S]*?`,\s*desc:\s*'[^']*'\s*\}/,
  `'ROADMAP.md': {\n    content: \`${esc(roadmapMd)}\`,\n    desc: 'Project Roadmap'\n  }`
);
data = data.replace(
  /'TECH_DEBT\.md':\s*\{\s*content:\s*`[\s\S]*?`,\s*desc:\s*'[^']*'\s*\}/,
  `'TECH_DEBT.md': {\n    content: \`${esc(techDebtMd)}\`,\n    desc: 'Technical Debt Log'\n  }`
);

// Remove deleted files from PROJECT_FILES
data = data.replace(/\s*'ARCHITECTURE\.md':\s*\{\s*content:\s*`[\s\S]*?`,\s*desc:\s*'[^']*'\s*\},?/g, '');
data = data.replace(/\s*'DEVELOPMENT_WORKFLOW\.md':\s*\{\s*content:\s*`[\s\S]*?`,\s*desc:\s*'[^']*'\s*\},?/g, '');
data = data.replace(/\s*'DECISIONS\.md':\s*\{\s*content:\s*`[\s\S]*?`,\s*desc:\s*'[^']*'\s*\},?/g, '');
data = data.replace(/\s*'PROMPT_CONVENTION\.md':\s*\{\s*content:\s*`[\s\S]*?`,\s*desc:\s*'[^']*'\s*\},?/g, '');

// Remove deleted files from FILE_TREE array
data = data.replace(/\s*\{\s*path:\s*'ARCHITECTURE\.md'[\s\S]*?\},?/g, '');
data = data.replace(/\s*\{\s*path:\s*'DEVELOPMENT_WORKFLOW\.md'[\s\S]*?\},?/g, '');
data = data.replace(/\s*\{\s*path:\s*'DECISIONS\.md'[\s\S]*?\},?/g, '');
data = data.replace(/\s*\{\s*path:\s*'PROMPT_CONVENTION\.md'[\s\S]*?\},?/g, '');

fs.writeFileSync('src/data.ts', data);
console.log('Successfully updated src/data.ts');
