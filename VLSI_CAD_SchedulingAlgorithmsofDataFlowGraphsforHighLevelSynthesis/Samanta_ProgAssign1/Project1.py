import networkx as nx
import numpy as np
from lpsolve55 import *
from pygraphviz import *
import re
import math
import time


def main():
    '''Main Method.
    
    Parameters
    ----------
    
    Returns
    -------
    
    '''
    # Remove Input nodes from processing. Add "Source" & "Sink" nodes with label as "nop"
    G = create_Source_Sink_Nodes()
    
    # Add delay information to the graph
    G = add_DelayAreaInfoToGraph(G)
    
    # Options for User Input
    print "-------------  ALGORITHMS  -------------"
    print "1:    MLRC_ILP"
    print "2:    MRLC_ILP"
    print "3:    MLRC_List"
    print "4:    MRLC_List"
    print "="*40
    option = int(raw_input("Enter Option: "))
    print "="*40
    
    if option == 1:
        MLRC_ILP(G)
    elif option == 2:
        MRLC_ILP(G)
    elif option == 3:
        MLRC_List(G)
    elif option == 4:
        MRLC_List(G)
    else:
        print "Sorry Invalid Option"
        exit(1)

def MLRC_ILP(G):
    '''Calculates the Minimum Latency under Resource Constraints
    
    Parameters
    ----------
    G: NetworkX Acyclic Di-graph
    
    Returns
    -------
    
    '''
    algorithm = "MLRC_ILP"
    # Step-1: Calculate the "Start Time" for each operation by ASAP
    (G, minLatency) = calc_ASAP(G)
    print "MLRC_ILP: Minimum Latency: %d" % minLatency
    
    # Step-2: Calculate the "Latest Time" for each operation by ALAP
    (G, exceptionStatus) = calc_ALAP(G, minLatency)                 # For MLRC, Input latency to ALAP is minimum latency calculated from ASAP

    # Step-3: Calculate Mobility of each operation
    G = calc_Mobility(G)
     
    # Step-4: Compute "Start Time" Constraints
    constraintOne = calc_constraints_StartTime(G, algorithm)
    file_Write('MLRC_ILP_Start_time_constraints.txt', constraintOne)
    
    # Step-5: Compute "Precedence" Constraints       
    constraintTwo = calc_constraints_Precedence(G, algorithm, constraintOne)
    file_Write('MLRC_ILP_Precedence_constraints.txt', constraintTwo)
     
    # Step-6: Compute "Resource" Constraints
    constraintThree = calc_constraints_Resource(G, algorithm, constraintOne)
    file_Write('MLRC_ILP_Resource_constraints.txt', constraintThree)
     
    # Step-7: Compute "Objective Function"
    objectiveFunction = create_Objective_Function(G, algorithm, constraintOne)
    file_Write('MLRC_ILP_Objective_Function.txt', objectiveFunction)
    
    start_time = time.time() 
    # Step-8: LP-Solve
    G = calc_LPSolve(G, algorithm, objectiveFunction, constraintOne, constraintTwo, constraintThree)
    
    print ("MLRC_ILP takes --- %s seconds --- to execute" % (time.time() - start_time))

def MRLC_ILP(G):
    '''Calculates the Minimum Resources under Latency Constraints
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph
    
    Returns
    -------
    
    '''
    algorithm = "MRLC_ILP"
    # Step-1: Calculate the "Start Time" for each operation by ASAP
    (G, minLatency) = calc_ASAP(G)
    print "MRLC_ILP: Minimum Latency: %d" % minLatency
    
    # Step-2: Calculate the "Latest Time" for each operation by ALAP
    inputLatency = int(raw_input("Enter Maximum Latency: "))
    print "="*40
    (G, exceptionStatus) = calc_ALAP(G, inputLatency)                   # For MRLC, Input latency to ALAP is User Input i.e. asks for Upper bound on Latency
    if exceptionStatus == 1:
        print "Solution not feasible: Maximum Latency %d is lower than Minimum Latency of %d" % (inputLatency, minLatency)
    else:
        start_time = time.time()
        # Step-3: Calculate Mobility of each operation
        
        G = calc_Mobility(G)
     
        # Step-4: Compute "Start Time" Constraints
        constraintOne = calc_constraints_StartTime(G, algorithm)
        file_Write('MRLC_ILP_Start_time_constraints.txt', constraintOne)
             
        # Step-5: Compute "Precedence" Constraints
        constraintTwo = calc_constraints_Precedence(G, algorithm, constraintOne)
        file_Write('MRLC_ILP_Precedence_constraints.txt', constraintTwo)
     
        # Step-6: Compute "Resource" Constraints
        constraintThree = calc_constraints_Resource(G, algorithm, constraintOne)
        file_Write('MRLC_ILP_Resource_constraints.txt', constraintThree)
     
        # Step-7: Compute "Objective Function"
        objectiveFunction = create_Objective_Function(G, algorithm, constraintOne)
        file_Write('MRLC_ILP_Objective_Function.txt', objectiveFunction)
     
        # Step-8: LP-Solve
        G = calc_LPSolve(G, algorithm, objectiveFunction, constraintOne, constraintTwo, constraintThree)
    print ("MRLC_ILP takes --- %s seconds --- to execute" % (time.time() - start_time))
        
def create_Source_Sink_Nodes():
    '''Removes the "inp" nodes from the graph and adds the Source and Sink nodes with label as "nop"
    
    Parameters
    ----------
    
    Returns
    -------
    G : Processed NetworkX Acyclic Di-graph
        Source node numbered "0" with label as "nop" is added to the graph for processing
        Sink node with label as "nop" is also added to the graph.
    '''
    # Step-1: Read the Input "dot" file
    print "="*40
    print "-------------    FILES     -------------"
    print "1:    hal.dot"
    print "2:    fir1.dot"
    print "3:    cosine1.dot"
    print "4:    cosine2.dot"
    print "5:    Any other .dot file"
    print "="*40
    fOption = int(raw_input("Enter the file option: "))
    print "="*40
    try:
        # Read Input File
        if fOption == 1:
            G = nx.DiGraph(nx.read_dot('hal.dot'))
        elif fOption == 2:
            G = nx.DiGraph(nx.read_dot('fir1.dot'))
        elif fOption == 3:
            G = nx.DiGraph(nx.read_dot('cosine1.dot'))
        elif fOption == 4:
            G = nx.DiGraph(nx.read_dot('cosine2.dot'))
        elif fOption == 5:
            fileInput = raw_input("Enter the dot file name: ")
            G = nx.DiGraph(nx.read_dot(fileInput))
            print "="*40
        else:
            print "Sorry... Invalid Option"
            exit(1)
    
        nodesWithoutPredecessors = list()
        nodesWithoutSuccessors = list()
        inpNodes = list()
        validNodes = list()
        successorsOfInpNodes = list()
        
        # Step-2: Identify the "Input" nodes and its successors from the graph
        for node in nx.topological_sort(G):
            if not G.predecessors(node) and G.node[node]["label"] == "inp":     # Input nodes have no valid 'predecessors'
                inpNodes.append(node)                        
                successorsOfInpNodes.append(G.successors(node))                 # Successors of Input nodes are identified
            else:
                validNodes.append(node)
        inpEdges = G.edges(inpNodes)                                            # Identify the edges from the Input nodes
          
        # Step-3: Generate the node number for the Sink node
        sink = str(max(int(n) for n in G.nodes_iter()) + 1)
        
        # Step-4: Remove the Nodes and Edges associated with the Input nodes
        G.remove_edges_from(inpEdges)
        G.remove_nodes_from(inpNodes)
        
        # Write the modified graph into a "dot" file
#         nx.write_dot(G, 'InputDotFile_with_Inp_removed.dot')
        
        # Step-5: Identify the nodes with No Predecessors and Successors
        for node in nx.topological_sort(G):
            if not G.predecessors(node):
                nodesWithoutPredecessors.append(node)
            
            if not G.successors(node):
                nodesWithoutSuccessors.append(node)
        
        # Step-6: Add the Source node and Sink node to the graph with label as "nop"
        G.add_node("0", label = "nop")
        G.add_node(sink, label = "nop")
         
        # Step-7.1: Add the edges from Source node to the nodes with No Predecessors
        newEdgesSource = list()
        for n in range(0, len(nodesWithoutPredecessors)):
            t = "0", nodesWithoutPredecessors[n]
            newEdgesSource.append(t)
        G.add_edges_from(newEdgesSource)
        
        # Step-7.2: Add the edges from Sink node to the nodes with No Successors
        newEdgesSink = list()
        for n in range(0, len(nodesWithoutSuccessors)):
            t = nodesWithoutSuccessors[n], sink
            newEdgesSink.append(t)
        G.add_edges_from(newEdgesSink)
        
        # Write the processed graph into a "dot" file
#         nx.write_dot(G, 'InputDotFile_with_Source_Sink.dot')
        
        return G
                
    except Exception:
        print "Oops! There was an Error"
        exit(1)


