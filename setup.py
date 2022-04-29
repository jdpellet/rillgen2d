from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setuptools.setup(
    name="rillgen2d",
    version="0.0.1",
    author1="Jon D Pelletier",
    author2="Tyson L Swetnam",
    author2_email="tswetnam@arizona.edu",
    author1_email="jdpellet@arizona.edu",
    description="Rillgen2d",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tyson-swetnam/rillgen2d",
    project_urls={
        "Funding": "",
        "Bug Tracker": "https://github.com/tyson-swetnam/rillgen2d/issues",
        "Changelog": "https://github.com/tyson-swetnam/rillgen2d/blob/main/CHANGELOG.md"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU GPLv3 License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)