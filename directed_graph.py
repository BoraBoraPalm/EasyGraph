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

    def __init__(self, measure_time:bool=False):
        self.clusters = {}
        self.nodes = {}
        self.dot = Digraph()
        self.node_previous_auto: str = None

        self.measure_time = measure_time
        if measure_time:
            self.time_start = time.time()
        self.time_node_previous = None

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
                    # 2) Format the text for the node
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
            ratio, level_colour = lavender_darkness(level=depth(name) + 1, levels=10)

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



    def _format_text(self, text:str, title_colour:str, text_width:float=50) -> str:
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
                .replace('<', '&lt;') # to be able to use < in HTML formation as text
                .replace('>', '&gt;') # to be able to use > in HTML formation as text
                .replace("[ ]", "☐")
                .replace("[X]", "☑") # for not being case-sensitive
                .replace("[x]", "☑") #
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


    def save(self, name, format='svg'):
        """
        For saving the graph which is created as image.

        :param name: name of the file
        :return: Nothing
        """
        self.dot.render(name, format=format, cleanup=True)


if __name__ == "__main__":

# TEST 1 (START)
    g = Graph()
    text = """Step: Acquire signals
    Description: Collect raw patient-monitoring data from devices.
        [X] ECG leads attached
        [X] Pulse oximeter streaming
        [X] Device clocks synced
    Note: Keep sampling rates uniform (e.g., 500 Hz ECG, 100 Hz SpO₂).
    Note: Record device IDs and firmware.
    """
    g.add_node(name="Acquire signals", text=text, title_colour="green")

    text = "This part cleans signals (band-pass, 50 Hz removal, short SpO₂ interpolation), extracts and normalizes HRV from R-peaks, then trains a decision-tree with 5-fold cross-validation."
    g.add_cluster(name="Signal Preprocessing Cluster", text=text, supercluster=None)

    text = """Step: Clean signals
    Description: Remove noise and fix any missing samples.
        [ ] Apply band-pass filter
        [X] Remove mains interference (50 Hz)
        [ ] Fill short gaps in SpO₂
    Note: For gaps <200 ms, use spline interpolation.
    Note: Check that filtering doesn’t distort ECG peaks.
    """
    g.add_node(name="Clean signals", text=text, title_colour="yellow", cluster="Signal Preprocessing Cluster")


    text = """Step: Get features and train
    Description: Extract key metrics and build a simple model.
        [ ] Detect R-peaks in ECG
        [X] Calculate heart-rate variability
        [ ] Try a basic classifier, first use a decision tree.
    Note: Normalize each patient’s HRV results.
    Note: Use 5-fold cross-validation.
    """
    g.add_node(name="Get features and train", text=text, title_colour="yellow", cluster="Signal Preprocessing Cluster")


    text = """Step: Test and integrate
    Description: Check performance and prepare for deployment.
        [ ] Plot ROC on test data
        [ ] Set decision thresholds
        [ ] Draft deployment guide
    Note: Aim for ≥95 % sensitivity and ≥90 % specificity.
    Note: Package code for real-time C++ use.
    """
    g.add_node(name="Test and integrate", text=text, title_colour="red")


    g.create()
    g.save("simple_auto_test")
# TEST 1 (END)

