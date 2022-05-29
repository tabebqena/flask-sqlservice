from setuptools import setup

setup(
    name='flask-sqlservice',
    # should match the package folder
    packages=['flasksqlservice'],
    version='1.0',
    author='Ahmad Yahia',
    description='Flask extension for integration with sqlservice package',
    # long_description='',
    # url='',
    keywords='flask, sql, extensions, sqlservice',
    python_requires='>=3.7, <4',
    install_requires=['sqlservice', 'flask'],
    # extras_require={
    #     'test': ['pytest', 'coverage'],
    # },
    entry_points={
        'runners': [
            'sample=sample:main',
        ]
    }
)