def add_DelayAreaInfoToGraph(G):
    '''Read the delay and area information from the 'Resource Definition file' and add the delay & area information to the graph for each operation
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph with 'No delay information'
    
    Returns
    -------
    G : Processed NetworkX Acyclic Di-graph with 'Delay and Area information' added   
    '''
    # Step-1: Add the "delay" & "area" attribute to all the nodes of the graph
    G.add_nodes_from([n for n in G], delay = 0)
    G.add_nodes_from([n for n in G], area = 0)
    
    # Step-2: Read the input resource definition file and obtain a file handle for it
    fileHandle = open('rdf.txt', 'r')
    
    resType = list()
    resDelay = list()
    resInitiationInterval = list()
    resArea2 = list()
    
    # Step-3: Read each of the lines of the file
    for line in fileHandle:
        line = line.rstrip()
        rType = re.findall('^\w+\s+(\w+)\s+\d+\s+\d+\s+\d+\s+\d+', line)
        rDelay = re.findall('^\w+\s+\w+\s+(\d+)\s+\d+\s+\d+\s+\d+', line)
        rDII = re.findall('^\w+\s+\w+\s+\d+\s+(\d+)\s+\d+\s+\d+', line)
        rArea2 = re.findall('^\w+\s+\w+\s+\d+\s+\d+\s+\d+\s+(\d+)', line)
        if len(rType) > 0:
            resType.append(rType)
        if len(rDelay) > 0:
            resDelay.append(rDelay)
        if len(rDII) > 0:
            resInitiationInterval.append(rDII)
        if len(rArea2) > 0:
            resArea2.append(rArea2)
            
    resourceType = list()
    resourceDelay = list()
    resourceInitiationInterval = list()
    resourceArea2 = list()
    
    for i in range(len(resType)):
        for j in range(len(resType[i])):
            resourceType.append(resType[i][j])
            resourceDelay.append(int(resDelay[i][j]))
            resourceInitiationInterval.append(int(resInitiationInterval[i][j]))
            resourceArea2.append(int(resArea2[i][j]))
       
    # Step-4: Add Delay & Area information to the graph for each node
    for node in G.nodes():
        for index in range(0, len(resourceType)):
            if G.node[node]["label"] == resourceType[index]:
                G.node[node]["delay"] = resourceDelay[index]
                G.node[node]["area"] = resourceArea2[index]
    
    # Write the processed graph into a "dot" file with the delay information
#     nx.write_dot(G, 'InputDotFile_with_DelayArea.dot')
    
    return G

    
def file_Write(fileName, fileObject):
    '''Writes a file with the necessary information
    
    Parameters
    ----------
    fileName   : The name of the file
    fileObject : The content to be written
    
    Returns
    -------
        
    '''
    # Step-1: Open the file to write
    f = open(fileName, 'w')
    
    # Step-2: Write into file
    for i in fileObject:
        f.write(str(i) + "\n")
        
    # Step-3: Close the file
    f.close()

    
def calc_ASAP(G):
    '''Calculate the 'Start time' for each operation based on Unconstrained 'As Soon As Possible' (ASAP) Scheduling scheme
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph with 'delay information'
    
    Returns
    -------
    G          : Processed NetworkX Acyclic Di-graph with 'Start Time' added
    minLatency : Minimum Latency
    '''
    # Step-1: Add the "Start Time" (ts) attribute to all the nodes of the graph
    G.add_nodes_from([n for n in G], ts = 0)
    
    # Step-2: Calculate the Start Time for all nodes
    for n in nx.topological_sort(G):
        if not G.predecessors(n):
            G.node[n]["ts"] = 1         # Set the Start time for source node as 1 (Delay of source node is 0)
        else:
            # Logic: ts_i = maximum of (ts_j + d_j)
            G.node[str(n)]["ts"] = max( [G.node[i]["ts"] + int(G.node[i]["delay"]) for i in G.predecessors(n)] )
    
    # Write the ASAP result into a "dot" file        
    nx.write_dot(G, 'ASAP.dot')
    
    # Step-3: Minimum Latency = Start_time_of_Sink_node - Start_time_of_Source_node
    minLatency = G.node[str(max(int(n) for n in G.nodes_iter()))]["ts"] - 1
    
    return (G, minLatency)


def calc_ALAP(G, latency):
    '''Calculate the 'Latest Start time' for each operation based on Unconstrained 'As Late As Possible' (ASAP) Scheduling scheme
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph with 'delay information'
    
    Returns
    -------
    G               : Processed NetworkX Acyclic Di-graph with 'Latest Start Time' added
    exceptionStatus : Exception Status = 1 (error) indicates input latency is less than minimum possible latency
                                       = 0 (no error) indicates input latency greater than equal to minimum possible latency   
    '''
    exceptionStatus = 0
    
    # Step-1: Add the "Latest Start Time" (tl) attribute to all the nodes of the graph
    G.add_nodes_from([n for n in G], tl = 0)
    
    # Step-2: Calculate the Latest Start Time for all nodes
    for n in nx.topological_sort(G, reverse=True):
        if not G.successors(n):
            G.node[n]["tl"] = latency + 1               # Set the Latest Start Time of the sink node as latency + 1
        else:
            # Logic: tl_i = minimum of (tl_j + d_i)
            G.node[str(n)]["tl"] = min( [G.node[i]["tl"] - int(G.node[n]["delay"]) for i in G.successors(n)] )
    
    # With the given input latency, if the latest start time of source node is less than 0, then raise an exception
    if G.node["0"]["tl"] <= 0:      # deviated from book
        exceptionStatus = 1
        
    # Write the ALAP result into a "dot" file
    nx.write_dot(G, 'ALAP.dot') 
    
    return (G, exceptionStatus)


def calc_Mobility(G):
    '''Calculate the 'Mobility' for each operation
    
    Mobility = Latest_Start_Time - Start_Time i.e. (ALAP - ASAP)
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph with Start Time (ts) and Latest Start Time (tl)
    
    Returns
    -------
    G : NetworkX Acyclic Di-graph with 'Mobility' information added
    '''
    # Step-1: Add the "Mobility" (mobility) attribute to all the nodes of the graph
    G.add_nodes_from([n for n in G], mobility = 0)
    
    # Step-2: Calculate Mobility for each node
    G_List = [d for n,d in G.nodes_iter(data=True)]
#     print G_List
    for item in G_List:
        # Logic: Mobility of each node = Latest_Start_Time - Start_Time of each node i.e. (ALAP - ASAP)
        item["mobility"] = item["tl"] - item["ts"]
    
    # Write the Mobility result into a "dot" file
    nx.write_dot(G,'Mobility.dot')
    
    return G


def calc_Start_Time(G):
    '''Returns the calculated 'Start time' for each operation in a List
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph
    
    Returns
    -------
    ts_List : List containing the Start Time of the nodes
    '''
    ts_List = list()
    
    for node in G.nodes():
        ts_List.append(G.node[node]["ts"])
    
#     print "Nodes = " + str(G.nodes())
#     print "ts_List = " + str(ts_List)   
    return ts_List


def calc_Latest_Start_Time(G):
    '''Returns the calculated 'Latest Start time' for each operation in a List
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph
    
    Returns
    -------
    tl_List : List containing the Latest Start Time of the nodes
    '''
    tl_List = list()
    
    for node in G.nodes():
        tl_List.append(G.node[node]["tl"])
    
#     print "Nodes = " + str(G.nodes())
#     print "tl_List = " + str(tl_List)
    return tl_List


def calc_Mobility_Org(G):
    '''Returns the calculated 'Actual Mobility' i.e. Slack for each operation in a List
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph
    
    Returns
    -------
    mobilityOriginal_List : List containing the Actual Mobility i.e. Slack of the nodes
    '''
    mobilityOriginal_List = list()
    
    for node in G.nodes():
        mobilityOriginal_List.append(G.node[node]["mobility"])
    
#     print "Nodes = " + str(G.nodes())
#     print "mobilityOriginal_List = " + str(mobilityOriginal_List)
    return mobilityOriginal_List

    
def calc_Mobility_Mod(G):
    '''Returns the 'Modified Mobility' i.e. (Modified_Mobility = Original_Mobility + 1) in a List
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph
    
    Returns
    -------
    mobilityModified_List : List containing the Modified Mobility i.e. (Slack + 1) of the nodes
    '''
    mobilityModified_List = list()
    
    for node in G.nodes():
        mobilityModified_List.append(G.node[node]["mobility"] + 1)
    
#     print "Nodes = " + str(G.nodes())
#     print "mobilityModified_List = " + str(mobilityModified_List)        
    return mobilityModified_List


