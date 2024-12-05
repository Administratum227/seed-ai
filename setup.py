"""
SEED Framework Setup
------------------
Installation configuration for the SEED framework.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="seed-ai-framework",
    version="0.1.0",
    author="SEED Framework Team",
    description="Scalable Ecosystem for Evolving Digital Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Administratum227/seed-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
    install_requires=[
        "textual>=0.1.18",
        "rich>=10.0.0",
        "typer>=0.4.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "seed=seed.cli.commands:main",
        ],
    },
    include_package_data=True,
    package_data={
        "seed": ["config/*.yaml"],
    },
)