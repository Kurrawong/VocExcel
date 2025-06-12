import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from pathlib import Path

from rdflib import Graph

from vocexcel import convert

TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_countrycodes():
    convert.excel_to_rdf(
        TESTS_DATA_DIR_PATH / "030_languages.xlsx",
        output_file=TESTS_DATA_DIR_PATH / "030_languages.ttl",
    )

    # file eg-languages-valid.ttl should have been created
    g = Graph().parse(TESTS_DATA_DIR_PATH / "030_languages.ttl")
    assert len(g) == 4940

    # clean up
    Path.unlink(TESTS_DATA_DIR_PATH / "030_languages.ttl", missing_ok=True)