def calc_Mobility_Cumulated(mobilityModified_List):
    '''Returns the 'Cumulated Mobility' in a List
    
    nodes =              ['11', '10', '12', '1', '0', '3', '2', '5', '4', '7', '6', '9', '8']
    mobility_Original =  [4, 4, 0, 0, 0, 0, 0, 0, 0, 1, 1, 3, 3]
    mobilty_Modified =   [5, 5, 1, 1, 1, 1, 1, 1, 1, 2, 2, 4, 4]
    mobility_Cumulated = [5, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 25, 29]
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph
    
    Returns
    -------
    mobilityCumulated_List : List containing the Modified Mobility i.e. (Slack + 1) of the nodes
    '''
    mobilityCumulated_List = np.array(np.cumsum(mobilityModified_List)).tolist()
    
    return mobilityCumulated_List

        
def calc_constraints_StartTime(G, algo):
    '''Calculates the Start Time Constraints
    
    Parameters
    ----------
    G    : NetworkX Acyclic Di-graph
    algo : The algorithm can be of type "MLRC" or "MRLC"
    
    Returns
    -------
    rows : List of list containing the valid coefficients of the nodes
           Outer List -> Number of rows corresponds to the number of the nodes in the graph
           Inner List -> Number of columns corresponds to the total number of terms that come up in the Start Time Constraints Equation
    '''
    mobilityOriginal_List = calc_Mobility_Org(G)   
    mobilityModified_List = calc_Mobility_Mod(G)
    mobilityCumulated_List = calc_Mobility_Cumulated(mobilityModified_List)
    
    print "Nodes                  = " + str(G.nodes())
    print "Start_Time_List        = " + str(calc_Start_Time(G))
    print "Latest_Start_Time_List = " + str(calc_Latest_Start_Time(G))
    print "Mobility_Original      = " + str(mobilityOriginal_List)
    print "Mobility_Modified      = " + str(mobilityModified_List)
    print "Mobility_Cumulated     = " + str(mobilityCumulated_List)
    
    rows = list()
    
    # Step-1: Create the matrix (list within a list) with rows corresponding to individual nodes
    #         and columns corresponding to the node-mobility combination that is set as 1 in the Start time constraints equation
    #         For MRLC: there are few more columns added to the original that corresponds to the unique resource types
    for i in range(0, G.order()):
        columns = list()
        if algo == "MLRC_ILP": 
            noOfColumns = sum(mobilityModified_List)
        elif algo == "MRLC_ILP":
            (nodes_TotalOperation, uniqueResourceTypes) = identify_Resources(G)
            noOfColumns = sum(mobilityModified_List) + len(uniqueResourceTypes)
        
        # Step-2: Initially set all the elements to 0
        for j in range(0, noOfColumns):
            columns.append(0)        
        rows.append(columns)
    
    # Step-3: Set the particular coefficients as 1
    for i in range(0, G.order()):                           # Iterate through rows
        for j in range(0, mobilityModified_List[i]):        # Iterate through columns
            rows[i][mobilityCumulated_List[i] - j - 1] = 1

    return rows


def calc_LX_il(G, algo, X_il, node):
    '''Calculate L * X
    
    Parameters
    ----------
    G    : NetworkX Acyclic Di-graph
    algo : The algorithm can be of type "MLRC" or "MRLC"
    X_il : The start time constraints [ [...] ] List within a list
    node : Node number 
    
    Returns
    -------
    LX_il : L * X
    '''
    LX_il = list()
    ts_List = calc_Start_Time(G)
    mobilityModified_List = calc_Mobility_Mod(G)
    
    allNodes_List = G.nodes()
    index = allNodes_List.index(str(node))

    count = 0
    if algo == "MLRC_ILP":
        noOfColumns = sum(mobilityModified_List)
    elif algo == "MRLC_ILP":
        (nodes_TotalOperation, uniqueResourceTypes) = identify_Resources(G)
        noOfColumns = sum(mobilityModified_List) + len(uniqueResourceTypes)
    
    for i in range(0, noOfColumns):
        LX_il.append(0)
        if (X_il[index][i] == 1): 
            LX_il[i] = ts_List[index] + count
            count += 1
        else:
            pass

    return LX_il


def calc_X(node, m, G, algo, X_il):
    '''Calculate X
    
    Parameters
    ----------
    node : 
    m    : 
    G    : NetworkX Acyclic Di-graph
    algo : The algorithm can be of type "MLRC" or "MRLC"
    X_il : The start time constraints [ [...] ] List within a list
    
    Returns
    -------
    X : List
    '''
    ts_List = calc_Start_Time(G)
    allNodes_List = G.nodes()
    pos = allNodes_List.index(node)

    mobilityModified_List = calc_Mobility_Mod(G)
    mobilityCumulated_List = calc_Mobility_Cumulated(mobilityModified_List)
    
    X = list()
    if algo == "MLRC_ILP":
        noOfColumns = sum(mobilityModified_List)
    elif algo == "MRLC_ILP":
        (nodes_TotalOperation, uniqueResourceTypes) = identify_Resources(G)
        noOfColumns = sum(mobilityModified_List) + len(uniqueResourceTypes)
    
    for i in range(0, noOfColumns):
        X.append(0)
    
    index = m - ts_List[pos]
    index = mobilityCumulated_List[pos] - mobilityModified_List[pos] + index
    
    X[index] = 1

    return X
    
def calc_constraints_Precedence(G, algo, X_il):
    '''Calculates the Precedence Constraints
    
    Parameters
    ----------
    G    : NetworkX Acyclic Di-graph
    algo : The algorithm can be of type "MLRC_ILP" or "MRLC_ILP"
    X_il : The start time constraints [ [...] ] List within a list
    
    Returns
    -------
    rows : List of list containing the valid coefficients of the nodes
    '''
    #mobility_mod_list = calc_Mobility_Mod(G) #DELETE
    
    nodesWithValidPredecessors_List = list()
    rows = list()
    rows_Xcoefficients = list()
    rows_Dcoefficients = list()
    newNodes_List = list()
    
    # Step-1: Identify the nodes that has some predecessors, otherwise ignore
    for n in nx.topological_sort(G):
        if not G.predecessors(n) or ("0" in G.predecessors(n)):
            pass
        else:
            nodesWithValidPredecessors_List.append(n)
  
    # Step-2: Iterate through the list of the nodes that has some predecessors and for each selected node, there are 2 possible cases
    #         Case 1: Selected node's mobility is 0
    #                 | a. --> Selected node's "Predecessor's" mobility is 0 - IGNORE 
    #                 | b. --> Selected node's "Predecessor" has some mobility - CONSIDER the node combination
    #         Case 2: Selected node has some mobility - CONSIDER
    for nodeIndex in range(0, len(nodesWithValidPredecessors_List)):
        predecessorNodes_List = G.predecessors(str(nodesWithValidPredecessors_List[nodeIndex]))     
        
        # Case 1:
        if (G.node[str(nodesWithValidPredecessors_List[nodeIndex])]["mobility"] == 0):
            for j in range(0, len(predecessorNodes_List)):
                
                # Case-1.a:
                if (G.node[str(predecessorNodes_List[j])]["mobility"] == 0):
                    pass
                # Case-1.b:
                else:
                    LX_il = calc_LX_il(G, algo, X_il, int(nodesWithValidPredecessors_List[nodeIndex]))
                    LX_jl = calc_LX_il(G, algo, X_il, int(predecessorNodes_List[j]))
                    LX_ijl = list(np.array(LX_il) - np.array(LX_jl))
                
                    delay_xjl = int(G.node[predecessorNodes_List[j]]["delay"])                
                
                    rows_Xcoefficients.append(LX_ijl)
                    rows_Dcoefficients.append(delay_xjl)
                    newNodes_List.append(nodesWithValidPredecessors_List[nodeIndex])
        # Case 2:
        else:
            for j in range(0, len(predecessorNodes_List)):
                LX_il = calc_LX_il(G, algo, X_il, int(nodesWithValidPredecessors_List[nodeIndex]))
                LX_jl = calc_LX_il(G, algo, X_il, int(predecessorNodes_List[j]))
                LX_ijl = list(np.array(LX_il) - np.array(LX_jl))
                
                delay_xjl = int(G.node[predecessorNodes_List[j]]["delay"])                
                
                rows_Xcoefficients.append(LX_ijl)
                rows_Dcoefficients.append(delay_xjl)
            
            newNodes_List.append(nodesWithValidPredecessors_List[nodeIndex])
    
    rows.append(rows_Xcoefficients)
    rows.append(rows_Dcoefficients)
    
    return rows


