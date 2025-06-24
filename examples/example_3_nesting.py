from ..directed_graph import Graph


if __name__ == "__main__":
    g = Graph()
    g.add_cluster(name="Cluster 1", text="By default 10 levels are possible. It gradually darkens until it is black.")
    g.add_cluster(name="Cluster 2", supercluster="Cluster 1")
    g.add_cluster(name="Cluster 3", supercluster="Cluster 2")
    g.add_cluster(name="Cluster 4", supercluster="Cluster 3")
    g.add_cluster(name="Cluster 5", supercluster="Cluster 4")
    g.add_cluster(name="Cluster 6", text="The Nodes can be easily \\n assigned to each cluster!", supercluster="Cluster 5")
    g.add_cluster(name="Cluster 7", supercluster="Cluster 6")
    g.add_cluster(name="Cluster 8", supercluster="Cluster 7")
    g.add_cluster(name="Cluster 9", supercluster="Cluster 8")
    g.add_cluster(name="Cluster 10", supercluster="Cluster 9")

    g.add_node(name="1st Node", cluster="Cluster 10")
    g.add_node(name="2nd Node", cluster="Cluster 1")
    g.add_node(name="3rd Node", cluster=None)
    g.add_node(name="4th Node", cluster="Cluster 6")


    g.create()
    g.save("EasyGraph/examples/nesting_test")
