"""pdf_splitter - Splits up a multipage PDF file into separate pages """

__version__ = '0.1.0'
__author__ = 'Michael Meer <michael.meer@gmail.com>'
__all__ = ['PdfSplitter', 'construct_output_filepath']

from .pdf_splitter import PdfSplitter, construct_output_filepath
