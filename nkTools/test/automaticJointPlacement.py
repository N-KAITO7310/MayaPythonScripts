
#Title: automaticJointPlacement.py
#Author: Noah Schnapp
#LinkedIn: https://www.linkedin.com/in/wnschnapp/
#Youtube: http://www.youtube.com/WilliamNoahSchnapp

####################
####################
#...Import Commands
####################
####################

import maya.cmds as cmds
import maya.mel as mel
import math, os, json

####################
####################

#...SCRIPT EDITOR USE
dirpath = r'C:\Users\kn_un\Documents\maya\scripts\nkTools\test'

# dirpath = r'C:\Users\kn_un\Documents\maya\scripts\nkTools\test'
# import sys, imp 
# sys.path.insert(0, dirpath) 
# import automaticJointPlacement 
# imp.reload(automaticJointPlacement)
# automaticJointPlacement.run_dev()

####################
####################

def run_dev():
    #...args
    # mode = "body";

    # #...name file
    # filepath = "%s/00_example_%s.mb"%(dirpath, mode);

    # #...open scene
    # cmds.file(filepath, o=True, f=True);

    # #...setLayout
    # # mel.eval('setNamedPanelLayout "layout_user";');

    # #...rename scene for testing
    # cmds.file(rename="untitled");

    #...openUI

    #...dev code
    cSkeletor = Skeletor();
    # cSkeletor.sample_one(sample_Array=cmds.ls(sl=True, fl=True)[:-1], node=cmds.ls(sl=True)[-1], auto=False);
    
    cSkeletor.sample_all("base_body", cmds.ls(sl=True));
    print(cSkeletor.data)

    return True

def dev_rotatePlanar():
    #...example rotate_planar

    return True

def openUI(dirpath=None):

    return True

class SkeletorUI(object):

    def __init__(self):

        #...classes

        #...vars

        pass

    def create_mainWindow(self, dirpath=None):

        #...set dirpath

        # Make a new window

        #...title

        #...dirpath

        #...buttons

        return True

    #...UI
    def btnCmd_setDirpath(self, *args, **kwargs):
        #...get dirpath

        #...update textfield

        return True

    def btnCmd_recordAll(self, *args, **kwargs):
        #...parse_selection

        #...update vars

        #...if confirm

        #...Overwrite

        #...record_all

        return True

    def btnCmd_recordOne(self, *args, **kwargs):
        #...record_one

        return True

    def btnCmd_mirrorRecords(self, *args, **kwargs):
        #...mirror_records

        return True

    def btnCmd_updatePositionRecords(self, *args, **kwargs):
        #...update_positionRecords

        return True

    def btnCmd_selectNodeSamples(self, *args, **kwargs):
        #...select_nodeSamples

        return True

    def btnCmd_selectNodesInAutoMode(self, *args, **kwargs):
        #...select autoNodes

        return True

    def btnCmd_reconformNodesToSelectedMesh(self, *args, **kwargs):
        #...reconform_all

        return True

