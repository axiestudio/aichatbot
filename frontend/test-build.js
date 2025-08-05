const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 DEVOPS TEAM - COMPREHENSIVE SYSTEM DIAGNOSTIC');
console.log('================================================');

// Test 1: Dependency Check
console.log('\n=== TEST 1: Dependency Verification ===');
try {
  console.log('Checking package.json dependencies...');
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const deps = Object.keys(packageJson.dependencies || {});
  const devDeps = Object.keys(packageJson.devDependencies || {});

  console.log(`✅ Dependencies: ${deps.length} production, ${devDeps.length} development`);
  console.log('Key dependencies:', deps.slice(0, 5).join(', '));
} catch (error) {
  console.log('❌ Package.json check failed:', error.message);
}

// Test 2: TypeScript Configuration
console.log('\n=== TEST 2: TypeScript Configuration ===');
try {
  const tsConfig = JSON.parse(fs.readFileSync('tsconfig.json', 'utf8'));
  console.log('✅ TypeScript config loaded');
  console.log(`Target: ${tsConfig.compilerOptions.target}`);
  console.log(`Module: ${tsConfig.compilerOptions.module}`);
  console.log(`Strict: ${tsConfig.compilerOptions.strict}`);
} catch (error) {
  console.log('❌ TypeScript config check failed:', error.message);
}

// Test 3: File Structure Validation
console.log('\n=== TEST 3: File Structure Validation ===');
const criticalFiles = [
  'src/App.tsx',
  'src/main.tsx',
  'src/components/ui/ProgressBar.tsx',
  'src/components/admin/AdvancedAnalytics.tsx',
  'src/components/admin/DocumentManager.tsx'
];

criticalFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file} - EXISTS`);
  } else {
    console.log(`❌ ${file} - MISSING`);
  }
});

// Test 4: TypeScript Compilation
console.log('\n=== TEST 4: TypeScript Compilation ===');
try {
  const tscOutput = execSync('npx tsc --noEmit --listFiles', {
    encoding: 'utf8',
    cwd: __dirname,
    stdio: 'pipe'
  });
  console.log('✅ TypeScript compilation successful');

  // Count compiled files
  const fileCount = (tscOutput.match(/\.tsx?/g) || []).length;
  console.log(`Compiled ${fileCount} TypeScript files`);

  fs.writeFileSync('tsc-success.log', tscOutput);
} catch (error) {
  console.log('❌ TypeScript compilation failed:');
  console.log('STDERR:', error.stderr);
  fs.writeFileSync('tsc-error.log', `STDERR:\n${error.stderr}\n\nSTDOUT:\n${error.stdout}`);

  // Parse specific errors
  if (error.stderr.includes('error TS')) {
    const errors = error.stderr.split('\n').filter(line => line.includes('error TS'));
    console.log(`Found ${errors.length} TypeScript errors:`);
    errors.slice(0, 3).forEach(err => console.log(`  - ${err.trim()}`));
  }
}

// Test 5: Vite Build
console.log('\n=== TEST 5: Vite Build ===');
try {
  const viteOutput = execSync('npx vite build --logLevel info', {
    encoding: 'utf8',
    cwd: __dirname,
    stdio: 'pipe'
  });
  console.log('✅ Vite build successful');

  // Check output size
  if (fs.existsSync('dist')) {
    const distFiles = fs.readdirSync('dist');
    console.log(`Generated ${distFiles.length} files in dist/`);
  }

  fs.writeFileSync('vite-success.log', viteOutput);
} catch (error) {
  console.log('❌ Vite build failed:');
  console.log('STDERR:', error.stderr);
  fs.writeFileSync('vite-error.log', `STDERR:\n${error.stderr}\n\nSTDOUT:\n${error.stdout}`);
}

// Test 6: Import/Export Validation
console.log('\n=== TEST 6: Import/Export Validation ===');
const uiComponents = [
  'src/components/ui/Button.tsx',
  'src/components/ui/Card.tsx',
  'src/components/ui/Input.tsx',
  'src/components/ui/Modal.tsx',
  'src/components/ui/Badge.tsx',
  'src/components/ui/ProgressBar.tsx',
  'src/components/ui/Textarea.tsx'
];

uiComponents.forEach(file => {
  if (fs.existsSync(file)) {
    const content = fs.readFileSync(file, 'utf8');
    const hasDefaultExport = content.includes('export default');
    const hasNamedExport = content.includes('export const') || content.includes('export function');

    console.log(`${file}: ${hasDefaultExport ? 'DEFAULT' : ''} ${hasNamedExport ? 'NAMED' : ''} exports`);
  }
});

console.log('\n🔍 DIAGNOSTIC COMPLETE');
console.log('======================');
console.log('Check generated log files for detailed analysis.');
console.log('- tsc-success.log / tsc-error.log');
console.log('- vite-success.log / vite-error.log');