"""Setup script for pyparsing-highlighting."""

from pathlib import Path

from setuptools import find_packages, setup

from pp_highlighting import __version__

BASE = Path(__file__).resolve().parent

setup(
    name='pyparsing-highlighting',
    version=__version__,
    description='Syntax highlighting for prompt_toolkit and HTML with pyparsing.',
    long_description=(BASE / 'README.rst').read_text(),
    url='https://github.com/crowsonkb/pyparsing-highlighting',
    author='Katherine Crowson',
    author_email='crowsonkb@gmail.com',
    license='MIT',
    packages=find_packages(),
    data_files=[('', ['LICENSE', 'README.rst', 'requirements.txt'])],
    include_package_data=True,
    install_requires=(BASE / 'requirements.txt').read_text().strip().split('\n'),
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Terminals',
    ],
    keywords=['console', 'highlighting', 'html', 'prompt', 'syntax', 'terminal'],
)
