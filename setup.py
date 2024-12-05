from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="seed-ai-framework",
    version="0.1.0",
    author="SEED AI Framework Team",
    author_email="admin@seed-ai.dev",
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
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.9",
    install_requires=[
        "aiohttp>=3.8.0",
        "pyyaml>=6.0",
        "rich>=10.0.0",
        "typer>=0.4.0",
        "textual>=0.1.18",
        "cryptography>=36.0.0",
        "pydantic>=1.9.0",
        "anthropic>=0.3.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "seed=seed.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "seed": ["config/*.yaml", "templates/*.md"],
    },
)