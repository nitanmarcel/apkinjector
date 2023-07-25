from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='apkinjector',
    version='1.0.2',
    description='Utilities to help injecting libraries and frida in apks.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Marcel Alexandru Nitan',
    author_email='nitan.marcel@gmail.com',
    url='https://nitanmarcel.github.io/apkinjector',
    keywords=['FRIDA', 'APK', 'INJECTION', 'INJECT'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'apkinjector = apkinjector.__main__:start'
        ]
    },
    install_requires=[
        'requests'
        'appdirs',
        'install-jdk',
        'click',
        'pyaxmlparser',
        'pyelftools',
        'colorama'
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',

    ]
)
