"""Setup script for pyparsing-highlighting."""

from pathlib import Path

from setuptools import setup

BASE = Path(__file__).resolve().parent

setup(
    name='pyparsing-highlighting',
    version='0.2.7',
    description='Syntax highlighting for prompt_toolkit and HTML with pyparsing.',
    long_description=(BASE / 'README.rst').read_text(),
    url='https://github.com/crowsonkb/pyparsing-highlighting',
    author='Katherine Crowson',
    author_email='crowsonkb@gmail.com',
    license='MIT',
    packages=['pp_highlighting'],
    include_package_data=True,
    zip_safe=False,
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
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Terminals',
    ],
    keywords=['console', 'highlighting', 'html', 'prompt', 'syntax', 'terminal'],
)
