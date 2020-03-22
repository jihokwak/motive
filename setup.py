import setuptools
from subprocess import check_output
install_requires = check_output(['pip', 'freeze']).decode().split("\n")

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="momopapa", # Replace with your own username
    version="1.0.1",
    author="momopapa",
    author_email="datamanage@hellonature.net",
    description="Bigdata Analysis Utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jihokwak/motive",
    install_requires= install_requires,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)