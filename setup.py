from setuptools import setup, find_packages
import MRITOOLS

VERSION = MRITOOLS.__version__

def readme():
    with open('README.md') as f:
        return f.read()

install_requires = [
    'nibabel',
    'nipype',
    'nilearn']

setup(
    name='MRITOOLS',
    version=VERSION,
    description='Python package for fMRI data processing',
    long_description=readme(),
    requires=install_requires,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics'],
    keywords="fMRI nipype preprocessing",
    url='https://github.com/N-HEDGER',
    author='Nick Hedger',
    license='MIT',
    platforms='Linux, Mac OS',
    packages=find_packages(),
zip_safe=False)