# TEST 2 (START)

    text = """Step: Preparing the data

    Description: Right formation of the data and also remove NaN data.

        [ ] Real data is used
        [X] Placeholder data
        [X] Something is missing here
        Note: Only placeholder values for T2. Using at the moment T2* instead of T2 (!) Need also for each metabolite map?
        Note: Finally need to combine T2 and T2*
    """

    text2 = """Step: Some dummy step

    Description: To do something which is really cool, but nobody anderstands how cool this is. Really, beliefe me!

        [ ] Real data / computation is used
        [X] Placeholder data / computation is used
        [X] Something is missing here
    """

    text3 = """Step: Haha

    Description: This is very funny. It is so funny that even my dog laughs. For sure here are some spelling issues. But still, look, my dog laughs so hard!

    """



    g = Graph()
    g.add_cluster(name="cluster 1",
                  text="Das ist Cluster 1, und dieses ist zuständig für ganz viele Dinge. Dinge, von denen wir nichts wissen wollen!")
    g.add_cluster(name="cluster 2",
                  text="Das ist Cluster 1, und dieses ist zuständig für ganz viele Dinge. Dinge, von denen wir nichts wissen wollen!")
    g.add_cluster(name="cluster 2", text="Das ist ein weiteres lustiges Cluster. Lalalalala!", supercluster="cluster 1")
    g.add_cluster(name="cluster 3", text="Lalalalala!", supercluster="cluster 2")
    g.add_cluster(name="cluster 4", text="Lalalalala!", supercluster="cluster 3")
    g.add_cluster(name="cluster 5", text="Lalalalala!", supercluster="cluster 1")
    g.add_cluster(name="cluster 6", text="Lalalalala!", supercluster="cluster 4")
    g.add_cluster(name="cluster 7", text="Lalalalala!", supercluster="cluster 6")

    g.add_node(name="node 1", text=text, cluster="cluster 1")
    g.add_node(name="node 2", text="Bindeglied, das 3te Rad!", connect_from="node 1", cluster="cluster 2")
    g.add_node(name="node 3", text=text2, connect_from="node 2", cluster="cluster 1")
    g.add_node(name="node 4", text=text3, connect_from="node 2")
    g.add_node(name="node 5", text="Alles ist so lustig, ich weiß garnicht wo hin mit meiner Lustigkeit! ", connect_from="node 10")
    g.add_node(name="node 6", text=text2, connect_from="node 2", cluster="cluster 3")
    g.add_node(name="node 7", text=text2, connect_from="node 2", cluster="cluster 4")
    g.add_node(name="node 0", text="test", cluster="cluster 5")

    g.add_node(name="node 8", text="test", connect_from="node 0", cluster="cluster 6")
    g.add_node(name="node 9", text="test", connect_from="node 8", cluster="cluster 6")
    g.add_node(name="node 10", text="test", connect_from="node 9", cluster="cluster 7")

    #####g.add_node(name="node 1", text="lala 1", cluster="cluster 1")
    #####g.add_node(name="node 2", text="lala 2")
    #####g.add_node(name="node 3", text="lala 3", cluster="cluster 1")
    #####g.add_node(name="node 4", text="lala 4", cluster="cluster X")
    #####
    #####g.add_node(name="node 5", text="lala 5", cluster="cluster 2")

    g.create()
    g.save("test")

# TEST 2 (END)

