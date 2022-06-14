from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="datacanvas",
    version="0.1.0",
    author="<YOUR_NAME>",
    author_email="<YOUR_EMAIL>",
    description="<SHORT_PACKAGE_DESCRIPTION>",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="<LINK_TO_YOUR_CODE_OR_PRODUCT>",
    packages=find_packages(
        where='.',
        include=['datacanvas*'],  # ["*"] by default
        exclude=['datacanvas.tests'],  # empty by default
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'seaborn',
        'Pillow'
    ],
    python_requires='>=3.10',
)