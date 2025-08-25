import sys
from pathlib import Path

import vocexcel.utils

sys.path.append(str(Path(__file__).parent.parent.absolute() / "vocexcel"))
from rdflib import URIRef
from rdflib.namespace import SKOS

TESTS_DATA_DIR_PATH = Path(__file__).parent.absolute() / "data"


def test_example_complex():
    from vocexcel import models
    from vocexcel.convert_030 import (
        extract_concept_scheme,
        extract_concepts_and_collections,
    )

    wb = vocexcel.utils.load_workbook(
        Path(__file__).parent.parent.resolve()
        / "vocexcel/templates"
        / "VocExcel-template-030.xlsx"
    )

    sheet = wb["example - complex"]
    cs = extract_concept_scheme(sheet)

    concepts, collections = extract_concepts_and_collections(sheet)

    g = models.Vocabulary(
        concept_scheme=cs, concepts=concepts, collections=collections
    ).to_graph()

    top_concepts = 0
    for s, o in g.subject_objects(SKOS.topConceptOf):
        top_concepts += 1
    assert top_concepts == 3, (
        f'Processing the test vocab ("example - complex" sheet in workbook '
        f"VocExcel-template.ttl) has yielded {top_concepts} top concepts but it should have "
        f"yielded 3"
    )

    for o in g.objects(
        URIRef(
            "http://resource.geosciml.org/classifierscheme/cgi/2016.01/particletype"
        ),
        SKOS.prefLabel,
    ):
        assert str(o) == "Particle Type", (
            f'The title (preferredLabel) of the "example - complex" sheet vocab in '
            f'the VocExcel-template.ttl is {s} but should be "Particle Type"'
        )


if __name__ == "__main__":
    test_example_complex()
