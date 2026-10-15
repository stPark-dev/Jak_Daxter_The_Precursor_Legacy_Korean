# 잭 & 덱스터: 구세계의 유산 — 한글화 (OpenGOAL)

PS2 『Jak and Daxter: The Precursor Legacy』(잭 1편)를 PC 포트 [OpenGOAL](https://github.com/open-goal/jak-project)에서 한국어로 즐기기 위한 비공식 팬 한글화 프로젝트입니다.

![표지](cover_ko.png)

> 진행 중인 작업입니다. 현황은 [docs/translation_status.md](docs/translation_status.md)를 보세요.

## 무엇을 하나

- **한글 표시**: 1편 폰트에는 한글이 없어서, 폰트 텍스처를 확장하고 새 코드페이지(리드 바이트 2·4–9·11·12·14·15 + 글리프 바이트)를 엔진에 추가했습니다. 최대 2,035 음절.
- **서체**: 메뉴는 배민 주아체, 자막은 Pretendard SemiBold (둘 다 OFL).
- **번역 범위**: 메뉴·힌트 텍스트, OpenGOAL 추가 메뉴, 컷신·힌트 자막 (총 2,039 항목). 음성은 영어 원본 그대로.
- **언어**: OpenGOAL 의 예약 언어 ID 17(korean)로 텍스트·자막 언어에 추가.

## 필요한 것

- 본인 소유의 **Jak and Daxter: The Precursor Legacy NTSC-U (SCUS-97124, Black Label) ISO**. 게임 데이터는 이 저장소에 포함되지 않습니다.
- Linux, clang, cmake, ninja, nasm, python3 (+ Pillow, pytest), `libssl-dev` 등 [OpenGOAL 빌드 요구 사항](https://github.com/open-goal/jak-project#building-and-running-the-game)

## 빌드

```bash
tools/setup_opengoal.sh /path/to/jak1.iso   # OpenGOAL 받기 + 패치 적용 + 빌드 + ISO 추출
tools/build_kr.sh dev                        # 번역 내보내기 → 한글 폰트 생성 → 게임 빌드
```

실행은 `jak-project/build/Release/bin/game/gk -- -boot -fakeiso` 후 설정에서 텍스트·자막 언어를 한국어(17)로 바꿉니다.
(`dev` 빌드는 미번역 줄을 영어 원문으로 채우며 배포용이 아닙니다. `release` 는 모든 줄이 검수 완료일 때만 성공합니다.)

## 저장소 구성

| 경로 | 내용 |
|---|---|
| `patches/opengoal-kr.patch` | OpenGOAL `b6c8430` 기준 엔진 수정 (폰트 코드페이지, 한국어 텍스트·자막 컴파일, 언어 17 등록, 테스트) |
| `tools/kr_font/` | 한글 폰트 텍스처·코드표 생성기 |
| `tools/translation/` | 번역 워크스페이스 도구 (검사·내보내기·읽기 속도 점검) |
| `translation/` | 번역 원문·번역문·검수 상태 |
| `docs/` | 결정 기록, 조사, PoC, 용어집, 진행 현황 |
| `fonts/` | 배민 주아체, Pretendard SemiBold 와 각 OFL 라이선스 |

## 테스트

```bash
(cd tools && python3 -m pytest -q kr_font text translation)   # 도구 테스트
jak-project/build/Release/bin/goalc-test                      # OpenGOAL 회귀 + 한국어 인코딩 테스트
(cd tools && python3 -m pytest -q test_build_output.py)       # 빌드 결과물 검사 (build_kr.sh 이후)
```

## 라이선스·고지

- 『Jak and Daxter』 및 관련 상표·캐릭터·원문 텍스트의 권리는 Sony Interactive Entertainment / Naughty Dog 에 있습니다. 이 프로젝트는 비공식 팬 작업이며 어떤 회사와도 관련이 없습니다.
- 용어집의 한국어 표기는 이 패치의 자체 결정이며 공식 한국어 명칭이 아닙니다 ([docs/glossary.md](docs/glossary.md)).
- 서체: 배민 주아체(© The Jua Project Authors), Pretendard(© Kil Hyung-jin) — SIL Open Font License 1.1.
- OpenGOAL 은 ISC 라이선스입니다.
