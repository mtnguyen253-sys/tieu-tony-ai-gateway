const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const agentsMd = fs.readFileSync('AGENTS.md', 'utf8');
const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

data = data.replace(
  /'AGENTS\.md':\s*\{\s*content:\s*`[\s\S]*?`,\s*desc:\s*'[^']*'\s*\}/,
  `'AGENTS.md': {\n    content: \`${esc(agentsMd)}\`,\n    desc: 'Project Governance'\n  }`
);

fs.writeFileSync('src/data.ts', data);
console.log('Successfully updated src/data.ts');
