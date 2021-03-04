"""
Graph parser is a file used to parse the graphs
from NetworkRepository into a ".gxl" file

@author: Anthony Gillioz
@date: 04.03.2021

"""
import os
from pathlib import Path
from collections import defaultdict, namedtuple
import xml.etree.ElementTree as ET
import xml.dom.minidom as md
import random


__FOLDER = './data/NCI1/'
__DATASET = 'NCI1'
__EXTENSIONS = {
    'edges': '.edges',
    'graph_idx': '.graph_idx',
    'graph_labels': '.graph_labels',
    'node_labels': '.node_labels',
}


def parser(folder, dataset):
    # nodes_lbls_per_graph = load_nodes_per_graph_with_lbls(folder, dataset)
    # edges = load_edges(folder, dataset)
    # edges_per_graph = create_edges_per_graph(nodes_lbls_per_graph, edges)
    #
    # parse_graph_xml(nodes_lbls_per_graph, edges_per_graph, folder)

    graph_lbls = load_file(folder, dataset, __EXTENSIONS['graph_labels'])
    labels_per_graph = defaultdict(list)
    for idx, graph_lbl in enumerate(graph_lbls):
        labels_per_graph[int(graph_lbl)].append((idx, int(graph_lbl)))

    random.seed(42)
    random.shuffle(labels_per_graph[0])
    random.shuffle(labels_per_graph[1])

    graphs_train = labels_per_graph[0][:750] + labels_per_graph[1][:750]
    graphs_val = labels_per_graph[0][750:1000] + labels_per_graph[1][750:1000]
    graphs_test = labels_per_graph[0][1000:] + labels_per_graph[1][1000:]
    print(len(labels_per_graph[0]))
    print(len(labels_per_graph[1]))
    print(len(graphs_train))
    print(len(graphs_test))
    parse_class_xml(graphs_train, folder, 'train')
    parse_class_xml(graphs_val, folder, 'validation')
    parse_class_xml(graphs_test, folder, 'test')

def parse_class_xml(classes, folder, name):
    graph_collection = ET.Element('GraphCollection')

    finger_prints = ET.SubElement(graph_collection, 'fingerprints')

    for idx_graph, class_ in classes:
        print_ = ET.SubElement(finger_prints, 'print')
        print_.set('file', f'molecule_{idx_graph}.gxl')
        print_.set('class', str(class_))

    b_xml = ET.tostring(graph_collection).decode()
    newxml = md.parseString(b_xml)

    folder_data = os.path.join(folder, 'data', '')
    Path(folder_data).mkdir(parents=True, exist_ok=True)

    filename = os.path.join(folder_data, f'{name}.cxl')
    with open(filename, mode='w') as f:
        f.write(newxml.toprettyxml(indent=' ', newl='\n'))


def parse_graph_xml(nodes_per_graph, edges_per_graph, folder):

    for graph_idx in nodes_per_graph.keys():
        graph_name = f'molecule_{graph_idx}'
        nodes = nodes_per_graph[graph_idx]
        edges = edges_per_graph[graph_idx]
        gxl = ET.Element('gxl')

        graph = ET.SubElement(gxl, 'graph')
        graph.set('id', graph_name)
        graph.set('edgeids', 'true')
        graph.set('edgemode', 'undirected')

        mapper = {}

        for idx_node, node in enumerate(nodes):
            mapper[node.node_id] = idx_node

            node_xml = ET.SubElement(graph, 'node')
            node_xml.set('id', str(idx_node))

            attr = ET.SubElement(node_xml, 'attr')
            attr.set('name', 'lbl')

            int_ = ET.SubElement(attr, 'int')
            int_.text = str(node.node_lbl)

        for edge in edges:
            edge_xml = ET.SubElement(graph, 'edge')
            node_idx_start = mapper[edge.node_idx_start]
            node_idx_end = mapper[edge.node_idx_end]
            edge_xml.set('from', str(node_idx_start))
            edge_xml.set('to', str(node_idx_end))

        b_xml = ET.tostring(gxl).decode()
        newxml = md.parseString(b_xml)

        folder_data = os.path.join(folder, 'data', '')
        Path(folder_data).mkdir(parents=True, exist_ok=True)

        filename = os.path.join(folder_data, f'{graph_name}.gxl')
        with open(filename, mode='w') as f:
            f.write(newxml.toprettyxml(indent=' ', newl='\n'))




def create_edges_per_graph(nodes_lbls_per_graph, edges):
    graph_idx = 0
    edges_per_graph = defaultdict(list)
    for max, edge in edges:
        max_node_idx = nodes_lbls_per_graph[graph_idx][-1].node_id

        if max > max_node_idx:
            graph_idx += 1

        edges_per_graph[graph_idx].append(edge)

    return edges_per_graph


def load_edges(folder, dataset):
    raw_edges = load_file(folder, dataset, __EXTENSIONS['edges'])

    edges = []
    Edge = namedtuple('Edge', ['node_idx_start', 'node_idx_end'])

    for edge in raw_edges:
        idx_1, idx_2 = [int(val) - 1 for val in edge.split(',')]

        edges.append((max(idx_1, idx_2), Edge(idx_1, idx_2)))

    return edges


def load_nodes_per_graph_with_lbls(folder, dataset):
    graph_idx = load_file(folder, dataset, __EXTENSIONS['graph_idx'])
    node_labels = load_file(folder, dataset, __EXTENSIONS['node_labels'])

    nodes_per_graph = defaultdict(list)
    Node = namedtuple('Node', ['node_id', 'node_lbl'])

    for idx, (gr_idx, lbl) in enumerate(zip(graph_idx, node_labels)):
        node_label = int(lbl.split(',')[-1])
        nodes_per_graph[int(gr_idx)-1].append(Node(idx, node_label))

    return nodes_per_graph


def load_file(folder, dataset, extension):
    filename = os.path.join(folder, f'{dataset}{extension}')
    with open(filename, mode='r') as fp:
        data = fp.readlines()
    return data


def main():
    parser(__FOLDER, __DATASET)


if __name__ == '__main__':
    main()