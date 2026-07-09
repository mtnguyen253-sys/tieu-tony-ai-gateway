const fs = require('fs');

const esc = (str) => str.replace(/\\/g, '\\\\').replace(/\`/g, '\\\`').replace(/\\$/g, '\\\\$');

function updateFileInTree(fileTreePath, sourceFilePath) {
    let data = fs.readFileSync('src/data.ts', 'utf8');
    const content = fs.readFileSync(sourceFilePath, 'utf8');
    const escapedContent = esc(content);
    
    // Use regex to replace the content block for the specific file
    const regex = new RegExp(`('${fileTreePath}':\\s*\\{\\s*content:\\s*)\`[\\s\\S]*?\`(,\\s*desc:\\s*'.*?'\\s*\\})`);
    
    if (regex.test(data)) {
        data = data.replace(regex, `$1\`${escapedContent}\`$2`);
        fs.writeFileSync('src/data.ts', data);
        console.log(`Updated ${fileTreePath} in src/data.ts`);
    } else {
        console.log(`Could not find entry for ${fileTreePath} in src/data.ts`);
    }
}

updateFileInTree('ai_gateway/core/circuit_breaker.py', 'ai_gateway/core/circuit_breaker.py');
updateFileInTree('ai_gateway/core/executor.py', 'ai_gateway/core/executor.py');
updateFileInTree('ai_gateway/tests/test_circuit_breaker.py', 'ai_gateway/tests/test_circuit_breaker.py');
updateFileInTree('ai_gateway/tests/test_executor.py', 'ai_gateway/tests/test_executor.py');
