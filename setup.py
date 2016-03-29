from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name='hcclient',
	version='0.1',
	description='Client Wrapper for the HouseCanary Property API',
	long_description=readme(),
	url='http://github.com/housecanary',
	author='Jeff Francisco',
	author_email='jeff.francisco7@gmail.com',
	license='MIT',
	packages=['hcclient'],
	zip_safe=False,
	test_suite='nose.collector',
	tests_require=['nose'])