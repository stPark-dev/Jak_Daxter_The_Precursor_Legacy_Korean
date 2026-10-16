"""Tests for tools/platform.sh (Linux / Windows Git Bash paths used by setup and build scripts)."""
import os
import subprocess
from pathlib import Path

PLATFORM = Path(__file__).resolve().parent / "platform.sh"


def _bash():
    # on Windows a bare "bash" is System32's WSL launcher; use the Git Bash next to git instead
    if os.name != "nt":
        return "bash"
    exec_path = subprocess.run(["git", "--exec-path"], capture_output=True, text=True, check=True).stdout
    return str(Path(exec_path.strip()).parents[2] / "bin" / "bash.exe")  # <git>/mingw64/libexec/git-core


def _vars(uname, root, *names):
    script = f'source "{PLATFORM}"; kr_platform "{root}"; ' + "; ".join(f'echo "${n}"' for n in names)
    out = subprocess.run([_bash(), "-c", script], env={"KR_UNAME": uname, "PATH": "/usr/bin:/bin"},
                         capture_output=True, text=True, check=True).stdout
    return out.splitlines()


def test_linux_paths():
    preset, build, extractor, gk = _vars("Linux", "/r", "KR_PRESET", "KR_BUILD_DIR", "KR_EXTRACTOR", "KR_GK")
    assert preset == "Release-linux-clang"
    assert build == "build/Release/bin"
    assert extractor == "build/Release/bin/decompiler/extractor"
    assert gk == "build/Release/bin/game/gk"


def test_windows_git_bash_paths():
    preset, build, extractor, gk = _vars("MINGW64_NT-10.0-19045", "/r", "KR_PRESET", "KR_BUILD_DIR",
                                         "KR_EXTRACTOR", "KR_GK")
    assert preset == "Release-windows-clang"
    assert build == "out/build/Release"
    assert extractor == "out/build/Release/bin/extractor.exe"
    assert gk == "out/build/Release/bin/gk.exe"


def test_iso_path_is_read_from_the_recorded_file(tmp_path):
    (tmp_path / "source").mkdir()
    (tmp_path / "source" / "iso_path").write_text("/games/jak1.iso\n")
    assert _vars("Linux", tmp_path, "KR_ISO") == ["/games/jak1.iso"]


def test_iso_path_falls_back_to_the_old_symlink(tmp_path):
    # repositories set up before the path file existed keep working
    assert _vars("Linux", tmp_path, "KR_ISO") == [f"{tmp_path}/source/jak1.iso"]
