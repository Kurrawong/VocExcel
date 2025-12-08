import sys
from pathlib import Path

from rdflib import URIRef, Literal
from rdflib.namespace import SDO, RDF, SKOS, XSD

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel import convert

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "vocexcel/templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_090():
    g = convert.excel_to_rdf(TESTS_DATA_DIR_PATH / "090.xlsx", output_format="graph")

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

    assert (
        URIRef("http://example.com/voc/rock-types/marble"),
        SDO.status,
        URIRef("https://linked.data.gov.au/def/reg-statuses/experimental"),
    ) in g

    assert (
        URIRef("http://example.com/voc/rock-types/m-types"),
        SKOS.member,
        URIRef("http://example.com/voc/rock-types/marble"),
    ) in g


def test_090GA():
    g = convert.excel_to_rdf(TESTS_DATA_DIR_PATH / "090GA.xlsx", output_format="graph")

    assert (
        URIRef("http://example.com/voc/rock-types"),
        SDO.status,
        URIRef("https://linked.data.gov.au/def/reg-statuses/experimental"),
    ) in g

    assert (
        URIRef("http://example.com/voc/rock-types/marble"),
        SDO.status,
        URIRef("https://linked.data.gov.au/def/reg-statuses/experimental"),
    ) in g

    assert (
        URIRef("http://example.com/voc/rock-types/m-types"),
        SKOS.member,
        URIRef("http://example.com/voc/rock-types/marble"),
    ) in g

    assert (
        URIRef("http://example.com/voc/rock-types"),
        SDO.identifier,
        Literal("https://pid.geoscience.gov.au/dataset/1234", datatype=XSD.anyURI),
    ) in g


def test_090_ntgs():
    g = convert.excel_to_rdf(
        TESTS_DATA_DIR_PATH / "090_ntgs.xlsx", output_format="graph"
    )

    assert (
        URIRef("https://linked.data.gov.au/def/cox-classification/carbonatite"),
        SKOS.topConceptOf,
        URIRef("https://linked.data.gov.au/def/cox-classification"),
    ) in g

    assert (
        URIRef("https://linked.data.gov.au/def/cox-classification/carbonatite"),
        SKOS.narrower,
        URIRef("https://linked.data.gov.au/def/cox-classification/carbonate-hosted-zn"),
    ) in g

    assert (
        URIRef("https://linked.data.gov.au/def/cox-classification/carbonate-hosted-zn"),
        SKOS.broader,
        URIRef("https://linked.data.gov.au/def/cox-classification/carbonatite"),
    ) in g

    assert (
        URIRef("https://linked.data.gov.au/def/cox-classification/carbonate-hosted-zn"),
        SKOS.inScheme,
        URIRef("https://linked.data.gov.au/def/cox-classification"),
    ) in g

    # print(g.serialize(format="longturtle"))
