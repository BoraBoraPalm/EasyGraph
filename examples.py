from directed_graph import Graph

g = Graph()


text = """Step: Create own AI ########################################################################

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



text = """Step: Connect AI to internet ###############################################################

Description: For training AI with more data!

    [X] Fetch data from typical search engines
    [ ] Prepare fetched data for AI
"""
##################################
# Place for code to connect cool #
# AI h internet                  #
##################################
g.add_node(name="Own AI internet", text=text, cluster="Own AI", title_colour="yellow")



text = """Step: AI plan ##############################################################################

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



text = "AI finds perfect plan but makes another person rich. #########################################"
##################################
# Place for whatever code        #
#                                #
##################################
g.add_node(name="Own AI Fail", text=text, cluster="Own AI")



text = """Step: Use public AI ########################################################################

Description: Use public AI instead of own AI, since own AI betrayed me from behind.

    [X] Ask AI how to build a boat.

Note: This might cost some money per month.
"""
##################################
# Place for secret AI plan       #
#                                #
##################################
g.add_node(name="Ask public AI", text=text, cluster="Deep Dream", title_colour="green", connect_from=None)



text = """Step: Build a boat #########################################################################

Description: To build a simple boat for the sea.

    [X] Because of less money use one of Thor Heyerdahl's rafts. Maybe Kon-Tiki.
    [X] Use Humboldt Current to reach Polynesia.

Note: Plan to bring plenty of supplies and fishing rods.
"""
##################################
# Place for secret AI plan       #
#                                #
##################################
g.add_cluster(name="Polynesia adventure", supercluster="Deep Dream")
g.add_node(name="Build and sail boat", text=text, cluster="Polynesia adventure", title_colour="green")



text = """Step: Find island ##########################################################################

Description: To find a nice island in Polynesia.

    [X] Drop anchor when on the beach.
    
Note: Beware of dangerous coral reefs!
"""
##################################
# Place for secret AI plan       #
#                                #
##################################
g.add_cluster(name="Nice island adventure", supercluster="Polynesia adventure")
g.add_node(name="Island adventure", text=text, cluster="Nice island adventure", title_colour="green")


text = "Plan to search hidden treasure ###############################################################"
g.add_node(name="Search hidden treasure", text=text, cluster="Nice island adventure")
##################################
# Area to write thoughts for     #
# code design.                   #
##################################


text = "Plan to be rich on lonely island! ############################################################"
g.add_node(name="Be rich", text=text, cluster="Nice island adventure")
##################################
# Area to write thoughts for     #
# code design.                   #
##################################


text = "Waking up ####################################################################################"
g.add_node(name="Wake up", text=text)
##################################
# Final code                     #
##################################



g.add_node(name="Wake up 2", text="Waking up", connect_from="Build and sail boat")
##################################
# Area for some code             #
#                                #
##################################

text = """Step: Doing life

Description: Live the life.
    
    [X] Work hard
    [X] Sleep soft
    [X] Earn money
"""
g.add_node(name="Life", text=text, title_colour="green")

text = """Step: Die young

    [ ] Apply to heaven.
    Note: Choose right planet
"""
g.add_node(name="Paradise", text=text, title_colour="red")

text = """Step: Locate

Description: One question arises: 'Where the hell am I?'

    [ ] Ask for current location
"""
g.add_cluster(name="Heaven or whatever", text="Living in a simulation, thus Simulation Theory applies.")
g.add_node(name="Locate", text=text, cluster="Heaven or whatever", title_colour="red")
##################################
# Area for some code             #
#                                #
##################################


g.add_node(name="Fail", cluster="Heaven or whatever")

g.add_node(name="Hacking plan", text="[ ] Make plan to hack heaven's master code.", cluster="Heaven or whatever")
g.add_node(name="Cheating", text="[ ] Add more lives to your own entity \n Note: Don't get caught!", cluster="Heaven or whatever")

g.create()
g.save(name="lalalalalala")



