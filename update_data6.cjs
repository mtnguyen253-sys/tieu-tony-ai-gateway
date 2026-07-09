const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const report = fs.readFileSync('REPORT_SPRINT_13.md', 'utf8');
const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

const newFiles = `
  'REPORT_SPRINT_13.md': {
    content: \`${esc(report)}\`,
    desc: 'Báo Cáo Cuối Sprint 13'
  },
`;

if (!data.includes('REPORT_SPRINT_13.md')) {
  data = data.replace(/};\n\nexport const FILE_TREE/, newFiles + '\n};\n\nexport const FILE_TREE');

  data = data.replace(
    /{ path: 'ARCHITECTURE_REVIEW\.md', name: 'ARCHITECTURE_REVIEW\.md', type: 'file', description: PROJECT_FILES\['ARCHITECTURE_REVIEW\.md'\]\.desc }/,
    `{ path: 'ARCHITECTURE_REVIEW.md', name: 'ARCHITECTURE_REVIEW.md', type: 'file', description: PROJECT_FILES['ARCHITECTURE_REVIEW.md'].desc },\n    { path: 'REPORT_SPRINT_13.md', name: 'REPORT_SPRINT_13.md', type: 'file', description: PROJECT_FILES['REPORT_SPRINT_13.md'].desc }`
  );

  fs.writeFileSync('src/data.ts', data);
  console.log('Successfully updated src/data.ts');
}
