import os
import pytest
from tests.conftest import EXAMPLES_DIR

EXP_DIR = os.path.join(EXAMPLES_DIR, "robot_brain_cmaes")


def mock_config():
    import examples.robot_brain_cmaes.config as config

    overrides = {
        "NUM_GENERATIONS": 2,
    }
    for key, value in overrides.items():
        assert (
            getattr(config, key, None) is not None
        ), f"key '{key}' not found in config"
        setattr(config, key, value)
    return config


@pytest.mark.path(EXP_DIR)
def test_experiment_can_complete(custom_path, mocker):
    """Test that main.py can complete (without crashing)."""

    # override default config (to reduce number of generations)
    mocker.patch(
        "examples.robot_brain_cmaes.main.get_config", return_value=mock_config()
    )
    import examples.robot_brain_cmaes.main as main_script

    main_script.main()
