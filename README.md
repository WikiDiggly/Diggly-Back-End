# Diggly-Back-Prototype
A repository for the backend system of the Diggly Project

Setting up the Diggly-Backend

**Needed Libraries:**
  - Django (1.5.11)
  - django-mongodb-engine (0.6.0)
  - djangotoolbox (1.8.0)
  - nltk (3.1)
  - pip (7.1.2)
  - pymongo (2.8)
  - requests (2.9.1)
  - setuptools (18.2)
  - wheel (0.24.0)
  
**Develop locally:**
  - It is recommended that you set a virtual environment for this python project. Use `virtualenv` which is a tool to create isolated Python environments. (see [here](https://pypi.python.org/pypi/virtualenv)).
  - Also install pip package management system (see [here](https://pip.pypa.io/en/stable/installing/)). This installation should also include "setuptools." If not included see [here](https://pip.pypa.io/en/stable/installing/#pip-included-with-python) for instructions. 

**Django Installation**

See [here](http://django-mongodb-engine.readthedocs.org/en/latest/topics/setup.html#installation) for more information or follow the instructions below.

Django Installation Steps:
  1. Install virtualenv:
  
     `pip install virtualenv`
  
  2. set up virtualenv for Diggly-Back-Prototype:
  
      `virtualenv Diggly-Back-Prototype`
      
  3. To join the environment, use (in Bash):
  
      `source Diggly-Back-Prototype/bin/activate`
      
  Ensure to install the following packages within the newly set up virtualenv (first activate the environemnt in step 3).
  
  4. Install Django-nonrel:
  
      `pip install git+https://github.com/django-nonrel/django@nonrel-1.5`
      
  5. Install djangotoolbox:
  
      `pip install git+https://github.com/django-nonrel/djangotoolbox`
  
  6. Install Django MongoDB Engine:
  
      `pip install git+https://github.com/django-nonrel/mongodb-engine`
      
      
**Other Installations**

  1. Install PyMongo:
  
      `pip install pymongo`
      
  2. Install Requests:
  
      `pip install requests`
      
  3. Install NLTK:
  
      `pip install nltk`    

  
You will have to setup Django superuser in order to use the admin site in your browser (see [here](https://docs.djangoproject.com/en/1.9/intro/tutorial02/#introducing-the-django-admin))

Next, start Mongodb mongod instance using the following command (see [here](https://docs.mongodb.org/manual/tutorial/manage-mongodb-processes/#start-mongod-processes))
  
Next, start the Django development server (see [here](https://docs.djangoproject.com/en/1.9/intro/tutorial01/#the-development-server)) 

Finally, if the server is started without any problems, you should see a console output that tells you which port the server is listening on. By default, Django uses 8000. So if you use the default port, you should be able to access the application at "http://127.0.0.1:8000/"

**Testing the Diggly application:**
  - See the diggly/urls.py file for defined application routes and example usage.
