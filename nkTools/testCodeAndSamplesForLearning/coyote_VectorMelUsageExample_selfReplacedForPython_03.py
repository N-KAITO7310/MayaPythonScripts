import maya.cmds as cmds;
import maya.api.OpenMaya as om;
import random;

# 選択頂点のランダム移動

vtxList = cmds.ls(sl=True, fl=True);

for vtx in vtxList:
    vec = om.MVector(1.0, 0.0, 0.0);
    rot = om.MEulerRotation(0.0, random.random() * 360, 0.0);
    vec = vec.rotateBy(rot);
    
    cmds.move(vec.x, vec.y, vec.z, r=True);
    