class Skeletor(object):

    def __init__(self):

        self.mesh = None;
        self.data = {};
        self.sampleCount = 60;

    #...record
    def record_all(self, sel_Array=None):
        #...parse_selection

        #...load_data

        #...analyze mesh

        #...save_data

        #...debug

        return True

    def record_one(self, sel_Array=None):
        #...parse_selection

        #...load_data

        #...analyze mesh

        #...save_data

        #...debug

        return True

    def mirror_records(self, sel_Array=None):
        #...parse_selection

        #...debug

        #...load_data

        #...mirror_all

        #...save_data

        #...debug

        return True

    def update_positionRecords(self, sel_Array=None):
        #...parse_selection

        #...debug

        #...load_data

        #...updateRecords

        #...save_data

        #...debug

        return True

    def select_nodeSamples(self, sel_Array=None):
        #...parse_selection

        #...debug

        #...load_data

        #...select sample

        #...construct meshVtx_Array

        #...select components

        return True

    def select_nodesInAutoMode(self, sel_Array=None):
        #...parse_selection

        #...debug

        #...load_data

        #...select auto_Array

        #...select

        return True

    def reconform_all(self, sel_Array=None):
        #...parse_selection

        #...debug

        #...filepath exists?

        #...load_data

        #...place_all

        #...debug

        return True

    #...analyze
    def get_vtxPositions(self, mesh):
        posFlatten_Array = cmds.xform("%s.vtx[*]"%mesh, q=True, ws=True, t=True);
        self.vtxPosition_Array = zip(posFlatten_Array[0::3], posFlatten_Array[1::3], posFlatten_Array[2::3]);

        return self.vtxPosition_Array

    def get_sampleArray(self, mesh, node, sampleCount = 30):
        #...need to reanalyze mesh?
        if self.mesh != mesh:
            self.vtxPosition_Array = self.get_vtxPositions(mesh);
        if self.vtxPosition_Array == []:
            self.vtxPosition_Array = self.get_vtxPositions(mesh);

        #...get node position
        xform_node = cmds.xform(node, q=True, t=True, ws=True);

        #...get distance
        distance_Array = [[distance(xform_vtx, xform_node), i] for i, xform_vtx in enumerate(self.vtxPosition_Array)];

        #...sort array
        distance_Array.sort();

        #...construct meshVtx_Array
        meshVtx_Array = ["%s.vtx[%s]"%(mesh, d[1]) for d in distance_Array[:sampleCount]];

        return meshVtx_Array

    def parse_selection(self, sel_Array=None):

        #...get sel_Array

        #...get sample_Array from selection

        #...get node/mesh from sel_Array

        return node_Array, mesh, sample_Array

    #...sample mesh and node relationship
    def sample_all(self, mesh, node_Array):
        #...add node position entries
        [self.sample_one(self.get_sampleArray(mesh, node, sampleCount=self.sampleCount), node, auto=True) for node in node_Array];

        return True

    def sample_one(self, sample_Array=None, node=None, auto=False):
        #...use existing sample_Array?
        if sample_Array == None:
            sample_Array = ["%s.vtx[%s]"%(self.mesh, d) for d in self.data[node][0]];
        
        #...check for node
        if node == None:
            return False;

        #...use existing auto setting?
        if auto == None:
            auto = self.data[node][3];

        #...get position of centroid of sel_Array
        pos_centroid = get_centroid(sample_Array);

        #...get position of node
        pos_node = cmds.xform(node, q=True, t=True, ws=True);

        #...get vector of centroid to node
        vector = get_vector(pos_centroid, pos_node);

        #...convert sample_Array to number_Array only 
        vertID_Array = [int((i.split(".vtx[")[1].split("]")[0])) for i in cmds.ls(sample_Array, fl=True)];

        #...get scaleFactor
        scaleFactor = get_scaleFactor(sample_Array);

        #...store in data ram
        self.data[node] = [vertID_Array, vector, scaleFactor, auto]
        return True

    def mirror_all(self, mesh, node_Array):
        #...mirror list

        return True

    def mirror_one(self, mesh, node):

        #...get data info

        #...create sample_Array

        #...mirror

        #...remove l side if l in nodeMirror:

        #...get mirror node, l => r, m => m

        #...sample one

        return True

    #...reconform nodes to new mesh
    def place_all(self, mesh, node_Array = None):
        #...node_Array == None, reconform nodes in self.data

        #...store parent_Array

        #...reparent hiearchy

        return True

    def place_one(self, mesh, node):
        #...get data info

        #...create sample_Array

        #...get position of centroid of sel_Array

        #...get new scaleFactor

        #...get new position from centroid + vector

        #...get new position from centroid + vector

        #...move node to reconform position

        return True

    #...save/load
    def save_data(self, mesh, dirpath=None):
        #...get dirpath

        #...get filepath

        #...save data

        #...debug

        return True

    def load_data(self, mesh, dirpath=None):
        #...define mesh

        #...get dirpath

        #...get filepath

        #...file exist?

        #...load data

        #...debug

        return self.data

#####################################################################
#####################################################################

#############################################
#...other funcs
#############################################
def unparent_hierarchy(node_Array):

        #...get child/parent

        return hierarchy_Array

def parent_hierarchy(hierarchy_Array):
        #...parent

        return True

def get_mirrorVerts(meshVtx_Array=None, select=False):
    #...get sel_Array

    #...turn on sym sel

    #...get mirror

    #...remove duplicates

    #...turn off sym sel

    #...clear selection

    #...select mirror_Array

    return mirror_Array

#############################################
#...math funcs
#############################################
def get_scaleFactor(node_Array):
    bb = cmds.exactWorldBoundingBox(node_Array, ignoreInvisible=True);
    scaleFactor = [0, 0, 0];
    scaleFactor[0] = abs(bb[3] - bb[0]);
    scaleFactor[1] = abs(bb[4] - bb[1]);
    scaleFactor[2] = abs(bb[5] - bb[2]);

    return scaleFactor

def get_vector(pt0 = None, pt1 = None):
    dx = pt1[0] - pt0[0];
    dy = pt1[1] - pt0[1];
    dz = pt1[2] - pt0[2];

    return [dx, dy, dz]

def get_centroid(node_Array):
#...get centroid of nodes
    posX = 0;
    posY = 0;
    posZ = 0;
    
    for node in node_Array:
        position = cmds.xform(node, query=True, translation=True, worldSpace=True);
        posX = posX + position[0];
        posY = posY + position[1];
        posZ = posZ + position[2];
        
    nodeCount = len(node_Array);
    centroid = [posX/nodeCount, posY/nodeCount, posZ/nodeCount];

    return centroid

def distance(pt0 = None, pt1 = None):
    dx = pt1[0] - pt0[0];
    dy = pt1[1] - pt0[1];
    dz = pt1[2] - pt0[2];
    distance = float(math.sqrt(dx*dx + dy*dy + dz*dz));

    return distance

def crossProduct(a, b):

    return cp

def normalize_Array(val_Array):

    return val_Array

def create_matrix(vectAx = None, vectAy = None, vectAz = None, shear_Array = None, position = None):

    return matrix

def rotate_planar(node_Array = None):
        #...Get Args from Selection

        #...store parent_Array

        #...get positions

        #...get vectors and matricies

        #...orient nodes

        #...reparent hiearchy

        return True


