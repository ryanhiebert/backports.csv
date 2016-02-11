from setuptools import setup

setup(
    name='backports.csv',
    description='Backport of Python 3 csv module',
    long_description=open('README.rst', 'rb').read().decode('utf-8'),
    author='Ryan Hiebert',
    author_email='ryan@ryanhiebert.com',
    url='https://github.com/ryanhiebert/backports.csv',
    version='1.0',
    py_modules=['backports.csv'],
    namespace_packages=['backports'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Progrmmming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Lnaguage :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    package_dir={'': 'src'},
)
