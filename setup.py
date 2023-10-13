from distutils.core import setup
from setuptools import find_packages
from Cython.Build import cythonize
import numpy
import glob
import platform

PLATFORM = platform.system()
from alphagens import __version__
# extensions = glob.glob("torchqtm/_C/*.pyx")
# extensions.extend(glob.glob("torchqtm/window/*.pyx"))
# extensions.extend(glob.glob("torchqtm/finance/*.pyx"))

install_requires = [
    'numpy',
    'pandas',
    'pandas_market_calendars',
]


def main():
    setup(
        # ext_modules=cythonize(extensions, annotate=True),
        include_dirs=[numpy.get_include()],
        name="alphagens",
        version=__version__,
        author="ny",
        author_email="nymath@163.com",
        install_requires=install_requires,
        description="An event-driven backtesting system",
        long_description=open('README.md', 'r').read(),
        long_description_content_type="text/markdown",
        url="https://github.com/nymath/alphagens",
        download_url="https://github.com/nymath/alphagens/releases/tag/v1.0",
        packages=find_packages(),
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python :: 3',
            "License :: OSI Approved :: MIT License",
            "Operating System :: Unix",
        ],
        project_urls={
            'Documentation': 'https://github.com/nymath/alphagens',
            # 'Funding': 'https://donate.pypi.org',
            'Source': 'https://github.com/nymath/alphagens',
            # 'Tracker': 'https://github.com/pypa/sampleproject/issues',
        },
        python_requires='>=3.9',
        entry_points={
        "console_scripts": [
            "texgen=alphagens.cli.texgen:main",
        ]
        }
    )


if __name__ == "__main__":
    main()

## setup cython
# python setup.py build_ext --inplace
## setup package
# pip install twine
# python setup.py sdist bdist_wheel
# twine upload dist/*
# twine upload --skip-existing dist/*

# ny.math
# xxx
