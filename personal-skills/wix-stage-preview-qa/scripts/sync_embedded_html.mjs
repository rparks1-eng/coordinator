#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { gzipSync, gunzipSync } from 'node:zlib';

const [htmlPath, widgetPath, constantName = 'SOURCE_GZIP_BASE64'] = process.argv.slice(2);
if (!htmlPath || !widgetPath) {
  console.error('Usage: sync_embedded_html.mjs <html> <widget> [constantName]');
  process.exit(2);
}

const html = readFileSync(htmlPath);
const widget = readFileSync(widgetPath, 'utf8');
const pattern = new RegExp(`(const\\s+${constantName}\\s*=\\s*['\"])([^'\"]+)(['\"])`);
if (!pattern.test(widget)) {
  console.error(`Could not find ${constantName} in ${widgetPath}`);
  process.exit(3);
}

const encoded = gzipSync(html, { level: 9 }).toString('base64');
const next = widget.replace(pattern, `$1${encoded}$3`);
writeFileSync(widgetPath, next);

const embeddedMatch = next.match(pattern);
const decoded = gunzipSync(Buffer.from(embeddedMatch[2], 'base64'));
const sha = (value) => createHash('sha256').update(value).digest('hex');
const exact = decoded.equals(html);

console.log(JSON.stringify({ htmlSha256: sha(html), embeddedSha256: sha(decoded), exact }, null, 2));
if (!exact) process.exit(4);
