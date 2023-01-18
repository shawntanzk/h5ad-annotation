import os
import csv
import shutil
import urllib.request
import pandas as pd

from rdflib import Graph

CL_URL = "http://purl.obolibrary.org/obo/cl.owl"
OLS_URL = "https://www.ebi.ac.uk/ols/ontologies/cl/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F"

TEMP_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../tmp/")
MAPPING_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../mappings.tsv")
MAPPING_NEW_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../mappings2.tsv")


def download_cl():
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)
    cl_file = os.path.join(TEMP_FOLDER, "cl.owl")
    if not os.path.isfile(cl_file):
        urllib.request.urlretrieve(CL_URL, cl_file)
    return cl_file


def delete_temp_folder():
    shutil.rmtree(TEMP_FOLDER)


def read_ontology(ontology_path):
    graph = Graph()
    print("reading ontology file...")
    graph.parse(ontology_path)
    print("ontology file read")
    return graph


def query_label(graph, entity):
    """
    Retrieves label of the given entity.
    Params:
        graph: ontology to query
        entity: ontology term to search
    Returns: labels joined with &
    """
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX CL: <http://purl.obolibrary.org/obo/CL_>
    SELECT DISTINCT (str(?class) as ?term) ?label
    WHERE {
      entity_sf rdfs:label ?label .
    }
    """.replace("entity_sf", entity)

    qres = graph.query(query)
    labels = set()
    for row in qres:
        labels.add(str(row.label).strip())

    return " & ".join(labels)


def enrich_mapping_table():
    g = read_ontology(download_cl())
    output = []
    with open(MAPPING_FILE) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            d = dict()
            d["name"] = row[0]
            d["cl_id"] = row[1]
            d["cl_label"] = query_label(g, row[1])
            d["ols"] = OLS_URL + str(row[1]).replace(":", "_")
            output.append(d)

    table = pd.DataFrame.from_records(output)
    table.to_csv(MAPPING_NEW_FILE, sep="\t", index=False)
    # delete_temp_folder()
    print("Success")


enrich_mapping_table()
