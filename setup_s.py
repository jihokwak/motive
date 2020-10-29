import setuptools

install_requires = [
    'botocore==1.17.28',
    'certifi==2020.6.20',
    'chardet==3.0.4',
    'docutils==0.15.2',
    'fsspec==0.7.4',
    'idna==2.10',
    'jmespath==0.10.0',
    'numpy==1.19.1',
    'pandas==1.0.5',
    'psycopg2-binary==2.8.5',
    'PyMySQL==0.10.0',
    'python-dateutil==2.8.1',
    'pytz==2020.1',
    'requests==2.24.0',
    's3fs==0.4.2',
    'six==1.15.0',
    'slacker==0.14.0',
    'SQLAlchemy==1.3.18',
    'urllib3==1.25.10'
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="momopapa_slim", # Replace with your own username
    version="1.0.2",
    author="momopapa",
    author_email="datamanage@hellonature.net",
    description="Bigdata Analysis Utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jihokwak/motive",
    install_requires= install_requires,
    packages = ['momopapa_slim'],
    package_data = {
        'momopapa_slim': ['*', 'bot/*', 'pandabase/*']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)