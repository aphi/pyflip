import setuptools

# Build and push to PyPI with:
# python setup.py bdist_wheel
# twine upload dist/*

setuptools.setup(
    name="pyflip",
    version="0.1.3",
    author="Antony Phillips",
    author_email="antony.e.phillips@gmail.com",
    description="A simple and modern library for Linear and Integer Programming in Python 3",
    long_description=\
"""PyFlip is a simple and modern library for Linear and Integer Programming in Python 3, offering an API to advanced solvers.
A major focus is features which speed up the model development process, e.g. prototyping, debugging, profiling, and integrating with metaheuristic algorithms.
This project has been written from scratch in 2018, having been inspired by PuLP, CyLP, rust-lp-modeler, and JuMP.

See full documentation on the project homepage: https://github.com/aphi/PyFlip """,
    url="https://github.com/aphi/pyflip",
    keywords='linear integer mathematical optimisation',
    package_dir = {'pyflip': ''},
    packages=['pyflip'],
    package_data={'pyflip':[
        '*.py',
        'src/*.py',
        'test/*.py',
        'README.md',
        'LICENSE.txt',
        'docs/*',
        'bin/win_32/cbc.exe',
        'bin/win_32/LICENSE.txt',
    ]},
    include_package_data=True,
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
)