def calc_constraints_ResourceType(G, algo, X_il, nodesOperation_List, operationTypeIndex):
    '''Supplementary method to calculate the Resource Constraints
    
    Parameters
    ----------
    G                   : NetworkX Acyclic Di-graph
    algo                : The algorithm can be of type "MLRC_ILP" or "MRLC_ILP"
    X_il                : The start time constraints [ [...] ] List within a list
    nodesOperation_List : List containing nodes having similar operation
    operationTypeIndex  : 
    
    Returns
    -------
    Outer2rows : List of list of list containing the valid coefficients of the nodes [ [ [...], [...] ],  [ [...], [...] ] ]
    '''
    # Step-1: Identify the range of "l" for any particular operation type i.e. Minimum Start Time and Maximum Latest Start Time
    #         for all nodes that correspond to a particular operation
    min_ts = min(G.node[str(i)]["ts"] for i in nodesOperation_List)
    max_tl = max(G.node[str(i)]["tl"] for i in nodesOperation_List)
    
    mobilityModified_List = calc_Mobility_Mod(G)
    
    Outer2rows = list()
    rows = list()
    
    # Step-2: Identify the different types of operations and group them 
    (nodes_TotalOperation, uniqueResourceTypes) = identify_Resources(G)
    
    # Step-3: Create the number of columns
    if algo == "MLRC_ILP":
        noOfColumns = sum(mobilityModified_List)
    elif algo == "MRLC_ILP":
        noOfColumns = sum(mobilityModified_List) + len(uniqueResourceTypes)
    
    # Step-4: 
    for l in range(min_ts, max_tl + 1):  
        columns = list()
        for j in range(0, noOfColumns):
            columns.append(0)
        
        for node in nodesOperation_List:
            # for each node selected, "l" must be greater than "ts" else ignore
            if l >= G.node[node]["ts"]:
                # IF (l - d_i + 1) >= ts THEN (m = l - d_i + 1)
                if ((l - int(G.node[node]["delay"]) + 1) >= int(G.node[node]["ts"])):
                    m = l - int(G.node[node]["delay"]) + 1
                # ELSE (m = ts)
                else:
                    m = int(G.node[node]["ts"])
                
                for j in range(m, min(G.node[node]["tl"], l) + 1):
                    columns = list(np.array(columns) + np.array(calc_X(node, j, G, algo, X_il)))              
            else:
                pass
            
            # For MRLC, Set the coefficients to -1 corresponding to a1, a2, ...
            if algo == "MRLC_ILP":
                columns[sum(mobilityModified_List) + operationTypeIndex] = -1
        rows.append(columns)
    
    Outer2rows.append(rows)
    
    resourceInstances = list()
    noOfInstancesOfResource = 0
    
    # Step-5.1: For MLRC, input the number of instances of resources
    if algo == "MLRC_ILP":
        if uniqueResourceTypes[operationTypeIndex] == "mul":
            noOfInstancesOfResource = int(raw_input("Enter the number of instances of Multiplier: "))
        elif uniqueResourceTypes[operationTypeIndex] == "add":
            noOfInstancesOfResource = int(raw_input("Enter the number of instances of Adder:      "))
        elif uniqueResourceTypes[operationTypeIndex] == "sub":
            noOfInstancesOfResource = int(raw_input("Enter the number of instances of Subtracter: "))
        elif uniqueResourceTypes[operationTypeIndex] == "les":
            noOfInstancesOfResource = int(raw_input("Enter the number of instances of Comparator: "))
        elif uniqueResourceTypes[operationTypeIndex] == "exp":
            noOfInstancesOfResource = int(raw_input("Enter the number of instances of Exponent:   "))
        else:
            pass
    # Step-5.2: For MRLC, there is no input resources to be taken from user
    elif algo == "MRLC_ILP":
        noOfInstancesOfResource = 0
        
    # Step-6: Appending the number of instances of Resources so as to create the RHS of the Resource Constraint Equation
    for i in range(0, max_tl + 1 - min_ts):
        resourceInstances.append(noOfInstancesOfResource)
    
    Outer2rows.append(resourceInstances)
        
    return Outer2rows


def identify_Resources(G):
    '''Identify the Resources and the nodes associated with particular operation
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph
    
    Returns
    -------
    nodes_TotalOperation : List of list containing nodes group together based on operations
    resourceType         : List containing type of resources
    '''
    nodes_mul = list()
    nodes_add = list()
    nodes_sub = list()
    nodes_les = list()
    nodes_exp = list()
    resourceType = list()
    nodes_TotalOperation = list()
    
    nodes_TotalOperation.append(nodes_mul)
    nodes_TotalOperation.append(nodes_add)
    nodes_TotalOperation.append(nodes_sub)
    nodes_TotalOperation.append(nodes_les)
    nodes_TotalOperation.append(nodes_exp)
    
    for node in G.nodes():
        if (G.node[node]["label"] == "mul"):
            nodes_mul.append(node)
        elif G.node[node]["label"] == "add":
            nodes_add.append(node)
        elif G.node[node]["label"] == "sub":
            nodes_sub.append(node)
        elif G.node[node]["label"] == "les":
            nodes_les.append(node)
        elif G.node[node]["label"] == "exp":
            nodes_exp.append(node)
        else:
            pass
    
    nodes_TotalOperation = [x for x in nodes_TotalOperation if x != []]

    for i in range(0, len(nodes_TotalOperation)):
        for node in nodes_TotalOperation[i]:
            if G.node[node]["label"] == "mul":
                resourceType.append("mul")
            elif G.node[node]["label"] == "add":
                resourceType.append("add")
            elif G.node[node]["label"] == "sub":
                resourceType.append("sub")
            elif G.node[node]["label"] == "les":
                resourceType.append("les")
            elif G.node[node]["label"] == "exp":
                resourceType.append("exp")
            break
    
    return (nodes_TotalOperation, resourceType)
    
    
def calc_constraints_Resource(G, algo, X_il):
    '''Calculates the Resource Constraints
    
    Parameters
    ----------
    G    : NetworkX Acyclic Di-graph
    algo : The algorithm can be of type "MLRC_ILP" or "MRLC_ILP"
    X_il : The start time constraints [ [...] ] List within a list
    
    Returns
    -------
    outerRows : List of list containing the valid coefficients of the nodes [[...], [...]]
    '''
    outerRows = list()
    
    # Step-1: Identify the different types of operations and group them  
    (nodes_TotalOperation, uniqueResourceTypes) = identify_Resources(G)
    print "Nodes associated with Operations = " + str(nodes_TotalOperation)
    print "Unique Resource Types = " + str(uniqueResourceTypes)
    print "="*80
    
    # Step-2: Calculate the Resource Constraint for each type of Operation
    for operationType in range(0, len(nodes_TotalOperation)):
        innerRows = calc_constraints_ResourceType(G, algo, X_il, nodes_TotalOperation[operationType], operationType)
        outerRows.append(innerRows)

    return outerRows


def create_Objective_Function(G, algo, X_il):
    '''Create the Objective Function
    
    Parameters
    ----------
    G    : NetworkX Acyclic Di-graph
    algo : The algorithm can be of type "MLRC_ILP" or "MRLC_ILP"
    X_il : The start time constraints [ [...] ] List within a list
    
    Returns
    -------
    LX_il / objectiveFunction : Objective Function for MLRC_ILP / MRLC_ILP
    '''
    mobilityOriginal_List = calc_Mobility_Org(G)
    mobilityModified_List = calc_Mobility_Mod(G)
    nonZeroMobilityNodes_List = list()
    
    allNodes_List = G.nodes()
    
    # Step-1:
    # MLRC: Objective Function has the X-terms
    if algo == "MLRC_ILP":
        for i in range(0, len(mobilityOriginal_List)):
            # The number of columns in the objective function should always match the number of columns in all the constraints for LP-Solve to work
            if i == 0:
                LX_il = [0] * sum(mobilityModified_List)
            
            # Step-1.1: The Objective function should contain the terms for which mobility varies else ignore
            if (mobilityOriginal_List[i] == 0):
                pass
            else:
                nonZeroMobilityNodes_List.append(allNodes_List[i])
                LX_il = list(np.array(LX_il) + np.array(calc_LX_il(G, algo, X_il, int(allNodes_List[i]))))                  
        
        return LX_il
    # MRLC: Objective Function has the area metrics for each of the Resource Types
    elif algo == "MRLC_ILP":
        # Step-1.1: Identify the different types of operations and group them
        (nodes_TotalOperation, uniqueResourceTypes) = identify_Resources(G)
        
        objectiveFunction = list()
        resourceArea = list()
        
        # The number of columns in the objective function should always match the number of columns in all the constraints for LP-Solve to work
        for i in range(0, sum(mobilityModified_List)):
            objectiveFunction.append(0)
    
        # Step-2: Input the Areas of the different resource types
        for i in range(0, len(uniqueResourceTypes)):         
            if uniqueResourceTypes[i] == "mul":
                nodeMul = nodes_TotalOperation[i][0]
                areaMul = G.node[nodeMul]["area"]
                resourceArea.append(areaMul)
                objectiveFunction.append(areaMul)
            elif uniqueResourceTypes[i] == "add":
                nodeAdd = nodes_TotalOperation[i][0]
                areaAdd = G.node[nodeAdd]["area"]
                resourceArea.append(areaAdd)
                objectiveFunction.append(areaAdd)
            elif uniqueResourceTypes[i] == "sub":
                nodeSub = nodes_TotalOperation[i][0]
                areaSub = G.node[nodeSub]["area"]
                resourceArea.append(areaSub)
                objectiveFunction.append(areaSub)
            elif uniqueResourceTypes[i] == "les":
                nodeLes = nodes_TotalOperation[i][0]
                areaLes = G.node[nodeLes]["area"]
                resourceArea.append(areaLes)
                objectiveFunction.append(areaLes)
            elif uniqueResourceTypes[i] == "exp":
                nodeExp = nodes_TotalOperation[i][0]
                areaExp = G.node[nodeExp]["area"]
                resourceArea.append(areaExp)
                objectiveFunction.append(areaExp)
    
        return objectiveFunction  
    

