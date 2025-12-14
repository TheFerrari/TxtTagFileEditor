from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.utils.tag_processing import build_full_key, matches_rule, normalize_whitespace, parse_tag_line
from app.services.file_service import process_file, write_file


def test_parse_tag_line():
    ns, tag, has_ns = parse_tag_line("artist:alacarte")
    assert ns == "artist"
    assert tag == "alacarte"
    assert has_ns is True

    ns, tag, has_ns = parse_tag_line("watersports")
    assert ns == "general"
    assert tag == "watersports"
    assert has_ns is False


def test_matches_rule_wildcard():
    key = build_full_key("meta", "2018")
    assert matches_rule(key, "meta:*")
    assert matches_rule("general:watersports", "*water*")
    assert not matches_rule(key, "meta:2017")


def test_process_file(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("artist:alacarte\nwatersports\nmeta:2018\n", encoding="utf-8")

    changed, removed, before, after = process_file(
        file_path,
        selected={"artist": ["alacarte"]},
        banned=["meta:2018"],
        case_insensitive=False,
        sort_lines=False,
    )

    assert changed is True
    assert removed == 2
    assert before == ["artist:alacarte", "watersports", "meta:2018"]
    assert after == ["watersports"]

    # ensure writer normalizes endings
    write_file(file_path, after)
    assert file_path.read_text(encoding="utf-8") == "watersports\n"
