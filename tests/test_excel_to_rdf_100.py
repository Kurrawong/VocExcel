import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from vocexcel.convert import rdf_to_excel
from vocexcel.utils import load_workbook

TEMPLATES_DIR_PATH = Path(__file__).parent.parent.absolute() / "vocexcel/templates"
TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"



def test_100():
    input_rdf_file = TESTS_DATA_DIR_PATH / "100GA.ttl"
    output_excel_file = TESTS_DATA_DIR_PATH / "100-from-rdf.xlsx"

    e = rdf_to_excel(input_rdf_file, output_excel_file)  # , template_version="1.0.0"

    wb = load_workbook(output_excel_file)
    assert wb["Introduction"]["E4"].value == "1.0.0"

    assert wb["Concept Scheme"]["B16"].value == "gatheme:sample_acquisition_and_management"

    output_excel_file.unlink(missing_ok=True)




def test_100_ga():
    input_rdf_file = TESTS_DATA_DIR_PATH / "100GA.ttl"
    output_excel_file = TESTS_DATA_DIR_PATH / "100GA-from-rdf.xlsx"

    e = rdf_to_excel(input_rdf_file, output_excel_file, template_version="1.0.0.GA")

    wb = load_workbook(output_excel_file)
    assert wb["Introduction"]["E4"].value == "1.0.0.GA"

    assert wb["Concept Scheme"]["B18"].value == "https://pid.geoscience.gov.au/dataset/ga/148553"

    assert wb["Additional Concept Properties"]["A5"].value == ":fake_child_broader"
    assert wb["Additional Concept Properties"]["I5"].value == ":waterSampling"

    output_excel_file.unlink(missing_ok=True)