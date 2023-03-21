from setuptools import setup, find_packages


setup(
    name="infinity",
    version="0.3.1",
    author="Naren Thiagarajan",
    author_email="narenst@gmail.com",
    url="http://narenst.github.io/",
    packages=find_packages(),
    data_files=[
        ('infinity/command', ['infinity/command/infinity_cloudformation.yaml']),
        ('infinity', ['infinity/settings.yaml'])
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "click",
        "requests",
        "pytz",
        "tabulate",
        "PyYAML",
        "boto3>=1.0.0",
        "sentry-sdk==1.14.0"
    ],
    setup_requires=[
        "flake8",
    ],
    dependency_links=[],
    entry_points={
        "console_scripts": [
            "infinity = infinity.main:cli",
            "infinity-volume = infinity.main:volume",
            "infinity-tools = infinity.main:tools",
        ],
    },
    tests_require=[
        "pytest",
        "mock>=1.0.1",
    ],
)
