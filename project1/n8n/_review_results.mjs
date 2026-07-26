import fs from 'fs';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const XLSX = require('../n8n-runtime/node_modules/xlsx');
const dir = 'C:/Users/seong/Downloads/결과';

const wf = JSON.parse(
  fs.readFileSync(dir + '/지출 메모 자동 분류 (n8n).json', 'utf8'),
);
console.log('=== WORKFLOW ===');
console.log('name', wf.name, 'active', wf.active, 'nodes', wf.nodes.length);
for (const n of wf.nodes) {
  const bits = [n.name, n.type.split('.').pop()];
  if (
    n.name.includes('기록') ||
    (n.type.includes('googleSheets') && !n.type.includes('Trigger'))
  ) {
    const p = n.parameters || {};
    bits.push(
      'doc=' + p.documentId?.mode + ':' + String(p.documentId?.value).slice(0, 20),
    );
    bits.push('sheet=' + p.sheetName?.value);
    bits.push('useAppend=' + p.options?.useAppend);
    bits.push('cols=' + Object.keys(p.columns?.value || {}).join('|'));
  }
  if (n.name === 'JSON 정규화') bits.push('codeMode=' + n.parameters?.mode);
  if (n.name === 'OpenAI 파싱') {
    bits.push(
      'jsonFmt=' +
        n.parameters?.options?.textFormat?.textOptions?.[0]?.type,
    );
  }
  console.log(' -', bits.join(' | '));
}

function dump(path) {
  const wb = XLSX.readFile(path);
  console.log('\n===', path.split('/').pop(), '===');
  for (const name of wb.SheetNames) {
    const rows = XLSX.utils.sheet_to_json(wb.Sheets[name], {
      defval: '',
      raw: false,
    });
    console.log('\n[' + name + '] rows=' + rows.length);
    if (!rows.length) continue;
    console.log('headers:', Object.keys(rows[0]).join(' | '));
    const recent = rows.filter((r) => {
      const s = JSON.stringify(r);
      return (
        s.includes('7/23') ||
        s.includes('2026-07-23') ||
        s.includes('n8n') ||
        s.includes('테스트') ||
        s.includes('검증') ||
        s.includes('노트북') ||
        s.includes('150000') ||
        s.includes('3500')
      );
    });
    console.log('recent/test-like rows:', recent.length);
    for (const r of recent) console.log('  *', JSON.stringify(r));
    console.log('last 8:');
    for (const r of rows.slice(-8)) console.log('  ', JSON.stringify(r));
  }
}
dump(dir + '/지출 메모 입력 폼 (응답).xlsx');
dump(dir + '/지출 자동 분류 결과.xlsx');

const log = fs.readFileSync(dir + '/llogg.txt', 'utf8');
const plain = log
  .replace(/<style[\s\S]*?<\/style>/gi, ' ')
  .replace(/<script[\s\S]*?<\/script>/gi, ' ')
  .replace(/<[^>]+>/g, '\n');
const lines = plain
  .split(/\n+/)
  .map((s) => s.trim())
  .filter(Boolean);
const interesting = lines.filter(
  (l) =>
    /Success|Failed|Error|고액|일반|검토|기록|정규화|Router|Trigger|파싱|검증|150000|3500|120000|노트북|amount|분류/.test(
      l,
    ) && l.length < 220,
);
console.log('\n=== LOG interesting (unique) ===');
[...new Set(interesting)].slice(0, 120).forEach((l) => console.log(l));
console.log('\nlog size', log.length);
