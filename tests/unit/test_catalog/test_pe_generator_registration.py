"""Guard the PE onboarding generator's registration and its query's shape.

``generate_pe`` creates a ``DcimDevice`` and adds it to the backbone's ``pes``.
If its query returned either one, the generator's query-group bookkeeping
(``collect_data(update_group=True)``) would track the nodes it creates and
destabilise inside the proposed-change pipeline, the failure described in
``test_sdwan_generator_registration.py``. The generator reads the other PEs'
loopbacks through the SDK instead (``generators/common.py:
backbone_pe_loopbacks``), and these tests fail if someone adds those fields
back to the query.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

QUERY_PATH = Path("queries/service/pe_onboarding.gql")


def _generator() -> dict:
    cfg = yaml.safe_load(Path(".infrahub.yml").read_text())
    return next(g for g in cfg["generator_definitions"] if g["name"] == "generate_pe")


def _query_without_comments() -> str:
    """Return the query text without `#` comments, which name the forbidden fields."""
    return "\n".join(line.split("#", 1)[0] for line in QUERY_PATH.read_text().splitlines())


def test_pe_generator_registered() -> None:
    g = _generator()
    assert g["class_name"] == "PeOnboardingGenerator"
    assert g["file_path"] == "generators/generate_pe.py"
    assert g["targets"] == "pe_onboardings"
    assert g["query"] == "pe_onboarding"
    assert Path(g["file_path"]).exists()


def test_pe_generator_runs_on_events_not_in_the_proposed_change_pipeline() -> None:
    """In the pipeline it races artifact rendering and the diff comes out empty."""
    assert _generator()["execute_in_proposed_change"] is False


def test_pe_generator_watches_the_helper_module_it_imports() -> None:
    """Infrahub does not follow imports, so a change to common.py must be declared."""
    assert "generators/common.py" in _generator()["watch"]["files"]


def test_joining_pe_onboardings_triggers_the_generator() -> None:
    """Without the trigger nothing runs the generator, and every request stays a draft."""
    documents = list(yaml.safe_load_all(Path("objects/events/00_triggers.yml").read_text()))
    rows = [row for doc in documents if doc for row in doc["spec"]["data"]]
    action = next(row for row in rows if row.get("generator") == "generate_pe")
    rule = next(row for row in rows if row.get("action") == action["name"])
    assert rule["group"] == "pe_onboardings"
    assert rule["member_update"] == "added"


def test_pe_generator_query_does_not_return_what_the_generator_creates() -> None:
    query = _query_without_comments()
    # `device_type` is an input and allowed; only the bare `device` relationship is not.
    for field in ("device", "pes"):
        assert not re.search(rf"\b{field}\s*\{{", query), (
            f"{QUERY_PATH} returns '{field}', which the generator creates or changes; "
            "this makes the generator query self-referential and destabilises the "
            "proposed-change pipeline"
        )
