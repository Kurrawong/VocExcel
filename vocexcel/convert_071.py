from pathlib import Path
from typing import Literal as TypeLiteral
from typing import Optional

from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, PROV, RDF, SDO, SKOS, XSD

REG = Namespace("http://purl.org/linked-data/registry#")

from vocexcel.convert_070 import excel_to_rdf as excel_to_rdf_070
from vocexcel.convert_070 import (
    extract_additions_concept_properties as extract_additions_concept_properties_070,
)
from vocexcel.convert_070 import extract_collections as extract_collections_070

# from vocexcel.convert_070 import extract_concept_scheme as extract_concept_scheme_070
from vocexcel.convert_070 import extract_concepts as extract_concepts_070
from vocexcel.convert_070 import extract_prefixes as extract_prefixes_070
from vocexcel.utils import (
    STATUSES,
    VOCDERMODS,
    ConversionError,
    bind_namespaces,
    make_agent,
    make_iri,
    split_and_tidy_to_strings,
)


def extract_prefixes(sheet: Worksheet):
    return extract_prefixes_070(sheet)


def extract_concept_scheme(
    sheet: Worksheet, prefixes, template_version="0.7.1"
) -> tuple[Graph, str]:
    iri_s = sheet["B3"].value
    title = sheet["B4"].value
    description = sheet["B5"].value
    created = sheet["B6"].value
    modified = sheet["B7"].value
    creator = sheet["B8"].value
    publisher = sheet["B9"].value
    custodian = sheet["B10"].value
    version = str(sheet["B11"].value).strip("'")
    history_note = sheet["B12"].value
    citation = sheet["B13"].value
    derived_from = sheet["B14"].value
    voc_der_mod = sheet["B15"].value
    themes = split_and_tidy_to_strings(sheet["B16"].value)
    status = sheet["B17"].value
    catalogue_pid = sheet["B18"].value

    if iri_s is None:
        raise ConversionError(
            "Your vocabulary has no IRI. Please add it to the Concept Scheme sheet"
        )
    else:
        iri = make_iri(iri_s, prefixes)

    if title is None:
        raise ConversionError(
            "Your vocabulary has no title. Please add it to the Concept Scheme sheet"
        )

    if description is None:
        raise ConversionError(
            "Your vocabulary has no description. Please add it to the Concept Scheme sheet"
        )

    if created is None:
        raise ConversionError(
            "Your vocabulary has no created date. Please add it to the Concept Scheme sheet"
        )

    if modified is None:
        raise ConversionError(
            "Your vocabulary has no modified date. Please add it to the Concept Scheme sheet"
        )

    if creator is None:
        raise ConversionError(
            "Your vocabulary has no creator. Please add it to the Concept Scheme sheet"
        )

    if publisher is None:
        raise ConversionError(
            "Your vocabulary has no publisher. Please add it to the Concept Scheme sheet"
        )

    if history_note is None:
        raise ConversionError(
            "Your vocabulary has no History Note statement. Please add it to the Concept Scheme sheet"
        )

    # citation

    if derived_from is not None:
        if voc_der_mod is None:
            raise ConversionError(
                "If you supply a 'Derived From' value - IRI of another vocab - "
                "you must also supply a 'Derivation Mode' value"
            )

        if voc_der_mod not in VOCDERMODS:
            raise ConversionError(
                f"You have supplied a vocab derivation mode for your vocab of {voc_der_mod} but it is not recognised. "
                f"If supplied, it must be one of {', '.join(VOCDERMODS.keys())}"
            )

        derived_from = make_iri(derived_from, prefixes)

    # keywords

    if status is not None and status not in STATUSES:
        raise ConversionError(
            f"You have supplied a status for your vocab of {status} but it is not recognised. "
            f"If supplied, it must be one of {', '.join(STATUSES.keys())}"
        )

    # catalogue PID

    g = Graph(bind_namespaces="rdflib")
    g.add((iri, RDF.type, SKOS.ConceptScheme))
    g.add((iri, SKOS.prefLabel, Literal(title, lang="en")))
    g.add((iri, SKOS.definition, Literal(description, lang="en")))
    g.add((iri, SDO.dateCreated, Literal(created.date(), datatype=XSD.date)))
    g.add((iri, SDO.dateModified, Literal(modified.date(), datatype=XSD.date)))
    g += make_agent(creator, SDO.creator, prefixes, iri)
    g += make_agent(publisher, SDO.publisher, prefixes, iri)

    if custodian is not None:
        for _custodian in split_and_tidy_to_strings(custodian):
            DATAROLES = Namespace("https://linked.data.gov.au/def/data-roles/")
            g += make_agent(_custodian, DATAROLES.custodian, prefixes, iri)
            g.bind("DATAROLES", DATAROLES)

    if version is not None:
        g.add((iri, SDO.version, Literal(str(version))))
        g.add((iri, OWL.versionIRI, URIRef(iri + "/" + str(version))))

    g.add((iri, SKOS.historyNote, Literal(history_note, lang="en")))

    if citation is not None:
        if str(citation).startswith("http"):
            val = Literal(citation, datatype=XSD.anyURI)
        else:
            val = Literal(citation)

        g.add((iri, SDO.citation, val))

    if derived_from is not None:
        qd = BNode()
        g.add((iri, PROV.qualifiedDerivation, qd))
        g.add((qd, PROV.entity, URIRef(derived_from)))
        g.add((qd, PROV.hadRole, URIRef(VOCDERMODS[voc_der_mod])))

    if themes is not None:
        for theme in themes:
            try:
                theme = make_iri(theme, prefixes)
            except ConversionError:
                theme = Literal(theme)
            g.add((iri, SDO.keywords, theme))

    if status is not None:
        g.add((iri, REG.status, URIRef(STATUSES[status])))

    if catalogue_pid is not None:
        if str(catalogue_pid).startswith("http"):
            val = Literal(catalogue_pid, datatype=XSD.anyURI)
        else:
            val = Literal(catalogue_pid)

        g.add((iri, SDO.identifier, val))

    bind_namespaces(g, prefixes)
    g.bind("", Namespace(str(iri) + "/"))
    return g, iri


def extract_concepts(sheet: Worksheet, prefixes, cs_iri):
    return extract_concepts_070(sheet, prefixes, cs_iri)


def extract_collections(sheet: Worksheet, prefixes, cs_iri):
    return extract_collections_070(sheet, prefixes, cs_iri)


def extract_additions_concept_properties(sheet: Worksheet, prefixes):
    return extract_additions_concept_properties_070(sheet, prefixes)


def excel_to_rdf(
    wb: Workbook,
    output_file_path: Optional[Path] = None,
    output_format: TypeLiteral[
        "longturtle", "turtle", "xml", "json-ld", "graph"
    ] = "longturtle",
    validate: bool = False,
    error_level=1,
    message_level=1,
    log_file: Optional[Path] = None,
):
    return excel_to_rdf_070(
        wb,
        output_file_path,
        output_format,
        validate,
        profile="vocpub-410",
        error_level=error_level,
        message_level=message_level,
        log_file=log_file,
        template_version="0.7.1",
    )
