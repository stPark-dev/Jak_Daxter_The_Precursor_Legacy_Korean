#!/bin/bash
# Jak 1 Korean patch: extract the user's ISO, then decompile and compile the game with the patch.
# usage: ./install.sh <jak1.iso>
set -euo pipefail
cd "$(dirname "$0")"
ISO=${1:?사용법: ./install.sh <잭 앤 덱스터 ISO (NTSC-U, SCUS-97124)>}
echo "게임 데이터를 추출하고 한글 패치를 빌드합니다. 몇 분 걸립니다..."
if ! ./extractor -e -v -d -c --disable-ansi "$ISO"; then
  echo "설치하지 못했습니다. data/log 폴더의 extractor 로그를 확인하세요." >&2
  exit 1
fi
echo "설치가 끝났습니다. ./play.sh 로 게임을 실행하세요."
