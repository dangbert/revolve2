"""Installation script."""

import os.path
import pathlib

from setuptools import find_namespace_packages, setup

revolve2_path = pathlib.Path(__file__).parent.parent.resolve()

setup(
    name="revolve2-core",
    version="0.3.10-beta1",
    description="Core package for revolve2",
    author="Computational Intelligence Group Vrije Universiteit",
    url="https://github.com/ci-group/revolve2",
    packages=find_namespace_packages(),
    package_data={
        "revolve2.analysis.core": ["py.typed"],
        "revolve2.core": ["py.typed"],
    },
    install_requires=[
        f"revolve2-actor-controller @ file://{os.path.join(revolve2_path, 'actor_controller')}",
        "numpy>=1.21.2",
        "matplotlib>=3.4.3",
        "scipy>=1.7.1",
        "pyrr>=0.10.3",
        "sqlalchemy>=2.0.0",
        "asyncssh>=2.9.0",
        "aiosqlite>=0.17.0",
    ],
    zip_safe=False,
)
