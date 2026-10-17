#!/bin/bash
# Package without an ISO (GitHub Actions): patched OpenGOAL + the committed generated/ outputs.
# usage: tools/ci_package.sh <version>
# Windows needs the VS C++ environment (vcvars64) and MSVC's link.exe ahead of Git Bash's.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
VERSION=${1:?usage: $0 <version>}
source "$ROOT/tools/generated.sh"

expected=$(cat "$ROOT/generated/INPUTS_HASH")
actual=$(kr_inputs_hash "$ROOT")
if [ "$expected" != "$actual" ]; then
  echo "generated/ is stale (translations, fonts or tools changed since it was made):" >&2
  echo "run tools/build_kr.sh release and commit generated/" >&2
  exit 1
fi

"$ROOT/tools/fetch_opengoal.sh"
kr_generated_copy "$ROOT" restore
mkdir -p "$ROOT/source"
echo release > "$ROOT/source/last_build"
"$ROOT/tools/package_kr.sh" "$VERSION"
