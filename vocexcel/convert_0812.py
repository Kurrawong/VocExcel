from pathlib import Path
from typing import Literal as TypeLiteral
from typing import Optional

from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from pyshacl import validate as shacl_validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SDO, SKOS, XSD

from vocexcel.convert_085 import (
    extract_prefixes as extract_prefixes_085,
    extract_concept_scheme as extract_concept_scheme_085,
    rdf_to_excel as rdf_to_excel_085,
)
from vocexcel.utils import (
    STATUSES,
    ConversionError,
    bind_namespaces,
    make_iri,
    return_error,
    split_and_tidy_to_iris,
    split_and_tidy_to_strings,
    add_top_concepts,
    RDF_FILE_ENDINGS,
    ShaclValidationError,
)

DATAROLES = Namespace("https://linked.data.gov.au/def/data-roles/")


def extract_prefixes(
    sheet: Worksheet,
    error_format: TypeLiteral["python", "cmd", "json"] = "python",
) -> dict[str, Namespace] | str | None:
    return extract_prefixes_085(sheet, error_format)


def extract_concept_scheme(
    sheet: Worksheet,
    prefixes,
    template_version="0.8.5",
    error_format: TypeLiteral["python", "cmd", "json"] = "python",
) -> tuple[Graph, str]:
    return extract_concept_scheme_085(sheet, prefixes, template_version, error_format)


def extract_concepts(
    sheet: Worksheet,
    prefixes,
    cs_iri,
    error_format: TypeLiteral["python", "cmd", "json"] = "python",
):
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

        iri = make_iri(iri_s, prefixes, namespace=cs_iri + "/")

        if pref_label is None:
            error = ConversionError(
                f"You must provide a Preferred Label for Concept {iri_s}"
            )
            return return_error(error, error_format)

        if definition is None:
            error = ConversionError(
                f"You must provide a Definition for Concept {iri_s}"
            )
            return return_error(error, error_format)

        if status is not None and status not in STATUSES:
            error = ConversionError(
                f"You have supplied a status for your Concept of {status} but it is not recognised. "
                f"If supplied, it must be one of {', '.join(STATUSES.keys())}"
            )
            return return_error(error, error_format)

        if image_url is not None:
            if not image_url.startswith("http"):
                error = ConversionError(
                    "If supplied, an Image URL must start with 'http'"
                )
                return return_error(error, error_format)

        # TODO: test embedded mage is not too large
        # image_embedded
        if image_embedded not in [None, "#VALUE!"]:
            error = ConversionError(
                "The Image Embedded colum, you must only insert images or leave it blank. "
                f"You have an unexpected value in Cell L{i}"
            )
            return return_error(error, error_format)

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
            for n in split_and_tidy_to_iris(narrower, prefixes, cs_iri + "/"):
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


def extract_collections(
    sheet: Worksheet,
    prefixes,
    cs_iri,
    error_format: TypeLiteral["python", "cmd", "json"] = "python",
):
    g = Graph(bind_namespaces="rdflib")
    i = 4
    while True:
        # get values
        iri_s = sheet[f"A{i}"].value
        pref_label = sheet[f"B{i}"].value
        definition = sheet[f"C{i}"].value
        members = sheet[f"D{i}"].value
        history_note = sheet[f"E{i}"].value

        # check values
        if iri_s is None:
            break

        iri = make_iri(iri_s, prefixes, namespace=cs_iri + "/")

        if pref_label is None:
            raise ConversionError(
                f"You must provide a Preferred Label for Collection {iri_s}"
            )

        if definition is None:
            raise ConversionError(
                f"You must provide a Definition for Collection {iri_s}"
            )

        # create Graph
        g.add((iri, RDF.type, SKOS.Collection))
        g.add((iri, SKOS.inScheme, cs_iri))
        g.add((iri, RDFS.isDefinedBy, cs_iri))
        if str(iri).startswith(str(cs_iri)):
            g.add((iri, RDFS.isDefinedBy, cs_iri))
        g.add((iri, SKOS.prefLabel, Literal(pref_label, lang="en")))
        g.add((iri, SKOS.definition, Literal(definition, lang="en")))

        if members is not None:
            for n in split_and_tidy_to_iris(members, prefixes, cs_iri + "/"):
                g.add((iri, SKOS.member, n))

        if history_note is not None:
            g.add((iri, SKOS.historyNote, Literal(history_note.strip())))

        i += 1

    bind_namespaces(g, prefixes)
    return g


def extract_additions_concept_properties(
    sheet: Worksheet,
    prefixes,
    cs_iri,
    error_format: TypeLiteral["python", "cmd", "json"] = "python",
):
    g = Graph(bind_namespaces="rdflib")
    i = 4
    while True:
        # get values
        iri_s = sheet[f"A{i}"].value
        related_s = sheet[f"B{i}"].value
        close_s = sheet[f"C{i}"].value
        exact_s = sheet[f"D{i}"].value
        narrow_s = sheet[f"E{i}"].value
        broad_s = sheet[f"F{i}"].value
        notation_s = sheet[f"G{i}"].value
        notation_type_s = sheet[f"H{i}"].value

        # check values
        if iri_s is None:
            break

        i += 1

        # ignore example Concepts
        if iri_s in [
            "http://example.com/geology",
        ]:
            continue

        # create Graph
        iri = make_iri(iri_s, prefixes, namespace=cs_iri + "/")

        if related_s is not None:
            related = make_iri(related_s, prefixes, namespace=cs_iri + "/")
            g.add((iri, SKOS.relatedMatch, related))

        if close_s is not None:
            close = make_iri(close_s, prefixes, namespace=cs_iri + "/")
            g.add((iri, SKOS.closeMatch, close))

        if exact_s is not None:
            exact = make_iri(exact_s, prefixes, namespace=cs_iri + "/")
            g.add((iri, SKOS.exactMatch, exact))

        if narrow_s is not None:
            narrow = make_iri(narrow_s, prefixes, namespace=cs_iri + "/")
            g.add((iri, SKOS.narrowMatch, narrow))

        if broad_s is not None:
            broad = make_iri(broad_s, prefixes, namespace=cs_iri + "/")
            g.add((iri, SKOS.broadMatch, broad))

        if notation_s is not None:
            notations = split_and_tidy_to_strings(notation_s)
            if notation_type_s is not None:
                notation_types = split_and_tidy_to_iris(notation_type_s, prefixes, cs_iri)
            else:
                notation_types = [XSD.token for x in notations]

            for j, notation in enumerate(notations):
                g.add(
                    (
                        iri,
                        SKOS.notation,
                        Literal(notation, datatype=notation_types[j]),
                    )
                )

    bind_namespaces(g, prefixes)
    return g


