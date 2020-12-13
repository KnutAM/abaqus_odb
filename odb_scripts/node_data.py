from __future__ import print_function
import sys
import numpy as np
import re

from abaqusConstants import *
from abaqus import session
import visualization


def get_multiple_positions(odb, inst_name, positions, variable, step_numbers, 
                           increments=['0:-1'], tol=1.e-2):
    """ Get given variable from odb at given positions for specified steps and 
    increments
    
    :param odb: The odb object to extract results from
    :type odb: Odb object (Abaqus)
    
    :param inst_name: The name of the instance to get results for
    :type inst_name: str
    
    :param position: Node coordinates where results will be extracted. 
                     Alternatively, name of set in odb instance 
                     containing nodes from which results shall be 
                     extracted. 
    :type position: list[ list[ float ] ] or str
    
    :param variable: Variable to extract
    :type variable: str
    
    :param step_numbers: List of step numbers from which to extract results
    :type step_numbers: list[ int ]
    
    :param increments: List of increments from which to extract results. 
                       ['0:-1'] implies all increments. 
                       Note that python negative numbering can be used, 
                       such that -1 implies last increment. Opposed to 
                       python lists, the last given index is included.
    :type increments: list[ int ]
    
    :param tol: Tolerance for node position
    :type tol: float
    
    :returns: Dictionary describing the results with fields containing 
              numpy arrays. Each row describe new time points
              
              - "step"
              - "incr"
              - "time"
              - "node"
              - 0
              - 1
              - ...
              - N-1
              
              Where the number 0-(N-1) is the index in the position list
              describing the node. The "node" entry is a Nx3 array with 
              the node coordinates. 
              
    :rtype: dict
    
    """
    
    odb_inst = odb.rootAssembly.instances[inst_name]
    
    # Get node labels based on the positions
    if isinstance(positions, str):
        node_labels = [n.label for n in odb_inst.nodeSets[positions].nodes]
    else:
        node_labels = get_node_labels(odb, inst_name, positions, tol)
    
    node_spec = ((inst_name, tuple(node_labels)),)
    
    # Translate the var list to the variable list format 
    # requried by xyDataListFromField
    variable_list = get_variable_list([variable])
    
    # Set the active frames
    step_data, incr_data = set_active_frames(odb, step_numbers, increments)
    
    # Get xy_data_list
    # Need to set odb active, otherwise the xyDataListFromField will fail!
    viewport = session.viewports[session.viewports.keys()[0]]
    viewport.setValues(displayedObject=odb)
    xy_data_list = session.xyDataListFromField(odb=odb, 
                                               outputPosition=NODAL,
                                               variable=variable_list, 
                                               nodeLabels=node_spec)
    
    node_data = {'step': step_data,
                 'incr': incr_data,
                 'node': []}
    
    odb_inst_node_labels = [n.label for n in odb_inst.nodes]

    for node_ind, xy_data in enumerate(xy_data_list):
        data = np.array(xy_data.data)
        if not 'time' in node_data:
            node_data['time'] = data[:,0]
        node_data[node_ind] = data[:,1]
        odb_node_ind = odb_inst_node_labels.index(node_labels[node_ind])
        node_data['node'].append(odb_inst.nodes[odb_node_ind].coordinates)

    node_data['node'] = np.array(node_data['node'])
    
    return node_data
    

def get_multiple_variables(odb, inst_name, position, variables, step_numbers,
                           increments=['0:-1'], tol=1.e-2):
    """ Get given variables from odb at given position for specified 
    steps and increments
    
    :param odb: The odb object to extract results from
    :type odb: Odb object (Abaqus)
    
    :param inst_name: The name of the instance to get results for
    :type inst_name: str
    
    :param position: Node coordinates where results will be extracted
    :type position: list[ float ]
    
    :param variables: List of variables to extract
    :type variables: list[ str ]
    
    :param step_numbers: List of step numbers from which to extract results
    :type step_numbers: list[ int ]
    
    :param increments: List of increments from which to extract results. 
                       ['0:-1'] implies all increments. 
                       Note that python negative numbering can be used, 
                       such that -1 implies last increment. Opposed to 
                       python lists, the last given index is included.
    :type increments: list[ int ]
    
    :param tol: Tolerance for node position
    :type tol: float
    
    :returns: Dictionary describing the results with fields containing numpy 
              arrays. Each row describe new time points
              
              - "step"
              - "incr"
              - "time"
              - "var_1"
              - "var_2"
              - ...
              - "var_N"
              
              Where "var_i" is the ith variable of the N variables given 
              in the list var.
              
    :rtype: dict
    
    """
    # Get node labels based on the positions
    node_label = get_node_labels(odb, inst_name, [position], tol)[0]
    node_spec = ((inst_name, (node_label,)),)
    
    # Translate the var list to the variable list format 
    # requried by xyDataListFromField
    variable_list = get_variable_list(variables)
    
    # Set the active frames
    step_data, incr_data = set_active_frames(odb, step_numbers, increments)
    
    # Get xy_data_list
    # Need to set odb active, otherwise the xyDataListFromField will fail!
    viewport = session.viewports[session.viewports.keys()[0]]
    viewport.setValues(displayedObject=odb)
    xy_data_list = session.xyDataListFromField(odb=odb, 
                                               outputPosition=NODAL,
                                               variable=variable_list, 
                                               nodeLabels=node_spec)
    time_set = False
    node_data = {'step': step_data,
                 'incr': incr_data}

    for xy_data, variable in zip(xy_data_list, variables):
        data = np.array(xy_data.data)
        if not time_set:
            node_data['time'] = data[:,0]
            time_set = True
        node_data[variable] = data[:,1]
        
    return node_data
    
    
