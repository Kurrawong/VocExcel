import sys
from pathlib import Path

from rdflib import URIRef
from rdflib.namespace import SDO, RDF, SKOS

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel import convert

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "vocexcel/templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_085():
    g = convert.excel_to_rdf(TESTS_DATA_DIR_PATH / "0811.xlsx", output_format="graph")

    assert (
        URIRef("http://example.com/voc/rock-types"),
        SDO.status,
        URIRef("https://linked.data.gov.au/def/reg-statuses/experimental"),
    ) in g

    assert (
        URIRef("http://example.com/voc/rock-types/igenous"),
        RDF.type,
        SKOS.Concept,
    ) in g

    assert (
        URIRef("http://example.com/voc/rock-types/metamorphic"),
        RDF.type,
        SKOS.Concept,
    ) in g

    assert (
        URIRef(
            "https://linked.data.gov.au/def/gswa-rock-classification-scheme/sedimentary"
        ),
        RDF.type,
        SKOS.Concept,
    ) in g

    assert (
        URIRef("http://example.com/voc/rock-types/marble"),
        RDF.type,
        SKOS.Concept,
    ) in g

    print(g.serialize(format="longturtle"))


def test_085_ntgs():
    g = convert.excel_to_rdf(
        TESTS_DATA_DIR_PATH / "0811_ntgs.xlsx", output_format="graph"
    )

    print(g.serialize(format="longturtle"))
