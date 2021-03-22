def save_xy_ip_data(inst_name, elem_num, ip_num=1, quantity='S', 
                    components=['S11', 'S22', 'S12']):
    """ save xy data from integration point, created with standard name
    with xydata from ODB field output.
    
    :param inst_name: Name of the instance with the requested element
    :type inst_name: str
    
    :param elem_num: Element number (within the given instance)
    :type elem_num: int
    
    :param ip_num: The integration point to get data from
    :type ip_num: int
    
    :param quantity: The quantity that is requested, e.g. stress ('S')
    :type quantity: str
    
    :param components: List of components to extract data for
    :type components: list[ str ]
    
    """
    
    def get_data(component):
        xy_data_name = (quantity + ':' + component
                        + ' PI: ' + inst_name 
                        + ' E: ' + str(elem_num) 
                        + ' IP: ' + str(ip_num))
        return session.xyDataObjects[xy_data_name].data
        
    save_data = []
    data = get_data(components[0])
    save_data.append(zip(*data)[0]) # Add time
    for comp in components:
        data = get_data(comp)
        save_data.append(zip(*data)[1]) # Add data for component
        
    filename = (quantity + '_E' + str(elem_num) 
                + '_IP' + str(ip_num) + '.dat')
    
    np.savetxt(filename, np.transpose(save_data), fmt='%20.12e')
    
    with open(filename, 'r') as fid:
        save_str = fid.read()
    
    with open(filename, 'w') as fid:
        fid.write('# %+18s' % 'Time')
        for comp in components:
            fid.write('%+21s' % comp)
        fid.write('\n')
        fid.write(save_str)
    
def save_xy_node_data(inst_name, node_num, quantity='U', 
                      components=['U1', 'U2']):
    """ save xy data from node, created with standard name
    with xydata from ODB field output.
    
    :param inst_name: Name of the instance with the requested node
    :type inst_name: str
    
    :param node_num: Node number (within the given instance)
    :type node_num: int
    
    :param quantity: The quantity that is requested, e.g. displacement 
                     ('U')
    :type quantity: str
    
    :param components: List of components to extract data for
    :type components: list[ str ]
    
    """
    
    def get_data(component):
        xy_data_name = (quantity + ':' + component
                        + ' PI: ' + inst_name 
                        + ' N: ' + str(node_num))
        return session.xyDataObjects[xy_data_name].data
        
    save_data = []
    data = get_data(components[0])
    save_data.append(zip(*data)[0]) # Add time
    for comp in components:
        data = get_data(comp)
        save_data.append(zip(*data)[1]) # Add data for component
        
    filename = quantity + '_N' + str(node_num) + '.dat'
    
    np.savetxt(filename, np.transpose(save_data), fmt='%20.12e')
    
    with open(filename, 'r') as fid:
        save_str = fid.read()
    
    with open(filename, 'w') as fid:
        fid.write('# %+18s' % 'Time')
        for comp in components:
            fid.write('%+21s' % comp)
        fid.write('\n')
        fid.write(save_str)