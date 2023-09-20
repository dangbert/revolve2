import os
import sys
from tests.conftest import EXAMPLES_DIR, add_path


# disabled for now because this test fails in the CI for some reason
#   TypeError: Evaluator.evaluate() takes 2 positional arguments but 5 were given
#   ^ I think it's maybe importing the evaluator from another example directory?
def test_experiment_can_complete(tmpdir):
    """Test that main.py can complete (without crashing)."""
    # with add_path(os.path.join(EXAMPLES_DIR, "robot_brain_cmaes")):
    from examples.robot_brain_cmaes.main import run
    import examples.robot_brain_cmaes.config as config

    overrides = {
        "RNG_SEED": 1001209834,
        "NUM_SIMULATORS": 4,
        "SIMULATION_TIME": 1,
        "SAMPLING_FREQUENCY": 5,
        "CONTROL_FREQUENCY": 15,
        "DATABASE_FILE": os.path.join(tmpdir, "run0.sqlite"),
        "POPULATION_SIZE": 4,
        "INITIAL_STD": 0.5,
        "NUM_GENERATIONS": 2,
    }
    for key, value in overrides.items():
        setattr(config, key, value)

    print(f"cmaes: sys.path = ", sys.path)
    run(config)
    assert os.path.exists(config.DATABASE_FILE)
