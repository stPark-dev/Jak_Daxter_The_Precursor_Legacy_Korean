# Platform paths shared by setup_opengoal.sh and build_kr.sh (source this file, then call kr_platform).
# Linux, or Windows through Git Bash (MINGW/MSYS). KR_UNAME overrides `uname -s` (tests).

kr_platform() {
  local root=$1
  case "${KR_UNAME:-$(uname -s)}" in
    MINGW* | MSYS* | CYGWIN*)
      KR_PRESET=Release-windows-clang
      KR_BUILD_DIR=out/build/Release          # CMakePresets base-windows-release
      KR_EXTRACTOR=out/build/Release/bin/extractor.exe
      KR_GK=out/build/Release/bin/gk.exe
      KR_PYTHON=python
      ;;
    *)
      KR_PRESET=Release-linux-clang
      KR_BUILD_DIR=build/Release/bin          # CMakePresets base-linux-release
      KR_EXTRACTOR=build/Release/bin/decompiler/extractor
      KR_GK=build/Release/bin/game/gk
      KR_PYTHON=python3
      ;;
  esac
  # the ISO path is recorded by setup_opengoal.sh (no symlink: Git Bash would copy the whole ISO)
  if [ -f "$root/source/iso_path" ]; then
    KR_ISO=$(head -n 1 "$root/source/iso_path")
  else
    KR_ISO=$root/source/jak1.iso
  fi
}
