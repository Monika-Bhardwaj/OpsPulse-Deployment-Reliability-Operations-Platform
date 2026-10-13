import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('HTML entry point has the OpsPulse page title', async () => {
  const html = await read('../index.html');

  assert.match(html, /OpsPulse/);
  assert.match(html, /Reliability Operations Platform/);
});

test('HTML entry point provides the React root element', async () => {
  const html = await read('../index.html');

  assert.match(html, /<div id="root"><\/div>/);
  assert.match(html, /src="\/src\/main\.jsx"/);
});

test('React application defines the backend API prefix', async () => {
  const source = await read('../src/main.jsx');

  assert.match(source, /const API = ['"]\/api['"]/);
  assert.match(source, /async function apiFetch/);
});

test('React application includes deployment and incident workflows', async () => {
  const source = await read('../src/main.jsx');

  assert.match(source, /Record a Deployment/);
  assert.match(source, /Report an Incident/);
  assert.match(source, /\/deployments/);
  assert.match(source, /\/incidents/);
});

test('React application handles API errors and loading states', async () => {
  const source = await read('../src/main.jsx');

  assert.match(source, /if \(!res\.ok\)/);
  assert.match(source, /Request failed/);
  assert.match(source, /Saving…/);
});
