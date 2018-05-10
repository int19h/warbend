from setuptools import setup
from warbend import __version__

setup(
    name='warbend',
    version=__version__,
    description='Mount & Blade save game editing toolkit',
    license='MIT',
    author='Pavel Minaev',
    author_email='int19h@gmail.com',
    url='https://github.com/int19h/warbend/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: MIT License',
    ],
    packages=['warbend'],
)
