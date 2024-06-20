import sys
from pathlib import Path

import pytest
from rdflib import URIRef
from rdflib.namespace import RDF, SKOS

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel.convert_070 import (
    extract_concept_scheme,
    extract_concepts,
    extract_prefixes,
)
from vocexcel.utils import load_workbook

TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


@pytest.fixture
def get_excel():
    return load_workbook(TESTS_DATA_DIR_PATH / "070_long.xlsx")


def test_extract_prefixes(get_excel):
    wb = get_excel
    n = extract_prefixes(wb["Prefixes"])

    assert n == {"ex:": "http://example.com/"}


def test_extract_concept_scheme(get_excel):
    wb = get_excel
    prefixes = extract_prefixes(wb["Prefixes"])
    cs, cs_iri = extract_concept_scheme(wb["Concept Scheme"], prefixes)

    assert cs_iri == URIRef(
        "https://pid.geoscience.gov.au/def/voc/ga/GeomorphologySettings"
    )


def test_extract_concepts(get_excel):
    wb = get_excel
    prefixes = extract_prefixes(wb["Prefixes"])
    cs, cs_iri = extract_concept_scheme(wb["Concept Scheme"], prefixes)
    cons = extract_concepts(wb["Concepts"], prefixes, cs_iri)

    concepts = []
    for c in cons.subjects(RDF.type, SKOS.Concept):
        concepts.append(c)

    assert (
        URIRef(
            "https://pid.geoscience.gov.au/def/voc/ga/GeomorphologySettings/Mass_Movement_Process"
        )
        in concepts
    )

    assert len(concepts) == 374


# @pytest.mark.xfail(reason="Failing since 0.6.2.")
# def test_extract_collections():
#     wb = load_workbook(Path(__file__).parent / "060_simple.xlsx")
#     prefixes = extract_prefixes(wb["Prefixes"])
#     cols = extract_collections(wb["Collections"], prefixes)
#     # print(cols.serialize(format="longturtle"))
#     expected = """
#         PREFIX dcterms: <http://purl.org/dc/terms/>
#         PREFIX ex: <http://example.com/>
#         PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
#
#         ex:small-chickens
#             a skos:Concept ;
#             dcterms:provenance "Just made up" ;
#             skos:definition "Breeds of small chickens"@en ;
#             skos:member
#                 ex:bantam ,
#                 ex:silkie ;
#             skos:prefLabel "Small Chickens"@en ;
#         .
#         """
#     g2 = Graph().parse(data=expected)
#     # print((g2 - cols).serialize(format="longturtle"))
#     # print("++++++++++++++")
#     # print((cols - g2).serialize(format="longturtle"))
#     # print(g2.serialize(format="longturtle"))
#     assert compare.isomorphic(cols, g2)
#
#
# def test_extract_additions_concept_properties():
#     wb = load_workbook(Path(__file__).parent / "060_simple.xlsx")
#     prefixes = extract_prefixes(wb["Prefixes"])
#     extra = extract_additions_concept_properties(
#         wb["Additional Concept Properties"], prefixes
#     )
#     expected = """
#         PREFIX ex: <http://example.com/>
#         PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
#
#         ex:bantam
#             skos:notation "ban"^^ex:other-system, "B"^^<http://system-x.com> ;
#             skos:relatedMatch <http://other-voc.com/bantam> ;
#         .
#         """
#     g2 = Graph().parse(data=expected)
#     assert compare.isomorphic(extra, g2)
#
#
# @pytest.mark.xfail(reason="Failing since 0.6.2.")
# def test_rdf_to_excel():
#     wb = load_workbook(Path(__file__).parent / "060_simple.xlsx")
#     g = excel_to_rdf(wb, output_format="graph")
#     # print(g.serialize(format="longturtle"))
#     expected = """
#         PREFIX cdterms: <http://purl.org/dc/terms/>
#         PREFIX ch: <http://example.com/chickens/>
#         PREFIX dcat: <http://www.w3.org/ns/dcat#>
#         PREFIX ex: <http://example.com/>
#         PREFIX isoroles: <http://def.isotc211.org/iso19115/-1/2018/CitationAndResponsiblePartyInformation/code/CI_RoleCode/>
#         PREFIX owl: <http://www.w3.org/2002/07/owl#>
#         PREFIX prov: <http://www.w3.org/ns/prov#>
#         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#         PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
#         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
#
#         ex:chickens
#             a skos:ConceptScheme ;
#             cdterms:created "2022-12-01"^^xsd:date ;
#             cdterms:creator [
#                     a prov:Agent ;
#                     rdfs:label "Nicholas Car"
#                 ] ;
#             cdterms:identifier "chickens"^^xsd:token ;
#             cdterms:modified "2022-12-01"^^xsd:date ;
#             cdterms:publisher <http://linked.data.gov.au/org/agldwg> ;
#             owl:versionIRI ch:0.0.1 ;
#             owl:versionInfo "0.0.1" ;
#             skos:definition "A vocabulary of breeds of chicken"@en ;
#             skos:prefLabel "Chickens Breeds"@en ;
#             prov:qualifiedAttribution [
#                     dcat:hadRole isoroles:custodian ;
#                     prov:agent [
#                             a prov:Agent ;
#                             rdfs:label "Nicholas Car"
#                         ]
#                 ] ;
#         .
#
#         ex:rhode-island-red
#             a skos:Concept ;
#             cdterms:provenance "Taken from Wikipedia" ;
#             cdterms:source "https://en.wikipedia.org/wiki/Rhode_Island_Red"^^xsd:anyURI ;
#             skos:definition "The Rhode Island Red is an American breed of domestic chicken. It is the state bird of Rhode Island."@en ;
#             skos:prefLabel "Rhode Island Red"@en ;
#         .
#
#         ex:small-chickens
#             a skos:Concept ;
#             cdterms:provenance "Just made up" ;
#             skos:definition "Breeds of small chickens"@en ;
#             skos:member
#                 ex:bantam ,
#                 ex:silkie ;
#             skos:prefLabel "Small Chickens"@en ;
#         .
#
#         ex:bantam
#             a skos:Concept ;
#             skos:notation "ban"^^ex:other-system, "B"^^<http://system-x.com> ;
#             cdterms:source "https://en.wikipedia.org/wiki/Bantam_(poultry)"^^xsd:anyURI ;
#             skos:definition "A bantam is any small variety of fowl, usually of chicken or duck."@en ;
#             skos:narrower ex:silkie ;
#             skos:prefLabel "Bantam"@en ;
#             skos:relatedMatch <http://other-voc.com/bantam> ;
#         .
#
#         <http://linked.data.gov.au/org/agldwg>
#             a prov:Agent ;
#             rdfs:label "Agldwg" ;
#         .
#
#         ex:silkie
#             a skos:Concept ;
#             skos:altLabel
#                 "Chinese silk chicken"@en ,
#                 "Silky"@en ;
#             skos:definition "The Silkie (also known as the Silky or Chinese silk chicken) is a breed of chicken named for its atypically fluffy plumage, which is said to feel like silk and satin."@en ;
#             skos:prefLabel "Silkie"@en ;
#         .
#     """
#     g2 = Graph().parse(data=expected)
#     assert compare.isomorphic(g, g2)
