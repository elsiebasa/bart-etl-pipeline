from setuptools import setup, find_packages

setup(
    name="bart-etl",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask==2.0.1",
        "werkzeug==2.0.3",
        "requests==2.31.0",
        "pandas==2.1.4",
        "flask-cors==4.0.0",
        "python-dotenv==1.0.0",
        "sqlalchemy==1.4.41",
    ],
) 