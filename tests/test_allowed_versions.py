import json
import sys
from pathlib import Path

from rdflib import Literal, URIRef
from rdflib.namespace import SDO, XSD
import pytest

from vocexcel.utils import ConversionError
from vocexcel import convert

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "vocexcel/templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"

def test_user_specified_versions():
    with pytest.raises(ValueError) as e:
        g = convert.excel_to_rdf(TESTS_DATA_DIR_PATH / "085.xlsx", output_format="graph", allowed_template_versions=["0.8.5.GA"])
        assert "You have restricted the allowed template versions" in e