def get_node_labels(odb, inst, pos, tol):
    """ 
    
    :param odb: The odb object to get node labels from
    :type odb: Odb object (Abaqus)
    
    :param inst: The name of the instance to get node labels from
    :type inst: str
    
    :param pos: List of node coordinates where results will be extracted
    :type pos: list[ list[ float ] ]
    
    :param tol: Tolerance for node position
    :type tol: float
    
    :returns: A list of node labels.
    :rtype: list[ int ]
    
    """
    # Convert pos to (tranposed) numpy array internally
    pos_ = np.transpose(pos)
    
    labels = np.zeros((len(pos),), dtype=np.int)
    n_missing = -len(pos)
    for node in odb.rootAssembly.instances[inst].nodes:
        coord = np.array(node.coordinates)
        d2 = 0.0
        for coord_comp, pos_comp in zip(coord, pos_):
            d2 += (coord_comp - pos_comp)**2

        log_vec = d2 < tol**2
        if any(log_vec):
            labels[log_vec] = node.label
            n_missing += 1
            
        if n_missing >= 0:
            break   # Should be done, but check ensures that a label not 
                    # written multiple times
            
    if any(labels==0):
        for label, the_pos in zip(labels, pos):
            if label == 0:
                print('Could not find the position: ' + str(the_pos))
        ValueError('Could not find all node positions or multiple nodes found')
    
    return list(labels)
    
    
def get_variable_list(variables):
    """Get a list of nodal variables to use in the Abaqus function 
    xyDataListFromField. The variable list should contain specifications that
    are formatted as var_label + str(comp_num), where var_label is a string and
    comp_num is the component number, e.g. 'U1' (var_label='U', var_num=1) 
    or 'UR2' (var_label='UR', var_num=2)
    
    :param variables: List of variables to get the variable list for
    :type variables: list[ str ]
    
    :returns: A list of variable specification, each item has the format
              (<var_label>, NODAL, ((COMPONENT, <comp_spec>),)
    :rtype: list[ tuple( str, CONST, tuple( tuple( CONST, str ) ) ) ]
    
    """
    
    def extraction_ok(the_variable, the_label, the_num):
        len_ok = len(the_variable) == len(the_label) + len(the_num)
        start_ok = the_variable.startswith(the_label)
        end_ok = the_variable.endswith(the_num)
        
        all_checks = [len_ok, start_ok, end_ok]
        all_ok = all(all_checks)
        
        if not all_ok:
            print('Extraction not ok, booleans:')
            print(all_checks)
        
        return all_ok
    
    var_list = []
    for variable in variables:
        var_label = re.search('\D+', variable).group()
        var_num = re.search('\d+', variable).group()
        
        if not extraction_ok(variable, var_label, var_num):
            raise ValueError('Could not extract variable from expression "' 
                             + variable + '". Got var_label = "' + var_label 
                             + '", and var_num = "' + var_num + '".')
                             
        var_list.append((var_label, NODAL, ((COMPONENT, variable),),))
    
    return var_list


def set_active_frames(odb, steps, incr):
    """ Set the active frames to the given steps and increments
    
    :param odb: The odb object to set active frames for
    :type odb: Odb object (Abaqus)
    
    :param steps: List of step numbers to set active
    :type steps: list[ int ]
    
    :param incr: List of increments from which to extract results. 
                 ['0:-1'] implies all increments. 
                 Note that python negative numbering can be used, 
                 such that -1 implies last increment. Opposed to 
                 python lists, the last given index is included.
    :type incr: list[ int or str ]
    
    :returns: lists of step numbers and increments that are set to active. 
              The length is equal to the number of active frames.
    :rtype: (list, list)
    """
    
    
    
    all_step_names = odb.steps.keys()
    active_step_names = [all_step_names[step] for step in steps]
    odb_data = session.odbData[odb.name]
    odb_data.setValues(activeFrames=[ (step_name, incr) 
                                     for step_name in active_step_names])
    step_data = []
    incr_data = []
    for step, step_spec in enumerate(odb_data.activeFrames):
        if isinstance(step_spec[1][0], str):
            # It is only string if all increments are included
            increments = range(len(odb_data.steps[step_spec[0]].frames))
        else:
            # Otherwise, a list of increments is given.
            increments = step_spec[1]
            
        for the_incr in increments:
            step_data.append(step)
            incr_data.append(the_incr)
    
    return step_data, incr_data
    
    
def debug_print(*args):
    msg_str = ''
    for arg in args:
        msg_str += str(arg) + ' '
    msg_str = msg_str[:-1]
    print(*args)
    sys.__stdout__.write(msg_str + '\n')
