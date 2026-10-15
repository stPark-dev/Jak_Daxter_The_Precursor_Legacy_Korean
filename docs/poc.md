# PoC 기록

## POC-001 한글 글리프 가시성 (확장 텍스처 + 새 코드페이지)

- **state**: pass (2026-10-15)
- **baseline**: OpenGOAL `b6c8430c` + 브랜치 `kr-poc` (jak-project), ISO SCUS-97124 ntsc_v1
- **환경**: Xvfb `:99` (llvmpipe, GL 4.5), 1280×720 창 모드, 격리 config (`scratchpad/cfg`)
- **질문**: (1) 크기가 다른 교체 PNG가 폰트(깊이버퍼 에뮬레이션) 경로에서 동작하는가
  (2) 원본 UV 재계산 후 기존 글자가 유지되는가 (3) 새 리드 바이트 페이지로 한글이 표시되는가

### A0 — 교체 PNG 크기 변경 (코드 무수정)
- `ascii.24lo` 를 512×1024(2배, nearest) + `S` 셀만 빨갛게 칠한 PNG로 교체
- 결과: 큰 폰트의 S 만 빨갛게 표시 → **교체 텍스처 적용·크기 무관 확인** (UV는 정규화 좌표)

### A1 — 2048² 캔버스 + UV 재계산 + 리드 바이트 0x02
- 도구: `tools/kr_font/build_font.py` (테스트 16개 통과), 폰트 Noto Sans CJK KR Bold (PoC 한정)
- 코드: `font.gc` 3개 그리기 루프 + `get-string-length` 에 리드 바이트(2, 4–9) 처리,
  `pc/kr-font.gc` 가 테이블 확장(1391항목)·원본 UV×(0.25, 0.5)·size-st 재계산,
  `pc/kr-font-data.gc` 는 생성물
- 표시 문자열: `잭과 덱스터 한글 테스트 ABC 123` (큰 폰트), `PRESS START 잭과 덱스터 한글 테스트` (작은 폰트)
- 결과: 한글·영문·숫자 모두 정상 표시, 그림자 정상 → **pass**
- 증거: `scratchpad/shots/a1.png`, `a1_zoom.png` (세션 로컬)

### A2 — 실제 텍스트 경로 (언어 ID 17)
- 컴파일러: `font_utils.cpp` `is_language_id_korean(JAK1_V2, 17)`, `convert_utf8_to_game_korean_jak1`
  (charmap `game/assets/fonts/jak1_korean_charmap.json`, **charmap 에 없는 음절은 빌드 실패**)
- gtest `test/test_font_korean_jak1.cpp` 5개 (RED→GREEN). 첫 구현의 charmap 로더 버그(구조적 바인딩 순회로 키 누락)를
  파일 로드 테스트로 재현 후 수정
- `game_text.gp` 에 `(file-json 17 …ko-KR…)` 등록, `game_base_text_ko-KR.json` = 영어 279항목 추출
  (`tools/text/extract_base_text.py`) + PoC 번역 2개(#x16e, #x15c)
- 누락 검사 실증: 폰트 갱신 전 컴파일 시 `Korean syllable '새' is not in the Jak 1 font charmap` 으로 중단
- 결과: `-boot` 타이틀 화면에 `시작 버튼을 누르세요` 가 **가운데 정렬로** 표시 → 텍스트 파이프라인 + 너비 계산 pass
- 증거: `scratchpad/shots/a2.png`

### 확인 안 된 것 (주장 범위 밖)
- 자막 경로 (`game_subtitle.gp`, `compile_subtitles_v1` 한국어 분기 없음)
- 공백 기준 줄바꿈이 긴 한국어 문장에서 맞는지
- 설정 메뉴에서 언어 17 선택 UI (현재는 설정 파일 직접 수정으로만 선택)
- 일본어 원본 page1 문자 (언어 5) 회귀
- GPU 실기(NVIDIA) 렌더러 — Xvfb llvmpipe 에서만 확인

### 회귀
- A2 이후 goalc-test 1,677/1,677 통과 (기존 1,672 + 한국어 5), tools pytest 21/21 통과
- A1 시점 goalc-test 1,672/1,672 통과 (수정 전 기준과 동일). 게임 실행 중 돌린 1차 실행은 리스너 포트 충돌로 3건 실패 → 무효 처리, 게임 종료 후 재실행으로 대체
- tools/kr_font pytest 16/16 통과

### 다음
- 텍스트 컴파일러에 한글 charmap 연결 → 언어 ID 17 로 실제 메뉴 문자열 표시
- 폰트 디자인(서체·크기·자간)은 사람 결정 사항 → D-002 후보

## POC-002 자막 경로 + 서체 분리 (D-002) 실게임 검증

- **state**: pass (2026-10-15)
- **환경**: 실제 GPU(NVIDIA), 960×540 창 모드, 격리 config, `subtitles? #t`, text/subtitle-language 17
- **방법**: REPL `(initialize! *game-info* 'game #f "intro-start")` 로 실제 오프닝 컷신 재생, 게임 창만 2–3초 간격 캡처
- **구현**: 자막 v1 컴파일러 한국어 분기(`compile_subtitles_v1`, `convert_utf8_to_game_korean_subtitle`), charmap 분리
  (`jak1_korean_charmap_menu.json` = 배민 주아체, `jak1_korean_charmap_subtitle.json` = Pretendard SemiBold)
- **발견 결함 → 수정**: '라'(trail 0x5F)가 악센트 기호로 표시. 원인 `subtitle.gc:321` 자막 줄바꿈이 `_`(95)를 공백으로 치환.
  0x5F 를 lo trail 에서 제외(용량 1,302 → 1,295), 회귀 테스트 `test_no_glyph_byte_is_rewritten_by_subtitle_wrap` 추가. 재생 확인 pass.
- **결과**: sage-intro-sequence-d1 한국어 자막 표시, 최장 줄도 1줄, 그림자·가운데 정렬 유지. 증거 `docs/evidence_opening_d1.png` (git 제외)
- **미검증**: 음성-자막 타이밍 체감(캡처로는 소리 확인 불가), 메뉴 화면의 주아체 실제 표시
- **회귀**: goalc-test 1,677/1,677, tools pytest 41/41

## POC-003 한글 용량 확장 (리드 바이트 11·12·14·15)

- **state**: pass (2026-10-15)
- **근거**: 자막 14% 번역 시점 자막 542 + 메뉴 12 음절. 메뉴(주아체)·자막(Pretendard)은 같은 음절도 별도 글리프 → 전체 수요가 1,295 초과 예상
- **변경**: `layout.LEADS` 에 11·12·14·15 추가 (10/13 = 개행이라 제외), `font.gc` `kr-lead-byte?` 확장. 용량 1,295 → **2,035**, 테이블 2,159항목, 셀 1,023/1,168
- **사전 조사**: 텍스트·자막·폰트·문자열 코드에서 바이트 11·12·14·15 특수 처리 없음 (grep)
- **실험**: 메뉴 세트에 KS X 1001 음절 1,475개를 덧붙인 실험 빌드 → 자막 글리프 전부가 리드 12·14·15 페이지로 이동 → 오프닝 재생에서 정상 표시. 실험 후 정상 빌드로 복구
- **회귀**: goalc-test 1,677/1,677, tools pytest 45/45
