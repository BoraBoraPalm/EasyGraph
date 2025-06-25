from easygraph import Graph

if __name__ == "__main__":
    g = Graph()

    text = """ ------------------------------------------------------------------
    Step: One lonely step
           
    Description: ´This description is too long, so I want to break the line here
                  in the comment-string and add the following line after the  
                  line break without a new line in the node. 
                  Additionally, the extra whitespaces should also not appear in 
                  the final node.´
                          
        [X] Creating this nice node!
        [X] Enjoying the wonderful day
        Note: Lala
    """
    g.add_node(name="Nice node", text=text, title_colour="green", width=1.04)

    text = """ -------------------------------------------------------------------
    ´Description: Therefore, use (1) two 'acute accents', (2) put text inside, and 
                  (3) enjoy a nice formatted comment-string, but also get a super 
                  cool node description in your graph!´
         
           ´Note: The new version (v. 0.2.0) also supports to create enumerations 
                  with ( 1 ), ( 2 ), ... ( 20 ). It is possible up to number 20. 
                  Just use as described but without spaces. Further, also letters 
                  are supported: (x), (y), (Y), (a), (b), (B), and so on...´ 
    """
    g.add_node(name="Another nice node", text=text, width=1.04)


    g.create()
    g.save("EasyGraph/examples/formatting_test")