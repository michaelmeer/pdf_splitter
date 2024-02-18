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
    input_file: pathlib.Path, output_directory: pathlib.Path, match: str
) -> pathlib.Path:
    output_file_name = f"{input_file.stem} {match}{input_file.suffix}"
    return output_directory / output_file_name


class PdfSplitter:
    def __init__(
        self,
        input_files: list[pathlib.Path],
        regex_pattern: str,
        output_directory: pathlib.Path,
    ):
        self._input_files = input_files
        for input_file in self._input_files:
            if not input_file.exists():
                raise ValueError(f"Input file {input_file} doesn't exist, quitting...")

        self._regex_pattern = regex_pattern
        self._output_directory = output_directory

    @cached_property
    def output_directory(self) -> pathlib.Path:
        output_directory = pathlib.Path(self._output_directory)
        output_directory.mkdir(exist_ok=True)
        return output_directory

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
                logger.info("Page %d: %s", current_page_nr, match)
                match_dict[match].append(current_page_nr)

        for match, page_nrs in match_dict.items():
            pdf_writer = PyPDF2.PdfWriter()
            for page_nr in page_nrs:
                pdf_writer.add_page(pdf_reader.pages[page_nr])

            output_file = construct_output_filepath(
                input_file, self.output_directory, match
            )
            with open(output_file, "wb") as fp:
                pdf_writer.write(fp)

    @cached_property
    def regex_pattern(self) -> re.Pattern:
        return re.compile(self._regex_pattern)


def main():
    parser = argparse.ArgumentParser(
        description="Splits multipage PDF into several pages, based on Regex matches"
    )
    parser.add_argument(
        "--input_files",
        type=str,
        help="Path to input PDF files; enclose in quotes, accepts * as wildcard for directories or filenames",
    )
    parser.add_argument(
        "--regex_pattern", type=str, help="Regex Pattern, e.g. (John Doe|Jane Smith)"
    )
    parser.add_argument(
        "--output_directory",
        type=pathlib.Path,
        help="Output Directory for the split up PDF files",
    )
    args = parser.parse_args()

    input_files_names = glob.glob(args.input_files)
    input_files = [pathlib.Path(input_file_name) for input_file_name in input_files_names]
    pdfSplitter = PdfSplitter(
        input_files=input_files,
        regex_pattern=args.regex_pattern,
        output_directory=args.output_directory,
    )
    pdfSplitter.do_split()


if __name__ == "__main__":
    main()
