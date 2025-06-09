import sys
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SDO, SKOS, XSD

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel import convert

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_080():
    g = convert.excel_to_rdf(TESTS_DATA_DIR_PATH / "080.xlsx", output_format="graph")

    assert (
        URIRef("http://example.com/voc/myvoc"),
        SDO.status,
        URIRef("https://linked.data.gov.au/def/reg-statuses/experimental"),
    ) in g

    assert (
        URIRef("http://example.com/voc/myvoc/cat"),
        SDO.status,
        URIRef("https://linked.data.gov.au/def/reg-statuses/stable"),
    ) in g

    assert (
        URIRef("http://example.com/voc/myvoc/cat"),
        SDO.image,
        Literal("Image at L4"),
    ) in g

    assert (
        URIRef("http://example.com/voc/myvoc/dog"),
        SDO.image,
        Literal(
            "https://en.wikipedia.org/wiki/Dog#/media/File:Huskiesatrest.jpg",
            datatype=XSD.anyURI,
        ),
    ) in g


def test_080GA():
    g = convert.excel_to_rdf(TESTS_DATA_DIR_PATH / "080GA.xlsx", output_format="graph")

    assert (
        URIRef("http://example.com/voc/myvoc"),
        SDO.status,
        URIRef("https://linked.data.gov.au/def/reg-statuses/experimental"),
    ) in g

    assert (
        URIRef("http://example.com/voc/myvoc"),
        SDO.identifier,
        Literal("https://pid.geoscience.gov.au/dataset/1234", datatype=XSD.anyURI),
    ) in g
