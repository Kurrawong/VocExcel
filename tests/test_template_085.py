import json
import sys
from pathlib import Path

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import SDO, XSD

from vocexcel.utils import ConversionError

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel import convert

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "vocexcel/templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_085():
    g = convert.excel_to_rdf(TESTS_DATA_DIR_PATH / "085.xlsx", output_format="graph")

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


def test_085GA():
    g = convert.excel_to_rdf(TESTS_DATA_DIR_PATH / "085GA.xlsx", output_format="graph")

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


def test_085_errors(capsys):
    XL_FILE = TESTS_DATA_DIR_PATH / "085GA.xlsz"
    ERROR_TXT = "Files for conversion to RDF must be Excel files ending .xlsx"

    with pytest.raises(ValueError):
        g = convert.excel_to_rdf(XL_FILE)  # error_format = "python"

    convert.excel_to_rdf(XL_FILE, error_format="cmd")
    assert ERROR_TXT in capsys.readouterr().out

    j = convert.excel_to_rdf(XL_FILE, error_format="json")
    assert ERROR_TXT in j
    p = json.loads(j)
    assert ERROR_TXT in p["message"]

    XL_FILE = TESTS_DATA_DIR_PATH / "080.xlsx"
    ERROR_TXT = "The version of your template, 0.8.0, is not supported"

    with pytest.raises(ConversionError):
        g = convert.excel_to_rdf(XL_FILE)  # error_format = "python"

    convert.excel_to_rdf(XL_FILE, error_format="cmd")
    assert ERROR_TXT in capsys.readouterr().out

    j = convert.excel_to_rdf(XL_FILE, error_format="json")
    assert ERROR_TXT in j
    p = json.loads(j)
    assert ERROR_TXT in p["message"]

    XL_FILE = TESTS_DATA_DIR_PATH / "085_invalid.xlsx"
    ERROR_TXT = (
        "Your vocabulary has no creator. Please add it to the Concept Scheme sheet"
    )

    with pytest.raises(ConversionError):
        g = convert.excel_to_rdf(XL_FILE)  # error_format = "python"

    convert.excel_to_rdf(XL_FILE, error_format="cmd")
    assert ERROR_TXT in capsys.readouterr().out

    j = convert.excel_to_rdf(XL_FILE, error_format="json")
    assert ERROR_TXT in j
    p = json.loads(j)
    assert ERROR_TXT in p["message"]

    XL_FILE = TESTS_DATA_DIR_PATH / "085_invalid2.xlsx"
    ERROR_TXT = "Your namespace value on sheet Prefixes, cell C5 is invalid. It must start with 'http'"

    with pytest.raises(ConversionError):
        g = convert.excel_to_rdf(XL_FILE)  # error_format = "python"

    convert.excel_to_rdf(XL_FILE, error_format="cmd")
    assert ERROR_TXT in capsys.readouterr().out

    j = convert.excel_to_rdf(XL_FILE, error_format="json")
    assert ERROR_TXT in j
    p = json.loads(j)
    assert ERROR_TXT in p["message"]
