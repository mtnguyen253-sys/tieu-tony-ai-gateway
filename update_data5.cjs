const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const retryPy = fs.readFileSync('ai_gateway/core/retry.py', 'utf8');
const orchestratorPy = fs.readFileSync('ai_gateway/core/orchestrator.py', 'utf8');
const testRetryPy = fs.readFileSync('ai_gateway/tests/test_retry.py', 'utf8');

const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

const newFiles = `
  'ai_gateway/core/retry.py': {
    content: \`${esc(retryPy)}\`,
    desc: 'Retry Strategy implementations.'
  },
  'ai_gateway/tests/test_retry.py': {
    content: \`${esc(testRetryPy)}\`,
    desc: 'Unit test cho Retry Strategy.'
  },
`;

// Replace orchestrator
const escapedOrchestrator = esc(orchestratorPy);
data = data.replace(
  /'ai_gateway\/core\/orchestrator\.py': \{\s+content: `[\s\S]*?`,\s+desc: 'Execution Orchestrator điều phối vòng đời request\.'\s+\},/g,
  `'ai_gateway/core/orchestrator.py': {\n    content: \`${escapedOrchestrator}\`,\n    desc: 'Execution Orchestrator điều phối vòng đời request.'\n  },`
);

if (!data.includes('ai_gateway/core/retry.py')) {
  data = data.replace(/};\n\nexport const FILE_TREE/, newFiles + '\n};\n\nexport const FILE_TREE');

  data = data.replace(
    /{ path: 'ai_gateway\/core\/orchestrator\.py', name: 'orchestrator\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/core\/orchestrator\.py'\]\.desc }/,
    `{ path: 'ai_gateway/core/orchestrator.py', name: 'orchestrator.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/orchestrator.py'].desc },\n        { path: 'ai_gateway/core/retry.py', name: 'retry.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/retry.py'].desc }`
  );

  data = data.replace(
    /{ path: 'ai_gateway\/tests\/test_orchestrator\.py', name: 'test_orchestrator\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/tests\/test_orchestrator\.py'\]\.desc }/,
    `{ path: 'ai_gateway/tests/test_orchestrator.py', name: 'test_orchestrator.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_orchestrator.py'].desc },\n        { path: 'ai_gateway/tests/test_retry.py', name: 'test_retry.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_retry.py'].desc }`
  );
}

fs.writeFileSync('src/data.ts', data);
console.log('Successfully updated src/data.ts');
