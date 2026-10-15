# 번역 진행 현황 (authoritative: translation/*.json 의 state, 이 문서는 요약)

분모: 화면 텍스트 279 + OpenGOAL 메뉴 231 + 화자 27 + 자막 1,502 = 2,039 항목 (`tools/translation/cli.py init`).

## 오프닝 (스토리 순서)

| 순서 | 장면 | 줄 | 상태 | 비고 |
|---|---|---|---|---|
| 1 | sage-intro-sequence-a | 20 | needs_review (2차 검수 반영) | 나레이션(???=사모스) |
| 2 | sidekick-human-intro-sequence-b | 4 | needs_review | 화자 OLD MAN/WOMAN 표기 hold |
| 3 | sidekick-human-intro-sequence-c | 16 | needs_review | |
| 4 | sage-intro-sequence-d1 | 22 | needs_review (사용자 조건부 승인 반영) | |
| 5 | sage-intro-sequence-d2 | 25 | needs_review | 불의 협곡 설명 = d2 0–2줄 (d1 직후 재생 확인), 케이라 말투 V-004 hold |
| 6 | sage-intro-sequence-e | 11 | needs_review | 가이저 록 훈련 후 재생 (오프닝 연속 재생엔 미포함, 미검증) |
| — | speakers | 3 | needs_review | 사모스·덱스터·케이라 |

검증: a→d2 실게임 재생(실 GPU, 960×540) 캡처로 표시·줄 수·그림자 확인. 읽기 속도 휴리스틱(`tools/translation/timing.py`, 30fps 가정, 12 cps) 위반 0.
남은 hold: G-007c(그린 이코), G-013(주머), G-018b(불의 협곡), G-018c(가이저 록), 화자 OLD MAN/WOMAN, V-004(케이라→사모스 해요체).

## 샌드오버 마을 (b02, 2026-10-15)

36개 장면 188줄 (사모스 리마인더 5, 케이라 5, 시장 5, 농부 4, 어부 6 + 배 장면 1, 새 관찰가 4, 조각가 3, 잭의 삼촌 4). 초벌 → 2차 검수 → 반영(25줄).
기계 검사·읽기 속도 위반 0. 실게임 표시 검증은 해당 장면 도달이 필요해 아직 (오프닝만 검증됨).
hold: G-012, G-014, G-018d, G-020~G-029, S-005~S-010, V-005, V-007~V-013 → 사용자 결정 대기 (2차 검수 권고: 전부 채택, S-008 은 '탐조가' 권장).
