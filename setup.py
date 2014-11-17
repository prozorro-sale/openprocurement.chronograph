import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'setuptools',
    'pyramid',
    'waitress',
    'couchdb',
    'apscheduler',
    'requests',
    'iso8601',
]

setup(name='openprocurement.chronograph',
      version='0.0',
      description='openprocurement.chronograph',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      namespace_packages=['openprocurement'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="openprocurement.chronograph",
      entry_points="""\
      [paste.app_factory]
      main = openprocurement.chronograph:main
      """,
      )
