Python-based Slicer from STL to PNG Images
==========

This code is in production and is not complete! 

Currently, it produces a folder of PNG images from an STL file. Each PNG has filled in contours signifying object geometry at that slice. There is currently no visualization or gui, but am working on this currently. All orientation settings must be completed beforehand (but I am working on adding such functionality). This code base is extended from a different [project](https://github.com/matthewelse/pySlice).

Please read through the available command line options for scaling and setting z-height resolution (in mm). Changing the size of the print bed (in mm) and size of the image (in pixels) is possible, but is currently not working correctly (under construnction).

### Getting started

This code was written in Python 3.6 while installing the various packages via pip. You should be able to do the same via ```pip install [name_of_modele]```.


### Original Text:
A 3D model Slicing algorithm, written by Matthew Else in Python. Written, firstly because I need a nice algorithm in Python, and secondly because alternative solutions are all licensed under AGPL, and I need a solution for myself that can be used commercially without releasing source code for everything else.

The code currently only supports the following file formats:
* STL

I plan to possibly support other formats such as OBJ, for example however at the moment STL is fine. It currently cannot generate G-Code, and all it will take is a for loop to generate all of the layers.

If you test pySlice successfully or unsuccessfully, let me know in the issues section of Github.

pySlice.py is licensed under the MIT license.