def calc_LPSolve(G, algo, objectiveFunction, startTimeConstraint, precedenceConstraint, resourceConstraint):
    '''Use Linear Programming Solver to compute the Exact Solution for an Objective Function
    
    Parameters
    ----------
    G                    : NetworkX Acyclic Di-graph
    algo                 : The algorithm can be of type "MLRC" or "MRLC"
    objectiveFunction    : Objective Function
    startTimeConstraint  : Start Time Constraints
    precedenceConstraint : Precedence Constraints
    resourceConstraint   : Resource Constraints
    
    Returns
    -------
    G : Processed graph
    '''
    # Separate out the X-coefficients and Delay coefficients from the Precedence Constraints
    precedenceConstraint_Coefficients = precedenceConstraint[0]
    precedenceConstraint_Delay = precedenceConstraint[1]
    
    # Step-1: 
    lp = lpsolve('make_lp', 0, len(objectiveFunction))

    # Step-2: Pass the Objective Function into the LP-Solver
    lpsolve('set_obj_fn', lp, objectiveFunction)
    print "OBJECTIVE FUNCTION  = " + str(objectiveFunction)
    for i in range(0, len(objectiveFunction)):
        lpsolve('set_int', lp, i, True)
        
    # Step-3: Add the Start Time Constraints
    for i in range(0, G.order()):
        lpsolve('add_constraint', lp, startTimeConstraint[i], EQ, 1)
    
    # Step-4: Add the Precedence Constraints
    for i in range(0, len(precedenceConstraint_Delay)):
        lpsolve('add_constraint', lp, precedenceConstraint_Coefficients[i], GE, precedenceConstraint_Delay[i])
    
    # Step-5: Add the Resource Constraints
    for i in range(0, len(resourceConstraint)):
        for j in range(0, len(resourceConstraint[i][0])):
            lpsolve('add_constraint', lp, resourceConstraint[i][0][j], LE, resourceConstraint[i][1][j])
    
    # Step-6: Write the Objective Function and Constraint Information into a "lp" file
    if algo == "MLRC_ILP":
        lpsolve('write_lp', lp, 'MLRC_ILP_LinearProgramInfo.lp')
    elif algo == "MRLC_ILP":
        lpsolve('write_lp', lp, 'MRLC_ILP_LinearProgramInfo.lp')
    
    # Step-7: Solve the LP problem
    lpsolve('solve', lp)
    
    # Step-8: Extract the information from LP-Solver
    get_objective = lpsolve('get_objective', lp)
    get_variables = lpsolve('get_variables', lp)[0]         # Actual Solution
    get_constraints = lpsolve('get_constraints', lp)[0]
    
    # Step-9: Print the Results to Console
    print "="*100
    print "Objective   = " + str(get_objective)
    print "Variables   = " + str(get_variables)
    print "Constraints = " + str(get_constraints)
    print "="*100
    
    # Step-10: Write the Results
    G = write_Output_ILP(G, algo, get_variables)
    
    return G


def write_Output_ILP(G, algo, finalCoefficients):
    '''Write the Results of ILP Solution into a "dot" file
    
    Parameters
    ----------
    G                    : NetworkX Acyclic Di-graph
    algo                 : The algorithm can be of type "MLRC" or "MRLC"
    finalCoefficients    : 
    
    Returns
    -------
    G : Processed graph
    '''
    ts_List = calc_Start_Time(G)
    mobilityModified_List = calc_Mobility_Mod(G)
    mobilityCumulated_List = calc_Mobility_Cumulated(mobilityModified_List)
    
    allNodes_List = G.nodes()
    
    (nodes_TotalOperation, uniqueResourceTypes) = identify_Resources(G)
       
    # Step-1: From the solution obtained from LP-Solver identify the positions at which 1 appears to calculate the time step
    G.add_nodes_from([n for n in G], time_step = 0)
    for node in G.nodes():
        lowerIndex = mobilityCumulated_List[allNodes_List.index(node)] - mobilityModified_List[allNodes_List.index(node)]
        upperIndex = mobilityCumulated_List[allNodes_List.index(node)]
        
        count = 0
        for j in range(lowerIndex, upperIndex):
            if finalCoefficients[j] == 1:
                G.node[node]["time_step"] = ts_List[allNodes_List.index(node)] + count
            count += 1
    
    # Step-0: Display Results for ILP_MLRC and ILP_MRLC
    print "-----------------------   RESULTS   -----------------------\n"
    if algo == "MLRC_ILP":
        for node in G.nodes():
            if node != "0" and G.node[node]["label"] == "nop":
                if G.node[node]["time_step"] == 0:
                    print "The Solution is INFEASIBLE"
                else:
                    print "Minimum Latency = %d" % (int(G.node[node]["time_step"]) - 1)
                break
            else:
                pass
    elif algo == "MRLC_ILP":
        count = 0
        for node in G.nodes():
            if node != "0" and G.node[node]["label"] == "nop":
                if G.node[node]["time_step"] == 0:
                    print "The Solution is INFEASIBLE"
                else:
                    print "Latency = %d\n" % (int(G.node[node]["time_step"]) - 1)
                break
            else:
                pass        
        for i in range(sum(mobilityModified_List), sum(mobilityModified_List) + len(uniqueResourceTypes)):
            if uniqueResourceTypes[count] == "mul":
                print "Number of instances of Multiplier needed = %d" % math.ceil(finalCoefficients[i])
            elif uniqueResourceTypes[count] == "add":
                print "Number of instances of Adder needed      = %d" % math.ceil(finalCoefficients[i])
            elif uniqueResourceTypes[count] == "sub":
                print "Number of instances of Subtracter needed = %d" % math.ceil(finalCoefficients[i])
            elif uniqueResourceTypes[count] == "les":
                print "Number of instances of Comparator needed = %d" % math.ceil(finalCoefficients[i])
            elif uniqueResourceTypes[count] == "exp":
                print "Number of instances of Exponent needed   = %d" % math.ceil(finalCoefficients[i])
            count += 1
    
    # Step-2: Identify the total number of Time Steps
    timeStep_List = list(set([d["time_step"] for n,d in G.nodes_iter(data=True)]))
    
    # Step-3: Identify the nodes that correspond to a particular "Time Step"
    rows = list()
    for timeStep in range(0, len(timeStep_List)):
        columns = list()
        for node in G.nodes():
            if timeStep_List[timeStep] == G.node[node]["time_step"]:
                s = "\n"
                seq = (node, G.node[node]["label"], str(G.node[node]["time_step"]))
                G.node[node]["label"] = s.join(seq)
                columns.append(node)
            
        rows.append(columns)
    
    # Step-4:
    if algo == "MLRC_ILP": 
        nx.write_dot(G,'MLRC_ILP_FinalOutput.dot')
        G2 = AGraph('MLRC_ILP_FinalOutput.dot')
    elif algo == "MRLC_ILP":
        nx.write_dot(G,'MRLC_ILP_FinalOutput.dot')
        G2 = AGraph('MRLC_ILP_FinalOutput.dot')
    
    # Step-5: The nodes corresponding a particular time step will be a part of sub-graph.
    #         Total number of sub-graphs corresponds to total time steps 
    for i in range(0, len(rows)):
        G2.add_subgraph(rows[i], rank = 'same')
    
    # Step-6: Create the Final "dot" file
    if algo == "MLRC_ILP":
        G2.write('MLRC_ILP_FinalOutput_formatted.dot')
    elif algo == "MRLC_ILP":
        G2.write('MRLC_ILP_FinalOutput_formatted.dot')
    
    return G


