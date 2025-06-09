import argparse
import logging
import sys
import warnings
from pathlib import Path
from typing import BinaryIO, Literal, Optional

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
from vocexcel.convert_080 import excel_to_rdf as excel_to_rdf_080
from vocexcel.convert_080 import rdf_to_excel as rdf_to_excel_080
from vocexcel.utils import (
    EXCEL_FILE_ENDINGS,
    KNOWN_FILE_ENDINGS,
    RDF_FILE_ENDINGS,
    ConversionError,
    get_template_version,
    load_workbook,
    validate_with_profile,
)

TEMPLATE_VERSION = None


def excel_to_rdf(
    input_file_path: Path | BinaryIO,
    profile="vocpub-49",
    sheet_name: Optional[str] = None,
    output_file_path: Optional[Path] = None,
    output_format: Literal["turtle", "xml", "json-ld", "graph"] = "longturtle",
    error_level=1,  # TODO: list Literal possible values
    message_level=1,  # TODO: list Literal possible values
    log_file: Optional[Path] = None,
    validate: Optional[bool] = False,
):
    """Converts a sheet within an Excel workbook to an RDF file"""
    wb = load_workbook(input_file_path)
    template_version = get_template_version(wb)

    if template_version in ["0.8.0", "0.8.0.GA"]:
        return excel_to_rdf_080(
            wb,
            output_file_path,
            output_format,
            template_version,
        )

    if template_version in ["0.7.1"]:
        return excel_to_rdf_070(
            wb,
            output_file_path,
            output_format,
            validate,
            profile,
            error_level,
            message_level,
            log_file,
            template_version,
        )

    if template_version in ["0.7.0"]:
        return excel_to_rdf_070(
            wb,
            output_file_path,
            output_format,
            validate,
            profile,
            error_level,
            message_level,
            log_file,
            template_version,
        )

    # The way the voc is made - which Excel sheets to use - is dependent on the particular template version
    elif template_version in ["0.6.2", "0.6.3"]:
        return excel_to_rdf_063(
            wb,
            output_file_path,
            output_format,
            validate,
            profile,
            error_level,
            message_level,
            log_file,
            template_version,
        )

    elif template_version in ["0.5.0", "0.6.0", "0.6.1"]:
        return excel_to_rdf_060(
            wb,
            output_file_path,
            output_format,
            validate,
            profile,
            error_level,
            message_level,
            log_file,
        )

    elif template_version in ["0.4.3", "0.4.4"]:
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

    elif template_version == "0.3.0" or template_version == "0.2.1":
        sheet = wb["vocabulary" if sheet_name is None else sheet_name]
        # read from the vocabulary sheet of the workbook unless given a specific sheet

        if template_version == "0.2.1":
            concepts, collections = extract_concepts_and_collections_021(sheet)
        elif template_version == "0.3.0":
            concepts, collections = extract_concepts_and_collections_030(sheet)

        try:
            cs = extract_concept_scheme_030(sheet)
        except ValidationError as e:
            raise ConversionError(f"ConceptScheme processing error: {e}")

    elif (
        template_version == "0.4.0"
        or template_version == "0.4.1"
        or template_version == "0.4.2"
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
            raise ConversionError(f"ConceptScheme processing error: {e}")

    # Build the total vocab
    vocab_graph = models.Vocabulary(
        concept_scheme=cs, concepts=concepts, collections=collections
    ).to_graph()

    if validate:
        validate_with_profile(
            vocab_graph,
            profile=profile,
            error_level=error_level,
            message_level=message_level,
            log_file=log_file,
        )

    if output_file_path is not None:
        vocab_graph.serialize(destination=str(output_file_path), format=output_format)
    else:  # print to std out
        if output_format == "graph":
            return vocab_graph
        else:
            return vocab_graph.serialize(format=output_format)


def rdf_to_excel(
    rdf_file: Path, output_file_path: Optional[Path] = None, template_version="0.8.0"
):
    rdf_to_excel_080(
        rdf_file,
        output_file_path,
        template_version,
    )


def main(args=None):
    if args is None:  # vocexcel run via entrypoint
        args = sys.argv[1:]

    if args is None or args == []:
        raise ValueError("You must supply the path to an Excel file to convert to RDF")

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
            print(
                "Files for conversion must either end with .xlsx (Excel) or one of the known RDF file endings, '{}'".format(
                    "', '".join(RDF_FILE_ENDINGS.keys())
                )
            )
            parser.exit()

        print(f"Processing file {args.input_file}")

        # input file looks like an Excel file, so convert Excel -> RDF
        if args.input_file.suffix.lower().endswith(tuple(EXCEL_FILE_ENDINGS)):
            try:
                o = excel_to_rdf(
                    args.input_file,
                    profile=None,
                    sheet_name=None,
                    output_file_path=args.outputfile,
                    output_format=None,
                    error_level=None,
                    message_level=None,
                    log_file=None,
                    validate=None,
                )
                if args.outputfile is None:
                    print(o)
            except ConversionError as err:
                logging.error("{0}".format(err))
                return 1

        # RDF file ending, so convert RDF -> Excel
        else:
            rdf_to_excel(
                args.input_file,
                output_file_path=args.outputfile,
            )
            if args.outputfile is None:
                print(f"Converted result at {args.input_file.with_suffix('.xlsx')}")
            else:
                print(f"Converted result at {args.outputfile}")


if __name__ == "__main__":
    try:
        retval = main(sys.argv[1:])
        if retval is not None:
            sys.exit(retval)
    except ValueError:
        print("You must supply a path to a file to convert")
