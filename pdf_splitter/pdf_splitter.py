""" Provides functionality to split up up a PDF with several pages into separate PDF files.


"""

import argparse
import glob
import logging
import pathlib
import re
from collections import defaultdict
from functools import cached_property

import PyPDF2

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pdf_splitter")
logger.setLevel(logging.DEBUG)


def construct_output_filepath(
    input_file: pathlib.Path,
    output_directory: pathlib.Path,
    match: str,
    results_into_subdirectories=False,
) -> pathlib.Path:
    """Utility function: Constructs an path & file name for a newly generated PDF based
    on a match"""
    output_file_name = f"{input_file.stem} {match}{input_file.suffix}"
    if results_into_subdirectories:
        return output_directory / match / output_file_name

    return output_directory / output_file_name


def construct_regex_pattern_from_search_words(search_words=list[str]) -> str:
    """Takes a list of search words and creates a regex pattern, e.g.
    ["John Doe", "Jane Smith"] --> (John Doe|Jane Smit)"""
    regex_pattern = f"({'|'.join(search_words)})"
    return regex_pattern


class PdfSplitter:
    def __init__(
        self,
        input_files: list[pathlib.Path],
        regex_pattern: str,
        output_directory: pathlib.Path,
        results_into_subdirectories: bool = False,
    ):
        self._input_files = input_files
        for input_file in self._input_files:
            if not input_file.exists():
                raise ValueError(f"Input file {input_file} doesn't exist, quitting...")

        self._regex_pattern = regex_pattern
        self._output_directory = output_directory
        self._results_into_subdirectories = results_into_subdirectories

    @cached_property
    def output_directory(self) -> pathlib.Path:
        output_directory = pathlib.Path(self._output_directory)
        output_directory.mkdir(exist_ok=True)
        return output_directory

    @property
    def results_into_subdirectories(self) -> bool:
        return self._results_into_subdirectories

    def do_split(self) -> None:
        for input_file in self._input_files:
            self.do_split_for_file(input_file)

    def do_split_for_file(self, input_file: pathlib.Path) -> None:
        pdf_reader = PyPDF2.PdfReader(input_file)
        nr_of_pages = len(pdf_reader.pages)
        logger.info("Input File '%s, %i pages", input_file, nr_of_pages)
        match_dict = defaultdict(list)
        for current_page_nr in range(nr_of_pages):
            current_page = pdf_reader.pages[current_page_nr]
            page_text = current_page.extract_text()
            result = self.regex_pattern.search(page_text)
            if result:
                match = result.group()
                logger.info("Page %d: '%s' matched...", current_page_nr + 1, match)
                match_dict[match].append(current_page_nr)
            else:
                logger.debug("Page %d: no matches", current_page_nr + 1)

        for match, page_nrs in match_dict.items():
            pdf_writer = PyPDF2.PdfWriter()
            for page_nr in page_nrs:
                pdf_writer.add_page(pdf_reader.pages[page_nr])

            output_file = construct_output_filepath(
                input_file,
                self.output_directory,
                match,
                self.results_into_subdirectories,
            )
            with open(output_file, "wb") as fp:
                logger.info("Writing outputfule: '%s'...", output_file)
                pdf_writer.write(fp)

    @cached_property
    def regex_pattern(self) -> re.Pattern:
        return re.compile(self._regex_pattern)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Splits multipage PDF file into several separate PDF file, based on"
                    " Regex matches or search words"
    )
    parser.add_argument(
        "--input_files",
        type=str,
        required=True,
        help="Path to input PDF files; enclose in quotes, accepts * as wildcard for "
             "directories or filenames",
    )
    parser.add_argument(
        "--regex_pattern",
        type=str,
        help="Regex Pattern that can match one or several possible values on a PDF page,"
             " e.g. '(John Doe|Jane Smith)'",
    )
    parser.add_argument(
        "--search_word",
        type=str,
        action="append",
        dest="search_words",
        help="A word to be matched on a PDF page, e.g. 'John Doe'",
    )
    parser.add_argument(
        "--output_directory",
        type=pathlib.Path,
        required=True,
        help="Output Directory for the split up PDF files",
    )
    parser.add_argument(
        "--results_into_subdirectories",
        type=bool,
        required=False,
        default=False,
        help="If True, each newly generated output PDF file is put into a separate "
        "subdirectory within the output_directory ",
    )
    args = parser.parse_args()

    input_files_names = glob.glob(args.input_files)
    input_files = [
        pathlib.Path(input_file_name) for input_file_name in input_files_names
    ]

    regex_pattern = None
    if args.regex_pattern:
        regex_pattern = args.regex_pattern
    elif args.search_words:
        regex_pattern = construct_regex_pattern_from_search_words(args.search_words)

    if regex_pattern is None:
        raise ValueError(
            "either --regex_pattern or --search_word parameters have to be provided!"
        )

    pdf_splitter = PdfSplitter(
        input_files=input_files,
        regex_pattern=regex_pattern,
        output_directory=args.output_directory,
        results_into_subdirectories=args.results_into_subdirectories,
    )
    pdf_splitter.do_split()


if __name__ == "__main__":
    main()
