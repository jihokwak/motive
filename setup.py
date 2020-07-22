import setuptools
# from subprocess import check_output
# import re
# install_requires = check_output(['pip', 'freeze']).decode().split("\n")
# install_requires = [i for i in install_requires if not re.findall('twine|tqdm', i) and i]

install_requires = [
    'bcrypt==3.1.7',
    'bleach==3.1.3',
    'certifi==2019.11.28',
    'cffi==1.14.0',
    'chardet==3.0.4',
    'cryptography==2.9.2',
    'docutils==0.16',
    'elasticsearch==7.8.0',
    'idna==2.9',
    'importlib-metadata==1.5.0',
    'keyring==21.2.0',
    'numpy==1.19.0',
    'pandas==1.0.5',
    'paramiko==2.7.1',
    'pkginfo==1.5.0.1',
    'psycopg2-binary==2.8.5',
    'pycparser==2.20',
    'Pygments==2.6.1',
    'PyNaCl==1.4.0',
    'python-dateutil==2.8.1',
    'pytz==2020.1',
    'readme-renderer==24.0',
    'redis==3.5.3',
    'requests==2.23.0',
    'requests-toolbelt==0.9.1',
    'six==1.14.0',
    'slacker==0.14.0',
    'SQLAlchemy==1.3.18',
    'sshtunnel==0.1.5',
    'urllib3==1.25.8',
    'webencodings==0.5.1',
    'zipp==3.1.0'
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="momopapa", # Replace with your own username
    version="2.0.4",
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