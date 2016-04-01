from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name='hcapi',
	version='0.1',
	description='Client Wrapper for the HouseCanary Property API',
	long_description=readme(),
	url='http://github.com/housecanary/hc-api-python',
	author='Jeff Francisco',
	author_email='jeff.francisco7@gmail.com',
	# license='TODO',
	packages=['hcapi'],
	zip_safe=False,
	test_suite='nose.collector',
	tests_require=['nose'])