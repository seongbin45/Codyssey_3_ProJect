/**
 * ========================================================
 * 지출 메모 입력 폼 & 결과 시트 자동 생성 스크립트
 * ========================================================
 * 
 * [사용 방법]
 * 1. https://script.google.com 접속
 * 2. "새 프로젝트" 클릭
 * 3. 기존 코드를 모두 지우고, 이 파일의 내용을 전체 복사-붙여넣기
 * 4. 상단 메뉴에서 "실행할 함수 선택" → "createExpenseForm" 선택
 * 5. ▶ 실행 버튼 클릭
 * 6. 최초 실행 시 Google 권한 승인 팝업 → "고급" → "프로젝트명(으)로 이동" → "허용"
 * 7. 실행 완료 후 "실행 로그"에서 폼 URL과 시트 URL 확인
 * 
 * [생성되는 항목]
 * - 구글 폼: "지출 메모 입력 폼" (장문형 질문 1개)
 * - 구글 시트: "지출 자동 분류 결과" (헤더 6열)
 * - 폼 응답이 자동으로 별도 시트에도 기록됨
 */

function createExpenseForm() {
  // =====================
  // 1. 구글 폼 생성
  // =====================
  var form = FormApp.create('지출 메모 입력 폼');
  form.setDescription(
    '자동화 워크플로우 테스트용 폼입니다.\n' +
    '아래에 지출 내역을 자유롭게 적어주세요.\n' +
    '예시: "점심 김치찌개 8000원", "택시비 15000원 강남→홍대"'
  );

  // 장문형(단락) 질문 추가
  var item = form.addParagraphTextItem();
  item.setTitle('지출 메모');
  item.setHelpText('지출 내역을 자유롭게 입력하세요. (예: 편의점에서 음료수 2000원)');
  item.setRequired(true);

  // 폼 설정: 응답 후 확인 메시지
  form.setConfirmationMessage('✅ 지출 메모가 접수되었습니다. 자동 분류가 진행됩니다.');

  // 폼 응답을 스프레드시트에 연결
  form.setDestination(FormApp.DestinationType.SPREADSHEET, createResponseSheet_(form));

  Logger.log('');
  Logger.log('========================================');
  Logger.log('✅ 구글 폼 생성 완료!');
  Logger.log('📋 폼 편집 URL: ' + form.getEditUrl());
  Logger.log('🔗 폼 응답 URL (이 링크를 공유하세요): ' + form.getPublishedUrl());
  Logger.log('========================================');

  // =====================
  // 2. 결과 기록용 시트 생성
  // =====================
  createResultSheet_();
}

/**
 * 폼 응답 연결용 스프레드시트 생성 (내부 함수)
 */
function createResponseSheet_(form) {
  var ss = SpreadsheetApp.create('지출 메모 입력 폼 (응답)');
  Logger.log('📊 폼 응답 시트 URL: ' + ss.getUrl());
  return ss.getId();
}

/**
 * 자동 분류 결과 기록용 스프레드시트 생성 (내부 함수)
 * Make/Zapier에서 데이터를 기록할 시트입니다.
 */
function createResultSheet_() {
  var ss = SpreadsheetApp.create('지출 자동 분류 결과');
  var sheet = ss.getActiveSheet();
  sheet.setName('분류 결과');

  // 헤더 설정 (6열)
  var headers = ['타임스탬프', '원본 메모', '카테고리', '금액', '요약', '특이사항'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);

  // 헤더 스타일링
  var headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setBackground('#4285F4');       // 구글 블루 배경
  headerRange.setFontColor('#FFFFFF');         // 흰색 글씨
  headerRange.setFontWeight('bold');           // 굵게
  headerRange.setHorizontalAlignment('center'); // 가운데 정렬

  // 열 너비 조정
  sheet.setColumnWidth(1, 160);  // 타임스탬프
  sheet.setColumnWidth(2, 300);  // 원본 메모
  sheet.setColumnWidth(3, 100);  // 카테고리
  sheet.setColumnWidth(4, 100);  // 금액
  sheet.setColumnWidth(5, 200);  // 요약
  sheet.setColumnWidth(6, 200);  // 특이사항

  // 첫 행 고정
  sheet.setFrozenRows(1);

  Logger.log('');
  Logger.log('========================================');
  Logger.log('✅ 결과 시트 생성 완료!');
  Logger.log('📊 결과 시트 URL: ' + ss.getUrl());
  Logger.log('========================================');
  Logger.log('');
  Logger.log('🎉 모든 준비가 완료되었습니다!');
  Logger.log('다음 단계: Make.com에서 워크플로우를 조립하세요.');
}
