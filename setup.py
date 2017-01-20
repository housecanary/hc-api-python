import codecs
import os
import re

from setuptools import setup


def read(*parts):
    return codecs.open(os.path.join(*parts), 'r').read().decode('UTF-8')


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(name='housecanary',
      version=find_version('housecanary', '__init__.py'),
      description='Client Wrapper for the HouseCanary API',
      long_description=read('README.rst'),
      url='http://github.com/housecanary/hc-api-python',
      author='HouseCanary',
      author_email='techops@housecanary.com',
      license='MIT',
      packages=['housecanary', 'housecanary.excel'],
      install_requires=['requests', 'docopt', 'openpyxl', 'python-slugify'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose', 'mock'],
      entry_points={
          'console_scripts': [
              'hc_api_excel_concat=housecanary.hc_api_excel_concat.hc_api_excel_concat:main',
              'hc_api_export=housecanary.hc_api_export.hc_api_export:main'
          ]
      })
