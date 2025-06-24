from ..directed_graph import Graph
from .example_2b_global import some_function_2b
from .example_2c_global import some_function_2c

import time


if __name__ == "__main__":
    g = Graph(measure_time=True)
    g.add_global(name="global test")

    g.add_cluster(name="Overview", text="The nodes are in different module (files) and the previous "
                                        "node is just defined by the calling order by default. "
                                        "However, it is also possible to define a previous node "
                                        "explicitly!")
    g.add_cluster(name="2a module", supercluster="Overview")
    g.add_node("Node 1", text="Node 1", cluster="2a module")

    time.sleep(1.5)
    some_function_2b()
    time.sleep(0.3)
    some_function_2c()

    g.add_node(name="Completed", text="The final step is again in the main file for example.", cluster="2a module")

    g.create()
    g.save("EasyGraph/examples/global_test")


