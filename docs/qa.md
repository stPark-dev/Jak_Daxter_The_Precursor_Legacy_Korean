# 인게임 자막 검수 절차 (자동 재생)

OpenGOAL Subtitle Editor 의 장면 재생과 같은 GOAL 명령(`game/assets/jak1/subtitle-editor-db.json` 기반,
`subtitle_editor_repl_client.cpp` 와 동일 순서)을 REPL 로 보내 장면을 재생하고, 게임 창만 캡처해 자막 띠를 모은다.
편집기 화면을 마우스로 조작할 필요가 없다.

## 실행

```bash
tools/build_kr.sh dev                    # 번역 → 폰트 → 게임 빌드
tools/qa/runtime.sh start                # 960x540 창 + REPL (설정: tools/qa/settings-template, 한국어 17)
python3 tools/qa/play.py <장면|힌트> ...  # 재생 + 캡처
tools/qa/runtime.sh stop
```

결과: `.qa/sheets/<이름>.png` (자막 띠 모음), `.qa/sheets/<이름>.txt` (id · 화자 · 원문 · 번역 대조표).
힌트는 `level-hint-spawn` 으로 재생한다. **힌트는 해당 레벨이 로드돼 있어야** 음성·자막이 나오므로
`이름@이어하기지점` 으로 지정한다 (예: `GAM-AM10@village2-start`, `asstvb41@training-start`).
이어하기 지점 이름은 `goal_src/jak1/engine/level/level-info.gc` 의 `:name`.
장면이 한 번에 트리거되지 않으면(레벨 로드 타이밍) 다시 실행한다 — 예: warrior-introduction 은 2회차에 재생됨.

## 검수 항목

1. 줄 수·순서가 대조표와 일치 (누락·중복 없음)
2. 글자 깨짐 없음 (charmap/트레일 바이트 결함 — 예: '라' 0x5F 사건)
3. 자막 2줄 이내, 화면 밖 화자 표시명 정상
4. 표시 시간 대비 읽기 속도: `tools/translation/timing.py` (30fps 가정, 12자/초. 끝줄은 영어 길이로 추정)
5. 음성 타이밍 체감은 사람이 소리와 함께 확인 (캡처로는 불가)

## Subtitle Editor 와 번역 파이프라인의 관계

- 편집기는 `subtitle_lines_<lang>.json` 을 직접 수정한다. 한국어 파일(`*_ko-KR.json`)은 `tools/translation/cli.py export` 가
  매 빌드마다 덮어쓰므로 **편집기에서 한국어 문장을 고치면 안 된다** (수정은 `translation/` 에서).
- 편집기는 재생·타이밍 참고용으로만 쓴다. 타이밍(meta) 변경이 필요하면 별도 결정으로 다룬다.
- `subtitle-editor-db.json` 에 없는 컷신(예: `fishermans-boat-ride-to-village1-alt`)은 자동 재생 불가 → 실제 진행으로 확인.

## 재생 DB 결함과 우회 (2026-10-16)

- `subtitle-editor-db.json` 의 green-sagecage-* 는 어부 좌표(move_to 262,2,-231)를 갖고 있어 성채에서 엉뚱한 곳으로 순간이동 → 화면 정지처럼 보였다.
  `play.py 장면@이어하기지점` 으로 지정하면 DB 위치 대신 그 지점만 쓴다.
- DB 의 지연 키는 `delay` (편집기는 이를 delay_frames 로 읽음). play.py 가 `delay_frames` 만 읽던 버그 수정.
- 레벨 이동 후 대기는 `@` 지정 여부와 관계없이 12초.
- 캡처 전 매번 게임 창(xwininfo)을 확인하고, 창이 없으면 중단한다 (게임이 죽은 뒤 데스크톱이 찍힌 사고 → 즉시 삭제, 2026-10-16).
- 성채 진입 시 그린 현자 우리 소개가 먼저 자동 재생된다 → 캡처 시간을 50초 늘려 뒤이어 나오는 장면을 확인.
- 1.5초 안팎의 짧은 줄은 1초 간격 캡처(실제 약 1.8초)에서 빠질 수 있다 → 해당 시점 근처를 다시 촘촘히 확인.
- 디버그 실행(-debug)에서는 text-id 가 zero 인 힌트에 "UNKNOWN TEXT ID" 가 뜬다 (ambient.gc, `*debug-segment*` 조건). 일반 실행·언어와 무관.

## 2026-10-16 인게임 확인 결과

| 장면 | 방법 | 결과 |
|---|---|---|
| fisher-reminder-1 → 낚시 질문(예/아니요) → fisher-reject, fisher-accept | 어부 상태를 직접 전환 (play-anim / play-reject / play-accept) | 전 줄 표시, 질문 화면 한국어 |
| minershort-introduction-orbs | DB 재생 + 짧은 줄 재확인 | 전 줄 (15줄) |
| asstvb24@ogre-start | 힌트 재생 | 전 줄 |
| green-sagecage-introduction, redsage/bluesage/yellowsage-resolution | 이어하기 지점 + 긴 캡처 | 전 줄 |
| green-sagecage-resolution → outro-preboss | 그린 현자 우리에 play-anim | 전 줄 |
| finalbosscam-white-eco → daxter-sacrifice | robotboss 를 white-eco-movie 상태로 | 전 줄 |
| outro-beat-boss-a → b → 엔딩 크레딧 | robotboss 에 white-eco-picked-up 이벤트 | 전 줄. **크레딧은 영어** (번역 대상 밖, 아래) |
| outro-beat-boss-need-cells / enough-cells / big-finish | 상태 강제 시 sage-finalboss 가 죽음 (강제 조작 부작용) | **미검증** — 실제 진행(크레딧 후 문 앞) 필요 |
| 진행 메뉴 임무 목록 | 새 게임에선 표시 안 됨, 같은 설정으로 직접 그려 폭 확인 | 실제 메뉴 표시는 미검증 |

크레딧: `game_text.txt` 의 `(credits :begin #x0b00 ...)` 111항목 (제목·역할·인명). base 추출(279)에 포함되지 않았다.

## 엔딩 크레딧 (2026-10-16)

- `credits.gc` 가 크레딧 동안 텍스트 언어를 음성 언어(영어)로 바꿔서 한국어 크레딧이 표시되지 않았다 → 한국어일 때는 바꾸지 않도록 엔진 수정 (patches/opengoal-kr.patch).
- 확인: 제목·역할명 한국어 표시, 악센트 인명(PÅL 등) 정상. 한글 제목이 영문 제목보다 작아 보임 → 사람 확인 필요.
