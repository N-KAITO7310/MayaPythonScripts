# -*- coding:utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as omApi;
import maya.api.OpenMayaAnim as OpenMayaAnimAPI
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMaya as om;
import os

import numpy as np
import json

import time

####################################################################

dirpath = r'C:\Users\kn_un\Documents\maya\scripts\nkTools\tool_resource\skinClusterIO_tests'

####################################################################

"""

SCRIPT EDITOR USE
py3:
import sys
import imp
import importlib
dirpath = r'C:\\Users\kn_un\Documents\maya\scripts\nkTools\test\skinClusterIO_tests'
sys.path.insert(0, dirpath)
import nkTools.test.skinClusterIO as skinClusterIO;
importlib.reload(skinClusterIO)

mesh = cmds.ls(sl=True)[0];

cSkinClusterIO_json = skinClusterIO.SkinClusterIO_json();
cSkinClusterIO_json.save(mesh, dirpath)

cSkinClusterIO_json.load(mesh, dirpath)

"""

class SkinClusterIO(object):

    def __init__(self):

        #...class init
        self.cDataIO 			    = DataIO()

        #...vars
        self.name                   = ''
        self.type                  	= 'skinCluster'
        self.weightsNonZero_Array   = []
        self.weights_Array          = []
        self.infMap_Array 			= []
        self.vertSplit_Array        = []
        self.inf_Array              = []
        self.skinningMethod         = 1
        self.normalizeWeights       = 1
        self.geometry               = None
        self.blendWeights           = []
        self.vtxCount               = 0
        self.envelope        		= 1
        self.skinningMethod         = 1
        self.useComponents         	= 0
        self.normalizeWeights       = 1
        self.deformUserNormals      = 1

        pass

    def get_mesh_components_from_tag_expression(self, skinPy, tag="*"):
        geo_types = ["mesh", "nurbsSurface", "nurbsCurve"];
        for t in geo_types:
            obj = skinPy.listConnection(et=True, t=t);
            if obj:
                geo = obj[0].getShape().name();
                
        # Get attr out of shape
        attr_out = cmds.deformableShape(geo, localShapeOutAttr=True)[0];
        
        # Get the output geometry data as MObject
        sel = om.MSelectionList();
        sel.add(geo);
        dep = om.MObject();
        sel.getDependNode(0, dep);
        fn_dep = om.MFnDependencyNode(dep);
        plug = fn_dep.findPlug(attr_out, True);
        obj = plug.asMObject();
        # Use the MFnGeometryData class to query the components for a tag expression
        fn_geodata = om.MFnGeometryData(obj);
        # Component MObject
        components = fn_geodata.resolveComponentTagExpression(tag);
        dagPath = om.MDagPath.getAPathTo(dep);
        return dagPath, components;

    def get_data(self, skinCluster):
        
        # ...get PyNode skinCluster
        skinPy = pm.PyNode(skinCluster);
        
        #...get the MFnSkinCluster for skinCluster
        selList = om.MSelectionList();
        selList.add(skinCluster);
        clusterNode = om.MObject();
        selList.getDependNode(0, clusterNode);
        skinFn = OpenMayaAnim.MFnSkinCluster(clusterNode);

        # ...Pre Maya 2022 or new component tag expression
        try:
            #...get components
            fnSet = om.MFnSet(skinFn.deformerSet());
            members = om.MSelectionList();
            fnSet.getMembers(members, False);
            dagPath = om.MDagPath();
            components = om.MObject();
            members.getDagPath(0, dagPath, components);
        except:
            dagPath, components = self.get_mesh_components_from_tag_expression(skinPy);
            
        #...get mesh
        geometry = cmds.skinCluster(skinCluster, q=True, geometry=True)[0];

        #...get vtxID_Array
        vtxID_Array = list(range(cmds.ls("{}.vtx[*]".format(geometry, fl=True))));

        #...get skin
        selList = omApi.MSelectionList();
        selList.add(mel.eval("findRelatedSkinCluster {}".format(geometry)));
        skinPath = selList.getDependNode(0);

        #...get mesh
        selList = omApi.MSelectionList();
        selList.add(geometry);
        meshPath = selList.getDagPath(0);

        #...get vtxs
        fnSkinCluster = OpenMayaAnimAPI.MFnSkinCluster(skinPath);
        fnVtxComp = omApi.MFnSingleIndexedComponent();
        vtxComponents = fnVtxComp.create(omApi.MFn.kMeshVertComponent);
        fnVtxComp.addElements(vtxID_Array);

        #...get weights/infs
        dWeights, infCount = fnSkinCluster.getWeights(meshPath, vtxComponents);
        weights_Array = np.array(list(dWeights), dtype="float64");
        inf_Array = [dp.partialPathName() for dp in fnSkinCluster.influenceObjects()];

        #...convert to weightsNonZero_Array
        weightsNonZero_Array, infMap_Array, vertSplit_Array = self.compress_weightData(weights_Array, infCount);

        #...gatherBlendWeights
        blendWeights_mArray = om.MDoubleArray();
        skinFn.getBlendWeights(dagPath, components, blendWeights_mArray);

        #...set data to self vars
        self.name = skinCluster;
        self.weights_Array = np.array(weightsNonZero_Array);
        self.infMap_Array = np.array(infMap_Array);
        self.vertSplit_Array = np.array(vertSplit_Array);
        self.inf_Array = np.array(inf_Array);
        self.geometry = geometry;
        self.blendWeightsf = np.array(blendWeights_mArray);
        self.vtxCount = len(vertSplit_Array) - 1;

        #...get attrs
        self.envelope = cmds.getAttr(skinCluster + ".envelope");
        self.skinningMethod = cmds.getAttr(skinCluster + ".skinningMethod");
        self.useComponents = cmds.getAttr(skinCluster + ".useComponents");
        self.normalizeWeights = cmds.getAttr(skinCluster + ".normalizeWeights");
        self.deformUserNormals = cmds.getAttr(skinCluster + ".deformUserNormals");

        return True

    def set_data(self, skinCluster):

        # get the MFnSkinCluster for skinCluster
        selList = om.MSelectionList();
        selList.add(skinCluster);
        skinClusterMObject = om.MObject();
        selList.getDependNode(0, skinClusterMObject);
        skinFn = OpenMayaAnim.MFnSkinCluster(skinClusterMObject);

        # Get dagPath and member components of skinned shape
        fnSet = om.MFnSet(skinFn.deformerSet());
        members = om.MSelectionList();
        fnSet.getMembers(members, False);
        dagPath = om.MDagPath();
        components = om.MObject();
        members.getDagPath(0, dagPath, components);

        ###################################################

        #...set infs
        influencePaths = om.MDagPathArray();
        infCount = skinFn.influenceObjects(influencePaths);
        influences_Array = [influencePaths[i].partialPathName() for i in range(influencePaths.length())];

        #...change the order in set(i,i)
        influenceIndices = om.MIntArray(infCount);
        [influenceIndices.set(i, i) for i in range(infCount)]

        ###################################################

        #...construct mArrays from normal/numpy arrays
        infCount = len(influences_Array);
        weightCounter = 0;
        weights_Array = [];
        weights_mArray = om.MDoubleArray();
        
        length = len(self.vertSplit_Array);
        for vtxId, splitStart in enumerate(self.vertSplit_Array):
            if vtxId < length - 1:
                vertChunk_Array = [0]*infCount;
                splitEnd = self.vertSplit_Array[vtxId+1];

                #...unpack data and replace zeros with nonzero weight vals
                for i in range(splitStart, splitEnd):
                    infMap = self.infMap_Array[i];
                    val = self.weightsNonZero_Array[i];
                    vertChunk_Array[infMap] = val;

                #...append to raw data array
                for vert in vertChunk_Array:
                    weights_mArray.append(vert);
                    
        blendWeights_mArray = om.MDoubleArray();
        for i in self.blendWeights:
            blendWeights_mArray.append(i);

        ###################################################
        #...set data
        skinFn.setWeights(dagPath, components, influenceIndices, weights_mArray, False);
        skinFn.setBlendWeights(dagPath, components, blendWeights_mArray);

        ###################################################
        #...set attrs of skinCluster
        cmds.setAttr("{}.envelope".format(skinCluster), self.envelope);
        cmds.setAttr("{}.skinningMethod".format(skinCluster), self.skinningMethod);
        cmds.setAttr("{}.useComponents".format(skinCluster), self.useComponents);
        cmds.setAttr("{}.normalizeWeights".format(skinCluster), self.normalizeWeights);
        cmds.setAttr("{}.deformUserNormals".format(skinCluster), self.deformUserNormals);

        #...name
        cmds.rename(skinCluster, self.name);

        return True

    def save(self, node=None, dirpath=None):
		
        #...get selection
        if node == None:
            node = cmds.ls(sl=True);
            if node == None:
                print("ERROR: Select Something!");
                return False;
            else:
                node = node[0];

        #...get skinCluster
        skinCluster = mel.eval("findRelatedSkinCluster " + node);
        if not cmds.objExists(skinCluster):
            print("ERROR: Node has no skinCluster!");
            return False;

        #...get dirpath
        if dirpath == None:
            startDir = cmds.workspace(q=True, rootDirectory=True);
            dirpath = cmds.fileDialog2(caption="Save SkinWeights", dialogStyle=2, fileMode=3, startingDirectory=startDir, fileFilter="*.npy", okCaption="Select");

        #...get filepath
        skinCluster = "skinCluster_{}".format(node);
        filepath = "{}/{}.npy".format(dirpath, skinCluster);

        #...timeStart
        timeStart = time.time();

        #...get data
        self.get_data(skinCluster);

        #...timeEnd
        timeEnd = time.time();
        timeElapsed = timeEnd - timeStart;

        #...print time
        print("GetData Elapsed: {}".format(timeElapsed));

        #...construct data_array
        legend =            (   'legend',
								'weightsNonZero_Array', 
								'vertSplit_Array',
								'infMap_Array',

								'inf_Array',
								'geometry',
								'blendWeights', 
								'vtxCount',

								'name',
								'envelope',
								'skinningMethod',
								'useComponents',

								'normalizeWeights',
								'deformUserNormals',

								'type',
								)

        data =              [   legend,
								self.weightsNonZero_Array, 
								self.vertSplit_Array,
								self.infMap_Array,

								self.inf_Array,
								self.geometry,
								self.blendWeights, 
								self.vtxCount,

								self.name,
								self.envelope,
								self.skinningMethod,
								self.useComponents,

								self.normalizeWeights,
								self.deformUserNormals,

								self.type,
								]

        #...timeStart
        timeStart = time.time();

        #...write data 
        np.save(filepath, data);

        #...timeEnd
        timeEnd = time.time();
        timeElapsed = timeEnd - timeStart;

        #...print time
        print("SaveData Elapsed: {}".format(timeElapsed));

        return True	

    def load(self, node=None, dirpath=None):

        #...get selection
        if node == None:
            node = cmds.ls(sl=True);
            if node == None:
                print("ERROR: Select Something!");
                return False;
            else:
                node = node[0];

        #...get dirpath
        if dirpath == None:
            startDir = cmds.workspace(q=True, rootDirectory=True);
            dirpath = cmds.fileDialog2(caption="Load SkinWeights", dialogStyle=2, fileMode=1, startingDirectory=startDir, fileFilter="*.npy", okCaption="Select");

        #...get filepath
        skinCluster = "skinCluster_{}".format(node);
        filepath = "{}/{}.npy".format(dirpath, skinCluster);

        #...check if skinCluster exists
        if not os.path.exists(filepath):
            print("ERROR: SkinCluster for node '{}' not found on disk!".format(node));

        #...unbind current skinCluster
        skinCluster = mel.eval("findRelatedSkinCluster " + node);
        if cmds.objExists(skinCluster):
            mel.eval("skinCluster -e -ub " + skinCluster);

        #...timeStart
        timeStart = time.time();

        #...read data
        data = np.load(filepath);

        #...timeEnd
        timeEnd = time.time();
        timeElapsed = timeEnd - timeStart;

        #...print time
        print("ReadData Elapsed: {}".format(timeElapsed));

        #...get item data from numpy array
        self.legend_Array = self.cDataIO.get_legendArrayFromData(data)
        self.weightsNonZero_Array = self.cDataIO.get_dataItem(data, 'weightsNonZero_Array', self.legend_Array)
        self.infMap_Array = self.cDataIO.get_dataItem(data, 'infMap_Array', self.legend_Array)
        self.vertSplit_Array = self.cDataIO.get_dataItem(data, 'vertSplit_Array', self.legend_Array)
        self.inf_Array = self.cDataIO.get_dataItem(data, 'inf_Array', self.legend_Array)
        self.blendWeights = self.cDataIO.get_dataItem(data, 'blendWeights', self.legend_Array)
        self.vtxCount = self.cDataIO.get_dataItem(data, 'vtxCount', self.legend_Array)
        self.geometry = self.cDataIO.get_dataItem(data, 'geometry', self.legend_Array)
        self.name = self.cDataIO.get_dataItem(data, 'name', self.legend_Array)
        self.envelope = self.cDataIO.get_dataItem(data, 'envelope', self.legend_Array)
        self.skinningMethod = self.cDataIO.get_dataItem(data, 'skinningMethod', self.legend_Array)
        self.useComponents = self.cDataIO.get_dataItem(data, 'useComponents', self.legend_Array)
        self.normalizeWeights = self.cDataIO.get_dataItem(data, 'normalizeWeights', self.legend_Array)
        self.deformUserNormals = self.cDataIO.get_dataItem(data, 'deformUserNormals', self.legend_Array)

        #...bind skin
        for inf in self.inf_Array:
            if not cmds.objExists(inf):
                cmds.select(cl=True);
                cmds.joint(n=inf);
        skinCluster = "skinCluster_{}".format(node);
        skinCluster = cmds.skinCluster(self.inf_Array, node, n=skinCluster, tsb=True)[0];

        #...timeStart
        timeStart = time.time();

        #...set data
        self.set_data(skinCluster);

        #...timeEnd
        timeEnd = time.time();
        timeElapsed = timeEnd - timeStart();

        #...print time
        print("SetData Elapsed: {}".format(timeElapsed));

        return True	

	###################################
    def compress_weightData(self, weights_Array, infCount):

		#...convert to weightsNonZero_Array
        weightsNonZero_Array = []
        infCounter = 0
        infMap_Chunk = []
        infMap_ChunkCount = 0
        vertSplit_Array = [infMap_ChunkCount]
        infMap_Array = []
        
        for w in weights_Array:
            if w != 0.0:
                weightsNonZero_Array.append(w);
                infMap_Chunk.append(infCounter)

			#...update inf counter
            infCounter += 1;
            if infCounter == infCount:
                infCounter = 0;
				
				#...update vertSplit_Array
                infMap_Array.extend(infMap_Chunk);
                infMap_ChunkCount = len(infMap_Chunk) + infMap_ChunkCount;
                vertSplit_Array.append(infMap_ChunkCount);
                infMap_Chunk = [];

        return weightsNonZero_Array, infMap_Array, vertSplit_Array

