from setuptools import setup, find_packages

setup(name='proycto',
      version='0.0.0',
      description="Proyecto 2017 Universidad Catolica",
      url='https://github.com/mazzanicolas/proyecto',
      author='',
      author_email='',
      packages=[package for package in find_packages()
                if package.startswith('proyecto')],
      install_requires=[
          'django>=2.0',
          'django-bootstrap3>=9.1.0',
          'django-tables2>=1.16',
          'django-filter>=1.1.0',
          'django-crispy-forms>=1.7.0',
          'psycopg2>=2.7.3.2',
          'shapely>=1.6.2',
          'pyshp>=1.2.12',
          'geopy>=1.11.0'
      ]
      )
