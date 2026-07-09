const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const techDebtMd = fs.readFileSync('TECH_DEBT.md', 'utf8');
const report16 = fs.readFileSync('REPORT_SPRINT_16.md', 'utf8');

const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

// update tech debt
data = data.replace(
  /'TECH_DEBT\.md':\s*\{\s*content:\s*`[\s\S]*?`,\s*desc:\s*'[^']*'\s*\}/,
  `'TECH_DEBT.md': {\n    content: \`${esc(techDebtMd)}\`,\n    desc: 'Technical Debt Log'\n  }`
);

// add report 16
const newReport = `
  'REPORT_SPRINT_16.md': {
    content: \`${esc(report16)}\`,
    desc: 'Sprint 16 Report'
  },
`;

if (!data.includes('REPORT_SPRINT_16.md')) {
  data = data.replace(/};\n\nexport const FILE_TREE/, newReport + '\n};\n\nexport const FILE_TREE');
  data = data.replace(
    /\];\n/,
    `  { path: 'REPORT_SPRINT_16.md', name: 'REPORT_SPRINT_16.md', type: 'file', description: PROJECT_FILES['REPORT_SPRINT_16.md'].desc }\n];\n`
  );
} else {
    data = data.replace(
      /'REPORT_SPRINT_16\.md':\s*\{\s*content:\s*`[\s\S]*?`,\s*desc:\s*'[^']*'\s*\}/,
      `'REPORT_SPRINT_16.md': {\n    content: \`${esc(report16)}\`,\n    desc: 'Sprint 16 Report'\n  }`
    );
}

fs.writeFileSync('src/data.ts', data);
console.log('Successfully updated src/data.ts');
