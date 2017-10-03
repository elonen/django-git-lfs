import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open('requirements.txt') as reqs:
    install_requires = [
        line for line in reqs.read().split('\n') if (line and not
                                                     line.startswith('--'))
    ]

setup(
    name='djlfs-standalone-server',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Git LFS server (standalone server django project).',
    long_description=README,
    url='https://github.com/elonen/djlfs-server',
    author='Jarno Elonen',
    author_email='elonen@iki.fi',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Version Control :: Git'
    ],
    zip_safe=False,
    install_requires=install_requires,
)
