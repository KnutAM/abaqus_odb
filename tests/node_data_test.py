import numpy as np

from odb_scripts import node_data


# Test 3d case
data_folder = 'data/'
odb_3d = session.openOdb(data_folder + 'test_3d.odb')
inst_name = 'TESTPART_3D-1'
var = ['U1', 'U2']
pos = [[60.0, 20.0, 30.0], [60.0, 20.0, 0.0]]
set = 'NODEEDGE'

data = node_data.get_multiple_positions(odb_3d, inst_name, pos, var[0], 
                                        step_numbers=[0,1], 
                                        increments=[0,1,-1])

# Check that time and data columns have equal length
assert(len(data['time']) == len(data[0]))

# Check that correct number of nodes found
assert(len(data['node']) == len(pos))

# Check correct values
node_u1_disp = 3.64039
assert(abs(data[0][-1] - node_u1_disp) < 1.e-5)

# Check data when getting from set
data = node_data.get_multiple_positions(odb_3d, inst_name, set, var[1], 
                                        step_numbers=[0,1], 
                                        increments=[0,1,-1])

ref_data = {'x': [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
            'uy': [0.0, -0.613598287106, -1.4601098299, -3.22972774506,
                   -5.13134479523, -7.53386449814, -9.82168292999]}
                   
sort_vec = np.argsort(data['node'][:,0])
x_values = data['node'][sort_vec, 0]
num_nodes = len(data['node'])
values = [data[sort_vec[i]][-1] for i in range(num_nodes)]

x_tol = 1.e-6
uy_tol = 1.e-5
for x, x_ref, uy, uy_ref in zip(x_values, ref_data['x'], values, ref_data['uy']):
    try:            
        assert(abs(x-x_ref) < x_tol)
        assert(abs(uy-uy_ref) < uy_tol)
    except AssertionError as ae:
        node_data.debug_print(x, x_ref, uy, uy_ref)
        raise ae
        

# Check getting multiple variables        
data = node_data.get_multiple_variables(odb_3d, inst_name, pos[0], var, 
                                        step_numbers=[0,1])
                      
# Check that requested variables are put in data                      
for vn in var:
    assert(vn in data)
    
# Check that a value is correctly extracted
node_u1_disp = 3.64039
assert(abs(data['U1'][-1] - node_u1_disp) < 1.e-5)
