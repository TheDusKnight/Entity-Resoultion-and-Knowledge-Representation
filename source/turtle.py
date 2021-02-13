from rdflib import Graph, URIRef, Literal, XSD, Namespace, RDF, RDFS, FOAF
import csv
import urllib
# FOAF = Namespace('http://xmlns.com/foaf/0.1/')
MYNS = Namespace('http://inf558.org/myfakenamespace#')
SCHEMA = Namespace('http://schema.org/')

my_kg = Graph()


def create_turtle(productionCompany, title, datePublished, directors, writers, actors, counter):
    my_kg.bind('myns', MYNS)
    my_kg.bind('foaf', FOAF)
    my_kg.bind('my_ns', MYNS)
    my_kg.bind('schema', SCHEMA)
    my_kg.bind('rdf', RDF)
    my_kg.bind('rdfs', RDFS)
    my_kg.bind('xsd', XSD)

    node_uri = URIRef(MYNS[productionCompany])
    my_kg.add((node_uri, RDF.type, SCHEMA['Class']))
    my_kg.add((node_uri, RDFS.subClassOf, SCHEMA['Organization']))
    my_kg.add((node_uri, FOAF.name, Literal(productionCompany)))

    node_uri = URIRef(MYNS['writers'])
    my_kg.add((node_uri, RDF.type, SCHEMA['Property']))
    my_kg.add((node_uri, RDFS.subPropertyOf, SCHEMA['name']))
    # my_kg.add((node_uri, FOAF.name, Literal('Peter')))

    node_uri = URIRef(MYNS[str(counter)])
    my_kg.add((node_uri, RDF.type, SCHEMA['Class']))
    my_kg.add((node_uri, RDFS.subClassOf, SCHEMA['Movie']))
    my_kg.add((node_uri, SCHEMA['productionCompany'], MYNS[productionCompany])) #
    my_kg.add((node_uri, SCHEMA['title'], Literal(title, datatype=XSD.string)))
    my_kg.add((node_uri, SCHEMA['datePublished'], Literal(datePublished, datatype=XSD.string)))
    my_kg.add((node_uri, SCHEMA['directors'], Literal(directors, datatype=XSD.string)))
    my_kg.add((node_uri, MYNS['writers'], Literal(writers, datatype=XSD.string)))
    my_kg.add((node_uri, SCHEMA['actors'], Literal(actors, datatype=XSD.string)))

    # my_kg.serialize('sample_.ttl', format="turtle")


# block_pair = set()
# block_imdb = set()
block_tmd = set()
with open('../Xirui_Zhong_hw03_el.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if int(row[-1]) == 1:
            # block_pair.add((int(row[0]), int(row[1])))
            # block_imdb.add(int(row[0]))
            block_tmd.add(int(row[1]))
file.close()

counter = 0
with open('../movies2/csv_files/imdb_clean.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        create_turtle('imdb', row[1], row[2], row[3], row[4], row[5], counter)
        counter += 1
file.close()

with open('../movies2/csv_files/tmd.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        if int(row[0]) not in block_tmd:
            create_turtle('tmd', row[1], row[2], row[3], row[4], row[5], counter)
            counter += 1
        else:
            print('duplicate found in tmd dataset: ' + row[0])
file.close()

my_kg.serialize('Xirui_Zhong_hw03_triples.ttl', format="turtle")
