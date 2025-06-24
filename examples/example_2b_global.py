from easygraph import Graph

def some_function_2b():
    Graph.globals["global test"].add_cluster("2b module", supercluster="Overview")
    Graph.globals["global test"].add_node(name="Node 2", cluster="2b module")