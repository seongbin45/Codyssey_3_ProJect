/**
 * Append 안정화 패치
 * - 입력: Downloads 최종 워크플로우 JSON
 * - 출력: Downloads + 프로젝트 복사본
 */
import fs from 'fs';

const SRC = 'C:\\Users\\seong\\Downloads\\지출 메모 자동 분류 (n8n).json';
const OUTS = [
  SRC,
  'C:\\Users\\seong\\Downloads\\Codyssey_3_ProJect\\Codyssey_3_ProJect\\n8n_지출_메모_자동_분류.workflow.json',
  'C:\\Users\\seong\\Downloads\\Codyssey_3_ProJect\\n8n_지출_메모_자동_분류.workflow.json',
];

const RESULT_SHEET_ID = '***RESULT_SHEET_ID***';
const RESULT_SHEET_NAME = '지출 자동 분류 결과';
const RESULT_SHEET_URL = `https://docs.google.com/spreadsheets/d/${RESULT_SHEET_ID}/edit`;

const TAB = {
  high: '고액 지출 분류 결과',
  normal: '일반 지출 분류 결과',
  review: '검토 필요',
};

const HEADER_SCHEMA = [
  '타임스탬프',
  '원본 메모',
  '카테고리',
  '금액',
  '요약',
  '특이사항',
].map((name) => ({
  id: name,
  displayName: name,
  required: false,
  defaultMatch: false,
  display: true,
  type: 'string',
  canBeUsedToMatch: true,
  removed: false,
}));

/** defineBelow 매핑 — 표현식을 문자열로 강제해 빈 셀 방지 */
const COLUMN_VALUE = {
  타임스탬프: "={{ String($json.timestamp ?? $json['타임스탬프'] ?? '') }}",
  '원본 메모': "={{ String($json.memo ?? $json['원본 메모'] ?? '') }}",
  카테고리: "={{ String($json.category ?? $json['카테고리'] ?? '') }}",
  금액: "={{ String($json.amount ?? $json['금액'] ?? '') }}",
  요약: "={{ String($json.summary ?? $json['요약'] ?? '') }}",
  특이사항:
    "={{ String($json.Classification ?? $json['특이사항'] ?? '') }}",
};

const CODE_JS = [
  '// 각 아이템마다 실행 (runOnceForEachItem)',
  '// OpenAI 응답 + Trigger 원본 → Switch/Append용 필드',
  'const openai = $json;',
  "const triggerItem = $('Google Sheets Trigger1').item;",
  'const trigger = triggerItem?.json ?? {};',
  '',
  'function pick(obj, keys) {',
  "  if (!obj || typeof obj !== 'object') return undefined;",
  '  for (const k of keys) {',
  "    if (obj[k] !== undefined && obj[k] !== null && String(obj[k]).trim() !== '') {",
  '      return obj[k];',
  '    }',
  '  }',
  '  return undefined;',
  '}',
  '',
  'function extractParsed(data) {',
  '  if (Array.isArray(data.output)) {',
  '    for (const item of data.output) {',
  "      if (item?.type === 'message' && Array.isArray(item.content)) {",
  '        for (const c of item.content) {',
  "          if (c?.type === 'output_text') {",
  "            if (typeof c.text === 'string') {",
  '              try { return JSON.parse(c.text); } catch (e) { /* continue */ }',
  '            }',
  "            if (c.text && typeof c.text === 'object') return c.text;",
  '          }',
  '        }',
  '      }',
  '    }',
  '  }',
  '  const raw = data.message?.content ?? data.text ?? data.content;',
  "  if (typeof raw === 'string') {",
  '    try { return JSON.parse(raw.trim()); } catch (e) { /* continue */ }',
  '  }',
  '  if (data.category !== undefined || data.amount !== undefined) return data;',
  "  if (raw && typeof raw === 'object') return raw;",
  "  throw new Error('OpenAI JSON parse failed: ' + JSON.stringify(data).slice(0, 300));",
  '}',
  '',
  'const parsed = extractParsed(openai);',
  "const timestamp = pick(trigger, ['Timestamp', '타임스탬프', 'timestamp'])",
  "  ?? pick(openai, ['Timestamp', '타임스탬프'])",
  '  ?? new Date().toISOString();',
  "const memo = pick(trigger, ['지출 메모', 'Expense memo', 'memo'])",
  "  ?? pick(openai, ['지출 메모', 'memo'])",
  "  ?? '';",
  "const amountNum = Number(String(parsed.amount ?? '').replace(/,/g, '').trim());",
  'const amount = Number.isFinite(amountNum) ? amountNum : 0;',
  "const category = parsed.category ?? '';",
  "const summary = parsed.summary ?? '';",
  "const Classification = String(parsed.Classification ?? '').trim();",
  '',
  'return {',
  '  json: {',
  '    timestamp,',
  '    memo,',
  '    category,',
  '    amount,',
  '    summary,',
  '    Classification,',
  "    '타임스탬프': timestamp,",
  "    '원본 메모': memo,",
  "    '카테고리': category,",
  "    '금액': amount,",
  "    '요약': summary,",
  "    '특이사항': Classification,",
  '  },',
  '};',
].join('\n');

function patchDocumentId(doc) {
  return {
    __rl: true,
    value: RESULT_SHEET_ID,
    mode: 'id', // list 캐시 의존 제거
    cachedResultName: RESULT_SHEET_NAME,
    cachedResultUrl: RESULT_SHEET_URL,
  };
}

