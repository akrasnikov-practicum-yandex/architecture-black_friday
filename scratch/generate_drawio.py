import xml.etree.ElementTree as ET
import uuid

def create_id():
    return str(uuid.uuid4())

def add_node(parent, id, value, style, x, y, width=120, height=60):
    node = ET.SubElement(parent, "mxCell", {"id": id, "value": value, "style": style, "vertex": "1", "parent": "1"})
    ET.SubElement(node, "mxGeometry", {"x": str(x), "y": str(y), "width": str(width), "height": str(height), "as": "geometry"})
    return node

def add_edge(parent, id, source, target):
    style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
    edge = ET.SubElement(parent, "mxCell", {"id": id, "style": style, "edge": "1", "parent": "1", "source": source, "target": target})
    geometry = ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
    return edge

def create_model(diagram_name):
    diagram = ET.Element("diagram", {"name": diagram_name, "id": create_id()})
    graph_model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "1000", "dy": "1000", "grid": "1", "gridSize": "10", 
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1", 
        "fold": "1", "page": "1", "pageScale": "1", "pageWidth": "1169", 
        "pageHeight": "827", "math": "0", "shadow": "0"
    })
    root = ET.SubElement(graph_model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    return diagram, root

mxfile = ET.Element("mxfile", {"version": "24.6.4"})

# Page 1: Sharding
diagram1, root1 = create_model("1. Sharding")
n_api = "api"
add_node(root1, n_api, "pymongo-api", "rounded=1;whiteSpace=wrap;html=1;", 360, 200)
n_mongos = "mongos"
add_node(root1, n_mongos, "mongos", "rounded=1;whiteSpace=wrap;html=1;", 560, 200)
n_config = "configSrv"
add_node(root1, n_config, "configSrv", "shape=cylinder3;whiteSpace=wrap;html=1;", 760, 100)
n_s1 = "shard1"
add_node(root1, n_s1, "shard1", "shape=cylinder3;whiteSpace=wrap;html=1;", 760, 200)
n_s2 = "shard2"
add_node(root1, n_s2, "shard2", "shape=cylinder3;whiteSpace=wrap;html=1;", 760, 300)

add_edge(root1, create_id(), n_api, n_mongos)
add_edge(root1, create_id(), n_mongos, n_config)
add_edge(root1, create_id(), n_mongos, n_s1)
add_edge(root1, create_id(), n_mongos, n_s2)
mxfile.append(diagram1)

# Page 2: Sharding + Replication
diagram2, root2 = create_model("2. Replication")
add_node(root2, n_api, "pymongo-api", "rounded=1;whiteSpace=wrap;html=1;", 260, 300)
add_node(root2, n_mongos, "mongos", "rounded=1;whiteSpace=wrap;html=1;", 460, 300)

add_node(root2, "c1", "configSrv 1", "shape=cylinder3;whiteSpace=wrap;html=1;", 660, 100, 80, 60)
add_node(root2, "c2", "configSrv 2", "shape=cylinder3;whiteSpace=wrap;html=1;", 760, 100, 80, 60)
add_node(root2, "c3", "configSrv 3", "shape=cylinder3;whiteSpace=wrap;html=1;", 860, 100, 80, 60)

add_node(root2, "s11", "shard1-1", "shape=cylinder3;whiteSpace=wrap;html=1;", 660, 300, 80, 60)
add_node(root2, "s12", "shard1-2", "shape=cylinder3;whiteSpace=wrap;html=1;", 760, 300, 80, 60)
add_node(root2, "s13", "shard1-3", "shape=cylinder3;whiteSpace=wrap;html=1;", 860, 300, 80, 60)

add_node(root2, "s21", "shard2-1", "shape=cylinder3;whiteSpace=wrap;html=1;", 660, 450, 80, 60)
add_node(root2, "s22", "shard2-2", "shape=cylinder3;whiteSpace=wrap;html=1;", 760, 450, 80, 60)
add_node(root2, "s23", "shard2-3", "shape=cylinder3;whiteSpace=wrap;html=1;", 860, 450, 80, 60)

# Group outlines
add_node(root2, "g_c", "Replica Set Config", "swimlane;horizontal=0;whiteSpace=wrap;html=1;", 640, 80, 320, 100)
add_node(root2, "g_s1", "Replica Set Shard 1", "swimlane;horizontal=0;whiteSpace=wrap;html=1;", 640, 280, 320, 100)
add_node(root2, "g_s2", "Replica Set Shard 2", "swimlane;horizontal=0;whiteSpace=wrap;html=1;", 640, 430, 320, 100)


add_edge(root2, create_id(), n_api, n_mongos)
add_edge(root2, create_id(), n_mongos, "c1")
add_edge(root2, create_id(), n_mongos, "s11")
add_edge(root2, create_id(), n_mongos, "s21")
mxfile.append(diagram2)


# Page 3: Caching
diagram3, root3 = create_model("3. Caching")
add_node(root3, n_api, "pymongo-api", "rounded=1;whiteSpace=wrap;html=1;", 260, 300)
add_node(root3, "redis", "redis", "shape=cylinder3;whiteSpace=wrap;html=1;", 260, 150)
add_node(root3, n_mongos, "mongos", "rounded=1;whiteSpace=wrap;html=1;", 460, 300)

add_node(root3, "c1", "configSrv 1", "shape=cylinder3;whiteSpace=wrap;html=1;", 660, 100, 80, 60)
add_node(root3, "c2", "configSrv 2", "shape=cylinder3;whiteSpace=wrap;html=1;", 760, 100, 80, 60)
add_node(root3, "c3", "configSrv 3", "shape=cylinder3;whiteSpace=wrap;html=1;", 860, 100, 80, 60)

add_node(root3, "s11", "shard1-1", "shape=cylinder3;whiteSpace=wrap;html=1;", 660, 300, 80, 60)
add_node(root3, "s12", "shard1-2", "shape=cylinder3;whiteSpace=wrap;html=1;", 760, 300, 80, 60)
add_node(root3, "s13", "shard1-3", "shape=cylinder3;whiteSpace=wrap;html=1;", 860, 300, 80, 60)

add_node(root3, "s21", "shard2-1", "shape=cylinder3;whiteSpace=wrap;html=1;", 660, 450, 80, 60)
add_node(root3, "s22", "shard2-2", "shape=cylinder3;whiteSpace=wrap;html=1;", 760, 450, 80, 60)
add_node(root3, "s23", "shard2-3", "shape=cylinder3;whiteSpace=wrap;html=1;", 860, 450, 80, 60)

# Group outlines
add_node(root3, "g_c", "Replica Set Config", "swimlane;horizontal=0;whiteSpace=wrap;html=1;", 640, 80, 320, 100)
add_node(root3, "g_s1", "Replica Set Shard 1", "swimlane;horizontal=0;whiteSpace=wrap;html=1;", 640, 280, 320, 100)
add_node(root3, "g_s2", "Replica Set Shard 2", "swimlane;horizontal=0;whiteSpace=wrap;html=1;", 640, 430, 320, 100)


add_edge(root3, create_id(), n_api, n_mongos)
add_edge(root3, create_id(), n_api, "redis")
add_edge(root3, create_id(), n_mongos, "c1")
add_edge(root3, create_id(), n_mongos, "s11")
add_edge(root3, create_id(), n_mongos, "s21")
mxfile.append(diagram3)

tree = ET.ElementTree(mxfile)
ET.indent(tree, space="  ")
tree.write("final_task1.drawio", encoding="utf-8", xml_declaration=False)
print("done")
