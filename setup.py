import setuptools
from subprocess import check_output
import re
install_requires = check_output(['pip', 'freeze']).decode().split("\n")
install_requires = [i for i in install_requires if not re.findall('twine|tqdm', i) and i]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="momopapa", # Replace with your own username
    version="2.0.0",
    author="momopapa",
    author_email="datamanage@hellonature.net",
    description="Bigdata Analysis Utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jihokwak/motive",
    install_requires= install_requires,
    packages = ['momopapa'],
    package_data = {
        'momopapa': ['*', 'bot/*']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)