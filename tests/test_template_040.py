import sys
from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef, compare
from rdflib.namespace import SKOS

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel import convert
from vocexcel.utils import ConversionError

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "vocexcel/templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_empty_template():
    with pytest.raises(
        ConversionError, match=".*7 validation errors for ConceptScheme.*"
    ):
        convert.excel_to_rdf(TEMPLATES_DIR_PATH / "VocExcel-template-040.xlsx")


@pytest.mark.xfail(
    reason="Incompatible with Pydantic v2, 40008 and 44005 are nto parsable as dates"
)
def test_simple():
    convert.excel_to_rdf(
        TESTS_DATA_DIR_PATH / "040_simple.xlsx",
        output_file=TESTS_DATA_DIR_PATH / "040_simple.ttl",
    )
    g = Graph().parse(TESTS_DATA_DIR_PATH / "040_simple.ttl")
    assert len(g) == 142
    assert (
        URIRef(
            "http://resource.geosciml.org/classifierscheme/cgi/2016.01/particletype"
        ),
        SKOS.prefLabel,
        Literal("Particle Type", lang="en"),
    ) in g, "PrefLabel for vocab is not correct"
    Path(TESTS_DATA_DIR_PATH / "040_simple.ttl").unlink()


def test_exhaustive_template_is_isomorphic():
    g1 = Graph().parse(TESTS_DATA_DIR_PATH / "040_exhaustive_comparison.ttl")
    g2 = convert.excel_to_rdf(
        TESTS_DATA_DIR_PATH / "040_exhaustive.xlsx", output_format="graph"
    )
    assert compare.isomorphic(g1, g2), "Graphs are not Isomorphic"


def test_minimal_template_is_isomorphic():
    g1 = Graph().parse(TESTS_DATA_DIR_PATH / "040_minimal_comparison.ttl")
    g2 = convert.excel_to_rdf(
        TESTS_DATA_DIR_PATH / "040_minimal.xlsx", output_format="graph"
    )
    assert compare.isomorphic(g1, g2), "Graphs are not Isomorphic"
