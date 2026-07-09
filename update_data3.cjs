const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const executorPy = fs.readFileSync('ai_gateway/core/executor.py', 'utf8');
const testExecutorPy = fs.readFileSync('ai_gateway/tests/test_executor.py', 'utf8');

const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

const newFiles = `
  'ai_gateway/core/executor.py': {
    content: \`${esc(executorPy)}\`,
    desc: 'Execution Engine quản lý luồng gọi provider và xử lý exception.'
  },
  'ai_gateway/tests/test_executor.py': {
    content: \`${esc(testExecutorPy)}\`,
    desc: 'Unit test kiểm tra 6 kịch bản Execution Engine.'
  },
`;

if (!data.includes('ai_gateway/core/executor.py')) {
  data = data.replace(/};\n\nexport const FILE_TREE/, newFiles + '\n};\n\nexport const FILE_TREE');

  data = data.replace(
    /{ path: 'ai_gateway\/core\/circuit_breaker\.py', name: 'circuit_breaker\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/core\/circuit_breaker\.py'\]\.desc }/,
    `{ path: 'ai_gateway/core/circuit_breaker.py', name: 'circuit_breaker.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/circuit_breaker.py'].desc },\n        { path: 'ai_gateway/core/executor.py', name: 'executor.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/executor.py'].desc }`
  );

  data = data.replace(
    /{ path: 'ai_gateway\/tests\/test_circuit_breaker\.py', name: 'test_circuit_breaker\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/tests\/test_circuit_breaker\.py'\]\.desc }/,
    `{ path: 'ai_gateway/tests/test_circuit_breaker.py', name: 'test_circuit_breaker.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_circuit_breaker.py'].desc },\n        { path: 'ai_gateway/tests/test_executor.py', name: 'test_executor.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_executor.py'].desc }`
  );
}

fs.writeFileSync('src/data.ts', data);
console.log('Successfully updated src/data.ts');
