const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

const capabilityPy = fs.readFileSync('ai_gateway/registry/capability.py', 'utf8');
const routerPy = fs.readFileSync('ai_gateway/core/router.py', 'utf8');
const testRouterPy = fs.readFileSync('ai_gateway/tests/test_router.py', 'utf8');

// We need to inject these into PROJECT_FILES and update FILE_TREE
const newFiles = `
  'ai_gateway/registry/capability.py': {
    content: \`${capabilityPy.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$')}\`,
    desc: 'Capability Registry định nghĩa Schema và quản lý Provider Capability.'
  },
  'ai_gateway/core/router.py': {
    content: \`${routerPy.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$')}\`,
    desc: 'PolicyRouter định tuyến logic cho các Provider dựa vào Capability và Policy.'
  },
  'ai_gateway/tests/test_router.py': {
    content: \`${testRouterPy.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$')}\`,
    desc: 'Unit test kiểm tra 10 kịch bản định tuyến của PolicyRouter.'
  },
`;

// Insert into PROJECT_FILES before the closing bracket of the object
data = data.replace(/};\n\nexport const FILE_TREE/, newFiles + '\n};\n\nexport const FILE_TREE');

// Update FILE_TREE children
// For ai_gateway/core
data = data.replace(
  /{ path: 'ai_gateway\/core\/compressor\.py', name: 'compressor\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/core\/compressor\.py'\]\.desc }/,
  `{ path: 'ai_gateway/core/compressor.py', name: 'compressor.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/compressor.py'].desc },\n        { path: 'ai_gateway/core/router.py', name: 'router.py', type: 'file', description: PROJECT_FILES['ai_gateway/core/router.py'].desc }`
);

// For ai_gateway/registry
data = data.replace(
  /{ path: 'ai_gateway\/registry\/__init__\.py', name: '__init__\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/registry\/__init__\.py'\]\.desc }/,
  `{ path: 'ai_gateway/registry/__init__.py', name: '__init__.py', type: 'file', description: PROJECT_FILES['ai_gateway/registry/__init__.py'].desc },\n        { path: 'ai_gateway/registry/capability.py', name: 'capability.py', type: 'file', description: PROJECT_FILES['ai_gateway/registry/capability.py'].desc }`
);

// For ai_gateway/tests
data = data.replace(
  /{ path: 'ai_gateway\/tests\/test_adapters\.py', name: 'test_adapters\.py', type: 'file', description: PROJECT_FILES\['ai_gateway\/tests\/test_adapters\.py'\]\.desc }/,
  `{ path: 'ai_gateway/tests/test_adapters.py', name: 'test_adapters.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_adapters.py'].desc },\n        { path: 'ai_gateway/tests/test_router.py', name: 'test_router.py', type: 'file', description: PROJECT_FILES['ai_gateway/tests/test_router.py'].desc }`
);

fs.writeFileSync('src/data.ts', data);
console.log('Successfully updated src/data.ts');
