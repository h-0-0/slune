from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    description = fh.read()

setup(
    name="slune-lib",
    version="0.0.11",
    author="Henry Bourne",
    author_email="hwbourne@gmail.com",
    packages=["slune"],
    description="A package for performing hyperparameter tuning with the SLURM scheduling system.",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/h-aze/slune",
    license='MIT',
    python_requires='>=3.8',
    install_requires=[
        "pandas"
    ]
)
