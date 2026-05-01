import sys
from pathlib import Path

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, SDO, SKOS, XSD

from vocexcel.utils import ConversionError

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel import convert

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "vocexcel/templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_100_GA():
    g = convert.excel_to_rdf(TESTS_DATA_DIR_PATH / "100.xlsx", output_format="graph")

    assert (
        URIRef("https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial"),
        SDO.status,
        URIRef("https://linked.data.gov.au/def/reg-statuses/experimental"),
    ) in g

    assert (
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement-x"
        ),
        RDF.type,
        SKOS.Concept,
    ) in g

    assert (
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement-x"
        ),
        SDO.status,
        URIRef("https://linked.data.gov.au/def/reg-statuses/experimental"),
    ) in g

    assert (
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement"
        ),
        SKOS.narrower,
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement-x"
        ),
    ) in g

    assert (
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement-x"
        ),
        SKOS.narrower,
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement-z"
        ),
    ) in g

    assert (
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement-y"
        ),
        SKOS.narrower,
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement-z"
        ),
    ) in g


def test_100_GA():
    g = convert.excel_to_rdf(TESTS_DATA_DIR_PATH / "100GA.xlsx", output_format="graph")

    assert (
        URIRef("https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial"),
        SDO.status,
        URIRef("https://linked.data.gov.au/def/reg-statuses/experimental"),
    ) in g

    assert (
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement-x"
        ),
        RDF.type,
        SKOS.Concept,
    ) in g

    assert (
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement-x"
        ),
        SDO.status,
        URIRef("https://linked.data.gov.au/def/reg-statuses/experimental"),
    ) in g

    assert (
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement"
        ),
        SKOS.narrower,
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial/cement-x"
        ),
    ) in g

    assert (
        URIRef("https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial"),
        SDO.keywords,
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/DataThemes/sample_acquisition_and_management"
        ),
    ) in g

    assert (
        URIRef("https://pid.geoscience.gov.au/def/voc/ga/BoreholeConstructionMaterial"),
        SDO.identifier,
        Literal(
            "https://pid.geoscience.gov.au/dataset/ga/123456",
            datatype=URIRef("https://pid.geoscience.gov.au/def/voc/ga/eCatID"),
        ),
    ) in g


def test_100_GA_invalid():
    with pytest.raises(
        ConversionError, match="All GA vocabularies must have an eCat ID"
    ):
        g = convert.excel_to_rdf(
            TESTS_DATA_DIR_PATH / "100GA-invalid.xlsx", output_format="graph"
        )
