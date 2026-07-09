const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const fallbackPy = fs.readFileSync('ai_gateway/core/fallback.py', 'utf8');
const testFallbackPy = fs.readFileSync('ai_gateway/tests/test_fallback.py', 'utf8');
const report14 = fs.readFileSync('REPORT_SPRINT_14.md', 'utf8');

const executorPy = fs.readFileSync('ai_gateway/core/executor.py', 'utf8');
const orchestratorPy = fs.readFileSync('ai_gateway/core/orchestrator.py', 'utf8');

const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

const newFiles = `
  'ai_gateway/core/fallback.py': {
    content: \`${esc(fallbackPy)}\`,
    desc: 'Fallback Strategy implementations.'
  },
  'ai_gateway/tests/test_fallback.py': {
    content: \`${esc(testFallbackPy)}\`,
    desc: 'Unit test cho Fallback Strategy.'
  },
  'REPORT_SPRINT_14.md': {
    content: \`${esc(report14)}\`,
    desc: 'Báo Cáo Cuối Sprint 14'
  },
`;

// Replace executor
data = data.replace(
  /'ai_gateway\/core\/executor\.py': \{\s+content: `[\s\S]*?`,\s+desc: 'Execution Engine thực thi request qua Provider\.'\s+\},/g,
  `'ai_gateway/core/executor.py': {\n    content: \`${esc(executorPy)}\`,\n    desc: 'Execution Engine thực thi request qua Provider.'\n  },`
);

// Replace orchestrator
data = data.replace(
  /'ai_gateway\/core\/orchestrator\.py': \{\s+content: `[\s\S]*?`,\s+desc: 'Execution Orchestrator điều phối vòng đời request\.'\s+\},/g,
  `'ai_gateway/core/orchestrator.py': {\n    content: \`${esc(orchestratorPy)}\`,\n    desc: 'Execution Orchestrator điều phối vòng đời request.'\n  },`
);

if (!data.includes('ai_gateway/core/fallback.py')) {
  data = data.replace(/};\n\nexport const FILE_TREE/, newFiles + '\n};\n\nexport const FILE_TREE');

  data = data.replace(
    /{ path: 'ai_gateway\/core\/retry\.py', name: 'retry\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/core\/retry\.py'\]\.desc }/,
    `{ path: 'ai_gateway/core/retry.py', name: 'retry.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/retry.py'].desc },\n        { path: 'ai_gateway/core/fallback.py', name: 'fallback.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/fallback.py'].desc }`
  );

  data = data.replace(
    /{ path: 'ai_gateway\/tests\/test_retry\.py', name: 'test_retry\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/tests\/test_retry\.py'\]\.desc }/,
    `{ path: 'ai_gateway/tests/test_retry.py', name: 'test_retry.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_retry.py'].desc },\n        { path: 'ai_gateway/tests/test_fallback.py', name: 'test_fallback.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_fallback.py'].desc }`
  );

  data = data.replace(
    /{ path: 'REPORT_SPRINT_13\.md', name: 'REPORT_SPRINT_13\.md', type: 'file', description: PROJECT_FILES\['REPORT_SPRINT_13\.md'\]\.desc }/,
    `{ path: 'REPORT_SPRINT_13.md', name: 'REPORT_SPRINT_13.md', type: 'file', description: PROJECT_FILES['REPORT_SPRINT_13.md'].desc },\n    { path: 'REPORT_SPRINT_14.md', name: 'REPORT_SPRINT_14.md', type: 'file', description: PROJECT_FILES['REPORT_SPRINT_14.md'].desc }`
  );

  fs.writeFileSync('src/data.ts', data);
  console.log('Successfully updated src/data.ts');
}
