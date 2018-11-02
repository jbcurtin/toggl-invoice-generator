"""
Sanic
"""
import codecs
import os
import re
import sys
from setuptools import setup

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON=(3, 5)
# Thank you DjangoProject.org
if CURRENT_PYTHON < REQUIRED_PYTHON:
  sys.stderr.write("""
==========================
Unsupported Python version
==========================
This version of Toggl API Bill Generator requires Python {}.{}, but you're trying to
install it on Python {}.{}.
This may be because you are using a version of pip that doesn't
understand the python_requires classifier. Make sure you
have pip >= 9.0 and setuptools >= 24.2, then try again:

  $ python -m pip install --upgrade pip setuptools
  $ python -m pip install toggl-api-bill-generator

This will install the latest version of Toggl API Bill Generator which works on your version of Python.
""".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
  sys.exit(1)

INSTALL_REQUIRES = open('build-tools/requirements.txt', 'r').read()
INSTALL_REQUIRES = [req for req in INSTALL_REQUIRES.split('\n') if req]
setup(
    name='Toggl API Bill Generator',
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
    version='1.0.0',
    url='https://github.com/jbcurtin/toggl.com-bill-generator',
    license=open('./LICENSE', 'r').read(),
    author='Joseph B. Curtin <codes@jbcurtin.io>',
    author_email='codes@jbcurtin.io',
    description="""A script that will generate a PDF from Toggl.com API. Easy to automate from CRON or use from
the Command Line Interface. Following Flask App Factory Pattern and 12 Factor App best practices. All configuration
can be accomplished through Environment Varibles.""",
    long_description=open('./README.md', 'r').read(),
    scripts=['toggl_api_bill_generator/toggl-bill-gen'],
    packages=['toggl_api_bill_generator'],
    platforms='any',
    install_requires=INSTALL_REQUIRES,
    classifiers=[
      'License :: OSI Approved :: MIT License',
      'Environment :: Console',
      'Environment :: Other Environment',
      'Framework :: AsyncIO',
      'Operating System :: MacOS',
      'Operating System :: Microsoft',
      'Operating System :: POSIX',
      'Operating System :: Unix',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      'Programming Language :: Python :: 3.8',
      'Programming Language :: Python :: 3 :: Only',
      'Topic :: Utilities'
    ],
)
