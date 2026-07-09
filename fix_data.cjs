const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

data = data.replace(
  "  children?: FileNode[\n  { path: 'AGENTS.md',",
  "  children?: FileNode[];\n}\n\nexport const FILE_TREE: FileNode[] = [\n  { path: 'AGENTS.md',"
);

// wait, there's another replace:
// data = data.replace(
//   /\];\n/,
//   `  { path: 'REPORT_SPRINT_16.md', name: 'REPORT_SPRINT_16.md', type: 'file', description: PROJECT_FILES['REPORT_SPRINT_16.md'].desc }\n];\n`
// );
// the `]` might have been replaced again? Let's check `data.ts` around REPORT_SPRINT_15.md
