from setuptools import setup, find_packages

setup(
    name="tender_parser",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "psycopg2-binary",
        "python-dotenv",
        "openpyxl"
    ],
)