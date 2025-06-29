const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Starting Vercel build process...');

// Install frontend dependencies and build
console.log('Installing frontend dependencies...');
execSync('cd frontend-vite && npm install', { stdio: 'inherit' });

console.log('Building frontend...');
execSync('cd frontend-vite && npm run build', { stdio: 'inherit' });

// Copy frontend build to the output directory
const distDir = path.join(process.cwd(), '.vercel', 'output', 'static');
const frontendDist = path.join(process.cwd(), 'frontend-vite', 'dist');

if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

// Copy files from frontend dist to vercel output
console.log('Copying frontend files...');
const copyRecursiveSync = (src, dest) => {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();
  
  if (isDirectory) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest);
    }
    fs.readdirSync(src).forEach(childItemName => {
      copyRecursiveSync(
        path.join(src, childItemName),
        path.join(dest, childItemName)
      );
    });
  } else {
    fs.copyFileSync(src, dest);
  }
};

copyRecursiveSync(frontendDist, distDir);

console.log('Vercel build completed successfully!');
