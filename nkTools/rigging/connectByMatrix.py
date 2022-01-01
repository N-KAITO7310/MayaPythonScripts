# -*- coding: utf-8 -*-
import maya.cmds as cmds;
"""

Connect by Matrix

1.check driver and driven hierarchy
2.get commonParent
3.multMatrix driverSide: from driver to obj under commonParent
4.multInverseMatrix drivenSide: from obj under commonParent to obj on driven
5.not same axis: duplicate driven and parent under driver,this is first mult target
6.decomposeMatrix and connect driven

from nkTools.rigging import connectByMatrix;
reload(connectByMatrix);
connectByMatrix;
"""
def revealHierarchyUp(obj):
    hierarchyList = [];
    p = cmds.listRelatives(obj, type="transform", p=True);
    while not p is None:
        hierarchyList.append(p[0]);
        p = cmds.listRelatives(p, type="transform", p=True);

    hierarchyList.reverse();

    return hierarchyList;

driver = str(cmds.ls(sl=True)[0]);
driven = str(cmds.ls(sl=True)[1]);

# TODO ui setting
sameAxis = False;

prefix = driven;
mult = cmds.shadingNode("multMatrix", au=True, n="{0}_multMatrix".format(prefix));
decompose = cmds.shadingNode("decomposeMatrix", au=True, n="{0}_decomposeMatrix".format(prefix));

# find common parent
driverParentList = revealHierarchyUp(driver);
drivenParentList = revealHierarchyUp(driven);

commonParent = "";
for driverP in driverParentList:
    for drivenP in drivenParentList:
        if driverP == drivenP:
            commonParent = driverP;

isWorld = False;
if commonParent == "":
    isWorld = True;

# get mult matrix target
driverSideMultTargetList = driverParentList;
drivenSideMultTargetList = drivenParentList;
if not isWorld:
    commonParentUpList = [commonParent];
    cp = cmds.listRelatives(commonParent, p=True);
    while not cp is None:
        commonParentUpList.append(cp[0]);
        cp = cmds.listRelatives(cp[0], p=True);

    for cp in commonParentUpList:
        driverSideMultTargetList.remove(cp);
        drivenSideMultTargetList.remove(cp);

# connect mult
# driverSide
driverSideMultTargetList.reverse();
driverSideMultTargetList.insert(0, driver);

if not sameAxis:
    dup = cmds.duplicate(driven, po=True)[0];
    cmds.parent(dup, driver);
    driverSideMultTargetList.insert(0, dup);

matrixInNum = 0
for driverSide in driverSideMultTargetList:
    cmds.connectAttr(driverSide + ".matrix",mult + ".matrixIn[{0}]".format(matrixInNum), f=True);
    matrixInNum = matrixInNum + 1;

# drivenSide
for i, drivenSide in enumerate(drivenSideMultTargetList):
    cmds.connectAttr(drivenSide + ".inverseMatrix",mult + ".matrixIn[{0}]".format(matrixInNum), f=True);
    matrixInNum = matrixInNum + 1;

# connect decompose
cmds.connectAttr(mult + ".matrixSum",decompose + ".inputMatrix", f=True);

# conntct driven
attrList = ["translate", "rotate", "scale"];# , "shear"
for attr in attrList:
    cmds.connectAttr("{0}.output{1}".format(decompose, str.capitalize(attr)), "{0}.{1}".format(driven, attr), f=True);

# set joint orient 0
if cmds.objectType(driven) == "joint":
    axisList = ["X", "Y", "Z"];
    for axis in axisList:
        cmds.setAttr(driven + ".jointOrient{0}".format(axis), 0);