const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const techDebtMd = fs.readFileSync('TECH_DEBT.md', 'utf8');
const report15 = fs.readFileSync('REPORT_SPRINT_15.md', 'utf8');

const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

// update tech debt
data = data.replace(
  /'TECH_DEBT\.md':\s*\{\s*content:\s*`[\s\S]*?`,\s*desc:\s*'[^']*'\s*\}/,
  `'TECH_DEBT.md': {\n    content: \`${esc(techDebtMd)}\`,\n    desc: 'Technical Debt Log'\n  }`
);

// add report 15
const newReport = `
  'REPORT_SPRINT_15.md': {
    content: \`${esc(report15)}\`,
    desc: 'Sprint 15 Report'
  },
`;

if (!data.includes('REPORT_SPRINT_15.md')) {
  data = data.replace(/};\n\nexport const FILE_TREE/, newReport + '\n};\n\nexport const FILE_TREE');
  data = data.replace(
    /\];\n/,
    `  { path: 'REPORT_SPRINT_15.md', name: 'REPORT_SPRINT_15.md', type: 'file', description: PROJECT_FILES['REPORT_SPRINT_15.md'].desc }\n];\n`
  );
}

fs.writeFileSync('src/data.ts', data);
console.log('Successfully updated src/data.ts');
