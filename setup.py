from setuptools import setup

def readme():
	with open('README.md') as f:
		return f.read()

setup(name='hc-api-python',
	version='0.1',
	description='Client Wrapper for the HouseCanary API',
	long_description=readme(),
	url='http://github.com/housecanary/hc-api-python',
	author='Jeff Francisco',
	author_email='jeff.francisco7@gmail.com',
	# license='TODO',
	packages=['housecanary'],
	zip_safe=False,
	test_suite='nose.collector',
	tests_require=['nose'])