def excel_to_rdf(
    wb: Workbook,
    output_file: Optional[Path] = None,
    template_version: str = "0.9.0",
    output_format: TypeLiteral[
        "graph",
        "rdf",
    ] = "rdf",
    error_format: TypeLiteral["python", "cmd", "json"] = "python",
):
    """Converts an Excel workbook file to RDF

    Parameters:
        excel_file: The Excel workbook file to convert
        output_file: Optional. If set, the RDF output will be written to this file in the turtle format.
        output_format: Optional, default rdf. rdf: return serialized RDF in the turtle format, graph: return an RDFLib Graph object
        error_format: Optional, default python. the kind of errors to return: python is Python, cmd is command line-formatted string, json is stringified JSON

    Returns:
        output_format or an error in one of the error_formats
    """

    if not isinstance(wb, Workbook):
        error = ValueError(
            "Files for conversion to Excel must end with one of the RDF file formats: '{}'".format(
                "', '".join(RDF_FILE_ENDINGS.keys())
            )
        )
        return return_error(error, error_format)

    if output_file is not None:
        if not Path(output_file).suffix in RDF_FILE_ENDINGS:
            error = ValueError(
                f"If specifying output_file, it must have a file suffix in {', '.join(RDF_FILE_ENDINGS)}, not {output_file}."
            )
            return return_error(error, error_format)

    if template_version not in ["0.8.12", "0.9.0", "0.9.0.GA"]:
        error = ValueError(
            f"This converter can only handle templates with versions 0.8.x or 0.8.x.GA, not {template_version}"
        )
        return return_error(error, error_format)

    allowed_output_formats = ["graph", "rdf"]
    if output_format not in allowed_output_formats:
        error = ValueError(
            f"If specifying output_format, it be in {', '.join(allowed_output_formats)}, not {output_format}."
        )
        return return_error(error, error_format)

    allowed_error_formats = ["python", "cmd", "json"]
    if error_format not in allowed_error_formats:
        error = ValueError(
            f"error_format must be on of {', '.join(allowed_error_formats)}, not {error_format}"
        )
        return return_error(error, error_format)

    prefixes = extract_prefixes(wb["Prefixes"], error_format)
    if not isinstance(prefixes, dict):
        return prefixes

    x = extract_concept_scheme(
        wb["Concept Scheme"], prefixes, template_version, error_format
    )
    if isinstance(x, tuple):
        cs, cs_iri = x
    else:
        return x

    cons = extract_concepts(wb["Concepts"], prefixes, cs_iri)
    if not isinstance(cons, Graph):
        return cons

    cols = extract_collections(wb["Collections"], prefixes, cs_iri)
    if not isinstance(cols, Graph):
        return cols

    extra = extract_additions_concept_properties(
        wb["Additional Concept Properties"], prefixes, cs_iri
    )
    if not isinstance(extra, Graph):
        return extra

    g = cs + cons + cols + extra
    g = add_top_concepts(g)
    g.bind("cs", cs_iri)

    # validate the RDF file
    shacl_graph = Graph().parse(Path(__file__).parent / "vocpub-5.1.ttl")
    v = shacl_validate(g, shacl_graph=shacl_graph, allow_warnings=True)
    if not v[0]:
        return return_error(ShaclValidationError(v[2], v[1]), error_format)

    if output_file is not None:
        g.serialize(destination=str(output_file), format="longturtle")
    else:  # print to std out
        if output_format == "graph":
            return g
        else:
            return g.serialize(format="longturtle")


def rdf_to_excel(
    rdf_file: Path,
    output_file: Optional[Path] = None,
    template_version="0.8.5",
    output_format: TypeLiteral["blob", "file"] = "file",
    error_format: TypeLiteral["python", "cmd", "json"] = "python",
):
    """Converts RDF files to Excel workbooks.

    Parameters:
        rdf_file: Required. An RDF file in one of the common formats understood by RDFLib
        output_file: Optional, default none. A name for an Excel file to output. Must end in .xlsx. Not used if output_format set to blob
        template_version: Optional, default 0.8.5. Currently only 0.8.5 and 0.8.5.GA are supported
        output_format: Optional, default file. Whether to return a binary blob (openpyxl Workbook instance) or write results to file.
        error_format: Optional, default python. the kind of errors to return: python is Python, cmd is command line-formatted string, json is stringified JSON

    Returns:
        output_format or an error in one of the error_formats
    """
    return rdf_to_excel_085(
        rdf_file, output_file, template_version, output_format, error_format
    )
