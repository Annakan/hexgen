from setuptools import setup, find_packages

setup(
    name='hexgen',
    version="1.4",
    packages=find_packages(),
    install_requires=[
        'pillow',
        'numpy',
    ],
    extras_require={
        'tests': [' pytest', ]
    },
    package_data={'': ['fonts/*']},
    scripts=['bin/hexgen'],
)
