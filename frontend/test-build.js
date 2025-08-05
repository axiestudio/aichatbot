const { execSync } = require('child_process');
const fs = require('fs');

console.log('🔍 Testing TypeScript compilation...');

try {
  // Test TypeScript compilation only
  console.log('Step 1: Running tsc --noEmit...');
  const tscOutput = execSync('npx tsc --noEmit --listFiles', {
    encoding: 'utf8',
    cwd: __dirname,
    stdio: 'pipe'
  });
  console.log('✅ TypeScript compilation successful');

  // Write output to file for analysis
  fs.writeFileSync('tsc-success.log', tscOutput);

} catch (error) {
  console.log('❌ TypeScript compilation failed:');
  console.log(error.stdout);
  console.log(error.stderr);

  // Write error to file for analysis
  fs.writeFileSync('tsc-error.log', `STDOUT:\n${error.stdout}\n\nSTDERR:\n${error.stderr}`);

  process.exit(1);
}