# TEST 3 (START)

    g = Graph()

    # Clusters represent major pipeline stages
    g.add_cluster(name="Acquisition", text="Raw multi-echo MRI data collection (GRE, SE, DWI)")
    g.add_cluster(name="Preprocessing", text="Corrections and artifact removal", supercluster="Acquisition")
    g.add_cluster(name="Quantitative Mapping", text="Compute T1, T2*, ADC maps", supercluster="Preprocessing")
    g.add_cluster(name="Segmentation", text="Tissue and lesion delineation", supercluster="Quantitative Mapping")
    g.add_cluster(name="FeatureExtraction", text="Extract volumes and shape metrics", supercluster="Segmentation")
    g.add_cluster(name="Classification", text="Machine-learning disease prediction", supercluster="FeatureExtraction")
    g.add_cluster(name="Visualization", text="3D renderings and reports", supercluster="Classification")

    # Nodes capture detailed tasks and flags
    text1 = "Step: Data Acquisition\n" \
            "Description: Collect multi-echo GRE, SE, and DWI sequences.\n" \
            "    [X] GRE sequence acquired\n" \
            "    [ ] DWI b-values defined\n" \
            "    [ ] Confirm coil sensitivity maps"

    text2 = "Step: Preprocessing\n" \
            "Description: Correct for motion, bias, and noise.\n" \
            "    [ ] Motion correction applied\n" \
            "    [X] N4 bias-field correction\n" \
            "    [X] Denoising via non-local means"

    text3 = "Step: T2* Mapping\n" \
            "Description: Fit exponential decay to multi-echo data.\n" \
            "    [X] ROI mask defined\n" \
            "    [X] SNR thresholding applied\n" \
            "    [ ] Outlier echoes excluded"

    text4 = "Step: Segmentation\n" \
            "Description: Delineate gray matter, white matter, lesions.\n" \
            "    [ ] U-net model loaded\n" \
            "    [X] Training placeholders used\n" \
            "    [ ] Post-processing cleanup"

    text5 = "Step: Classification\n" \
            "Description: Predict pathology from extracted features.\n" \
            "    [ ] Features normalized per subject\n" \
            "    [X] Random forest classifier\n" \
            "    [ ] 10-fold cross-validation"

    # Add nodes and link workflow edges
    g.add_node(name="node_acq", text=text1, cluster="Acquisition")
    g.add_node(name="node_pre", text=text2, connect_from="node_acq", cluster="Preprocessing")
    g.add_node(name="node_map", text=text3, connect_from="node_pre", cluster="Quantitative Mapping")
    g.add_node(name="node_seg", text=text4, connect_from="node_map", cluster="Segmentation")
    g.add_node(name="node_feat", text="Step: Feature Extraction\nDescription: Compute volumes, shapes and textures.", connect_from="node_seg", cluster="FeatureExtraction")
    g.add_node(name="node_cls", text=text5, connect_from="node_feat", cluster="Classification")
    g.add_node(name="node_vis", text="Step: Visualization\nDescription: Generate 3D renders and summary report.", connect_from="node_cls", cluster="Visualization")

    # Finalize and save the graph
    g.create()
    g.save("mri_pipeline_workflow_test")

# TEST 3 (END)

