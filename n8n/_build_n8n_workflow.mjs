import fs from 'fs';
import crypto from 'crypto';

const id = () => crypto.randomUUID();

const systemPrompt = `당신은 지출 내역 분석 비서입니다. 사용자의 메모를 분석하여 반드시 아래 JSON 구조로만 응답하세요. 마크다운 기호(\`\`\`)를 절대 포함하지 말고 순수 JSON 문자열만 출력하세요.

{
  "category": "식비, 교통비, 문화생활, 생필품, 기타, 분류불가 중 택1",
  "amount": "지출 금액을 0 이상의 정수로만 기재",
  "summary": "지출 내역을 10자 이내로 요약",
  "Classification": "분류 가능 여/부 표시"
}

분류 규칙:
1. 메모에서 금액을 명확히 추출할 수 있고 그 값이 0보다 크면, amount에 해당 숫자를 그대로 기재하고 category는 내용에 맞게 분류하세요.
2. 실제로 비용이 들지 않은 정당한 지출(예: "무료 쿠폰으로 커피 받음", "친구가 밥 사줌")은 amount를 0으로 기재하되, category는 "분류불가"가 아니라 내용에 맞는 정상 카테고리로 분류하세요.
3. 아래에 해당하는 경우에만 Classification를 "분류불가"로, amount는 0으로 기재하세요.
   - 금액이 음수로 표현된 경우 (예: "-1000", "마이너스 5000원")
   - 금액을 특정할 수 없거나 메모에 금액 자체가 없는 경우
   - 지출 내용과 금액의 연결이 불명확해 파싱을 신뢰할 수 없는 경우`;

const codeJs = `// Make parseJSONResponse 대응: OpenAI 응답 + Trigger 원본 합치기
const openai = $input.first().json;
const trigger = $('Google Sheets Trigger').first().json;

function pick(obj, keys) {
  for (const k of keys) {
    if (obj[k] !== undefined && obj[k] !== null && obj[k] !== '') return obj[k];
  }
  return undefined;
}

let parsed;
// simplify=true 시 output[].content[].text (json_object면 이미 객체일 수 있음)
if (Array.isArray(openai.output)) {
  for (const item of openai.output) {
    if (item?.type === 'message' && Array.isArray(item.content)) {
      for (const c of item.content) {
        if (c?.type === 'output_text') {
          parsed = typeof c.text === 'string' ? JSON.parse(c.text) : c.text;
        }
      }
    }
  }
}
if (!parsed) {
  const raw = openai.message?.content ?? openai.text ?? openai.content ?? openai;
  parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;
}

const timestamp = pick(trigger, ['타임스탬프', 'Timestamp', 'timestamp'])
  ?? Object.values(trigger)[0];
const memo = pick(trigger, ['지출 메모', 'Expense memo', 'memo'])
  ?? Object.values(trigger)[1];

return [{
  json: {
    timestamp,
    memo,
    category: parsed.category ?? '',
    amount: Number(parsed.amount) || 0,
    summary: parsed.summary ?? '',
    Classification: parsed.Classification ?? '',
  }
}];`;

function condNumber(left, op, right, cid) {
  return {
    id: cid,
    leftValue: left,
    rightValue: right,
    operator: {
      type: 'number',
      operation: op,
    },
  };
}

function condString(left, op, right, cid) {
  return {
    id: cid,
    leftValue: left,
    rightValue: right,
    operator: {
      type: 'string',
      operation: op,
    },
  };
}

function filterBlock(conditions, combinator = 'and') {
  return {
    options: {
      caseSensitive: true,
      leftValue: '',
      typeValidation: 'strict',
      version: 2,
    },
    conditions,
    combinator,
  };
}