class SkinClusterIO_json(object):

    def __init__(self):

        pass

    def save(self, node=None, dirpath=None):
        #...get selection
        if node == None:
            node = cmds.ls(sl=True);
            if node == None:
                print("ERROR: Select Something!");
                return False;
            else:
                node = node[0];

		#...get skinCluster
        skinCluster = mel.eval("findRelatedSkinCluster " + node);
        if not cmds.objExists(skinCluster):
            print("ERROR: Node has no skinCluster!");
            return False;

		#...get dirpath
        if dirpath == None:
            startDir = cmds.workspace(q=True, rootDirectory=True);
            dirpath = cmds.fileDialog2(caption="Save Skinweights", dialogStyle=2, fileMode=3, startingDirectory=startDir, fileFilter='*.json', okCaption = "Select");

		#...get filepath
        filepath = "{}\{}.json".format(dirpath, "skinCluster_{}".format(node));

		#...timeStart
        timeStart = time.time();

		#...get data
        data = {};
        shape = cmds.listRelatives(node, c=True)[0];
        vtx_Array = ["{}.vtx[{}]".format(shape, x) for x in cmds.getAttr(shape + ".vrts", multiIndices=True)];
        for vtx in vtx_Array:
            inf_Array = cmds.skinPercent(skinCluster, vtx, transform=None, q=True);
            weights = cmds.skinPercent(skinCluster, vtx, q=True, v=True);
            data[vtx] = list(zip(inf_Array, weights));

		#...timeEnd
        timeEnd = time.time();
        timeElapsed = timeEnd - timeStart;

		#...print time
        print("GetData Elapsed: {}".format(timeElapsed));

		#...timeStart
        timeStart = time.time();

        #...write data
        with open(filepath, 'w', encoding="utf-8") as fh:
            json.dump(data, fh, indent=4, sort_keys=True)

		#...timeEnd
        timeEnd = time.time();
        timeElapsed = timeEnd - timeStart;

		#...print time
        print("SaveData Elapsed: {}".format(timeElapsed));

        return True

    def load(self, node=None, dirpath=None):
		
		#...get selection
        if node == None:
            node = cmds.ls(sl=True);
            if node == None:
                print("ERROR: Select Something!");
                return False;
            else:
                node = node[0];

		#...get dirpath
        if dirpath == None:
            startDir = cmds.workspace(q=True, rootDirectory=True);
            dirpath = cmds.fileDialog2(caption="Load SkinWeights", dialogStyle=2, fileMode=1, startingDirectory=startDir, fileFilter="*.json", okCaption="Select");
            
		#...get filepath
        skinCluster = "skinCluster_{}".format(node);
        filepath = "{}/{}.json".format(dirpath, skinCluster);

		#...check if skinCluster exists
        if not os.path.exists(filepath):
            print("ERROR: SkinCluster for node '{}' not found on disk!").format(node);
            return False;

		#...unbind current skinCluster
        skinCluster = mel.eval("findRelatedSkinCluster " + node);
        print(skinCluster)
        if cmds.objExists(skinCluster):
            mel.eval("skinCluster -e -ub " + skinCluster);

		#...timeStart
        timeStart = time.time();

		#...load
        fh = open(filepath, "r");
        data = json.load(fh);
        fh.close();

		#...timeEnd
        timeEnd = time.time();
        timeElapsed  = timeEnd - timeStart;

		#...print time
        print("ReadData Elapsed: {}".format(timeElapsed));
        
		#...bind skin
        for vtx, weights in data.items():
            inf_Array = [inf[0] for inf in weights];
            break;
        # ...create the joint if it doesnt exist
        for inf in inf_Array:
            if not cmds.objExists(inf):
                cmds.select(cl=True);
                cmds.joint(n=inf);
        skinCluster = "skinCluster_{}".format(node);
        skinCluster = cmds.skinCluster(inf_Array, node, n=skinCluster, tsb=True)[0];

		#...timeStart
        timeStart = time.time();

		#...set data
        [cmds.skinPercent(skinCluster, vtx, tv=data[vtx], zri=True) for vtx in data.keys()];

		#...timeEnd
        timeEnd = time.time();
        timeElapsed = timeEnd - timeStart;

		#...print time
        print("SetData Elapsed: {}".format(timeElapsed));
		
        return True

class DataIO(object):

    def __init__(self):

        pass

    @staticmethod
    def get_legendArrayFromData(data):

        return data[0]

    @staticmethod
    def get_dataItem(data, item, legend_Array=None):
        if item not in data[0]:
            print("ERROR: '{}' Not Found in data!".format(item));
            return False;
		#...no legend_Array
        if legend_Array is None:
            legend_Array = [key for key in data[0]];

		#...with legend_Array
        return data[legend_Array.index(item)]

    @staticmethod
    def set_dataItems(data, itemData_Array):

        return data




