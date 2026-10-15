"""Tests for the scene playback form generator (mirrors OpenGOAL's Subtitle Editor)."""
import pytest

import play

ENTRY = {
    "entity_type": "assistant",
    "process_name": "assistant-11",
    "continue_name": "village1-hut",
    "move_to": [],
    "execute_code": "(send-event __GET-PROCESS__ 'play-anim)",
    "requirements": [],
}
PROC = "(the-as assistant (process-by-name \"assistant-11\" *active-pool*))"


def test_cutscene_forms_match_subtitle_editor_order():
    forms = play.cutscene_forms(ENTRY)
    assert forms[:2] == ["(set! (-> *game-info* mode) 'debug)",
                         "(initialize! *game-info* 'game (the-as game-save #f) (the-as string #f))"]
    assert "(start 'play (get-continue-by-name *game-info* \"village1-hut\"))" in forms
    assert forms[-2:] == ["(send-event *camera* 'teleport)", f"(send-event {PROC} 'play-anim)"]


def test_requirements_and_move_first_order():
    e = dict(ENTRY, move_first=True, move_to=[1, 2, 3], requirements=["(foo __GET-PROCESS__)"])
    forms = play.cutscene_forms(e)
    i_cont = forms.index("(start 'play (get-continue-by-name *game-info* \"village1-hut\"))")
    i_req = forms.index(f"(foo {PROC})")
    assert i_cont < i_req


def test_delay_frames_wraps_execute_in_process():
    forms = play.cutscene_forms(dict(ENTRY, delay_frames=30))
    assert forms[-1].startswith("(process-spawn-function process (lambda () (dotimes (i 30) (suspend))")


def test_hint_forms():
    forms = play.hint_forms("ASSTLP01")
    assert forms[-1] == ("(level-hint-spawn (text-id zero) \"ASSTLP01\" (the-as entity #f) "
                         "*entity-pool* (game-task none))")


def test_scene_duration_from_meta():
    meta = [{"clear": False, "frame_start": 0}, {"clear": True, "frame_start": 300}]
    assert play.duration_seconds(meta) == pytest.approx(10.0)


def test_unknown_scene_is_reported():
    with pytest.raises(KeyError):
        play.forms_for("no-such-scene", db={}, hints={})


def test_hint_at_continue_point_moves_there_first():
    forms = play.hint_forms("GAM-AM10", continue_name="village2-start")
    assert "(start 'play (get-continue-by-name *game-info* \"village2-start\"))" in forms
    assert forms[-1].startswith("(level-hint-spawn (text-id zero) \"GAM-AM10\"")


def test_parse_target_with_at_suffix():
    assert play.parse_target("GAM-AM10@village2-start") == ("GAM-AM10", "village2-start")
    assert play.parse_target("warrior-introduction") == ("warrior-introduction", None)
