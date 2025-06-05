from pathlib import Path
from typing import Literal as TypeLiteral
from typing import Optional

from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, PROV, RDF, RDFS, SDO, SKOS, XSD

from vocexcel.convert_070 import (
    extract_additions_concept_properties as extract_additions_concept_properties_070,
)
from vocexcel.convert_070 import extract_collections as extract_collections_070
from vocexcel.convert_070 import extract_prefixes as extract_prefixes_070
from vocexcel.utils import (
    STATUSES,
    VOCDERMODS,
    ConversionError,
    add_top_concepts,
    bind_namespaces,
    make_agent,
    make_iri,
    split_and_tidy_to_iris,
    split_and_tidy_to_strings,
    validate_with_profile,
)


def extract_prefixes(sheet: Worksheet):
    return extract_prefixes_070(sheet)


def extract_concept_scheme(
    sheet: Worksheet, prefixes, template_version="0.8.0"
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
    if template_version == "0.8.0.GA":
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

    if template_version == "0.8.0.GA":
        if catalogue_pid is None or not str(catalogue_pid).startswith(
            "https://pid.geoscience.gov.au/"
        ):
            raise ConversionError(
                "All GA vocabularies must have an eCat ID starting https://pid.geoscience.gov.au/dataset/..., assigned in the Concept Scheme metadata"
            )

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
        g.add((iri, SDO.status, URIRef(STATUSES[status])))

    if template_version == "0.8.0.GA":
        g.add((iri, SDO.identifier, Literal(catalogue_pid, datatype=XSD.anyURI)))

    bind_namespaces(g, prefixes)
    g.bind("", Namespace(str(iri) + "/"))
    return g, iri


def extract_concepts(sheet: Worksheet, prefixes, cs_iri):
    g = Graph(bind_namespaces="rdflib")
    i = 4
    while True:
        # get values
        iri_s = sheet[f"A{i}"].value
        pref_label = sheet[f"B{i}"].value
        definition = sheet[f"C{i}"].value
        alt_labels = sheet[f"D{i}"].value
        narrower = sheet[f"E{i}"].value
        history_note = sheet[f"F{i}"].value
        citation = sheet[f"G{i}"].value
        is_defined_by = sheet[f"H{i}"].value
        status = sheet[f"I{i}"].value
        example = sheet[f"J{i}"].value
        image_url = sheet[f"K{i}"].value
        image_embedded = sheet[f"L{i}"].value

        # check values
        if iri_s is None:
            break

        iri = make_iri(iri_s, prefixes)

        if pref_label is None:
            raise ConversionError(
                f"You must provide a Preferred Label for Concept {iri_s}"
            )

        if definition is None:
            raise ConversionError(f"You must provide a Definition for Concept {iri_s}")

        if status is not None and status not in STATUSES:
            raise ConversionError(
                f"You have supplied a status for your Concept of {status} but it is not recognised. "
                f"If supplied, it must be one of {', '.join(STATUSES.keys())}"
            )

        if image_url is not None:
            if not image_url.startswith("http"):
                raise ConversionError(
                    "If supplied, an Image URL must start with 'http'"
                )

        # TODO: test embedded mage is not too large
        # image_embedded
        if image_embedded not in [None, "#VALUE!"]:
            raise ConversionError(
                "The Image Embedded colum, you must only insert images or leave it blank. "
                f"You have an unexpected value in Cell L{i}"
            )

        # ignore example Concepts
        if iri_s in [
            "http://example.com/earth-science",
            "http://example.com/atmospheric-science",
            "http://example.com/geology",
        ]:
            continue

        # create Graph
        g.add((iri, RDF.type, SKOS.Concept))
        g.add((iri, SKOS.inScheme, cs_iri))

        if "@" in pref_label:
            val, lang = pref_label.strip().split("@")
            g.add((iri, SKOS.prefLabel, Literal(val, lang=lang)))
        else:
            g.add((iri, SKOS.prefLabel, Literal(pref_label.strip(), lang="en")))
        g.add((iri, SKOS.definition, Literal(definition.strip(), lang="en")))

        if alt_labels is not None:
            for al in split_and_tidy_to_strings(alt_labels):
                g.add((iri, SKOS.altLabel, Literal(al, lang="en")))

        if narrower is not None:
            for n in split_and_tidy_to_iris(narrower, prefixes):
                g.add((iri, SKOS.narrower, n))
                g.add((n, SKOS.broader, iri))

        if history_note is not None:
            g.add((iri, SKOS.historyNote, Literal(history_note.strip())))

        if citation is not None:
            for _citation in split_and_tidy_to_strings(citation):
                g.add(
                    (iri, SDO.citation, Literal(_citation.strip(), datatype=XSD.anyURI))
                )

        if is_defined_by is not None:
            g.add((iri, RDFS.isDefinedBy, URIRef(is_defined_by.strip())))
        else:
            g.add((iri, RDFS.isDefinedBy, cs_iri))

        if status is not None:
            g.add((iri, SDO.status, URIRef(STATUSES[status])))

        if example is not None:
            g.add((iri, SKOS.example, Literal(str(example).strip())))

        if image_url is not None:
            g.add(
                (iri, SDO.image, Literal(str(image_url).strip(), datatype=XSD.anyURI))
            )

        if image_embedded == "#VALUE!":
            g.add((iri, SDO.image, Literal(f"Image at L{i}")))

        i += 1

    bind_namespaces(g, prefixes)
    return g


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
    profile="vocpub-51",
    error_level=1,
    message_level=1,
    log_file: Optional[Path] = None,
    template_version="0.8.0",
):
    prefixes = extract_prefixes(wb["Prefixes"])
    cs, cs_iri = extract_concept_scheme(
        wb["Concept Scheme"], prefixes, template_version
    )
    cons = extract_concepts(wb["Concepts"], prefixes, cs_iri)
    cols = extract_collections(wb["Collections"], prefixes, cs_iri)
    extra = extract_additions_concept_properties(
        wb["Additional Concept Properties"], prefixes
    )

    g = cs + cons + cols + extra
    g = add_top_concepts(g)
    g.bind("cs", cs_iri)

    if validate:
        validate_with_profile(
            g,
            profile=profile,
            error_level=error_level,
            message_level=message_level,
            log_file=log_file,
        )

    if output_file_path is not None:
        g.serialize(destination=str(output_file_path), format=output_format)
    else:  # print to std out
        if output_format == "graph":
            return g
        else:
            return g.serialize(format=output_format)
