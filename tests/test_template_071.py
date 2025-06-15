import sys
from pathlib import Path

import pytest
from rdflib import URIRef
from rdflib.namespace import RDF, SKOS

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel import convert
from vocexcel.convert_071 import (
    extract_concept_scheme,
    extract_concepts,
    extract_prefixes,
)
from vocexcel.utils import ConversionError, load_workbook

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "vocexcel/templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_empty_template():
    with pytest.raises(ConversionError, match=".*Your vocabulary has no IRI.*"):
        convert.excel_to_rdf(TEMPLATES_DIR_PATH / "VocExcel-template-071.xlsx")


def test_empty_template_ga():
    with pytest.raises(ConversionError, match=".*Your vocabulary has no IRI.*"):
        convert.excel_to_rdf(TEMPLATES_DIR_PATH / "VocExcel-template-071-GA.xlsx")


@pytest.fixture
def get_excel():
    return load_workbook(TESTS_DATA_DIR_PATH / "071_demo.xlsx")


def test_extract_concepts(get_excel):
    wb = get_excel
    prefixes = extract_prefixes(wb["Prefixes"])
    cs, cs_iri = extract_concept_scheme(wb["Concept Scheme"], prefixes)
    cons = extract_concepts(wb["Concepts"], prefixes, cs_iri)

    concepts = []
    for c in cons.subjects(RDF.type, SKOS.Concept):
        concepts.append(c)

    assert URIRef("http://example.com/chicken-breeds/thisisabad__-URI") in concepts

    assert len(concepts) == 2
