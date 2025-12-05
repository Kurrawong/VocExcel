import json
import sys
from pathlib import Path

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import SDO, XSD, RDF, SKOS

from vocexcel.utils import ConversionError

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel import convert

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "vocexcel/templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_085():
    g = convert.excel_to_rdf(TESTS_DATA_DIR_PATH / "0810.xlsx", output_format="graph")

    print(g.serialize(format="longturtle"))

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
        URIRef("https://linked.data.gov.au/def/gswa-rock-classification-scheme/sedimentary"),
        RDF.type,
        SKOS.Concept,
    ) in g

    assert (
        URIRef("http://example.com/voc/rock-types/marble"),
        RDF.type,
        SKOS.Concept,
    ) in g

    # assert (
    #     URIRef("http://example.com/voc/myvoc/cat"),
    #     SDO.image,
    #     Literal("Image at L4"),
    # ) in g
    #
    # assert (
    #     URIRef("http://example.com/voc/myvoc/dog"),
    #     SDO.image,
    #     Literal(
    #         "https://en.wikipedia.org/wiki/Dog#/media/File:Huskiesatrest.jpg",
    #         datatype=XSD.anyURI,
    #     ),
    # ) in g
