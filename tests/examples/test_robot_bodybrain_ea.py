import os
import sys
from tests.conftest import EXAMPLES_DIR


def test_experiment_can_complete(tmpdir):
    """Test that main.py can complete (without crashing)."""
    sys.path.append(os.path.join(EXAMPLES_DIR, "robot_bodybrain_ea"))
    from examples.robot_bodybrain_ea.main import run
    import examples.robot_bodybrain_ea.config as config

    overrides = {
        "RNG_SEED": 245713412312,
        "NUM_SIMULATORS": 4,
        "SIMULATION_TIME": 1,
        "SAMPLING_FREQUENCY": 5,
        "CONTROL_FREQUENCY": 15,
        "DATABASE_FILE": os.path.join(tmpdir, "run0.sqlite"),
        "POPULATION_SIZE": 4,
        "OFFSPRING_SIZE": 2,
        "NUM_GENERATIONS": 2,
    }
    for key, value in overrides.items():
        setattr(config, key, value)

    run(config)
    assert os.path.exists(config.DATABASE_FILE)
