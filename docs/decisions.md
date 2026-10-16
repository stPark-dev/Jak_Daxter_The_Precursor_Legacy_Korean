# 전략 결정 기록

## D-001 대상 플랫폼: OpenGOAL (PC 포트)

- **state**: adopted (2026-10-15)
- **question**: 잭 앤 덱스터 1편 한글화를 PS2 ISO 패치로 할지, OpenGOAL 모드로 할지
- **achieved_result (결정 시점 근거)**:
  - 공개된 1편 한글패치 없음 (PS2 정식판 비한글, 팬패치 검색 결과 없음)
  - OpenGOAL `game/assets/jak1/{text,subtitle}/*ko-KR.json` 은 en-US 와 바이트 동일 = 번역 0%
  - OpenGOAL 한글 렌더링(`font_utils_korean.cpp`, `convert-korean-text`)은 Jak2/Jak3 전용, Jak1 미지원
  - PS2 원본 1편에는 컷신 자막 기능 자체가 없음
- **options**:
  - A. PS2 ISO 패치 — 메뉴/힌트 텍스트만 가능, 자막은 시스템 신규 구현 필요, 폰트·GOAL 바이너리 수정 위험 큼
  - B. OpenGOAL — 자막 시스템·JSON 텍스트 존재, 엔진 소스 공개. 1편에 한글 폰트/인코딩 경로 신설 필요
- **recommendation**: B
- **human_decision**: B (사용자, 대화 중 "응 OpenGOAL로 진행해")
- **effects**: 결과물은 OpenGOAL 실행 환경 전용. PCSX2/PS2 실기 미지원. 사용자는 정품 ISO 필요.
- **reassessment**: OpenGOAL 업스트림이 1편 한글 지원을 자체 추가하거나, 폰트 경로가 불가능으로 판명될 때

## D-002 서체: 메뉴 배민 주아체 + 자막 Pretendard SemiBold

- **state**: adopted (2026-10-15), 게임 화면 검증 후 확정 예정
- **question**: 한글 서체. 메뉴와 자막은 같은 큰 폰트 시트(`ascii.24lo/hi`)를 공유 (`subtitle.gc:776` `font-flags ... large`)
- **options**: 주아체 통일 / Pretendard 통일 / 메뉴 주아체 + 자막 Pretendard / 화면 비교 후 결정
- **human_decision**: 메뉴 주아체 + 자막 Pretendard SemiBold (사용자). 원작 UI 스타일·색·외곽선·그림자 유지, 자막 2줄 이내
- **effects**: 자막 파일(`17SUBTIT.TXT`)은 별도 charmap·별도 글리프 셀로 인코딩 → 한글 수용량(현재 7페이지 1,302자)을 두 서체가 나눠 씀.
  초과 시 리드 바이트 확장(11·12·14·15) 검토. 공통 텍스트를 자막 렌더러로 띄우는 안내문(notice)은 메뉴 서체로 표시됨.
- **reassessment**: 게임 화면 검증에서 가독성·용량 문제 발생 시

## D-003 용어·말투·진행 기준

- **state**: adopted (2026-10-15)
- **human_decision**: `docs/glossary.md` 의 approved 항목 (사용자 승인 원문 기준). 작품명 「잭 & 덱스터: 구세계의 유산」 확정.
  PlayStation 공식 한국어 자료 우선, 확인 불가 용어는 일관성 기준. 미확정 용어는 추측 확정 금지 → 보류 + 근거 기록.
- **진행**: 오프닝부터 스토리 순서. 오프닝 22줄 검수 후 같은 기준으로 확장. 화면 텍스트 510개는 별도 작업.
  번역 완료 시 실제 게임 화면에서 줄바꿈·가독성·음성 타이밍 검증.

## D-004 배포 범위·승인

- **state**: adopted (2026-10-16)
- **human_decision** (사용자):
  1. 번역 2,158항목(자막 1,502 + 화자 27 + 메뉴·크레딧 397 + OpenGOAL 메뉴 232) **전체 일괄 승인** → `distribution_eligible`.
  2. 미검증 장면(크레딧 뒤 3장면, 진행 메뉴 임무 목록)은 확인 진행.
  3. **텍스처(그래픽) 글자는 번역하지 않는다** (예: 진행 메뉴 "AUTO SAVE OFF", 타이틀 로고). 영문 유지.
  4. 설치 방법 정리, 배포 빌드 생성과 검증.
- **effects**: release 빌드 가능. 그래픽 글자는 배포 범위 밖 → README 에 영문으로 남는다고 명시.
