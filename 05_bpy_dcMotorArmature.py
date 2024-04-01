
#
# author: Nadeem Elahi
# nadeem.elahi@gmail.com
# nad@3deem.com
# license: gpl v3
# 

#
# Automated Rotated Geometry Generation
#

import bpy
from math import sin
from math import cos
from math import atan 
from math import radians
from math import sqrt


def removeMeshes ( ) :
	for obj in bpy.data.objects:
		if obj.type == 'MESH':
			bpy.data.objects.remove(obj)

removeMeshes ( )


def makeMesh ( name , verts , faces ) : 

	# Create Mesh Datablock 
	mesh = bpy.data.meshes.new ( name ) 
	mesh.from_pydata ( verts, [], faces ) 
	# mesh from vertices, edges and faces. 
	# if you pass a faces list you can skip edges

	# Create Object and link to scene 
	obj = bpy.data.objects.new(name, mesh) 
	bpy.context.scene.collection.objects.link ( obj ) 


#
#
# circle section
#
#

def makeAnglesList( step , divisions ) :

	#step = 5 # degrees
	#divisons = 3 # step degrees how many times, going +ve and -ve

	positiveAngles = []
	negativeAngles = []
	angles = []

	for idx in range ( divisions + 1 ):
		positiveAngles.append ( step * idx )
	#print ( positiveAngles )

	# 5*(3-0) , 5*(3-1) , 5*(3-2) = [ 15 , 10 , 5 ] 
	for idx in range ( divisions ):
		negativeAngles.append ( -1 * step * ( divisions - idx ) )
	#print ( negativeAngles )

	angles = negativeAngles + positiveAngles
	# [ -15 , -10 , -5 , 0 , 5 , 10 , 15 ]
	#print ( angles )

	return angles


def vertsInnerOuter ( rot ) :
	
	verts = []

	def vertsByAngleAndRadius ( rad , ang , rot ) :

		xloc = rad * cos ( ang + rot ) 
		yloc = rad * sin ( ang + rot )  

		verts.append( [ xloc , yloc , 0 ] )

		return verts


	for idx in range( vertsCnt ):
		vertsByAngleAndRadius ( inner , angles [ idx ] , rot )
		vertsByAngleAndRadius ( outer , angles [ idx ] , rot )

	return verts 


def appendFaces ( offset , cnt ) :

	last = cnt * 2 - 2
	idx = 0
	faces = []

	while ( idx < last ) :
		index = idx + offset * vertsCnt * 2
		faces.append ( [ 
			index , 
			index + 1 , 
			index + 3 , 
			index + 2 
			] )
		idx += 2
	
	return faces


#
#
# END circle section
#
#



#
#
# rectangle 
#
#



def vertsByRot ( rot ) :

	verts = []

	def verts2d_at_3dz0_rot ( xloc , yloc , rot ) :

		rad = sqrt ( xloc * xloc + yloc * yloc )
		ang = atan ( yloc / xloc )

		verts.append ( [ 
			rad * cos ( ang + rot ) , 
			rad * sin ( ang + rot ) , 
			0 
			] )


	verts2d_at_3dz0_rot ( xlft , ybtm , rot ) # bottom left
	verts2d_at_3dz0_rot ( xrgt , ybtm , rot ) # bottom right

	verts2d_at_3dz0_rot ( xrgt , ytop , rot ) # top right
	verts2d_at_3dz0_rot ( xlft , ytop , rot ) # top left

	return verts


#
#
# END rectangle 
#
#



#
#
# Settings circle section
#
#

# Settings circle section

coilCnt = 8 # 360 / 3 = 120 degrees apart

inner = 17  # radius inner
outer = 20 # radius outer

step = 5 # degrees
divisions = 3 # step degrees how many times, going +ve and -ve


# Settings rectangle  

xlft = 5 # shaft radius - flat edged shaft
thickness = 2


#
# RUN mushroom cap
#

nameCap = 'armatureMushroomCap' 

angles = makeAnglesList( step , divisions )

vertsCnt = len ( angles ) #vertsCnt = 2 * divisions + 1  

# convert to radians
for idx in range ( vertsCnt ) :
	angles [ idx ] = radians ( angles [ idx ] )

vertsCap = []
facesCap = []

for idx in range ( coilCnt ) :
	rot = radians ( idx * 360 / coilCnt )
	verts = vertsInnerOuter ( rot )
	faces = appendFaces ( idx , vertsCnt )
	vertsCap += verts 
	facesCap += faces

#
# RUN stem 
#

nameStem = 'armatureStem' 

xrgt = inner
ytop =  thickness / 2
ybtm = -ytop

vertsStem = []
facesStem = []

for idx in range ( coilCnt ):
	rot = radians ( idx * 360 / coilCnt )
	verts = vertsByRot ( rot );
	vertsStem += verts

	offset = idx * 4 # 4 verts per rectangle/face
	facesStem.append( [ offset , offset + 1 , offset + 2 , offset + 3 ] )


makeMesh ( nameCap , vertsCap , facesCap )
makeMesh ( nameStem , vertsStem , facesStem )


# 
# Next Steps
#
# FIRST:
#
# There are two meshes there, the shaft or stem
# and the armature end pieces or mushroom cap.
# We will want to union-ize the two (Boolean).
# There is an overlap which we will want to rememdy.
#
# SECOND: Overlap Remedy
#
# Select the armatureStem mesh - the rectangles
#   - add Modifier Boolean - Difference
#       - select object - armatureMushroomCap mesh 
# 
# The boolean makes the cut fine 
# BUT it does not seem to delete the interecting vertices
# Select one of them, then go to the Select menu
# Select -> Select Similar ( SHIFT + G )
#                -> Amount of Adjacent Adjacent Faces
#   - this will skip the other nearby vertices
#     but also selects the two verts each vertices
#     at the base of the arm
#   - you can easily desect those with a scroll and click
#     using Circle Select [ C ]
#
# THIRD: Boolean Union 
#
# Now that we have a single mesh we will want to extrude.
# We have a flat plate.  Extrude to your desired thickness.
# 
# FOURTH: Beveling edges
# Subsurf will look funny
# and marking seems will be tedious
# I was able to select the end faces
# of the end pieces/mushroom caps
# in face select mode by 
# Select Similar ( SHIFT + G )
# Select By Area
# I was able to select the rest of the edges using
# Select By Length
#
# FIFTH: Center Ring
# I added a cylinder scaled long
# Again, I wanted to cutout the intersecting area
# add Modifier Boolean - Difference
#   - object cylinder
#   - problem, some of the arms disappeared
#   - check [ x ] Self Intersection - fixes above problem
# Again add Modifier - Union
#
# SIXTH: Shaft
# Add Mesh Cylinder - scale long
# 
# LAST: Array
# DC Motor Armatures are made up of an number of plates
# so to maximize the magnitization capability.
# add Modifier - Array
#
# FINISH
# Lamps
# Floor
# Materials
#
#

