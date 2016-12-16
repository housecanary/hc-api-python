from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='housecanary',
      version='0.6.1',
      description='Client Wrapper for the HouseCanary API',
      long_description=readme(),
      url='http://github.com/housecanary/hc-api-python',
      author='HouseCanary',
      author_email='techops@housecanary.com',
      license='MIT',
      packages=['housecanary', 'housecanary.excel'],
      install_requires=['requests', 'docopt', 'openpyxl'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose', 'mock'],
      scripts=['bin/hc_api_export'])
