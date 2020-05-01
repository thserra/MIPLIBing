from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='MIPLIBing',
    version='1.0.0',
    description='MIPLIBing is a library for downloading MIP benchmark instances.',
    url='https://github.com/thserra/MIPLIBing',
    author='Thiago Serra',
    author_email='Thiago.Serra@bucknell.edu',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='mip benchmarks optimization',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.4.*',
    install_requires=['numpy', 'pandas', 'requests'],
    project_urls={
        'Bug Reports': 'https://github.com/thserra/MIPLIBing/issues',
        'Source': 'https://github.com/thserra/MIPLIBing',
    },
)
