# -*- coding: utf-8 -*-
import maya.cmds as cmds

"""

Set OffsetParentMatrix Tool

1.Duplicate Target
2.connect dup.matrix to target.offsetParentMatrix
3.set Attr target trans rot scale shear 0
4.delete dup

from nkTools.rigging import setOffsetParentMatrix;
reload(setOffsetParentMatrix);
setOffsetParentMatrix;
"""
# prepare var
matrixAttr = ".matrix";
worldMatrixAttr = ".worldMatrix";
offsetPMatirxAttr = ".offsetParentMatrix";
axisList = ["X", "Y", "Z"];
transAttr = ".translate";
rotateAttr = ".rotate";

targetList = cmds.ls(sl=True);

for target in targetList: 

    # get target and duplicate
    target = str(target);
    dup = str(cmds.duplicate(target, n="offsetParentDup", po=True)[0]);

    # is parentNode?
    useMatrixAttr = matrixAttr;
    if cmds.listRelatives(target, p=True) is None:
        useMatrixAttr = worldMatrixAttr;

    # connect offsetParentMatrix
    cmds.connectAttr(dup + useMatrixAttr, target + offsetPMatirxAttr, f=True);

    # set attr 0
    attrList = [transAttr, rotateAttr];
    if cmds.objectType(target) == "joint":
        attrList.append(".jointOrient");
        
    for axis in axisList:
        for attr in attrList:
            cmds.setAttr(target + attr + axis, 0);

    # disconnect and delete dup
    cmds.disconnectAttr(dup + useMatrixAttr, target + offsetPMatirxAttr)
    cmds.delete(dup);
    
    cmds.select(targetList);