import maya.cmds as cmds;
import maya.api.OpenMaya as om;

vtxList = cmds.ls(sl=True, fl=True);
checkDist = 1.0;

cmds.select(cl=True);

for vtxA in vtxList:
    posA = cmds.pointPosition(str(vtxA), l=True);
    vecA = om.MVector(posA[0], posA[1], posA[2]);
    for vtxB in vtxList:
        posB = cmds.pointPosition(str(vtxB), l=True);
        vecB = om.MVector(posB[0], posB[1], posB[2]);
        
        distVec = vecB - vecA;
        
        if distVec.length() < checkDist:
            cmds.select(vtxA, vtxB, add=True);
            
    vtxList.remove(vtxA);