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
