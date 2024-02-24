import io
import os
import re

from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type("")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())


setup(
    name="pdf_splitter",
    version="0.1.0",
    url="https://github.com/michael.meer/pdf_splitter",
    license='MIT',

    author="Michael Meer",
    author_email="michael.meer@gmail.com",

    description="Splits up a multipage PDF file into separate pages based on search matches",
    long_description=read("README.rst"),

    packages=['pdf_splitter'],

    install_requires=['PyPDF2', 'pytest'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.12',
    ],
)
