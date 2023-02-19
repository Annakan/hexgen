from setuptools import setup, find_packages

setup(
    name = 'hexgen',
    packages = find_packages(),
    install_requires=[
          'pillow',
          'numpy',
      ],
    extras_require={
        'tests': ['pytest',]
},
)
