# -*- coding: utf-8 -*-
import maya.cmds as cmds;
import maya.api.OpenMaya as om;
import nameUtils;

def createOffset(obj):
    parent = cmds.listRelative(p=True);
    if parent:
        parent = parent[0];

    temp = obj.split("_");

    groupName = nameUtils.getUniqueName(temp[1], temp[0], "offsetGrp");
    if not groupName:
        om.MGlobal.displayError("Error generating name");
        return;

    grp = cmds.createNode("transform", n=groupName);

    cmds.matchTransform(grp, obj, pos=True, rot=True);
    cmds.parent(obj, grp);

    if parent:
        cmds.parent(grp, parent);