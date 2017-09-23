from setuptools import setup

setup (
	name = 'KC31AutoLevel',
	packages=['KC31AutoLevel'],
	include_package_data = True,
	install_requires = [
		'flask',
		'pymongo',
		'requests',
		'ipython',
		'sympy',
		'numpy',
		'pyserial'
	],
)
