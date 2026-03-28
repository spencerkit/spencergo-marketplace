#!/usr/bin/env node
const { spawnSync } = require('node:child_process');
const path = require('node:path');

const buildCommand = (svgPath, pngPath) => ['resvg', path.resolve(svgPath), path.resolve(pngPath)];

const main = () => {
  const [svgPath, pngPath] = process.argv.slice(2);
  if (!svgPath || !pngPath) {
    console.error('Usage: node export_report_png.js <report.svg> <report.png>');
    process.exit(1);
  }

  const command = buildCommand(svgPath, pngPath);
  const result = spawnSync(command[0], command.slice(1), {
    encoding: 'utf-8',
    stdio: 'inherit',
  });

  if (result.error) {
    console.error(result.error.message);
    process.exit(1);
  }

  process.exit(result.status ?? 1);
};

main();
