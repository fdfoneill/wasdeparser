# The directory containing this file
HERE = pathlib.Path(__file__).parent

def readme():
	with open('README.md') as f:
		return f.read()

exec(open('wasdeparser/_version.py').read())

setup(name='wasdeparser',
		version=__version__,
		description='Download and clean WASDE agricultural data',
		long_description=readme(),
		long_description_content_type='text/markdown',
		author="F. Dan O'Neill",
		author_email='fdfoneill@gmail.com',
		license='MIT',
		packages=['wasdeparser'],
		include_package_data=True,
		# third-party dependencies
		install_requires=[
			'pandas',
			'requests',
			'xlrd',
			'XlsxWriter'
			],
		# tests
		test_suite='nose.collector',
		tests_require=[
			'nose'
			],
		zip_safe=False,
		# console scripts
		entry_points = {

			'console_scripts': [
				]
			}
		)