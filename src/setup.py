"""Setup file for pypi"""
from pathlib import Path
from setuptools import setup, find_packages
from jmc import VERSION


with (Path(__file__).parents[1] / "README.md").open(encoding="utf-8") as file:
    README = "\n" + file.read()

DESCRIPTION = "Compiler for JMC (JavaScript-like Minecraft Function), a mcfunction extension language for making Minecraft Datapack."
version = VERSION.replace("-alpha.", "a").replace("-beta.", "b")[1:]

if ("/" + VERSION + "/") not in README:
    raise ValueError("README file's version has not been updated")

setup(
    name="jmcfunction",
    version=version,
    author="WingedSeal",
    author_email="firm09719@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=README,
    packages=find_packages(),
    install_requires=[],
    keywords=[
        "python",
        "minecraft",
        "mcfunction",
        "datapack",
        "compiler"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        "console_scripts": [
            "jmc=jmc.__main__:main",
        ]
    },
    python_requires=">=3.10",
    project_urls={
        "Documentation": "https://jmc.wingedseal.com/",
        "Repository": "https://github.com/WingedSeal/jmc",
    },
    license="MIT License"
)
