from setuptools import setup, find_packages

setup(
    name='seed-ai',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'pyyaml>=6.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'isort>=5.0.0',
            'mypy>=1.0.0',
        ],
    },
    python_requires='>=3.8',
    author='Administratum227',
    description='SEED AI Framework for Agent Development',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Administratum227/seed-ai',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)