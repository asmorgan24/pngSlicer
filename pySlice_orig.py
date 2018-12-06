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


def slice_file(f=None, resolution=0.1):
	print("Status: Loading File.")

	model = STLModel(f)
	scale = 10
	stats = model.stats()

	sub_vertex = Vector3(stats['extents']['x']['lower'], stats['extents']['y']['lower'], stats['extents']['z']['lower'])
	add_vertex = Vector3(0.5,0.5,0.5)

	model.xmin = model.xmax = None
	model.ymin = model.ymax = None
	model.zmin = model.zmax = None

	print("Status: Scaling Triangles.")

	for triangle in model.triangles:
		triangle.vertices[0] -= sub_vertex
		triangle.vertices[1] -= sub_vertex
		triangle.vertices[2] -= sub_vertex

		# The lines above have no effect on the normal.

		triangle.vertices[0] = (triangle.vertices[0] * scale) + add_vertex
		triangle.vertices[1] = (triangle.vertices[1] * scale) + add_vertex
		triangle.vertices[2] = (triangle.vertices[2] * scale) + add_vertex

		# Recalculate the triangle normal

		u = model.triangles[0].vertices[1] - model.triangles[0].vertices[0]
		v = model.triangles[0].vertices[2] - model.triangles[0].vertices[0]

		triangle.n = Normal((u.y * v.z)-(u.z*v.y), (u.z*v.x)-(u.x*v.z), (u.x*v.y)-(u.y*v.x))
		model.update_extents(triangle)

	print("Status: Calculating Slices")

	interval = scale * resolution
	stats = model.stats()
	print(stats)

	tic = time.time()

	for targetz in range(1, int(stats['extents']['z']['upper']), int(interval)):
		dwg = Drawing('outputs/svg/'+str(targetz)+'.svg', profile='full')
		pairs = model.slice_at_z(targetz)
		#for pair in pairs:
		#	dwg.add(dwg.line(pair[0], pair[1], stroke=rgb(0, 0, 0, "%")))
		#dwg.attribs['viewBox']= str(model.xmin)+" "+str(model.ymin)+" "+ str(model.xmax)+" "+str(model.ymax)
		#dwg.save()
		#cairosvg.svg2png(url = 'outputs/svg/'+str(targetz)+'.svg' , write_to='outputs/png/'+str(targetz)+'.png')


		#Now process vertices
		a = np.asarray(pairs)
		b = a.flatten()
		vert_array = b.reshape(b.shape[0]/2, 2) #this is now twice as long and just not four wide, it is now too wide
		tree = KDTree(vert_array, leaf_size = 3)
		current_index = 1
		vertices = []
		vertice_sets = []
		visited_vertices = [current_index]
		vertices.append(tuple(vert_array[current_index]))
		for i in range(vert_array.shape[0]/2):
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
			sys.stdout.write("\r%d%%" % int((float(targetz)/(float(len(range(1, int(stats['extents']['z']['upper']), int(interval))))))*100))
			sys.stdout.flush()

		#Save the last one to the vertice set
		vertice_sets.append(vertices)
		img = Image.new('RGB', (2000, 2000)) # Use RGB
		draw = ImageDraw.Draw(img)
		for i in range(len(vertice_sets)):
			if len(vertice_sets[i])>2:
				draw.polygon(vertice_sets[i], fill = (255, 0, 0))
		img.save('outputs/png_filled/'+str(targetz)+'.png', 'PNG')


	print("Status: Finished Outputting Slices")
	print 'Time: ', time.time() - tic

if __name__ == '__main__':
	# Run as a command line program.
	import argparse
	parser = argparse.ArgumentParser(
						description='Takes a 3D Model, and slices it at regular intervals')
	parser.add_argument('file',
						metavar='FILE',
						help='File to be sliced',
						nargs='?',
						default='models/yodabust.stl',
						type=argparse.FileType('rb'))
	parser.add_argument('-r', '--resolution', type=float,
						default=0.1,
						help='The Z-Axis resolution of the printer, in mms')

	args = parser.parse_args()
	slice_file(args.file, args.resolution)
