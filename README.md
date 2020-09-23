Python-based Slicer from STL to PNG Images
==========

This code is in production and is not complete. While running, it produces png images from an STL file. There is currently no visualization or gui. All scalining and orientation setting must be completed beforehand. This code base is extended from a different [project] (https://github.com/matthewelse/pySlice).


Original Text:
A 3D model Slicing algorithm, written by Matthew Else in Python. Written, firstly because I need a nice algorithm in Python, and secondly because alternative solutions are all licensed under AGPL, and I need a solution for myself that can be used commercially without releasing source code for everything else.

The code currently only supports the following file formats:
* STL

I plan to possibly support other formats such as OBJ, for example however at the moment STL is fine. It currently cannot generate G-Code, and all it will take is a for loop to generate all of the layers.

If you test pySlice successfully or unsuccessfully, let me know in the issues section of Github.

pySlice.py is licensed under the MIT license.
