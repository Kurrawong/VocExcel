import sys
from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef, compare
from rdflib.namespace import DCTERMS, SKOS

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel import convert
from vocexcel.utils import ConversionError

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "vocexcel/templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_empty_template():
    with pytest.raises(ConversionError) as e:
        convert.excel_to_rdf(TEMPLATES_DIR_PATH / "VocExcel-template-043.xlsx")
    assert "7 validation errors for ConceptScheme" in str(e)

@pytest.mark.xfail(reason="Incompatible with Pydantic v2, 40008 and 44005 are nto parsable as dates")
def test_simple():
    g = convert.excel_to_rdf(
        TESTS_DATA_DIR_PATH / "043_simple_valid.xlsx",
        # output_file=TESTS_DATA_DIR_PATH /"043_simple_valid_nc.ttl"
        output_format="graph",
    )
    assert (
        URIRef(
            "http://resource.geosciml.org/classifierscheme/cgi/2016.01/particletype"
        ),
        SKOS.prefLabel,
        Literal("Particle Type", lang="en"),
    ) in g, "PrefLabel for vocab is not correct"
    assert (
        URIRef("http://resource.geosciml.org/classifier/cgi/particletype/bioclast"),
        DCTERMS.provenance,
        Literal("NADM SLTTs 2004", lang="en"),
    ) in g, "Provenance for vocab is not correct"


def test_exhaustive_template_is_isomorphic():
    g1 = Graph().parse(TESTS_DATA_DIR_PATH / "043_exhaustive.ttl")
    g2 = convert.excel_to_rdf(
        TESTS_DATA_DIR_PATH / "043_exhaustive.xlsx", output_format="graph"
    )
    assert compare.isomorphic(g1, g2), "Graphs are not Isomorphic"


@pytest.mark.xfail(reason="Incompatible with VocPub 3.1. Failing since 0.6.2.")
def test_rdf_to_excel():
    TESTS_DATA_DIR_PATH = Path(__file__).parent
    g1 = Graph().parse(TESTS_DATA_DIR_PATH / "043_exhaustive.ttl")
    convert.rdf_to_excel(
        TESTS_DATA_DIR_PATH / "043_exhaustive.ttl",
        output_file=TESTS_DATA_DIR_PATH / "043_exhaustive_roundtrip.xlsx",
    )
    g2 = convert.excel_to_rdf(
        TESTS_DATA_DIR_PATH / "043_exhaustive.xlsx", output_format="graph"
    )

    # clean up files
    Path(TESTS_DATA_DIR_PATH / "043_exhaustive_roundtrip.xlsx").unlink(missing_ok=True)
    assert compare.isomorphic(g1, g2), "Graphs are not Isomorphic"