def MLRC_List(G):
    '''Compute the Minimum Latency for a given Number of Resources under List Scheduling scheme
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph  
    
    Returns
    -------
    G : Processed graph
    '''
    # Step-1: Priority function is based on mobility i.e. lower the mobility, lower is the flexibility of the node to be assigned
    #         in a later time step. So, nodes will be selected based on the lowest mobility value
    
    (G, minLatency) = calc_ASAP(G)
    (G, exceptionStatus) = calc_ALAP(G, minLatency)
    G = calc_Mobility(G)
    
    # Step-2.1: Identify the different types of operations and group them
    (nodes_TotalOperation, uniqueResourceTypes) = identify_Resources(G)
    print "Nodes associated with Operations = " + str(nodes_TotalOperation)
    print "Unique Resource Types = " + str(uniqueResourceTypes)
    print "="*80
    
    # Step-2.2: Accept the number of instances of each Resource Type
    noOfInstances = list()
    for noOfUniqueResourceTypesIndex in range(0, len(uniqueResourceTypes)):
        if uniqueResourceTypes[noOfUniqueResourceTypesIndex] == "mul":
            noOfInstancesOfMultiplier = int(raw_input("Enter the number of instances of Multiplier: "))
            noOfInstances.append(noOfInstancesOfMultiplier)
        elif uniqueResourceTypes[noOfUniqueResourceTypesIndex] == "add":
            noOfInstancesOfAdder      = int(raw_input("Enter the number of instances of Adder:      "))
            noOfInstances.append(noOfInstancesOfAdder)
        elif uniqueResourceTypes[noOfUniqueResourceTypesIndex] == "sub":
            noOfInstancesOfSubtracter = int(raw_input("Enter the number of instances of Subtracter: "))
            noOfInstances.append(noOfInstancesOfSubtracter)
        elif uniqueResourceTypes[noOfUniqueResourceTypesIndex] == "les":
            noOfInstancesOfComparator = int(raw_input("Enter the number of instances of Comparator: "))
            noOfInstances.append(noOfInstancesOfComparator)
        elif uniqueResourceTypes[noOfUniqueResourceTypesIndex] == "exp":
            noOfInstancesOfExponent   = int(raw_input("Enter the number of instances of Exponent:   "))
            noOfInstances.append(noOfInstancesOfExponent)
        else:
            pass
    
    print "Number of Instances of Unique Resource Types = " + str(noOfInstances)
     
    start_time = time.time()
    # Step-3.1: Prepare a List of Unscheduled nodes
    unscheduledNodesList = list()
    for node in G.nodes():
        unscheduledNodesList.append(node)
        
    # Step-3.2: Schedule the Source node at time step = 1
    t = 1
    G.add_nodes_from([n for n in G], time_step = 0, scheduled = 0)      # Add scheduled attribute to the graph. Default value of 0 indicates nodes are "Unscheduled"
    G.node["0"]["time_step"] = 1
    G.node["0"]["scheduled"] = 1
    
    # Step-4: Logic for Selection of Valid Unscheduled nodes at time step "time_step"
    T_U = list()
    B = list()
    
    # Continue as long as Unscheduled List has the Sink Node
    while unscheduledNodesList:
        # Terminating condition: List has only the Sink node to be scheduled and its predecessors have completed their operation
        if (len(unscheduledNodesList) == 1) and (G.node[unscheduledNodesList[0]]["label"] == "nop"):
            sinkPredecessorNodes_List = G.predecessors(unscheduledNodesList[0])
            exitTime = max((G.node[node]["time_step"] + G.node[node]["delay"])for node in sinkPredecessorNodes_List)
            if exitTime == t:
                print "-------------------------Start of t = %d-------------------------\n" %t
                print "Sink Node scheduled at t = %d" % t
                G.node[unscheduledNodesList[0]]["scheduled"] = 1
                G.node[unscheduledNodesList[0]]["time_step"] = t
                print "\n=========================End of t = %d=========================\n" %t
                print "----------------------      RESULTS      ----------------------\n"
                # Print the final Results
                print "Minimum Latency = %d" %(t - 1)
                
                # Write the Output
                write_Output_LS(G, "MLRC_List")
                break
            else:
                pass
        
        # For time step = 1, T_U has the nodes that are connected to Source node
        # for other time steps, T_U will have the unscheduled nodes to continue
        if t == 1:
            T_U = G.successors("0")
            for i in range(0, len(uniqueResourceTypes)):
                B.append([])
        else:
            T_U = list(unscheduledNodesList)
        
        print "-------------------------Start of t = %d-------------------------\n" %t
        print "Un-scheduled Nodes    = " + str(unscheduledNodesList)
        print "Nodes before deletion = " + str(T_U)
        
        # Delete the nodes if any of its predecessors are not scheduled
        toDeleteUNodesList = list()
        for node in T_U:
            predecessorNodesList = G.predecessors(node)
            for n in predecessorNodesList:
                if G.node[n]["scheduled"] == 0:
                    toDeleteUNodesList.append(node)
                else:
                    pass

        toDeleteUNodesList = list(set(toDeleteUNodesList))
        
        for n in toDeleteUNodesList:
            T_U.remove(n)
            
        print "Nodes with no valid Scheduled Predecessor = " + str(toDeleteUNodesList)
        print "Nodes after 'Nodes with no valid Scheduled Predecessor' removed = " + str(T_U)
        
        # Eliminate the nodes that are still busy in the current time step
        toDelNodesList = list()
        for node in T_U:
            predNodesList = G.predecessors(node)
            for n in predNodesList:
                if n == "0":
                    continue
                elif G.node[n]["time_step"] + G.node[n]["delay"] - 1 >= t:
                    toDelNodesList.append(node)
                else:
                    pass
        toDelNodesList = list(set(toDelNodesList))
        
        for n in toDelNodesList:
            T_U.remove(n)
        
        print "Nodes with Predecessor Still Busy = " + str(toDelNodesList)
        print "Nodes after Invalid 'Nodes with Predecessor Still Busy' removed = " + str(T_U)
        
        (G, unscheduledNodesList, scheduledNodesList) = compute_LS_L(G, nodes_TotalOperation, uniqueResourceTypes, noOfInstances, unscheduledNodesList, T_U, t)
        
        # Step-10: Advance time step
        t = t + 1
    
    print ("MLRC_List takes --- %s seconds --- to execute" % (time.time() - start_time))
    return G

def compute_LS_L(G, nodes_TotalOperation, uniqueResourceTypes, noOfInstances, unscheduledNodesList, T_U, t):
    '''Supplementary method to calculate LS_L
    
    Parameters
    ----------
    G                    : NetworkX Acyclic Di-graph  
    nodes_TotalOperation : List of list having nodes corresponding to different resource types
    uniqueResourceTypes  : List containing the different resource types
    inputLatency         : Input Latency
    noOfInstances        : List having the number of instances of resource types that will be used for scheduling
    unscheduledNodesList : List of nodes that are yet to be scheduled in the current time step "time_step"
    T_U                  : List containing the nodes that are eligible for selection
    t                    : time step
    
    Returns
    -------
    G                    : Processed graph
    unscheduledNodesList : List of nodes that are yet to be scheduled after the current time step "time_step"
    scheduledNodesList   : List of nodes that got scheduled in the current time step 't'
    '''
    U = list()
    B = list()
    S = list()                  # List of list containing the nodes that satisfy |S_t,m| + |B_t,m| <= a_m
    M = list()
    M_Star = list()             # List of list containing the mobilities in increasing order
    U_Star = list()             # List of list containing the nodes corresponding to increasing mobilities
    
    for i in range(0, len(uniqueResourceTypes)):
        U.append([])
        B.append([])
        S.append([])
        M.append([])
        M_Star.append([])
        U_Star.append([])
    
    for node in T_U:
        for i in range(0, len(uniqueResourceTypes)):
            if G.node[node]["label"] == uniqueResourceTypes[i]:
                U[i].append(node)
                break
    
    # Step-5: Mobility Calculation M
    for i in range(0, len(uniqueResourceTypes)):
        if not U[i]:        # No need to calculate Mobility as input list is empty
            M[i] = -1
            pass
        else:
            for node in U[i]:
                for n in G.nodes():
                    if node == n:
                        M[i].append(G.node[node]["mobility"])
                        break
                    else:
                        pass
                    
    # Step-6: Priority function is based on mobility i.e. lower the mobility, lower is the flexibility of the node to be assigned
    #         in a later time step. So, nodes will be selected based on the lowest mobility value 
    #         M* -> Increasing mobility
    #         U* -> Nodes corresponding to Increasing mobility
    for i in range(0, len(uniqueResourceTypes)):
        if not U[i]:
            pass
        else:
            # Similar logic in place: Refer to logic for V in LS_R
            M_Star[i] = sorted(M[i])
            for j in M_Star[i]:
                    for k in range(0, len(M[i])):
                        if (j == M[i][k]) and (U[i][k] in U_Star[i]):
                            continue
                        elif (j == M[i][k]) and (U[i][k] not in U_Star[i]):
                            U_Star[i].append(U[i][k])
                            break
                        else:
                            pass        
    
    # Step-7: B is the list that contains the nodes that are busy i.e. they are executing at time step "time_step"
    if t == 1:
        pass
    else:
        for i in range(0, len(nodes_TotalOperation)):
            for n in nodes_TotalOperation[i]:
                if (G.node[n]["scheduled"] == 1) and (G.node[n]["time_step"] + G.node[n]["delay"] - 1 >= t):
                    B[i].append(n)
                else:
                    pass
    
    # Step-8: Selection of S under under the constraint: S + B <= a
    noOfPossibleNodes = list()
    for i in range(0, len(nodes_TotalOperation)):
        noOfPossibleNodes.append(noOfInstances[i] - len(B[i]))
       
    for i in range(0, len(nodes_TotalOperation)):
        if (noOfPossibleNodes[i] > 0) and U[i]:
            for j in range(0, min(len(U[i]), noOfPossibleNodes[i])):
                S[i].append(U_Star[i][j])
        else:
            pass
    
    # Step-9: Create the Scheduled nodes list corresponding nodes in list "S"
    scheduledNodesList = list()
    for i in range(0, len(uniqueResourceTypes)):
        if S[i]:
            for j in range(0, len(S[i])):
                scheduledNodesList.append(S[i][j])
        else:
            pass
    
    # Update the "time step" and "scheduled status" for the nodes that have been scheduled in the current time step "time_step"
    for node in scheduledNodesList:
        G.node[node]["time_step"] = t
        G.node[node]["scheduled"] = 1
    
    # Update the Unscehduled list i.e. remove the nodes that got scheduled
    for scheduledNode in scheduledNodesList:
        for unscheduledNode in unscheduledNodesList:
            if scheduledNode == unscheduledNode:
                unscheduledNodesList.remove(scheduledNode)
            else:
                pass
    if t == 1:
        unscheduledNodesList.remove("0")            # Source node "0" got scheduled in time step 1
    else:
        pass
    
    print "U                  = " + str(U)
    print "B                  = " + str(B)
    print "S                  = " + str(S)
    print "M                  = " + str(M)
    print "M*                 = " + str(M_Star)
    print "U*                 = " + str(U_Star)
    print "Scheduled Nodes    = " + str(scheduledNodesList)
    print "Un-scheduled Nodes = " + str(unscheduledNodesList)
    print "\n-------------------------End of t = %d-------------------------" %t
    
    return (G, unscheduledNodesList, scheduledNodesList)


