from pathlib import Path

from rdflib import SDO, SKOS, Literal, URIRef

from vocexcel.convert_080 import excel_to_rdf, rdf_to_excel
from vocexcel.utils import STATUSES, load_workbook


def test_basic_080():
    RDF_FILE = Path(__file__).parent / "data" / "eg-valid-080.ttl"
    XL_FILE = RDF_FILE.with_suffix(".xlsx")
    rdf_to_excel(RDF_FILE, output_file_path=XL_FILE)

    g = excel_to_rdf(load_workbook(XL_FILE), output_format="graph")
    # g.serialize(destination=RDF_FILE.with_suffix(".2.ttl"), format="longturtle")

    assert (
        URIRef("https://linked.data.gov.au/def/induration-style"),
        SDO.status,
        URIRef(STATUSES["Experimental"]),
    ) in g

    assert (
        URIRef("https://linked.data.gov.au/def/induration-style"),
        SKOS.historyNote,
        Literal("Created from GA's exiting vocab for VocExcel testing"),
    ) in g

    assert (
        URIRef("https://linked.data.gov.au/def/induration-style/duricrust"),
        SKOS.relatedMatch,
        URIRef("http://example.com/fake"),
    ) in g

    assert (
        URIRef("https://linked.data.gov.au/def/induration-style/bauxitic_nodules"),
        SKOS.notation,
        Literal(
            "NO10",
            datatype=URIRef("https://linked.data.gov.au/def/induration-style/gaId"),
        ),
    ) in g

    XL_FILE.unlink(missing_ok=True)


def test_basic_080GA():
    RDF_FILE = Path(__file__).parent / "data" / "eg-valid-080GA.ttl"
    XL_FILE = RDF_FILE.with_suffix(".xlsx")
    rdf_to_excel(RDF_FILE, output_file_path=XL_FILE)

    g = excel_to_rdf(load_workbook(XL_FILE), output_format="graph")
    # g.serialize(destination=RDF_FILE.with_suffix(".2.ttl"), format="longturtle")
    assert (
        URIRef("https://linked.data.gov.au/def/induration-style"),
        SDO.status,
        URIRef(STATUSES["Experimental"]),
    ) in g

    assert (
        URIRef("https://linked.data.gov.au/def/induration-style"),
        SKOS.historyNote,
        Literal("Created from GA's exiting vocab for VocExcel testing"),
    ) in g

    XL_FILE.unlink(missing_ok=True)
