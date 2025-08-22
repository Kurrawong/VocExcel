import sys
from pathlib import Path

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import DCTERMS, SKOS

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel import convert
from vocexcel.utils import ConversionError

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "vocexcel/templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_empty_template():
    with pytest.raises(
        ConversionError, match=".*7 validation errors for ConceptScheme.*"
    ):
        convert.excel_to_rdf(TEMPLATES_DIR_PATH / "VocExcel-template-042.xlsx")


@pytest.mark.xfail(
    reason="Incompatible with Pydantic v2, 40008 and 44005 are nto parsable as dates"
)
def test_simple():
    g = convert.excel_to_rdf(
        TESTS_DATA_DIR_PATH / "042_simple.xlsx", output_format="graph"
    )
    assert len(g) == 142
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
    # tidy up
    # Path(Path(__file__).parent / "042_simple_example.ttl").unlink()
