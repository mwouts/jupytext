import json

import pytest

from jupytext_config.labconfig import LabConfig


@pytest.fixture()
def sample_viewer_config():
    return {
        "@jupyterlab/docmanager-extension:plugin": {
            "defaultViewers": {
                "markdown": "Jupytext Notebook",
                "myst": "Jupytext Notebook",
                "r-markdown": "Jupytext Notebook",
                "quarto": "Jupytext Notebook",
                "julia": "Jupytext Notebook",
                "python": "Jupytext Notebook",
                "r": "Jupytext Notebook",
            }
        }
    }


@pytest.fixture()
def sample_empty_viewer_config():
    return {"@jupyterlab/docmanager-extension:plugin": {"defaultViewers": {}}}


@pytest.fixture()
def settings_file(tmp_path):
    return tmp_path / "default_setting_overrides.json"


def test_read_config(settings_file, sample_viewer_config):
    (settings_file).write_text(json.dumps(sample_viewer_config))
    labconfig = LabConfig(settings_file=settings_file).read()
    assert labconfig.config == sample_viewer_config


def test_set_unset_default_viewers(
    settings_file, sample_viewer_config, sample_empty_viewer_config
):
    labconfig = LabConfig(settings_file=settings_file)
    labconfig.set_default_viewers()
    assert labconfig.config == sample_viewer_config
    labconfig.unset_default_viewers()
    assert labconfig.config == sample_empty_viewer_config


def test_write_config(settings_file, sample_viewer_config):
    labconfig = LabConfig(settings_file=settings_file)
    labconfig.set_default_viewers()
    labconfig.write()
    assert json.loads(settings_file.read_text()) == sample_viewer_config
