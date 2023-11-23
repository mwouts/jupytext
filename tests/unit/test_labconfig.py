import json

import pytest

from jupytext_config.labconfig import LabConfig


@pytest.fixture()
def sample_lab_config():
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


def test_read_config(tmp_path, sample_lab_config):
    (tmp_path / "default_setting_overrides.json").write_text(
        json.dumps(sample_lab_config)
    )
    labconfig = LabConfig(settings_path=tmp_path).read()
    assert labconfig.config == sample_lab_config


def test_set_default_viewers(tmp_path, sample_lab_config):
    labconfig = LabConfig(settings_path=tmp_path)
    labconfig.set_default_viewers()
    assert labconfig.config == sample_lab_config


def test_write_config(tmp_path, sample_lab_config):
    labconfig = LabConfig(settings_path=tmp_path)
    labconfig.set_default_viewers()
    labconfig.write()
    assert (
        json.loads((tmp_path / "default_setting_overrides.json").read_text())
        == sample_lab_config
    )
