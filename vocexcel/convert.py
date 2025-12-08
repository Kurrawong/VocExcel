import argparse
import sys
import warnings
from pathlib import Path
from typing import BinaryIO, Literal, Optional
from typing import Literal as TypeLiteral

from openpyxl.workbook import Workbook
from pydantic import ValidationError

warnings.simplefilter(action="ignore", category=UserWarning)

THIS_FILE_PATH = Path(__file__)
sys.path.append(str(THIS_FILE_PATH.parent.parent))

from vocexcel import models
from vocexcel.convert_021 import (
    extract_concepts_and_collections as extract_concepts_and_collections_021,
)
from vocexcel.convert_030 import (
    extract_concept_scheme as extract_concept_scheme_030,
)
from vocexcel.convert_030 import (
    extract_concepts_and_collections as extract_concepts_and_collections_030,
)
from vocexcel.convert_040 import (
    extract_concept_scheme as extract_concept_scheme_040,
)
from vocexcel.convert_040 import (
    extract_concepts_and_collections as extract_concepts_and_collections_040,
)
from vocexcel.convert_043 import (
    create_prefix_dict,
)
from vocexcel.convert_043 import (
    extract_concept_scheme as extract_concept_scheme_043,
)
from vocexcel.convert_043 import (
    extract_concepts_and_collections as extract_concepts_and_collections_043,
)
from vocexcel.convert_060 import excel_to_rdf as excel_to_rdf_060
from vocexcel.convert_063 import excel_to_rdf as excel_to_rdf_063
from vocexcel.convert_070 import excel_to_rdf as excel_to_rdf_070
from vocexcel.convert_085 import excel_to_rdf as excel_to_rdf_085
from vocexcel.convert_0812 import excel_to_rdf as excel_to_rdf_0812
from vocexcel.convert_085 import rdf_to_excel as rdf_to_excel_085
from vocexcel.utils import (
    EXCEL_FILE_ENDINGS,
    KNOWN_FILE_ENDINGS,
    KNOWN_TEMPLATE_VERSIONS,
    RDF_FILE_ENDINGS,
    ConversionError,
    get_template_version,
    load_workbook,
    return_error,
)

TEMPLATE_VERSION = None


def excel_to_rdf(
    excel_file: Path | BinaryIO,
    output_file: Optional[Path] = None,
    allowed_template_versions=None,
    output_format: Literal["rdf", "graph"] = "rdf",
    error_format: TypeLiteral["python", "cmd", "json"] = "python",
):
    """Converts an Excel workbook file to RDF

    Parameters:
        excel_file: The Excel workbook file to convert
        output_file: Optional. If set, the RDF output will be written to this file in the turtle format
        allowed_template_versions: Optional. User-specified list of allowed template versions. If not given, all versions allowed
        output_format: Optional, default rdf. rdf: return serialized RDF in the turtle format, graph: return an RDFLib Graph object
        error_format: Optional, default python. the kind of errors to return: python is Python, cmd is command line-formatted string, json is stringified JSON

    Returns:
        output_format or an error in one of the error_formats
    """
    wb = load_workbook(excel_file, error_format)
    if not isinstance(wb, Workbook):
        return wb

    actual_template_version = get_template_version(wb, error_format)

    if allowed_template_versions is not None:
        if not set(allowed_template_versions).issubset(KNOWN_TEMPLATE_VERSIONS):
            error = ValueError(
                f"You have restricted the allowed template versions to unknown template versions. Known template versions are {', '.join(KNOWN_TEMPLATE_VERSIONS)}"
            )
            return return_error(error, error_format)
        elif actual_template_version not in allowed_template_versions:
            error = ValueError(
                f"You have restricted the allowed template versions to {', '.join(allowed_template_versions)} but supplied a template of version {actual_template_version}"
            )
            return return_error(error, error_format)
    elif actual_template_version not in KNOWN_TEMPLATE_VERSIONS:
        error = ConversionError(
            f"Unknown template version: {actual_template_version}. Must be one of {', '.join(KNOWN_TEMPLATE_VERSIONS)}"
        )
        return return_error(error, error_format)

    if actual_template_version in ["0.8.12", "0.9.0", "0.9.0.GA"]:
        return excel_to_rdf_0812(
            wb, output_file, actual_template_version, output_format, error_format
        )

    elif actual_template_version in ["0.8.5", "0.8.5.GA"]:
        return excel_to_rdf_085(
            wb, output_file, actual_template_version, output_format, error_format
        )

    elif actual_template_version in ["0.7.1"]:
        return excel_to_rdf_070(
            wb,
            output_file,
            output_format,
            template_version=actual_template_version,
        )

    elif actual_template_version in ["0.7.0"]:
        return excel_to_rdf_070(
            wb,
            output_file,
            output_format,
            template_version=actual_template_version,
        )

    # The way the voc is made - which Excel sheets to use - is dependent on the particular template version
    elif actual_template_version in ["0.6.2", "0.6.3"]:
        return excel_to_rdf_063(
            wb,
            output_file,
            "longturtle" if output_format == "rdf" else "graph",
            template_version=actual_template_version,
        )

    elif actual_template_version in ["0.5.0", "0.6.0", "0.6.1"]:
        return excel_to_rdf_060(
            wb,
            output_file,
            "longturtle" if output_format == "rdf" else "graph",
        )

    elif actual_template_version in ["0.4.3", "0.4.4"]:
        try:
            sheet = wb["Concept Scheme"]
            concept_sheet = wb["Concepts"]
            additional_concept_sheet = wb["Additional Concept Features"]
            collection_sheet = wb["Collections"]
            prefix_sheet = wb["Prefix Sheet"]
            prefix = create_prefix_dict(prefix_sheet)

            concepts, collections = extract_concepts_and_collections_043(
                concept_sheet, additional_concept_sheet, collection_sheet, prefix
            )
            cs = extract_concept_scheme_043(sheet, prefix)
        except ValidationError as e:
            raise ConversionError(f"ConceptScheme processing error: {e}")

    elif actual_template_version == "0.3.0" or actual_template_version == "0.2.1":
        sheet = wb["vocabulary"]
        # read from the vocabulary sheet of the workbook unless given a specific sheet

        if actual_template_version == "0.2.1":
            concepts, collections = extract_concepts_and_collections_021(sheet)
        elif actual_template_version == "0.3.0":
            concepts, collections = extract_concepts_and_collections_030(sheet)

        try:
            cs = extract_concept_scheme_030(sheet)
        except ValidationError as e:
            raise ConversionError(f"ConceptScheme processing error: {e}")

    elif (
        actual_template_version == "0.4.0"
        or actual_template_version == "0.4.1"
        or actual_template_version == "0.4.2"
    ):
        try:
            sheet = wb["Concept Scheme"]
            concept_sheet = wb["Concepts"]
            additional_concept_sheet = wb["Additional Concept Features"]
            collection_sheet = wb["Collections"]

            concepts, collections = extract_concepts_and_collections_040(
                concept_sheet, additional_concept_sheet, collection_sheet
            )
            cs = extract_concept_scheme_040(sheet)
        except ValidationError as e:
            error = ConversionError(f"ConceptScheme processing error: {e}")
            return return_error(error, error_format)

    # Build the total vocab
    vocab_graph = models.Vocabulary(
        concept_scheme=cs, concepts=concepts, collections=collections
    ).to_graph()

    if output_file is not None:
        return vocab_graph.serialize(destination=str(output_file), format="longturtle")
    else:  # print to std out
        if output_format == "graph":
            return vocab_graph
        else:
            return vocab_graph.serialize(format="longturtle")


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
        rdf_file,
        output_file,
        template_version,
        output_format,
        error_format,
    )