def compute_Slack(G, v_nodes_List, latency, time):
    '''Compute the Slack for the nodes
    
    Slack_of_the_Node = Latest_Start_Time_of_the_Node - Time_Step
    i.e. s(v) = ALAP(v, latency) - t
    
    Parameters
    ----------
    G            : NetworkX Acyclic Di-graph
    v_nodes_List : The algorithm can be of type "MLRC" or "MRLC"
    latency      : <optional>
    time         :    
    
    Returns
    -------
    s_slack_List : List containing slack values
    '''
    s_slack_List = list()
    
    # Step-1: s(v) = ALAP(v, latency) - t
    #         Here, the Latest Start time is already present in the Graph since ALAP is already calculated. So, "tl" value is only fetched and is not calculated here
    for node in v_nodes_List:
        s_slack_List.append(G.node[node]["tl"] - time)
        
    return s_slack_List

   
def MRLC_List(G):
    '''Compute the Minimum Resources for a given latency under List Scheduling scheme
    
    Parameters
    ----------
    G : NetworkX Acyclic Di-graph  
    
    Returns
    -------
    G : Processed graph
    '''
   
    # Step-1: Allocate resource instances of 1 unit each to start with
    (nodes_TotalOperation, uniqueResourceTypes) = identify_Resources(G)
    print "Nodes associated with Operations = " + str(nodes_TotalOperation)
    print "Unique Resource Types = " + str(uniqueResourceTypes)
    print "="*80
    
    noOfInstances = list()
    for n in range(len(uniqueResourceTypes)):
        noOfInstances.append(1)
    
    # Add delay information to the graph
    G = add_DelayAreaInfoToGraph(G)
    
    # Perform ASAP to compute the minimum Latency
    (G, minLatency) = calc_ASAP(G)
    print "MRLC_List: Minimum Latency: %d" % minLatency
    
    # Step-2: Compute ALAP
    inputLatency = int(raw_input("Enter Latency: "))

    (G, exceptionStatus) = calc_ALAP(G, inputLatency)
    if exceptionStatus == 1:
        print "Solution not feasible: Latency %d is lower than Minimum Latency of %d" % (inputLatency, minLatency)
        return
    else:
        pass
     
    start_time = time.time()
    # Step-3.1: Prepare a List of Unscheduled nodes
    unscheduledNodesList = list()
    for node in G.nodes():
        unscheduledNodesList.append(node)  
    # Step-3.2: Schedule the Source node at time step = 1
    t = 1
    G.add_nodes_from([n for n in G], time_step = 0, scheduled = 0)          # Add scheduled attribute to the graph. Default value of 0 indicates nodes are "Unscheduled"
    G.node["0"]["time_step"] = 1
    G.node["0"]["scheduled"] = 1
    
    # Step-4:
    T_U = list()        # Total U_t is the Unprocessed U_t that has the probable nodes of all operation types of "r" that can be selected at time step "time_step"
                        # After repeated filtering out of the nodes, T_U will have the valid set of nodes
    B = list()          # B_t,r indicates operations of type "r" that are executing at time "time_step"
    
    # Continue as long as Unscheduled List has the Sink Node
    while unscheduledNodesList:
        # Terminating condition: List has only the Sink node to be scheduled and its predecessors have completed their operation
        if (len(unscheduledNodesList) == 1) and (G.node[unscheduledNodesList[0]]["label"] == "nop"):
            sinkPredecessorNodes_List = G.predecessors(unscheduledNodesList[0])
            exitTime = max((G.node[node]["time_step"] + G.node[node]["delay"])for node in sinkPredecessorNodes_List)
            if exitTime == t:
                print "-------------------------Start of t = %d-------------------------\n" %t
                print "Sink Node scheduled at t = %d" % t
                
                G.node[unscheduledNodesList[0]]["scheduled"] = 1
                G.node[unscheduledNodesList[0]]["time_step"] = t
                
                print "\n=========================End of t = %d=========================\n" %t
                print "-------------------------   RESULTS   -------------------------\n"
                print "Latency = %d\n" % (t - 1)
                
                # Print the final Results
                for i in range(0, len(uniqueResourceTypes)):
                    if uniqueResourceTypes[i] == "mul":
                        print "Number of Multiplier units required  = %d" % noOfInstances[i]
                    elif uniqueResourceTypes[i] == "add":
                        print "Number of Adder units required       = %d" % noOfInstances[i]
                    elif uniqueResourceTypes[i] == "sub":
                        print "Number of Subtracter units required  = %d" % noOfInstances[i]
                    elif uniqueResourceTypes[i] == "les":
                        print "Number of Comparator units required  = %d" % noOfInstances[i]
                    elif uniqueResourceTypes[i] == "exp":
                        print "Number of Exponent units required    = %d" % noOfInstances[i]
                        
                # Write the Output
                write_Output_LS(G, "MRLC_List")
                break
            else:
                pass
        
        # For time step = 1, T_U has the nodes that are connected to Source node
        # for other time steps, T_U will have the unscheduled nodes to continue
        if t == 1:
            T_U = G.successors("0")
            for i in range(0, len(uniqueResourceTypes)):
                B.append([])
        else:
            T_U = list(unscheduledNodesList)
        
        print "-------------------------Start of t = %d-------------------------\n" %t
        print "Un-scheduled Nodes    = " + str(unscheduledNodesList)
        print "Nodes before deletion = " + str(T_U)
        
        # Delete the nodes if any of its predecessors are not scheduled
        toDeleteUNodesList = list()
        for node in T_U:
            predecessorNodesList = G.predecessors(node)
            for n in predecessorNodesList:
                if G.node[n]["scheduled"] == 0:
                    toDeleteUNodesList.append(node)
                else:
                    pass
        toDeleteUNodesList = list(set(toDeleteUNodesList))
        
        for n in toDeleteUNodesList:
            T_U.remove(n)
            
        print "Nodes with no valid Scheduled Predecessor = " + str(toDeleteUNodesList)
        print "Nodes after 'Nodes with no valid Scheduled Predecessor' removed = " + str(T_U)
        
        # Eliminate the nodes that are still busy in the current time step
        # Class example: ['1', '2'] nodes are still busy 
        toDelNodesList = list()
        for node in T_U:
            predNodesList = G.predecessors(node)
            for n in predNodesList:
                if n == "0":
                    continue
                elif G.node[n]["time_step"] + G.node[n]["delay"] - 1 >= t:
                    toDelNodesList.append(node)
                else:
                    pass
        toDelNodesList = list(set(toDelNodesList))
        
        for n in toDelNodesList:
            T_U.remove(n)        
        
        print "Nodes with Predecessor Still Busy = " + str(toDelNodesList)
        print "Nodes after Invalid 'Nodes with Predecessor Still Busy' removed = " + str(T_U)
        
        (G, unscheduledNodesList, scheduledNodesList, noOfInstances) = compute_LS_R(G, nodes_TotalOperation, uniqueResourceTypes, inputLatency, noOfInstances, unscheduledNodesList, T_U, t)
        
        # Step-11: Advance time step
        t = t + 1
    
    print ("MRLC_List takes --- %s seconds --- to execute" % (time.time() - start_time))    
    return G


