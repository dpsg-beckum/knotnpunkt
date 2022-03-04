from setuptools import setup, find_packages

setup(
    name='knotnpunkt',
    description='Zelte- und Materialverwaltung der DPSG St. Stephanus Beckum',
    url='https://github.com/dpsg-beckum/knotnpunkt',
    version='0.1.0',
    packages=find_packages(where='.'),
    install_requires=[
        'Flask',
        'Flask-Login',
        'Flask-Migrate',
        'Flask-SQLAlchemy',
        'humanize'
    ]
)
