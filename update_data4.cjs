const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const orchestratorPy = fs.readFileSync('ai_gateway/core/orchestrator.py', 'utf8');
const testOrchestratorPy = fs.readFileSync('ai_gateway/tests/test_orchestrator.py', 'utf8');

const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

const newFiles = `
  'ai_gateway/core/orchestrator.py': {
    content: \`${esc(orchestratorPy)}\`,
    desc: 'Execution Orchestrator điều phối vòng đời request.'
  },
  'ai_gateway/tests/test_orchestrator.py': {
    content: \`${esc(testOrchestratorPy)}\`,
    desc: 'Unit test kiểm tra 4 kịch bản Execution Orchestrator.'
  },
`;

if (!data.includes('ai_gateway/core/orchestrator.py')) {
  data = data.replace(/};\n\nexport const FILE_TREE/, newFiles + '\n};\n\nexport const FILE_TREE');

  data = data.replace(
    /{ path: 'ai_gateway\/core\/executor\.py', name: 'executor\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/core\/executor\.py'\]\.desc }/,
    `{ path: 'ai_gateway/core/executor.py', name: 'executor.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/executor.py'].desc },\n        { path: 'ai_gateway/core/orchestrator.py', name: 'orchestrator.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/orchestrator.py'].desc }`
  );

  data = data.replace(
    /{ path: 'ai_gateway\/tests\/test_executor\.py', name: 'test_executor\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/tests\/test_executor\.py'\]\.desc }/,
    `{ path: 'ai_gateway/tests/test_executor.py', name: 'test_executor.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_executor.py'].desc },\n        { path: 'ai_gateway/tests/test_orchestrator.py', name: 'test_orchestrator.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_orchestrator.py'].desc }`
  );
}

fs.writeFileSync('src/data.ts', data);
console.log('Successfully updated src/data.ts');