function sheetsAppend(name, sheetName, position, nodeId) {
  return {
    parameters: {
      operation: 'append',
      documentId: {
        __rl: true,
        value: '***RESULT_SHEET_ID***',
        mode: 'list',
        cachedResultName: '지출 자동 분류 결과',
        cachedResultUrl:
          'https://docs.google.com/spreadsheets/d/***RESULT_SHEET_ID***/edit',
      },
      sheetName: {
        __rl: true,
        value: sheetName,
        mode: 'name',
      },
      columns: {
        mappingMode: 'defineBelow',
        value: {
          타임스탬프: '={{ $json.timestamp }}',
          '원본 메모': '={{ $json.memo }}',
          카테고리: '={{ $json.category }}',
          금액: '={{ $json.amount }}',
          요약: '={{ $json.summary }}',
          특이사항: '={{ $json.Classification }}',
        },
        matchingColumns: [],
        schema: [
          {
            id: '타임스탬프',
            displayName: '타임스탬프',
            required: false,
            defaultMatch: false,
            display: true,
            type: 'string',
            canBeUsedToMatch: true,
          },
          {
            id: '원본 메모',
            displayName: '원본 메모',
            required: false,
            defaultMatch: false,
            display: true,
            type: 'string',
            canBeUsedToMatch: true,
          },
          {
            id: '카테고리',
            displayName: '카테고리',
            required: false,
            defaultMatch: false,
            display: true,
            type: 'string',
            canBeUsedToMatch: true,
          },
          {
            id: '금액',
            displayName: '금액',
            required: false,
            defaultMatch: false,
            display: true,
            type: 'string',
            canBeUsedToMatch: true,
          },
          {
            id: '요약',
            displayName: '요약',
            required: false,
            defaultMatch: false,
            display: true,
            type: 'string',
            canBeUsedToMatch: true,
          },
          {
            id: '특이사항',
            displayName: '특이사항',
            required: false,
            defaultMatch: false,
            display: true,
            type: 'string',
            canBeUsedToMatch: true,
          },
        ],
        attemptToConvertTypes: false,
        convertFieldsToString: false,
      },
      options: {
        cellFormat: 'USER_ENTERED',
      },
    },
    type: 'n8n-nodes-base.googleSheets',
    typeVersion: 4.7,
    position,
    id: nodeId,
    name,
    credentials: {
      googleSheetsOAuth2Api: {
        id: 'TO_SELECT_IN_UI',
        name: 'Google Sheets account (OAuth2 — Trigger와 동일 Google 계정)',
      },
    },
  };
}

const ids = {
  trigger: 'd617ce96-a059-43e5-b769-329c6c5e9adf',
  openai: 'f91f4e67-d8c8-4c80-b6be-71bfa34ab83b',
  code: id(),
  sw: id(),
  high: id(),
  normal: id(),
  review: id(),
  note: id(),
};

