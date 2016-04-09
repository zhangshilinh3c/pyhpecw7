from distutils.core import setup
from setuptools import find_packages

setup(
  name='pyhpecw7',
  packages=find_packages(),
  version='0.0.9',
  description='Python package to simplify working with HP Comware devices ',
  author='HPE',
  url='https://github.com/networktocode/pyhpecw7',
  download_url='https://github.com/networktocode/pyhpecw7/tarball/0.0.9',
  package_data={'pyhpecw7': ['utils/templates/textfsm_temps/*.tmpl']},
  install_requires=[
      'gtextfsm==0.2.1',
      'lxml',
      'ncclient',
      'scp',
      'ipaddr>=2.1.11',
      'paramiko'
  ],
)
