try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Diggly Backend Application',
    'author': 'Diggly',
    'url': 'http://rack36.cs.drexel.edu:8000/diggly',
    'author_email': 'hoo25@drexel.edu',
    'version': '1.0',
    'install_requires': [
        'Django==1.6.11',
        'django-mongodb-engine==0.6.0',
        'djangorestframework==3.2.5',
        'djangotoolbox==1.8.0',
        'flufl.enum==4.1',
        'nltk==3.1',
        'numpy==1.11.0',
        'pymongo==2.8',
        'requests==2.9.1',
        'scipy=0.17.0',
        'scikit-learn=0.17.1',
        'wheel==0.24.0',
        'pytest==2.8.7',
	'beautifulsoup4==4.4.1'
    ],
    'tests_require': [],
    'packages': ['diggly'],
    #'scripts': [],
    'name': 'diggly'
}

setup(**config)
