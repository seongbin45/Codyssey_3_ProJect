/**
 * ========================================================
 * FinFit 문의 접수 폼 & 결과 시트 자동 생성 스크립트 (프로젝트2)
 * ========================================================
 *
 * [사용 방법]
 * 1. https://script.google.com 접속
 * 2. "새 프로젝트" 클릭
 * 3. 기존 코드를 모두 지우고, 이 파일의 내용을 전체 복사-붙여넣기
 * 4. 상단 메뉴에서 "실행할 함수 선택" → "createInquiryForm" 선택
 * 5. ▶ 실행 버튼 클릭
 * 6. 최초 실행 시 Google 권한 승인 팝업 → "고급" → "프로젝트명(으)로 이동" → "허용"
 * 7. 실행 완료 후 "실행 로그"에서 폼 URL과 시트 URL 확인
 *
 * [생성되는 항목]
 * - 구글 폼: "FinFit 문의 접수 폼" (문의 내용 장문형 1개 + 연락처 단답형 1개)
 * - 구글 시트: "FinFit 문의 자동 분류 결과" (탭 2개: 긴급 문의 / 일반 문의, 각 헤더 6열)
 * - 폼 응답이 자동으로 별도 응답 시트에도 기록됨 (Make Trigger 대상)
 *
 * [주의] 폼 질문 순서를 바꾸지 마세요.
 *   1번째 질문(문의 내용) → 응답 시트 B열 → Blueprint의 {{1.`1`}}
 *   2번째 질문(연락처)   → 응답 시트 C열 → Blueprint의 {{1.`2`}}
 */

function createInquiryForm() {
  // =====================
  // 1. 구글 폼 생성
  // =====================
  var form = FormApp.create('FinFit 문의 접수 폼');
  form.setDescription(
    'FinFit 팀 문의/피드백 자동 분류 워크플로우용 폼입니다.\n' +
    '문의하실 내용을 자유롭게 적어주세요.\n' +
    '예시: "결제가 안 돼요, 지금 당장 필요해요", "다크모드 지원 언제 되나요?"'
  );

  // 1번 질문: 문의 내용 (장문형, 필수)
  var contentItem = form.addParagraphTextItem();
  contentItem.setTitle('문의 내용');
  contentItem.setHelpText('문의하실 내용을 자유롭게 입력하세요.');
  contentItem.setRequired(true);

  // 2번 질문: 연락처 (단답형, 선택)
  var contactItem = form.addTextItem();
  contactItem.setTitle('연락처');
  contactItem.setHelpText('회신 받으실 이메일 또는 연락처 (선택 입력)');
  contactItem.setRequired(false);

  // 폼 설정: 응답 후 확인 메시지
  form.setConfirmationMessage('✅ 문의가 접수되었습니다. 담당자 확인 후 순차 안내드립니다.');

  // 폼 응답을 스프레드시트에 연결
  form.setDestination(FormApp.DestinationType.SPREADSHEET, createResponseSheet_(form));

  Logger.log('');
  Logger.log('========================================');
  Logger.log('✅ 구글 폼 생성 완료!');
  Logger.log('📋 폼 편집 URL: ' + form.getEditUrl());
  Logger.log('🔗 폼 응답 URL (이 링크를 공유하세요): ' + form.getPublishedUrl());
  Logger.log('========================================');

  // =====================
  // 2. 결과 기록용 시트 생성 (탭 2개)
  // =====================
  createResultSheet_();
}

/**
 * 폼 응답 연결용 스프레드시트 생성 (내부 함수)
 */
function createResponseSheet_(form) {
  var ss = SpreadsheetApp.create('FinFit 문의 접수 폼 (응답)');
  Logger.log('📊 폼 응답 시트 URL: ' + ss.getUrl());
  return ss.getId();
}

/**
 * 자동 분류 결과 기록용 스프레드시트 생성 (내부 함수)
 * Make에서 분기별로 이 두 탭에 각각 기록합니다.
 */
function createResultSheet_() {
  var ss = SpreadsheetApp.create('FinFit 문의 자동 분류 결과');
  var headers = ['타임스탬프', '원본 문의', '긴급도', '카테고리', '요약', '연락처'];

  // 기본 시트를 "긴급 문의" 탭으로 사용
  var urgentSheet = ss.getActiveSheet();
  urgentSheet.setName('긴급 문의');
  setupHeader_(urgentSheet, headers);

  // "일반 문의" 탭 추가
  var normalSheet = ss.insertSheet('일반 문의');
  setupHeader_(normalSheet, headers);

  Logger.log('');
  Logger.log('========================================');
  Logger.log('✅ 결과 시트 생성 완료! (탭: 긴급 문의 / 일반 문의)');
  Logger.log('📊 결과 시트 URL: ' + ss.getUrl());
  Logger.log('========================================');
  Logger.log('');
  Logger.log('🎉 모든 준비가 완료되었습니다!');
  Logger.log('다음 단계: Make.com에서 Blueprint를 Import하고 연결을 재매핑하세요.');
}

/**
 * 시트 탭 하나에 헤더 6열을 세팅 (내부 함수)
 */
function setupHeader_(sheet, headers) {
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);

  var headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setBackground('#4285F4');
  headerRange.setFontColor('#FFFFFF');
  headerRange.setFontWeight('bold');
  headerRange.setHorizontalAlignment('center');

  sheet.setColumnWidth(1, 160); // 타임스탬프
  sheet.setColumnWidth(2, 300); // 원본 문의
  sheet.setColumnWidth(3, 90);  // 긴급도
  sheet.setColumnWidth(4, 100); // 카테고리
  sheet.setColumnWidth(5, 220); // 요약
  sheet.setColumnWidth(6, 160); // 연락처

  sheet.setFrozenRows(1);
}