function patchSheetName(title) {
  return {
    __rl: true,
    value: title,
    mode: 'name',
  };
}

function patchAppendNode(node, tabTitle) {
  const p = node.parameters || {};
  p.resource = 'sheet';
  p.operation = 'append';
  p.documentId = patchDocumentId(p.documentId);
  p.sheetName = patchSheetName(tabTitle);
  p.columns = {
    mappingMode: 'defineBelow',
    value: { ...COLUMN_VALUE },
    matchingColumns: [],
    schema: HEADER_SCHEMA.map((s) => ({ ...s })),
    attemptToConvertTypes: false,
    convertFieldsToString: true, // 숫자/객체 강제 문자열
  };
  p.options = {
    ...(p.options || {}),
    cellFormat: 'USER_ENTERED',
    useAppend: true, // values:append API — 빈 행 탐색 실패 회피
    locationDefine: {
      values: {
        headerRow: 1,
      },
    },
  };
  node.parameters = p;
  return node;
}

const raw = fs.readFileSync(SRC, 'utf8');
const workflow = JSON.parse(raw);
const notes = [];

for (const node of workflow.nodes) {
  // --- Code: 아이템 단위 처리 ---
  if (node.type === 'n8n-nodes-base.code' || node.name === 'JSON 정규화') {
    node.parameters = {
      mode: 'runOnceForEachItem',
      language: 'javaScript',
      jsCode: CODE_JS,
    };
    notes.push('JSON 정규화 → runOnceForEachItem + 파싱 강화 + 한글 헤더 필드 병행');
  }

  // --- OpenAI: JSON 모드 복구 + user role ---
  if (node.type?.includes('openAi') || node.name === 'OpenAI 파싱') {
    const responses = node.parameters.responses?.values || [];
    for (const msg of responses) {
      if (msg.role === 'system') continue;
      // user 메시지 role 누락 보정
      if (!msg.role || msg.role === '') {
        msg.role = 'user';
        msg.type = msg.type || 'text';
        notes.push('OpenAI user 메시지 role=user 보정');
      }
    }
    node.parameters.simplify = true;
    node.parameters.options = {
      ...(node.parameters.options || {}),
      maxTokens: 2048,
      temperature: 1,
      textFormat: {
        textOptions: [
          {
            type: 'json_object',
            verbosity: 'medium',
          },
        ],
      },
    };
    // model id 모드 유지
    if (node.parameters.modelId) {
      node.parameters.modelId = {
        __rl: true,
        mode: 'id',
        value: node.parameters.modelId.value || 'gpt-4.1',
      };
    }
    notes.push('OpenAI textFormat json_object 복구');
  }

  // --- Sheets Append x3 ---
  if (node.name === '고액 지출 기록') {
    patchAppendNode(node, TAB.high);
    notes.push('고액 지출 기록: documentId=id, useAppend, 컬럼 매핑 강화');
  }
  if (node.name === '일반 지출 기록') {
    patchAppendNode(node, TAB.normal);
    notes.push('일반 지출 기록: documentId=id, useAppend, 컬럼 매핑 강화');
  }
  if (node.name === '검토 필요 기록') {
    patchAppendNode(node, TAB.review);
    notes.push('검토 필요 기록: documentId=id, useAppend, 컬럼 매핑 강화');
  }

  // Trigger documentId도 id 모드로 고정 (선택)
  if (node.type === 'n8n-nodes-base.googleSheetsTrigger') {
    if (node.parameters.documentId) {
      node.parameters.documentId.mode = 'id';
      node.parameters.documentId.value =
        node.parameters.documentId.value ||
        '***RESPONSE_SHEET_ID***';
    }
    notes.push('Trigger documentId mode=id 고정');
  }
}

// sticky note 업데이트
const sticky = workflow.nodes.find((n) => n.type === 'n8n-nodes-base.stickyNote');
if (sticky) {
  sticky.parameters.content = `## Append 안정화 패치
1. Sheets: documentId **id 모드**, **useAppend=true**, 헤더 1행 고정
2. 컬럼: 타임스탬프~특이사항 6열 문자열 매핑
3. Code: **아이템마다** 파싱 (first() 버그 제거)
4. OpenAI: **json_object** 복구

Import 후 Append 3노드 credential = Google Sheets account 확인
테스트: n8n검증-고액 150000 / 일반 3500 / 미분류 -1000`;
}

const json = JSON.stringify(workflow, null, 2);
for (const out of OUTS) {
  fs.writeFileSync(out, json, 'utf8');
  console.log('wrote', out, json.length);
}

console.log('\\nPatch notes:');
for (const n of notes) console.log(' -', n);

// sanity
const sheets = workflow.nodes.filter((n) =>
  ['고액 지출 기록', '일반 지출 기록', '검토 필요 기록'].includes(n.name),
);
for (const n of sheets) {
  console.log('\\n', n.name);
  console.log('  doc mode', n.parameters.documentId.mode, n.parameters.documentId.value);
  console.log('  sheet', n.parameters.sheetName.value);
  console.log('  useAppend', n.parameters.options.useAppend);
  console.log('  cols', Object.keys(n.parameters.columns.value).join(', '));
}
const code = workflow.nodes.find((n) => n.name === 'JSON 정규화');
console.log('\\nCode mode', code?.parameters?.mode);
const oai = workflow.nodes.find((n) => n.name === 'OpenAI 파싱');
console.log(
  'OpenAI json format',
  oai?.parameters?.options?.textFormat?.textOptions?.[0]?.type,
);
