# -*- coding: utf-8 -*-

from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui;
import pymel.core as pm;


"""
connection mainJnt to fk and ik trans and rot

from nkTools.rigging import connectMaintJntToFKIK;
reload(connectMaintJntToFKIK);
connectMaintJntToFKIK;

HowToUse
1.select fkikSwitchCtrl
2.select mainJnts
3.apply
"""

switchCtrl = str(cmds.ls(sl=True)[0]);
mainJnts = cmds.ls(sl=True)[1:]

# setup fkikSwitch
for i, mainJnt in enumerate(mainJnts):
    """
    if i == len(mainJnts)-1:
        break;
    """
    
    mainJnt = str(mainJnt);
    fkJnt = mainJnt[:mainJnt.rfind("_jnt")] + "_fk_jnt";
    ikJnt = mainJnt[:mainJnt.rfind("_jnt")] + "_ik_jnt";
    transBC = cmds.shadingNode("blendColors", au=True, n=mainJnt + "_trans_BC");
    rotBC = cmds.shadingNode("blendColors", au=True, n=mainJnt + "_rot_BC");
    cmds.connectAttr(switchCtrl + ".FKIKSwitch", transBC + ".blender");
    cmds.connectAttr(switchCtrl + ".FKIKSwitch", rotBC + ".blender");
    xyz = ["X", "Y", "Z"];
    rgb = ["R", "G", "B"];
    for i, axis in enumerate(xyz):
        cmds.connectAttr(fkJnt + ".translate" + axis, transBC + ".color2" + rgb[i]);
        cmds.connectAttr(ikJnt + ".translate" + axis, transBC + ".color1" + rgb[i]);
        cmds.connectAttr(transBC + ".output" + rgb[i], mainJnt + ".translate" + axis);
    for i, axis in enumerate(xyz):
        cmds.connectAttr(fkJnt + ".rotate" + axis, rotBC + ".color2" + rgb[i]);
        cmds.connectAttr(ikJnt + ".rotate" + axis, rotBC + ".color1" + rgb[i]);
        cmds.connectAttr(rotBC + ".output" + rgb[i], mainJnt + ".rotate" + axis);
