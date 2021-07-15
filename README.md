Python-based Slicer from STL to PNG Images
==========

This code works mostly as desired but is still under construction! 

Currently, it produces a folder of PNG images from an STL file. Each PNG has filled in contours signifying object geometry at that slice. There is currently no visualization or gui, but am working on this currently. All orientation settings must be completed beforehand (but I am working on adding such functionality). This code base is extended from a different [project](https://github.com/matthewelse/pySlice).

Please read through the available command line options for scaling and setting z-height resolution (in mm). Changing the size of the print bed (in mm) and size of the image (in pixels) is possible, but is currently not working correctly (under construnction).

### Getting started

This code was written in Python 3.6 while installing the various packages via pip. You should be able to do the same via ```pip install [name_of_module]```.
