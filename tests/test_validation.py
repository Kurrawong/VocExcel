import os
import sys
from pathlib import Path

from pyshacl import validate

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel.convert import excel_to_rdf

TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_validate_070_vocpub_410():
    input_exel_file_path = TESTS_DATA_DIR_PATH / "070_long.xlsx"
    validator_file_path = TESTS_DATA_DIR_PATH / "vocpub-4.10.ttl"
    output_file = TESTS_DATA_DIR_PATH / "test_validation_output.ttl"

    excel_to_rdf(input_exel_file_path, output_file=output_file)

    c, rg, rt = validate(
        str(output_file), shacl_graph=str(validator_file_path), allow_warnings=True
    )

    os.unlink(Path(output_file))

    assert c


def test_validate_071_vocpub_410():
    input_exel_file_path = TESTS_DATA_DIR_PATH / "071_demo.xlsx"
    validator_file_path = TESTS_DATA_DIR_PATH / "vocpub-4.10.ttl"
    output_file = TESTS_DATA_DIR_PATH / "test_validation_output.ttl"

    excel_to_rdf(input_exel_file_path, output_file=output_file)

    c, rg, rt = validate(
        str(output_file), shacl_graph=str(validator_file_path), allow_warnings=True
    )

    os.unlink(Path(output_file))

    assert c