def main(args=None):
    if args is None:  # vocexcel run via entrypoint
        args = sys.argv[1:]

    if args is None or args == []:
        return return_error(
            ValueError("You must supply the path to a file to convert"), "cmd"
        )

    parser = argparse.ArgumentParser(
        prog="vocexcel", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-i",
        "--info",
        help="The version and other info of this instance of VocExcel.",
        action="store_true",
    )

    parser.add_argument(
        "input_file",
        nargs="?",  # allow 0 or 1 file name as argument
        type=Path,
        help="The Excel file to convert to a SKOS vocabulary in RDF or an RDF file to convert to an Excel file.",
    )

    parser.add_argument(
        "-o",
        "--outputfile",
        help="An optionally-provided output file path. If not provided, output from Excel-> RDF is to standard out and RDF->Excel is input file with .xlsx file ending.",
        required=False,
    )

    args = parser.parse_args(args)

    if not args:
        parser.print_help()
        parser.exit()

    if args.info:
        # not sure what to do here, just removing the errors
        from vocexcel import __version__

        print(f"VocExel version: {__version__}")
        from vocexcel.utils import KNOWN_TEMPLATE_VERSIONS

        print(
            f"Known template versions: {', '.join(sorted(KNOWN_TEMPLATE_VERSIONS, reverse=True))}"
        )
    elif args.input_file:
        if not args.input_file.suffix.lower().endswith(tuple(KNOWN_FILE_ENDINGS)):
            error = ValueError(
                "Files for conversion must either end with .xlsx (Excel) or one of the known RDF file endings, '{}'".format(
                    "', '".join(RDF_FILE_ENDINGS.keys())
                )
            )
            return return_error(error, "cmd")

        print(f"Processing file {args.input_file}")

        # input file looks like an Excel file, so convert Excel -> RDF
        if args.input_file.suffix.lower().endswith(tuple(EXCEL_FILE_ENDINGS)):
            try:
                o = excel_to_rdf(
                    args.input_file, output_file=args.outputfile, output_format="rdf"
                )
                if args.outputfile is None:
                    print(o)
            except Exception as e:
                return return_error(e, "cmd")

        # RDF file ending, so convert RDF -> Excel
        else:
            rdf_to_excel(args.input_file, args.outputfile, error_format="cmd")

            if args.outputfile is None:
                print(f"Converted result at {args.input_file.with_suffix('.xlsx')}")
            else:
                print(f"Converted result at {args.outputfile}")
    return None


if __name__ == "__main__":
    try:
        retval = main(sys.argv[1:])
        if retval is not None:
            sys.exit(retval)
    except ValueError:
        print("You must supply a path to a file to convert")
