from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="cdataclass",
    version="0.1.1",
    packages=find_packages(exclude=("tests*",)),
    package_data={"cdataclass": ["py.typed"]},
    author="hajoks",
    author_email="syari4369@gmail.com",
    description="Integration of ctypes and dataclasses",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/hajoks/cdata",
    download_url="https://github.com/hajoks/cdata",
    license="MIT",
    keywords="dataclasses ctypes",
    install_requires=[
        'dataclasses;python_version=="3.6"',
    ],
    python_requires=">=3.6",
    extras_require={"dev": []},
    include_package_data=True,
)
