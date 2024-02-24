from pathlib import Path

import PyPDF2
import pytest

from pdf_splitter import (
    PdfSplitter,
    construct_output_filepath,
    construct_regex_pattern_from_search_words,
)


@pytest.mark.parametrize(
    "results_into_subdirectories, expected_filepath",
    [
        [False, Path("/output/An Input Document John Doe.pdf")],
        [True, Path("/output/John Doe/An Input Document John Doe.pdf")],
    ],
)
def test_construct_output_filepath(
    results_into_subdirectories: bool, expected_filepath: Path
) -> None:
    input_file = Path("/input/An Input Document.pdf")
    match = "John Doe"
    output_directory = Path("/output")

    output_file = construct_output_filepath(
        input_file,
        output_directory,
        match,
        results_into_subdirectories=results_into_subdirectories,
    )
    assert output_file.as_uri() == expected_filepath.as_uri()


def test_construct_regex_pattern_from_search_words() -> None:
    search_words = ["John Doe", "Jane Smith", "Anneliese Muster"]
    assert (
        "(John Doe|Jane Smith|Anneliese Muster)"
        == construct_regex_pattern_from_search_words(search_words)
    )


def test_split(tmp_path: Path) -> None:
    pdf_splitter = PdfSplitter(
        input_files=[
            Path("testData/PDF Splitter Example Doc.pdf"),
        ],
        regex_pattern=r"(John Doe)",
        output_directory=tmp_path,
    )

    pdf_splitter.do_split()
    assert pdf_splitter.output_directory.exists()
    output_file = (
        pdf_splitter.output_directory / "PDF Splitter Example Doc John Doe.pdf"
    )
    assert output_file.exists()
    reader = PyPDF2.PdfReader(output_file)
    assert len(reader.pages) == 1


def test_split_several(tmp_path: Path) -> None:
    pdf_splitter = PdfSplitter(
        input_files=[
            Path("testData/PDF Splitter Example Doc.pdf"),
        ],
        regex_pattern=r"(John Doe|Anneliese Muster)",
        output_directory=tmp_path,
    )

    pdf_splitter.do_split()
    assert pdf_splitter.output_directory.exists()
    for name in ["John Doe", "Anneliese Muster"]:
        output_file = (
            pdf_splitter.output_directory / f"PDF Splitter Example Doc {name}.pdf"
        )
        assert output_file.exists()
        reader = PyPDF2.PdfReader(output_file)
        assert len(reader.pages) == 1
