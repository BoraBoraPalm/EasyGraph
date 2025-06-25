from easygraph import Graph
from types import SimpleNamespace

if __name__ == "__main__":

    # To create the main object. Multiple objects are possible. By default, it does
    # not count the time (measure_time = False).
    g = Graph(True)

    # A) One step is defined by a comment, and can be separated with more than three =,-, #
    #    in a row. It will be removed automatically inside the node.
    text = """Step: First Step ==============================================================
    
    Description: This is the description of the first step.
    
    [ ] An item to complete. Use brackets and a white space.
    [X] An completed item. Lower x or capital X can be used.
    Note: Use 'Note' If there is something special to consider. 
    """
    # B) To create the first node. The colour yellow could denote an uncompleted step.
    g.add_node(name="The first step", text=text, title_colour="yellow")

    # C) It is intended that here some code can be inserted, and the comment above describes
    # roughly what's done in this step, and also shows what is missing.
    # I would suggest to use this kind of node, with detailed description in the main module.
    dummy = SimpleNamespace()
    dummy.name = "There is a ghost in the shell"
    dummy.number = "42"
    print("")


    # Define another step by a comment. It is also possible to only use parts of the
    # step in terms of keywords: "Step", "Description", "[ ]", "[X]", "Note".
    text = """ ============================================================================
    Description: We only use the 'Description' and 'Note' keyword here. Simple text 
    without a keyword is also possible.
    
        Note: Additionally, using 60% of normal width of node.
    """
    # To add the second node.
    g.add_node("The second step", text=text, width=0.6)
    # Some code here which the node describes.
    dummy_2 = SimpleNamespace()
    dummy_2.name = "No idea which name would fit ;)"
    dummy_2.unit = "arbitrary"



    # Define the 3rd step without a comment. This might be useful for smalls steps or not
    # yet implemented smaller steps somewhere in the code, maybe in other modules.
    g.add_node(name="The third step =====================================================",
               text="This step can be anywhere! No concrete idea yet, or just "
                    "small step.",
               width=0.4)


    # To create and save the graph (by default as svg)
    g.create()
    g.save("old/examples/basic_test")














