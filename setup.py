from setuptools import setup, find_packages

setup(
    name="infinity",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "pytz",
        "tabulate",
        "PyYAML",
        "boto3>=1.0.0"
    ],
    setup_requires=[
        "flake8",
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