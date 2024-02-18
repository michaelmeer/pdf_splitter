from pdf_splitter import PdfSplitter, construct_output_filepath
from pathlib import Path
import PyPDF2


def test_construct_filename():
    input_file = Path("/input/An Input Document.pdf")
    match = "John Doe"
    output_directory = Path("/output")

    output_file = construct_output_filepath(input_file, output_directory, match)
    assert (
        output_file.as_uri() == Path("/output/An Input Document John Doe.pdf").as_uri()
    )


def test_split(tmp_path):
    pdf_splitter = PdfSplitter(
        input_files=[
            Path("testData/PDF Splitter Example Doc.pdf"),
        ],
        regex_pattern=r"(John Doe)",
        output_directory=tmp_path,
    )

    pdf_splitter.do_split()
    assert pdf_splitter.output_directory.exists()
    output_file = pdf_splitter.output_directory / "PDF Splitter Example Doc John Doe.pdf"
    assert output_file.exists()
    reader = PyPDF2.PdfReader(output_file)
    assert len(reader.pages) == 1


def test_split_several(tmp_path):
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
