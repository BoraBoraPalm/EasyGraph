from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8") if (here / "README.md").exists() else ""

setup(
    name="easygraph",
    version="0.2.1",
    author="Markus Schuster",
    description="old: pretty Graphviz Digraphs with clusters and formatted nodes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BoraBoraPalm/EasyGraph",
    packages=find_packages(exclude=["tests*", "docs*"]),
    install_requires=[
        "graphviz>=0.20",
    ],
    python_requires=">=3.6,<4",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="graphviz graph clusters workflow diagram",
    include_package_data=True,
)
