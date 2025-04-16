from setuptools import setup, find_packages

setup(
    name="bart-etl",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask==2.0.1",
        "werkzeug==2.0.1",
        "requests",
    ],
) 