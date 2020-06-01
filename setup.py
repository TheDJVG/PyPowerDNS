import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = ['PyPowerDNS']

requires = ['requests']

setuptools.setup(
    name='PyPowerDNS',
    version='2020.6.1',
    install_requires=requires,
    author="D. van Gorkum",
    author_email="djvg@djvg.net",
    description="Python 3 module to talk to authoritative PowerDNS API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheDJVG/PyPowerDNS",
    python_requires='>=3.6',
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)