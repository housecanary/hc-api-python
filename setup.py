from setuptools import setup


def readme():
    with open('README.rst', 'rb') as f:
        return f.read().decode('UTF-8')

setup(name='housecanary',
      version='0.6.3',
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
      entry_points={
        'console_scripts': [
            'hc_api_excel_concat=housecanary.hc_api_excel_concat.hc_api_excel_concat:main',
            'hc_api_export=housecanary.hc_api_export.hc_api_export:main'
        ]
      })
