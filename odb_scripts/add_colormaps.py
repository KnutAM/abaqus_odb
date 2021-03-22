import visualization


def add_colormap(file, name=None):
    """ Add a colormap from a csv file. A set of those files are
    available in the data/colormaps folder.
    
    :param file: path to the .csv file containing a colormap. First line
                 is ignored, the remaining line should contain 4 comma
                 separated values, of which the 3 last should be byte
                 RGB values (0-255).
    :type file: str, path-like object
    
    :param name: The name of the colormap to be saved. If None, the 
                 name of the file (excluding path and suffix) is used.
    :type name: str
    
    :returns: None
    
    """
    
    if name is None:
        name = file.split('/')[-1].split('\\')[-1].split('.')[0]
    
    colors = []
    with open(file, 'r') as fid:
        fid.readline()  # Ignore first line
        for line in fid:
            colors.append([int(c) for c in line.split(',')[1:]])
    
    colors_hex = []
    for color in colors:
        color_hex = '#'
        for rgb_val in color:
            color_hex += hex(rgb_val)[2:]
        colors_hex.append(color_hex)
    
    session.Spectrum(name=name, colors=colors_hex)

