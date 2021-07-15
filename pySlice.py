#!/usr/bin/python

"""
The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from Model3D import STLModel, Vector3, Normal
from svgwrite import Drawing, rgb
import sys, cairosvg, IPython, time
from PIL import Image, ImageDraw
import numpy as np
from sklearn.neighbors import KDTree
import IPython

#determine how much space a pixel takes up physically
def calculateMultiplier(pixels, mm):
	return pixels/mm

def mmToinch(num):
	return num/25.4

def inchTomm(num):
	return num*25.4

def convertToPixels(vSet, width_multiplier, height_multiplier, object_center, center_image):
	mmSet = inchTomm(np.asarray(vSet))
	mmSet[:,0]*=width_multiplier #now in pixels
	mmSet[:,1]*=height_multiplier #now in pixels

	#center the object
	mmSet[:,0]+=(center_image[0])
	mmSet[:,0]-=(inchTomm(object_center[0])*width_multiplier)
	mmSet[:,1]+=(center_image[1])
	mmSet[:,1]-=(inchTomm(object_center[1])*height_multiplier)

	m = list(mmSet)
	for i in range(len(mmSet)):
		m[i]= tuple(m[i])
	return m


def slice_file(resolution, f=None, scale_model = None,width_px = None, height_px = None, width_printer = None, height_printer = None):

	print("Status: Loading File.")

	width_multiplier = calculateMultiplier(width_px, width_printer) #converstion from mm to pixels
	height_multiplier = calculateMultiplier(height_px, height_printer) #conversion from mm to pixels

	model = STLModel(f)
	stats = model.stats()


	#Note these are in inches not mm
	sub_vertex = Vector3(stats['extents']['x']['lower'], stats['extents']['y']['lower'], stats['extents']['z']['lower'])

	center_image= [int(width_px/2), int(height_px/2)] #pixels

	model.xmin = model.xmax = None
	model.ymin = model.ymax = None
	model.zmin = model.zmax = None

	print("Status: Scaling Triangles.")

	for triangle in model.triangles:
		triangle.vertices[0] -= sub_vertex
		triangle.vertices[1] -= sub_vertex
		triangle.vertices[2] -= sub_vertex

		# The lines above have no effect on the normal.

		triangle.vertices[0] = (triangle.vertices[0] * scale_model) #in inches
		triangle.vertices[1] = (triangle.vertices[1] * scale_model) #in inches
		triangle.vertices[2] = (triangle.vertices[2] * scale_model) #in inches

		# Recalculate the triangle normal

		u = model.triangles[0].vertices[1] - model.triangles[0].vertices[0]
		v = model.triangles[0].vertices[2] - model.triangles[0].vertices[0]

		triangle.n = Normal((u.y * v.z)-(u.z*v.y), (u.z*v.x)-(u.x*v.z), (u.x*v.y)-(u.y*v.x))
		model.update_extents(triangle)

	print("Status: Calculating Slices")

	stats = model.stats()

	#This is after scaling the object
	sub_vertex = Vector3(stats['extents']['x']['lower'], stats['extents']['y']['lower'], stats['extents']['z']['lower'])
	sup_vertex = Vector3(stats['extents']['x']['upper'], stats['extents']['y']['upper'], stats['extents']['z']['upper'])
	obj_center_xyz = [(sup_vertex.x+sub_vertex.x)/2,(sup_vertex.y+sub_vertex.y)/2,(sup_vertex.z+sub_vertex.z)/2] #in inches

	slices = np.linspace(0.001, stats['extents']['z']['upper']-0.001, int(stats['extents']['z']['upper']/(mmToinch(resolution)))+1)

	tic = time.time()

	for slice in range(len(slices)):#1, int(stats['extents']['z']['upper']), int(interval)):
		dwg = Drawing('outputs/svg/'+str(slice)+'.svg', profile='full')
		pairs = model.slice_at_z(slices[slice])
		#for pair in pairs:
		#	dwg.add(dwg.line(pair[0], pair[1], stroke=rgb(0, 0, 0, "%")))
		#dwg.attribs['viewBox']= str(model.xmin)+" "+str(model.ymin)+" "+ str(model.xmax)+" "+str(model.ymax)
		#dwg.save()
		#cairosvg.svg2png(url = 'outputs/svg/'+str(targetz)+'.svg' , write_to='outputs/png/'+str(targetz)+'.png')


		#Now process vertices
		a = np.asarray(pairs)
		b = a.flatten()
		vert_array = b.reshape(int(b.shape[0]/2), 2) #this is now twice as long and just not four wide, it is now too wide
		tree = KDTree(vert_array, leaf_size = 3)
		current_index = 1
		vertices = []
		vertice_sets = []
		visited_vertices = [current_index]
		vertices.append(tuple(vert_array[current_index]))
		for i in range(int(vert_array.shape[0]/2)):
			to_query = np.reshape(vert_array[current_index], (1,2))
			dist, ind = tree.query(to_query, k =2)
			for id in list(ind[0]): #there should only ever be two
				if id != current_index:
					#if len(visited_vertices) >= vert_array.shape[0]/2:
					#	print 'GOT INTO HERE'
					#	break
					#if we have found a loop,
					if id in visited_vertices:
						vertices.append(tuple(vert_array[id]))
						vertice_sets.append(vertices)
						vertices = []
						for next_vert in range(vert_array.shape[0]):
							if next_vert not in visited_vertices:
								current_index = next_vert
					#Now that we have found the match, find the corresponding vertex, remember that they are in pairs of two
					elif id%2 ==1:
						current_index = id - 1
						break
					else:
						current_index = id + 1
						break
			visited_vertices.append(id)
			vertices.append(tuple(vert_array[current_index]))
			visited_vertices.append(current_index)

		#Draw the percentage done
		sys.stdout.write("\r%d%%" % int(slice/len(slices)*100))
		sys.stdout.flush()

		#Save the last one to the vertice set
		vertice_sets.append(vertices)
		img = Image.new('RGB', (height_px, width_px)) # Use RGB, these may be backwards TODO
		draw = ImageDraw.Draw(img)
		for i in range(len(vertice_sets)):
			if len(vertice_sets[i])>2:
				set = convertToPixels(vertice_sets[i], width_multiplier, height_multiplier, obj_center_xyz, center_image)
				draw.polygon(set, fill = (255, 255, 255))
		img.save('outputs/png_filled/'+str(slice)+'.png', 'PNG')

	print("Status: Finished Outputting Slices")
	print('Time: ', time.time()-tic)

if __name__ == '__main__':
	# Run as a command line program.
	import argparse
	parser = argparse.ArgumentParser(
						description='Takes a 3D Model, and slices it at regular intervals')
	parser.add_argument('file',
						metavar='FILE',
						help='File to be sliced',
						nargs='?',
						# default='models/cube.STL',
						default='models/yodabust.stl',
						type=argparse.FileType('rb'))
	parser.add_argument('-s', '--scale', type=float,
						default=0.05,
						help='Scale multiplier of the model')
	parser.add_argument('-r', '--resolution', type=float,
						default=3.,
						help='The Z-Axis resolution of the printer, in mms')
	parser.add_argument('-wi', '--width', type=int,
						default=2000,
						help='PNG image width')
	parser.add_argument('-he', '--height', type=int,
						default=2000,
						help='PNG image height')
	parser.add_argument('-heP', '--height_printer', type=int,
						default=200,
						help='actual height of the 3d printers bed size, in mms')
	parser.add_argument('-wiP', '--width_printer', type=int,
						default=200,
						help='actual width of the 3d printers bed size, in mms')

	args = parser.parse_args()
	slice_file(args.resolution, args.file, args.scale, args.width, args.height, args.width_printer, args.height_printer)
