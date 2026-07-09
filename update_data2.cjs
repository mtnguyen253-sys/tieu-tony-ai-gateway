const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const circuitBreakerPy = fs.readFileSync('ai_gateway/core/circuit_breaker.py', 'utf8');
const testCircuitBreakerPy = fs.readFileSync('ai_gateway/tests/test_circuit_breaker.py', 'utf8');
const routerPy = fs.readFileSync('ai_gateway/core/router.py', 'utf8'); // need to update router too

// Escape strings
const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

// We need to inject these into PROJECT_FILES and update FILE_TREE
const newFiles = `
  'ai_gateway/core/circuit_breaker.py': {
    content: \`${esc(circuitBreakerPy)}\`,
    desc: 'CircuitBreaker kiểm soát trạng thái Provider.'
  },
  'ai_gateway/tests/test_circuit_breaker.py': {
    content: \`${esc(testCircuitBreakerPy)}\`,
    desc: 'Unit test kiểm tra kịch bản CircuitBreaker và Router.'
  },
`;

// Replace existing router file content with the updated one
const escapedRouter = esc(routerPy);
// We can use a regex to replace the router content
data = data.replace(
  /'ai_gateway\/core\/router\.py': \{\s+content: `[\s\S]*?`,\s+desc: 'PolicyRouter định tuyến logic cho các Provider dựa vào Capability và Policy\.'\s+\},/g,
  `'ai_gateway/core/router.py': {\n    content: \`${escapedRouter}\`,\n    desc: 'PolicyRouter định tuyến logic cho các Provider dựa vào Capability và Policy.'\n  },`
);

// Insert into PROJECT_FILES before the closing bracket of the object
if (!data.includes('ai_gateway/core/circuit_breaker.py')) {
  data = data.replace(/};\n\nexport const FILE_TREE/, newFiles + '\n};\n\nexport const FILE_TREE');

  // Update FILE_TREE children
  // For ai_gateway/core
  data = data.replace(
    /{ path: 'ai_gateway\/core\/router\.py', name: 'router\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/core\/router\.py'\]\.desc }/,
    `{ path: 'ai_gateway/core/router.py', name: 'router.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/router.py'].desc },\n        { path: 'ai_gateway/core/circuit_breaker.py', name: 'circuit_breaker.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/circuit_breaker.py'].desc }`
  );

  // For ai_gateway/tests
  data = data.replace(
    /{ path: 'ai_gateway\/tests\/test_router\.py', name: 'test_router\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/tests\/test_router\.py'\]\.desc }/,
    `{ path: 'ai_gateway/tests/test_router.py', name: 'test_router.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_router.py'].desc },\n        { path: 'ai_gateway/tests/test_circuit_breaker.py', name: 'test_circuit_breaker.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_circuit_breaker.py'].desc }`
  );
}

fs.writeFileSync('src/data.ts', data);
console.log('Successfully updated src/data.ts');
