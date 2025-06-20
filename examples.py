from directed_graph import Graph

g = Graph()


text = """Step: Create own AI

Description: To create my own AI with a super cool framework.

    [X] Collect data
    [X] Prepare data
    [X] Code AI
    [X] Train / Test AI
    
Note: Keep AI secret.
"""
##################################
# Place for my cool AI Code      #
#                                #
##################################
g.add_cluster(name="Deep Dream")
g.add_cluster(name="Own AI", supercluster="Deep Dream")
g.add_node(name="Create AI", text=text, cluster="Own AI", title_colour="green")



text = """Step: Connect AI to internet

Description: For training AI with more data!

    [X] Fetch data from typical search engines
    [ ] Prepare fetched data for AI
"""
##################################
# Place for code to connect cool #
# AI h internet                  #
##################################
g.add_node(name="Own AI internet", text=text, cluster="Own AI", title_colour="yellow")



text = """Step: AI plan

Description: Let AI create a plan how to get rich and how to find the meaning of life.
    [ ] Add some magic to AI code
    [ ] Keep AI secret.
    
Note: This might blow up your mind.
"""
##################################
# Place for secret AI plan       #
#                                #
##################################
g.add_node(name="Secret AI Plan", text=text, cluster="Own AI", title_colour="red")



text = "AI finds perfect plan but makes another person rich."
##################################
# Place for whatever code        #
#                                #
##################################
g.add_node(name="Own AI Fail", text=text, cluster="Own AI")



text = """Step: Use public AI

Description: Use public AI instead of own AI, since own AI betrayed me from behind.

    [X] Ask AI how to build a boat.

Note: This might cost some money per month.
"""
##################################
# Place for secret AI plan       #
#                                #
##################################
g.add_node(name="Ask public AI", text=text, cluster="Deep Dream", title_colour="green", connect_from=None)



text = """Step: Build a boat

Description: To build a simple boat for the sea.

    [X] Because of less money use one of Thor Heyerdahl's rafts. Maybe Kon-Tiki.
    [X] Use Humboldt Current to reach Polynesia.

Note: Plan to bring plenty of supplies and fishing rods.
"""
##################################
# Place for secret AI plan       #
#                                #
##################################
g.add_node(name="Build and sail boat", text=text, cluster="Deep Dream", title_colour="green")


g.add_node(name="Test1", text="abc", cluster="Deep Dream", connect_from="Build and sail boat")
g.add_node(name="Test2", text="def", cluster="Deep Dream", connect_from="Build and sail boat")

g.create()
g.save(name="lalalalalala")


# TODO: connect to multiple previous nodes (!)

