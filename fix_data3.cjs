const fs = require('fs');
let data = fs.readFileSync('src/data.ts', 'utf8');

data = data.replace(
  "  }\n  'ai_gateway/registry/capability.py': {",
  "  },\n  'ai_gateway/registry/capability.py': {"
);

fs.writeFileSync('src/data.ts', data);