def compute_LS_R(G, nodes_TotalOperation, uniqueResourceTypes, inputLatency, noOfInstances, unscheduledNodesList, T_U, t):      
    '''Supplementary method to calculate LS_R
    
    Parameters
    ----------
    G                    : NetworkX Acyclic Di-graph  
    nodes_TotalOperation : List of list having nodes corresponding to different resource types
    uniqueResourceTypes  : List containing the different resource types
    inputLatency         : Input Latency
    noOfInstances        : List having the number of instances of resource types that will be used for scheduling
    unscheduledNodesList : List of nodes that are yet to be scheduled in the current time step "time_step"
    T_U                  : List containing the nodes that are eligible for selection
    t                    : time step
    
    Returns
    -------
    G                    : Processed graph
    unscheduledNodesList : List of nodes that are yet to be scheduled after the current time step "time_step"
    scheduledNodesList   : List of nodes that got scheduled in the current time step 't'
    noOfInstances        : List having the number of instances of resource types that were used for scheduling
    '''
    U = list()
    B = list()
    S = list()
    U_Star = list()
    V = list()
    
    for i in range(0, len(uniqueResourceTypes)):
        U.append([])
        B.append([])
        S.append([])
        U_Star.append([])
        V.append([])
    
    # Separate U's created for different Resource Types
    # Group the nodes based on the type of operation U_t,r
    # Example: U is a list of list
    # U[0] -> resourceType 1, U[1] -> resourceType 2, ...
    # U[0][...] -> nodes that are related to resourceType 1
    # U[1][...] -> nodes that are related to resourceType 2    
    for node in T_U:
        for i in range(0, len(uniqueResourceTypes)):
            if G.node[node]["label"] == uniqueResourceTypes[i]:
                U[i].append(node)                               # U_t,r
                break
    
    # Step-5: Slack Calculation
    for i in range(0, len(uniqueResourceTypes)):
        if not U[i]:        # No need to calculate slack as input node's list is empty
            S[i] = -1       # Slack of -1 represents invalid slack
            pass
        else:
            # U_operationType is not empty then only calculate slack
            S[i] = compute_Slack(G, U[i], inputLatency, t)
    
    # Step-6: U* is the list that contains the nodes having slack as 0 i.e. these must be scheduled at time step "time_step" 
    for i in range(0, len(uniqueResourceTypes)):
        if not U[i]:
            pass
        else:
            for index in range(0, len(U[i])):
                if S[i][index] == 0:
                    U_Star[i].append(U[i][index])
                else:
                    pass
       
    # Step-7: B is the list that contains the nodes that are busy i.e. they are executing at time step "time_step"
    if t == 1:
        pass
    else:
        for i in range(0, len(nodes_TotalOperation)):
            for n in nodes_TotalOperation[i]:
                if (G.node[n]["scheduled"] == 1) and (G.node[n]["time_step"] + G.node[n]["delay"] - 1 >= t):
                    B[i].append(n)
                else:
                    pass
                
    # Step-8: Increase the number of resources if the total number of nodes in U* and B list is more than the current number of resources
    for i in range(0, len(uniqueResourceTypes)):
        noOfInstances[i] = max(noOfInstances[i], len(U_Star[i]) + len(B[i]))
    
    # Step-9: V is the list that corresponds to the additional operations that can be schdeuled at time step "time_step" 
    #         within the number of resources obtained in Step-8
    for i in range(0, len(uniqueResourceTypes)):
        if len(U_Star[i]) < noOfInstances[i]:
            noOfNodesAllocationPossible = noOfInstances[i] - (len(U_Star[i]) + len(B[i]))
            
            tempNodesList = [node for node in U[i] if node not in U_Star[i]]      # tempNodes = U - U*
            tempSlackList = list()
            # If (U - U*) is not empty and number of avaible resouces that can be allocated to nodes is > 0 THEN allocate
            if tempNodesList and (noOfNodesAllocationPossible > 0):
                count = 0
                for k in U[i]:
                    for l in tempNodesList:
                        if l == k:
                            tempSlackList.append(S[i][count])
                        else:
                            pass
                    count += 1
                
                # Priority function: Logic for nodes selection is based on the value of slack i.e.
                # a lower value of Slack will indicate less flexibility i.e. more urgency for allocation
                increasingSlackList = sorted(tempSlackList)         # Sort in increasig order of slack
                increasingNodesList = list()                        # Arrange the nodes corresponding to the increasing slack
                for j in increasingSlackList:
                    for k in range(0, len(tempSlackList)):
                        # The below logic is in place since slack can have dupliacte values but normal fetching logic
                        # will fetch one node for all the same values of slack. So, other nodes having the same slack value will be left out.
                        # Only one node corresponding to a particular salck value will be present
                        # Illustartion: Nodes = ['3', '2', '1', '4', '0']
                        #               Slack = [ 3,   2,   1,   2,   0 ]
                        #    Increasing_Slack = [ 0,   1,   2,   2,   3 ]
                        #    Increasing_Nodes = ['0', '1', '2', "4", '3']        Correct Logic in place
                        #   Increasing_Nodes* = ['0', '1', '2', "2", '3']        With Missing Logic: Node "4" will be missing
                        
                        if (j == tempSlackList[k]) and (tempNodesList[k] in increasingNodesList):
                            continue
                        elif (j == tempSlackList[k]) and (tempNodesList[k] not in increasingNodesList):
                            increasingNodesList.append(tempNodesList[k])
                            break
                        else:
                            pass
                for j in range(0, min(len(U[i]) - len(U_Star[i]), noOfNodesAllocationPossible)):
                    V[i].append(increasingNodesList[j])
            else:
                pass
        else:
            pass
    
    # Step-10: Create the Scheduled nodes list which is the sum total of (U* and V) i.e. the nodes that have been allocated in the current time step
    scheduledNodesList = list()
    for i in range(0, len(uniqueResourceTypes)):
        if U_Star[i]:           # U* not empty
            for j in range(0, len(U_Star[i])):
                scheduledNodesList.append(U_Star[i][j])
        else:
            pass
        if V[i]:                # V not empty
            for j in range(0, len(V[i])):
                scheduledNodesList.append(V[i][j])
        else:
            pass
    
    # Update the "time step" and "scheduled status" for the nodes that have been scheduled in the current time step "time_step"
    for node in scheduledNodesList:
        G.node[node]["time_step"] = t
        G.node[node]["scheduled"] = 1           # "scehduled" = 1 -> Scheduled, 0 -> Unscheduled 
    
    # Update the Unscehduled list i.e. remove the nodes that got scheduled
    for scheduledNode in scheduledNodesList:
        for unscheduledNode in unscheduledNodesList:
            if scheduledNode == unscheduledNode:
                unscheduledNodesList.remove(scheduledNode)
            else:
                pass
    if t == 1:
        unscheduledNodesList.remove("0")        # Source node "0" got scheduled in time step 1
    else:
        pass
    
    print "U                   = " + str(U)
    print "B                   = " + str(B)
    print "S                   = " + str(S)
    print "U*                  = " + str(U_Star)
    print "V                   = " + str(V)    
    print "Number Of Instances = " + str(noOfInstances)
    print "Scheduled Nodes     = " + str(scheduledNodesList)
    print "Un-scheduled Nodes  = " + str(unscheduledNodesList)
    print "\n-------------------------End of t = %d-------------------------" %t
    
    return (G, unscheduledNodesList, scheduledNodesList, noOfInstances)          


def write_Output_LS(G, algo):
    '''Write the Results of LS Solution into a "dot" file
    
    Parameters
    ----------
    G    : NetworkX Acyclic Di-graph
    algo : The algorithm can be of type "MLRC_List" or "MRLC_List"
    
    Returns
    -------
    G : Processed graph
    '''    
    # Step-1: Identify the total number of Time Steps
    timeStep_List = list(set([d["time_step"] for n,d in G.nodes_iter(data=True)]))
    
    # Step-2: Identify the nodes that correspond to a particular "Time Step"
    rows = list()
    for timeStep in range(0, len(timeStep_List)):
        columns = list()
        for node in G.nodes():
            if timeStep_List[timeStep] == G.node[node]["time_step"]:
                s = "\n"
                seq = (node, G.node[node]["label"], str(G.node[node]["time_step"]))
                G.node[node]["label"] = s.join(seq)
                columns.append(node)
            
        rows.append(columns)
    
    # Step-3:
    if algo == "MLRC_List": 
        nx.write_dot(G,'MLRC_List_FinalOutput.dot')
        G2 = AGraph('MLRC_List_FinalOutput.dot')
    elif algo == "MRLC_List":
        nx.write_dot(G,'MRLC_List_FinalOutput.dot')
        G2 = AGraph('MRLC_List_FinalOutput.dot')
        
    # Step-4: The nodes corresponding a particular time step will be a part of sub-graph.
    #         Total number of sub-graphs corresponds to total time steps 
    for i in range(0, len(rows)):
        G2.add_subgraph(rows[i], rank = 'same')
    
    # Step-5: Create the Final "dot" file
    if algo == "MLRC_List":
        G2.write('MLRC_List_FinalOutput_formatted.dot')
    elif algo == "MRLC_List":
        G2.write('MRLC_List_FinalOutput_formatted.dot')
    
    return G


if __name__ == '__main__':
    main()
