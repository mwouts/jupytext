from jupytext.cli import system


def test_jupytext_config_cli(tmp_path):
    system("jupytext-config", "-h")
    system(
        "jupytext-config",
        "--settings-path",
        tmp_path,
        "set-default-viewer",
        "python",
        "markdown",
    )
    assert "python" in (tmp_path / "default_setting_overrides.json").read_text()
    assert "markdown" in system(
        "jupytext-config", "--settings-path", tmp_path, "list-default-viewer"
    )
