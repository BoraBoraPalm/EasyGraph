import sys

from graphviz import Digraph
import textwrap
import time
import re


class Graph:
    """
    For creating a graph with nodes and clusters. Descriptions can be assigned to the nodes and clusters.
    """

    # To be able to store and access global an instance of this class.
    # Thus, possible to access and extend one Graph from each modul.
    globals: dict = {}

    def __init__(self, measure_time:bool=False, levels:int=10):
        """
        * If measure_time=True, also the time passed will be measured for each node.
        * The levels are defining the maximal depth of nesting for clusters. This defines
          the darkening of the deeper clusters.

        """
        self.clusters = {}
        self.nodes = {}
        self.dot = Digraph()
        self.node_previous_auto: str = None

        self.measure_time = measure_time
        if measure_time:
            self.time_start = time.time()
        self.time_node_previous = None

        if levels < 2:
            print(f"Error: Maximum level depth need to me minimum 2! But you have chosen {levels}")
        else:
            self.levels = levels

    def _format_delta(self, delta_seconds: float) -> str:
        """
        Format a time interval in seconds into the most appropriate unit:
        ns, μs, ms, s, min, or h.
        """
        # nanoseconds
        if delta_seconds < 1e-6:
            value = delta_seconds * 1e9
            unit = "ns"
        # microseconds
        elif delta_seconds < 1e-3:
            value = delta_seconds * 1e6
            unit = "μs"
        # milliseconds
        elif delta_seconds < 1.0:
            value = delta_seconds * 1e3
            unit = "ms"
        # seconds
        elif delta_seconds < 60.0:
            value = delta_seconds
            unit = "s"
        # minutes
        elif delta_seconds < 3600.0:
            value = delta_seconds / 60.0
            unit = "min"
        # hours (and beyond)
        else:
            value = delta_seconds / 3600.0
            unit = "h"

        # Format with up to three significant digits
        fmt = f"{value:.3g} {unit}"
        return fmt


    def _collapse_inside_markers(self, text: str, marker: str = '´') -> str:
        """
        For being able to write comment-like strings and also break the line for a nicer
        string formation in the code file. Also, then intends can be added and will be removed.
        This prepares the comment-string for the node text with no intends and line breaks
        inside ` ` and also removes the ` `.

        For each pair of marker characters in `text`:
            * Capture everything between them (incl. real newlines)
            * Strip spaces on each line and drop blanks
            * Collapse into a single line
            * Remove both markers

        :param text: The input string
        :return: String where extra whitespaces and linebreaks inside ´ ´ parts is removed.
        """
        esc = re.escape(marker)
        # \s* around the capture lets us trim stray spaces immediately inside the markers
        pattern = re.compile(f'{esc}\\s*([\\s\\S]*?)\\s*{esc}')

        def _repl(m):
            block = m.group(1)
            lines = block.splitlines()
            # strip each line and drop empty ones
            pieces = [ln.strip() for ln in lines if ln.strip()]
            return " ".join(pieces)

        return pattern.sub(_repl, text)


    def _replace_with_circles(self, text: str) -> str:
        """
        This method recognises patterns like ' (letter or number) ' and replaces
        it with a corresponding symbol. Preparation for node text.

        Thus, replaces occurrences of "(...)" in the given text with:
            * ①–⑳ for (1)–(20)
            * Ⓐ–Ⓩ for (A)–(Z)
            * ⓐ–ⓩ for (a)–(z)
        For (XX) → only the last character 'X' is used → ⒳
        For numbers greater than 20 (e.g. (21)) → remains '(21)' unchanged.

        :param text: The input string
        :return: String with circles added
        """
        # Prepare mappings for circled characters
        circled_numbers = {str(i): chr(0x2460 + i - 1) for i in range(1, 21)}
        circled_upper = {chr(ord('A') + i): chr(0x24B6 + i) for i in range(26)}
        circled_lower = {chr(ord('a') + i): chr(0x24D0 + i) for i in range(26)}

        def _repl(m: re.Match) -> str:
            inner = m.group('inner')
            # Only digits?
            if inner.isdigit():
                return circled_numbers.get(inner, m.group(0))
            # Only a single letter
            if inner.isalpha() and len(inner) == 1:
                ch = inner  # exactly one char now
                if ch.isupper():
                    return circled_upper.get(ch, m.group(0))
                else:
                    return circled_lower.get(ch, m.group(0))
            # Everything else (including "XX", "a1", etc.): leave unchanged
            return m.group(0)

        # Substitute and return the modified text
        return re.sub(r'\((?P<inner>[^)]+)\)', _repl, text)


    def add_global(self, name:str):
        """
        To make object global available and accessible via a unique key.

        :param name: The key under which the current Graph object can be accessed!
        :return: Nothing
        """

        Graph.globals[name] = self

    def add_cluster(self, name:str=None, text:str="", supercluster:str=None):
        """
        For defining and adding a new cluster to the graph. Nesting can be carried out by defining a supercluster.

        :param name: Name of the cluster
        :param text: An additional description of the cluster. Appearing in the cluster.
        :param supercluster: For inserting this cluster into a super cluster, thus for nesting clusters.
        :return: Nothing
        """

        if name in self.clusters:
            print(f"(!) Cluster already exists: {name}")
        else:
            self.clusters[name] = {"text": text, "supercluster": supercluster}


    def add_node(self,
                 name:str, *,
                 connect_from:str|list[str]|None="auto",
                 text:str|None=None,
                 cluster:str|None=None,
                 title_colour:str="yellow",
                 width:float=1):
        """
        For defining and adding a new node to the graph.

        * With 'connect from' a connection to the previous node can be carried out manually. But using the default value 'auto' this node automatically connects to the previous created and thus called node. \n

        * With 'text' A) a simple text describing the node can be inserted. Another option is to use a specific from b):
        For example for the specific form of 'text':
            ''' Step: This is step 1, describe it as desired

                Description: This step is just a dummy step. Her you can insert any text.

                [ ] This defines a not finished task
                [X] This defines a completed task
                Note: This defines something which needs attention!
            '''

        * Further, the following title background colours are available: 'green', 'yellow', 'red'. This should visually mark if a step is completed, in progress, or has an issue.

        :param name: The name of the node as string
        :param connect_from: If not specified, then automatically connected to previous node. Otherwise, previous node of this can be defined by name.
        :param text: The text describing the node. Simple text or formatted text is possible. See description of this method.
        :param cluster: If this node should be assigned to a cluster than define name of the cluster. The cluster already need to be exists.
        :param title_colour: Possible 'green' for a completed node, 'yellow' for a node in progress, and 'red' for a faulty node.
        :return:
        """


        # Prevent duplicating nodes with same name
        if name in self.nodes:
            print(f"(!) Node already exists: {name}")
        # If node not already exists
        else:
            # Not creating node if desired cluster does not exist
            if (cluster is not None) and (cluster not in self.clusters):
                print(f"Error in creating node '{name}' since cluster '{cluster}' does not exists!")
            # If desired cluster exists for the node
            else:
                # If text for the node is desired, then format it for a 'prettier' appearance in the node
                if text is not None:
                    # 1) Remove more than three ###, ===, --- in string.
                    pattern = re.compile(r'[#=-]{4,}')
                    text = pattern.sub('', text)
                    # 2) For the text inside """´This is a Description: The text starts here,
                    #                           (  some whitespaces  ) and continues here´ """
                    # The leading --^ whitespaces will be removed in the node text and and
                    # also the \n generated by the triple quotes """ """ here.
                    text = self._collapse_inside_markers(text=text)
                    # 3) Replace for example (X) -> Ⓧ, (1) -> ①. For numbers possible up to 20
                    #    Note (XX) -> yields only (X) for example
                    text = self._replace_with_circles(text=text)

                    # 4) Format the text for the node
                    text = self._format_text(self._find_lines(text), title_colour=title_colour, text_width=50*width)

                # a) Applied automatic chaining, thus connecting to previous node if desired
                if connect_from == "auto":
                    previous_node = self.node_previous_auto  # will be None the very first node
                    self.node_previous_auto = name           # to remember this node for next time
                # b) If no connection to previous is applied
                elif connect_from is None:
                    self.node_previous_auto = name
                    previous_node = None

                # c) Applies manual chaining, thus previous node is defined by user
                else:
                    # Check if previous node(s) existing
                    # -> Case for list of strings. Remove not existing nodes.
                    if isinstance(connect_from, list):
                        missing_list = list(set(connect_from) - self.nodes.keys())
                        if missing_list:
                            print(f"Error: The following previous nodes are not existing: {missing_list}")
                            connect_from = [c for c in connect_from if c in self.nodes.keys()]
                    # -> Case for only one string. Set to None if not existing.
                    elif isinstance(connect_from, str):
                        if connect_from not in self.nodes.keys():
                            print(f"Error: The following previous node does not exist: {connect_from}")
                            connect_from = None

                    previous_node = connect_from
                    self.node_previous_auto = name

                # d) Measure time if defined at beginning
                if self.measure_time:
                    delta_seconds = time.time() - self.time_start
                    delta_time_absolute = self._format_delta(delta_seconds=delta_seconds)

                    if self.time_node_previous is None:
                        delta_seconds = time.time() - self.time_start
                        self.time_node_previous = time.time()
                    else:
                        delta_seconds = time.time() - self.time_node_previous
                        self.time_node_previous = time.time()

                    delta_time_relative = self._format_delta(delta_seconds=delta_seconds)


                else:
                    delta_time_absolute, delta_time_relative = None, None

                # Finally, store the information of this node in the dict
                self.nodes[name] = {"connect_from": previous_node,
                                    "cluster": cluster,
                                    "text": text,
                                    "time_absolute": delta_time_absolute,
                                    "time_relative": delta_time_relative,
                                    "width": width}



    def create(self):
        """
        For using the created dictionary to create a graphviz Digraph object.

        :return: Nothing
        """

        ### section for inner methods of create ### START
        def depth(name):
            """
            For obtaining the level of the cluster in the dictionary.

            :param name: the name of the cluster
            :return: the depth (thus the level) of the cluster
            """

            d = 0
            # While supercluster exists get name of it and go one step deeper (thus deeper level)
            while self.clusters[name]["supercluster"]:
                name = self.clusters[name]["supercluster"]
                d += 1

            return d

        def lavender_darkness(level: int, levels: int) -> tuple[float, str]:
            """
            Return a hex colour of 'lavender' of a different darkness level based on the level and total levels.

            level=1 -> pure lavender, and level=levels -> black.

            :param level: the current level
            :param levels: the total levels
            :return: a hex as string representing lavender of a certain darkness level
            """

            # The base lavender RGB
            base_r, base_g, base_b = 0xE6, 0xE6, 0xFA

            # For having minimum 2 levels!
            if levels < 2:
                raise ValueError("levels must be >= 2")

            # Clamp level into [1, levels]
            level = max(1, min(level, levels))

            # For compute how far toward black we are, from 0.0 (level=1) to 1.0 (level=levels)
            frac = (level - 1) / (levels - 1)

            # For interpolating each channel toward 0 (black)
            r = int(base_r * (1 - frac))
            g = int(base_g * (1 - frac))
            b = int(base_b * (1 - frac))

            ratio = frac

            return ratio, f"#{r:02X}{g:02X}{b:02X}"

        ### section for inner methods of create ### END


        # 1) For creating raw cluster objects
        for name, val in self.clusters.items():
            text = textwrap.fill(val["text"], 50)

            # build an internal graphviz ID that satisfies the rule
            cid = f"cluster_{name.replace(' ', '_')}" # because cluster name need to start with 'cluster'
            g = Digraph(name=cid)  # ← use cid, not the label itself

            g.attr(label=f"{name}\\n{text}",
                   style='rounded,dashed,filled',
                   color='grey',
                   fontcolor='grey',
                   fillcolor='white',
                   fontname='DejaVu Sans')
            val["obj"] = g

        # 2) To assign the nodes to their clusters
        for n, val in self.nodes.items():
            if val["cluster"]:
                c = self.clusters[val["cluster"]]["obj"]
                c.node(n,
                       label=val["text"],
                       shape='rect',
                       style='rounded,filled',
                       fillcolor='azure',
                       penwidth='2',
                       color='black',
                       fontname="DejaVu Sans")

        # 3) To build the nesting from the bottom up
        for name in sorted(self.clusters, key=depth, reverse=True):
            sup = self.clusters[name]["supercluster"]
            ratio, level_colour = lavender_darkness(level=depth(name) + 1, levels=self.levels)

            # Switch from gray text colout to white to be visible in deeper nested cluster
            font_colour = "#EEEEEE" if ratio >= 0.2 else "grey"

            # Assign the fill colour and font colour of the respective level
            self.clusters[name]["obj"].attr(fillcolor=level_colour, fontcolor=font_colour)

            # If supercluster exists of a cluster then nest it
            if sup:
                self.clusters[sup]["obj"].subgraph(self.clusters[name]["obj"])


        # 4) For dropping the top–level clusters into the root digraph
        for name, val in self.clusters.items():
            if val["supercluster"] is None:
                self.dot.subgraph(val["obj"])

        # 5) Treat nodes that are not in a cluster differently
        for n, val in self.nodes.items():
            if val["cluster"] is None:
                self.dot.node(n, label=val["text"],
                              shape='rect',
                              style='rounded,filled',
                              fillcolor='azure', # 'gray93'
                              penwidth='2',
                              fontname="DejaVu Sans")

        # 6) Finally, add the edges between the nodes to generate a directed graph!
        for n, val in self.nodes.items():
            # a) If multiple previous nodes are existing, thus list of strings
            if isinstance(val["connect_from"], list):
                for edge in val["connect_from"]:
                    if val["time_absolute"] is not None and val["time_relative"] is not None:
                        self.dot.edge(edge, n, label=f"Δt={val['time_relative']}\n       ({val['time_absolute']})", fontname='DejaVu Sans', fontsize='10')
                    else:
                        self.dot.edge(edge, n)
            # b) If only string is available, thus on previous node
            elif val["connect_from"]:
                if val["time_absolute"] is not None and val["time_relative"] is not None:
                    self.dot.edge(val["connect_from"], n, label=f"Δt={val['time_relative']}\n       ({val['time_absolute']})", fontname='DejaVu Sans', fontsize='10')
                else:
                    self.dot.edge(val["connect_from"], n)



    def _format_text(self, text:str, title_colour:str, text_width:int=50) -> str:
        """
        For HTML formating different string parts differently. Thuy, certain text blocks are extracted from the input string and are formatted accordingly:

        *) Step block: centered, bold, background colour ('green', 'yellow', 'red'), text break after 50 letters, blank line after \n
        *) Description block: left aligned, blank line after, text break after 50 letters \n
        *) [X] block: yields symbol: ☑. Left aligned, text break after 48 letters, indentation adjusted for enumeration \n
        *) [ ] block: yields symbol: ☐. Same as previous block
        *) Note block: yields symbol: ⚠. Same as previous block

        :param text: The input test that should be formatted. Need to follow a certain formation. Use \""" Some text \""" and keywords 'Step:', 'Description', '[X]', '[ ]', 'Note', followed by a desired text.
        :param title_colour: At the moment only 'green', 'yellow', 'red' supported.
        :return: HTML formatted string
        """

        BULLETS = ("☐", "☑", "⚠")  # bullet-like symbols
        GREEN_BG = '#a1ddb2'
        YELLOW_BG = '#f8ec99'
        RED_BG = '#ff8080'

        # Choose the respective colour:
        if title_colour == "green":
            STEP_BG = GREEN_BG
        elif title_colour == "yellow":
            STEP_BG = YELLOW_BG
        elif title_colour == "red":
            STEP_BG = RED_BG
        else:
            print(f"Desired colour {title_colour} not yet supported for the title")

        def subst(s) -> str:
            """
            For replacing some parts of the string with symbols.

            :param s: The string
            :return: String containing symbols.
            """

            return (
                s.replace('&', '&amp;')  # to be able to use & in HTML formation as text (otherwise master escape)
                .replace('<', '&lt;')    # to be able to use < in HTML formation as text
                .replace('>', '&gt;')    # to be able to use > in HTML formation as text
                .replace("[ ]", "☐")
                .replace("[X]", "☑")     # for not being case-sensitive
                .replace("[x]", "☑")     #
                .replace("Note:", "⚠")
            )

        BLANK_ROW = '<TR><TD ALIGN="LEFT">&nbsp;</TD></TR>'

        rows = []

        for raw in text:
            raw = raw.strip()
            if not raw:
                continue

            # 1) FORMATION FOR: STEP / TITLE ==========================================
            if raw.startswith("Step:"):
                for part in textwrap.wrap(subst(raw), text_width, break_long_words=True):
                    rows.append(
                        f'<TR><TD BGCOLOR="{STEP_BG}" ALIGN="CENTER">'
                        f'<B>{part}</B></TD></TR>'
                    )
                rows.append(BLANK_ROW)  # blank after Step
                continue

            # FORMATION FOR: DESCRIPTION ==============================================
            if raw.startswith("Description:"):
                for part in textwrap.wrap(subst(raw), text_width, break_long_words=True):
                    rows.append(
                        f'<TR><TD ALIGN="LEFT"><I>{part}</I></TD></TR>'
                    )
                rows.append(BLANK_ROW)  # blank after Description
                continue

            # FORMATION FOR: BULLET / WARNING =========================================
            line = subst(raw)
            if line and line[0] in BULLETS:
                bullet, rest = line[0], line[1:].lstrip()
                # wrap at 48 chars, but only break on spaces
                wrapped = textwrap.wrap(rest, text_width-2, break_long_words=True)

                # First line: bullet + single space + first chunk
                rows.append(
                    f'<TR><TD ALIGN="LEFT">{bullet}&nbsp;{wrapped[0]}</TD></TR>'
                )

                # The '&#8203;&nbsp;&nbsp;&nbsp;&nbsp;' is for adding some whitespaces
                for part in wrapped[1:]:
                    rows.append(
                        f'<TR><TD ALIGN="LEFT">&#8203;&nbsp;&nbsp;&nbsp;&nbsp;{part}</TD></TR>'
                    )
                continue

            # FORMATION FOR: PLAIN TEXT ===============================================
            for part in textwrap.wrap(line, text_width, break_long_words=True):
                rows.append(f'<TR><TD ALIGN="LEFT">{part}</TD></TR>')

        html = (
                '<TABLE BORDER="0" CELLBORDER="0" CELLPADDING="0">'
                + "".join(rows)
                + "</TABLE>"
        )
        return f"<{html}>"


    def _find_lines(self, text) -> list[str]:
        """
        For finding the individual lines of the string and extract it.

        :param text: whole input string
        :return: Returns list of strings.
        """
        text = textwrap.dedent(text)    # removes the common left margin
        return [ln.lstrip()             # keep keywords flush-left
                for ln in text.splitlines()
                if ln.strip()]          # drop blank lines


    def save(self, name, format:str='svg'):
        """
        For saving the graph which is created as image.

        :param name: name of the file
        :return: Nothing
        """
        self.dot.render(name, format=format, cleanup=True)

