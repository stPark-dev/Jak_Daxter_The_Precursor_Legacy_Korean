#!/bin/bash
# Fetch OpenGOAL at the supported commit into jak-project/ and apply the Korean patch.
# usage: tools/fetch_opengoal.sh   (used by setup_opengoal.sh and ci_package.sh)
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
J=$ROOT/jak-project
OPENGOAL_COMMIT=b6c8430c0b0a5cb139b939bcf0ffd25285b896c7

if [ ! -d "$J/.git" ]; then
  # no CRLF conversion on Windows, or the patch will not apply
  git init -q "$J"
  git -C "$J" config core.autocrlf false
  git -C "$J" remote add origin https://github.com/open-goal/jak-project.git
fi
if ! git -C "$J" cat-file -e "$OPENGOAL_COMMIT^{commit}" 2>/dev/null; then
  git -C "$J" fetch --depth 1 origin "$OPENGOAL_COMMIT"
fi
git -C "$J" checkout -q --detach "$OPENGOAL_COMMIT"
git -C "$J" apply "$ROOT/patches/opengoal-kr.patch"