const workflow = {
  name: '지출 메모 자동 분류 (n8n)',
  nodes: [
    {
      parameters: {
        content:
          '## Make 1:1 대응\n1. **OpenAI** credential 연결 확인\n2. Append 3개 노드: **Google Sheets OAuth2** credential 필요 (Trigger OAuth와 타입이 다름 → 같은 Client ID/Secret으로 새 credential 만들고 Sign in)\n3. 결과 시트 탭명: `고액 지출 분류 결과` / `일반 지출 분류 결과` / `검토 필요`\n4. Trigger 테스트 후 전체 실행',
        height: 320,
        width: 380,
        color: 5,
      },
      type: 'n8n-nodes-base.stickyNote',
      typeVersion: 1,
      position: [-320, -120],
      id: ids.note,
      name: 'Setup notes',
    },
    {
      parameters: {
        pollTimes: { item: [{ mode: 'everyMinute' }] },
        documentId: {
          __rl: true,
          value: '***RESPONSE_SHEET_ID***',
          mode: 'list',
          cachedResultName: '지출 메모 입력 폼 (응답)',
          cachedResultUrl:
            'https://docs.google.com/spreadsheets/d/***RESPONSE_SHEET_ID***/edit',
        },
        sheetName: {
          __rl: true,
          value: '***SHEET_GID***',
          mode: 'list',
          cachedResultName: 'Form Responses 1',
          cachedResultUrl:
            'https://docs.google.com/spreadsheets/d/***RESPONSE_SHEET_ID***/edit#gid=***SHEET_GID***',
        },
        event: 'rowAdded',
        options: {},
      },
      type: 'n8n-nodes-base.googleSheetsTrigger',
      typeVersion: 1,
      position: [0, 16],
      id: ids.trigger,
      name: 'Google Sheets Trigger',
      credentials: {
        googleSheetsTriggerOAuth2Api: {
          id: 'cfnGyrJpbIQqNpAO',
          name: 'Google Sheets Trigger account',
        },
      },
    },
    {
      parameters: {
        modelId: {
          __rl: true,
          mode: 'id',
          value: 'gpt-4.1',
        },
        responses: {
          values: [
            {
              type: 'text',
              role: 'system',
              content: systemPrompt,
            },
            {
              type: 'text',
              role: 'user',
              content:
                "={{ $json['지출 메모'] ?? $json['Expense memo'] ?? Object.values($json)[1] }}",
            },
          ],
        },
        simplify: true,
        builtInTools: {},
        options: {
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
        },
      },
      type: '@n8n/n8n-nodes-langchain.openAi',
      typeVersion: 2.3,
      position: [280, 16],
      id: ids.openai,
      name: 'OpenAI 파싱',
      credentials: {
        openAiApi: {
          id: 'NdURDYGp8WsvhqUH',
          name: 'OpenAI account',
        },
      },
    },
    {
      parameters: {
        mode: 'runOnceForAllItems',
        language: 'javaScript',
        jsCode: codeJs,
      },
      type: 'n8n-nodes-base.code',
      typeVersion: 2,
      position: [560, 16],
      id: ids.code,
      name: 'JSON 정규화',
    },
    {
      parameters: {
        mode: 'rules',
        rules: {
          values: [
            {
              conditions: filterBlock([
                condNumber('={{ $json.amount }}', 'gte', 50000, id()),
              ]),
              renameOutput: true,
              outputKey: '고액지출',
            },
            {
              conditions: filterBlock(
                [
                  condNumber('={{ $json.amount }}', 'lt', 50000, id()),
                  condString(
                    '={{ $json.Classification }}',
                    'notEquals',
                    '분류불가',
                    id(),
                  ),
                ],
                'and',
              ),
              renameOutput: true,
              outputKey: '일반지출',
            },
            {
              conditions: filterBlock(
                [
                  condNumber('={{ $json.amount }}', 'equals', 0, id()),
                  condString(
                    '={{ $json.Classification }}',
                    'equals',
                    '분류불가',
                    id(),
                  ),
                ],
                'and',
              ),
              renameOutput: true,
              outputKey: '미분류',
            },
          ],
        },
        options: {
          fallbackOutput: 'extra',
        },
      },
      type: 'n8n-nodes-base.switch',
      typeVersion: 3.3,
      position: [820, 16],
      id: ids.sw,
      name: 'Router 3분기',
    },
    sheetsAppend(
      '고액 지출 기록',
      '고액 지출 분류 결과',
      [1120, -160],
      ids.high,
    ),
    sheetsAppend(
      '일반 지출 기록',
      '일반 지출 분류 결과',
      [1120, 16],
      ids.normal,
    ),
    sheetsAppend('검토 필요 기록', '검토 필요', [1120, 200], ids.review),
  ],
  pinData: {},
  connections: {
    'Google Sheets Trigger': {
      main: [[{ node: 'OpenAI 파싱', type: 'main', index: 0 }]],
    },
    'OpenAI 파싱': {
      main: [[{ node: 'JSON 정규화', type: 'main', index: 0 }]],
    },
    'JSON 정규화': {
      main: [[{ node: 'Router 3분기', type: 'main', index: 0 }]],
    },
    'Router 3분기': {
      main: [
        [{ node: '고액 지출 기록', type: 'main', index: 0 }],
        [{ node: '일반 지출 기록', type: 'main', index: 0 }],
        [{ node: '검토 필요 기록', type: 'main', index: 0 }],
        [],
      ],
    },
  },
  active: false,
  settings: {
    executionOrder: 'v1',
    binaryMode: 'separate',
    availableInMCP: false,
  },
  versionId: id(),
  meta: {
    templateCredsSetupCompleted: true,
    instanceId:
      '992248aea2934574552108c3309f14b259aab3915df23f1fd1750968247afad5',
  },
  nodeGroups: [],
  id: 'v7swu5iLt6oYJM5r',
  tags: [],
};

const out1 =
  'C:\\Users\\seong\\Downloads\\지출 메모 자동 분류 (n8n).json';
const out2 =
  'C:\\Users\\seong\\Downloads\\Codyssey_3_ProJect\\Codyssey_3_ProJect\\n8n_지출_메모_자동_분류.workflow.json';
fs.writeFileSync(out1, JSON.stringify(workflow, null, 2), 'utf8');
fs.writeFileSync(out2, JSON.stringify(workflow, null, 2), 'utf8');
console.log('wrote', out1);
console.log('wrote', out2);
console.log(
  'nodes',
  workflow.nodes.map((n) => n.name + ' / ' + n.type).join('\n'),
);
