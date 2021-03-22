# abaqus_odb
Utilities for accessing results in Abaqus odb files

# Notes about visualizing results in Abaqus.
Many of the built-in colormaps are not so good for visualization. A better alternative is proposed at http://www.kennethmoreland.com/color-maps/.
This colormap can be made available in Abaqus with the following python command:
`session.Spectrum(name="ColorMap", colors =('#B40426', '#DCDCDC', '#3A4CC0', ))`
