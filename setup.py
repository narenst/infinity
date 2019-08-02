from setuptools import setup, find_packages

__version__ = '0.1'

setup(
    name="infinity",
    version=__version__,
    install_requires=[
        "click",
        "requests",
        "pytz",
        "tabulate",
        "PyYAML",
    ],
    setup_requires=[
        "pylint",
    ],
    dependency_links=[],
    entry_points={
        "console_scripts": [
            "infinity = infinity.main:cli",
        ],
    },
    tests_require=[
        "pytest",
        "mock>=1.0.1",
    ],
)