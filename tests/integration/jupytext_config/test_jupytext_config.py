from jupytext.cli import system


def test_jupytext_config_cli(tmp_path):
    settings_file = tmp_path / "default_setting_overrides.json"
    system("jupytext-config", "-h")
    system(
        "jupytext-config",
        "--settings-file",
        str(settings_file),
        "set-default-viewer",
        "python",
        "markdown",
    )
    assert "python" in (settings_file).read_text()
    assert "markdown" in system(
        "jupytext-config", "--settings-file", settings_file, "list-default-viewer"
    )
    system(
        "jupytext-config",
        "--settings-file",
        str(settings_file),
        "unset-default-viewer",
        "markdown",
    )
    list_viewers = system(
        "jupytext-config", "--settings-file", settings_file, "list-default-viewer"
    )
    assert "python" in list_viewers
    assert "markdown" not in list_viewers
