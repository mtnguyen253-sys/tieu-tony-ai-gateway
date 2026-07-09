const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const techDebt = fs.readFileSync('TECH_DEBT.md', 'utf8');
const archReview = fs.readFileSync('ARCHITECTURE_REVIEW.md', 'utf8');

const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

const newFiles = `
  'TECH_DEBT.md': {
    content: \`${esc(techDebt)}\`,
    desc: 'Technical Debt Log'
  },
  'ARCHITECTURE_REVIEW.md': {
    content: \`${esc(archReview)}\`,
    desc: 'Architecture Review Sprint 12.5'
  },
`;

if (!data.includes('TECH_DEBT.md')) {
  data = data.replace(/};\n\nexport const FILE_TREE/, newFiles + '\n};\n\nexport const FILE_TREE');

  data = data.replace(
    /{ path: 'ai_gateway\/main\.py', name: 'main\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/main\.py'\]\.desc }/,
    `{ path: 'ai_gateway/main.py', name: 'main.py', type: 'file', description: PROJECT_FILES['ai_gateway/main.py'].desc },\n    { path: 'TECH_DEBT.md', name: 'TECH_DEBT.md', type: 'file', description: PROJECT_FILES['TECH_DEBT.md'].desc },\n    { path: 'ARCHITECTURE_REVIEW.md', name: 'ARCHITECTURE_REVIEW.md', type: 'file', description: PROJECT_FILES['ARCHITECTURE_REVIEW.md'].desc }`
  );

  fs.writeFileSync('src/data.ts', data);
  console.log('Successfully updated src/data.ts');
}
