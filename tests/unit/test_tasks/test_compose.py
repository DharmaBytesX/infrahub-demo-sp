"""Compose file layering used by ``invoke start``.

The catalog and Batfish runner images are pulled by default. The dev compose file
that builds them from the checkout must be layered only on request, otherwise a
plain ``invoke start`` would build images the user expects to pull.
"""

from __future__ import annotations

from tasks import CATALOG_DEV_FILE, OVERRIDE_FILE, _compose_base


def test_default_invocation_layers_only_the_override_file() -> None:
    """A plain start uses the committed override and not the dev build file."""
    cmd = _compose_base()

    assert f"-f {OVERRIDE_FILE}" in cmd
    assert str(CATALOG_DEV_FILE) not in cmd


def test_local_build_layers_the_dev_file_after_the_override() -> None:
    """A local build adds the dev file last, so its build blocks win."""
    cmd = _compose_base(local_build=True)

    assert cmd.index(str(OVERRIDE_FILE)) < cmd.index(str(CATALOG_DEV_FILE))


def test_override_images_point_at_the_published_registry() -> None:
    """The override names the published images, so a start pulls them."""
    text = OVERRIDE_FILE.read_text(encoding="utf-8")

    assert "registry.opsmill.io/opsmill/infrahub-demo-sp-streamlit" in text
    assert "registry.opsmill.io/opsmill/infrahub-demo-sp-batfish-runner" in text
    assert "build:" not in text
