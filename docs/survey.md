# 초기 조사 (현재 결론)

경로는 `jak-project/` 기준. 업스트림 기준 커밋: `b6c8430c0b0a5cb139b939bcf0ffd25285b896c7` (2026-10-14).
상태 표기: **확정**(소스/실측 근거) · **가설**(검증 전) · **미해결**.

## 1. 입력

| 항목 | 값 | 상태 |
|---|---|---|
| 원본 | `Jak and Daxter - The Precursor Legacy (USA) (En,Fr,De,Es,It).iso`, 1,460,535,296 B | 확정 |
| SHA-1 | `0db5976cdf9ea188bd64d8efdb4de095c38ea65f` | 확정 |
| 시리얼 | SCUS-97124, elf_hash 7280758013604870207 | 확정 (추출기 판별) |
| 리비전 | NTSC-U Black Label, 디컴파일러 설정 `ntsc_v1`. 추출·디컴파일·전체 컴파일(1317 타깃) 성공 | 확정 |

## 2. 텍스트 모집단 (분량)

| 모집단 | 소스 | 분량 | 상태 |
|---|---|---|---|
| 원본 게임 텍스트 (메뉴·힌트·UI) | `decompiler_out/jak1/assets/game_text.txt` (group common, 언어 0–6) | 279 항목 / 영어 6,438자 / 1,157단어, 최장 103자 | 확정 |
| OpenGOAL 추가 텍스트 | `game/assets/jak1/text/game_custom_text_en-US.json` | 231 문자열 / 552단어 | 확정 |
| 자막 (cutscenes·hints·speakers) | `game/assets/jak1/subtitle/subtitle_lines_en-US.json` | 대사 1,502줄 + 화자 이름 27 = 1,529 문자열 (고유 1,496) / 11,175단어 | 확정 |
| 그래픽 텍스트 (로고 등) | 텍스처 | — | 미해결 |

`*_ko-KR.json` 은 en-US 와 바이트 동일 (번역 0%). 합계 약 12,900 영어 단어.

## 3. 글리프 경로 (정적 분석 + 텍스처 실측)

- 실행되는 `draw-string` 은 GOAL 판 (`goal_src/jak1/engine/gfx/font.gc:595`). mips2c 판은 덮어써짐.
- 바이트 해석 `font.gc:997-1100`: `0`=끝, `1`=확장(다음 바이트로 page1), `~`=제어코드(`~Y/~Z` 위치 저장/복원, `~nH` 이동), 그 외 `b-16` 인덱스. 바이트 2–15 미처리.
- 코드페이지 2개뿐: page0(0x10–0xFF), page1(`\x1`+바이트). `*font24-table*` 289항목, `*font12-table*` 250항목.
- 폰트 텍스처: tpage `gamefontnew`(1278) 의 `ascii.12hi/12lo/24hi/24lo`, GAME.CGO. PC 에서는 각각 독립 RGBA 텍스처로 에뮬레이션 (`DirectRenderer2.cpp:344`).
- 셀: 10열×16행 = 텍스처당 160칸. 텍스처 실측 `ascii.24lo/hi` 256×512 (셀 24×32px), `ascii.12lo/hi` 128×256. 빈 칸 실측: 24lo 32칸(행 1 일부, 12–15), 24hi 30칸(행 13–15). 원본 글꼴은 대문자 전용 손글씨풍 + 일본어 한자 일부.
- 결론: 기존 텍스처 빈 칸(~60)으로는 한글 음절 수요(번역 후 수백~천여 자 예상)를 감당 못함 → 텍스처 확장 또는 자모 조합 필요.
- 너비 측정 `get-string-length` (`font.gc:1476`) 는 별도 파서 → 수정 시 동기화 필요.

## 4. 한국어 관련 기존 자산

- `pc-language` 에 `korean 17` 예약됨 (`goal_src/jak1/pc/pckernel-impl.gc:39`), 미사용.
- 2편 방식: 컴파일러가 음절을 `0x4,n,자모…` 로 인코딩 → 런타임 `convert-korean-text` 가 `~Y 자모 ~Z ~+26H` 로 겹쳐 그림. 자모 글리프는 Jak2 원본 폰트(코드페이지 1·3)에 있음 → **Jak1 에 없음**.
- 텍스트 직렬화 `common/serialization/text/text_ser.cpp:253` 는 이미 한국어 분기 존재. 자막 v1 컴파일러(`goalc/data_compiler/game_text_common.cpp:88`)는 없음.
- 텍스처 교체: `custom_assets/jak1/texture_replacements/<tpage>/<name>.png` (추출 시 적용).

## 5. 진행/위험 표

| 미해결 조건 | 영향 | 다음 근거 |
|---|---|---|
| 교체 PNG 크기 변경 시 UV/`font-set-tex0` 정상 여부 | 방식 ②의 성립 | **가시성 PoC**: 확대 PNG + 테이블 UV 재계산 후 기존 글자 정상 + 새 칸 글자 표시 |
| 한글 표시 방식 (자모 조합 / 완성형 / PC 렌더러) | 설계 전체 | PoC 결과 + 사용자 결정 |
| 자막 줄바꿈이 공백 기준 | 한국어 줄바꿈 품질 | 번역 샘플로 표시 확인 |