# TEST 4 (START)

    g = Graph()

    # === Requirements & Planning ===
    g.add_cluster(
        name="Requirements & Planning",
        text="Define scope, user stories, and technical specifications"
    )
    g.add_node(
        name="Gather User Stories",
        text="""Step: User Stories
        Description: Interview research team & clinicians
            [X] Initial interviews done
            [X] Consolidate feedback
            [X] Prioritize features
        Note: All user requirements captured.""",
        cluster="Requirements & Planning",
        title_colour="green"
    )
    g.add_node(
        name="Draft Technical Spec",
        connect_from="Gather User Stories",
        text="""Step: Tech Spec
        Description: Document APIs, data models, simulation requirements
            [X] Define data schema
            [X] Specify performance targets
            [X] Outline error-handling
        Note: Spec ready for review.""",
        cluster="Requirements & Planning",
        title_colour="green"
    )

    # === Architecture Design ===
    g.add_cluster(
        name="Architecture Design",
        text="High-level modules and interactions"
    )
    g.add_node(
        name="Define Modules",
        connect_from="Draft Technical Spec",
        text="""Step: Modules
        Description: Decompose into Core, I/O, Utils, UI
            [X] Core engine defined
            [ ] I/O interfaces outlined
            [ ] Visualization draft
        Note: Pending I/O and UI details.""",
        cluster="Architecture Design",
        title_colour="yellow"
    )
    g.add_node(
        name="Select Technology Stack",
        text="""Step: Tech Stack
        Description: Choose languages, frameworks, tools
            [ ] Python core
            [ ] C++ extensions
            [ ] Qt or web UI
        Note: Finalize stack by next sprint.""",
        cluster="Architecture Design",
        title_colour="red"
    )

    # === Implementation ===
    g.add_cluster(
        name="Implementation",
        text="Write, integrate, and test code modules"
    )
    g.add_cluster(name="Core Module", supercluster="Implementation")
    g.add_node(
        name="Core Development",
        connect_from="Select Technology Stack",
        text="""Step: Core Dev
        Description: Implement simulation loop, data structures
            [ ] Loop skeleton
            [ ] State management
            [ ] Configuration parsing
        Note: Use abstract classes.""",
        cluster="Core Module",
        title_colour="red"
    )
    g.add_node(
        name="Core Testing",
        connect_from="Core Development",
        text="""Step: Core Tests
        Description: Unit tests for core components
            [X] Scheduler tests
            [X] Data integrity tests
            [X] Config load tests
        Note: Core test suite passing.""",
        cluster="Core Module",
        title_colour="green"
    )
    g.add_cluster(name="I/O Module", supercluster="Implementation")
    g.add_node(
        name="I/O Handlers",
        connect_from="Core Testing",
        text="""Step: I/O
            [ ] CSV reader
            [ ] HDF5 checkpoint
            [X] JSON config parser
        Note: Complete JSON support.""",
        cluster="I/O Module",
        title_colour="yellow"
    )
    g.add_node(
        name="I/O Validation",
        connect_from="I/O Handlers",
        text="""Task: Validate I/O
            [ ] Roundtrip tests
            [ ] Performance benchmark
        Note: Ensure throughput > 100 MB/s.""",
        cluster="I/O Module",
        title_colour="red"
    )

    # === Simulation Pipeline ===
    g.add_cluster(
        name="Simulation Pipeline",
        text="Configure and run batch simulations"
    )
    g.add_cluster(name="Model Config", supercluster="Simulation Pipeline")
    g.add_node(
        name="Parameter Setup",
        connect_from="I/O Validation",
        text="""Step: Param Setup
        Description: Define Monte Carlo parameters
            [ ] Temperature range
            [ ] Time-step stability
            [ ] Random seed control
        Note: Use Latin Hypercube sampling.""",
        cluster="Model Config",
        title_colour="red"
    )
    g.add_node(
        name="Parameter Verification",
        connect_from="Parameter Setup",
        text="""Task: Verify Params
            [ ] Value bounds
            [ ] Convergence checks
        Note: Validate parameter combinations.""",
        cluster="Model Config",
        title_colour="red"
    )
    g.add_cluster(name="Execution Engine", supercluster="Simulation Pipeline")
    g.add_node(
        name="Batch Execution",
        connect_from="Parameter Verification",
        text="""Step: Execute
        Description: Submit jobs to HPC cluster
            [X] SLURM scripts ready
            [X] Job arrays configured
            [ ] Fault-tolerance logic
        Note: Checkpoint every 100 steps.""",
        cluster="Execution Engine",
        title_colour="yellow"
    )
    g.add_node(
        name="Job Monitoring",
        connect_from="Batch Execution",
        text="""Task: Monitor
            [ ] Real-time logs
            [X] Alert on failure
        Note: Integrate with Slack API.""",
        cluster="Execution Engine",
        title_colour="yellow"
    )

    # === Post-Processing ===
    g.add_cluster(
        name="Post-Processing",
        text="Analyze results and generate reports"
    )
    g.add_node(
        name="Data Aggregation",
        connect_from="Job Monitoring",
        text="""Step: Aggregate
        Description: Merge output files
            [X] HDF5 merge
            [ ] CSV export
            [ ] Metadata logging
        Note: Automate directory discovery.""",
        cluster="Post-Processing",
        title_colour="yellow"
    )
    g.add_node(
        name="Result Visualization",
        connect_from="Data Aggregation",
        text="""Step: Visualize
            [ ] Time-series plots
            [ ] Heatmaps
            [X] Summary charts
        Note: Use matplotlib and Plotly.""",
        cluster="Post-Processing",
        title_colour="yellow"
    )

    # Build graph and save
    g.create()
    g.save("advanced_simulation_workflow_2")

# TEST 4 (END)

