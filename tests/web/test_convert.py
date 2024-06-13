from fastapi.testclient import TestClient
from rdflib import Graph
from pathlib import Path

TESTS_DATA_DIR_PATH = Path(__file__).parent.parent.absolute() / "data"


def test(client: TestClient):
    with open(TESTS_DATA_DIR_PATH / "062_simple1.xlsx", "rb") as file:
        files = {"upload_file": file}
        response = client.post("/api/v1/convert", files=files)

        assert response.status_code == 200
        assert "text/turtle" in response.headers.get("content-type")

        graph = Graph()
        graph.parse(data=response.text)
        assert len(graph) > 0
