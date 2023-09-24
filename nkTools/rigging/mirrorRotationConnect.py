# -*- coding: utf-8 -*-
import maya.cmds as cmds;

"""
MirrorRotationConnect
created: 2022/02/02

スケール-1を利用した回転の反転ギミックを用い、driverからdrivenへ接続を行う

ScriptEditorUse:
from nkTools.rigging import mirrorRotationConnect;
reload(mirrorRotationConnect);
mirrorRotationConnect;
"""

# prepare var
driver = str(cmds.ls(sl=True)[0]);
driven = str(cmds.ls(sl=True)[1]);
driverSideNull = cmds.createNode("transform", n="{0}_driverSideNull".format(driver));

# TODO:need to input axis by UI
axisList = ["X", "Y", "Z"];

# driverSide to drivenSide
cmds.setAttr("{0}.sx".format(driverSideNull), -1);
multMatrix = cmds.shadingNode("multMatrix", au=True);
cmds.connectAttr("{0}.matrix".format(driver), "{0}.matrixIn[0]".format(multMatrix), f=True);
cmds.connectAttr("{0}.matrix".format(driverSideNull), "{0}.matrixIn[1]".format(multMatrix), f=True);
decompose = cmds.createNode("decomposeMatrix");
cmds.connectAttr("{0}.matrixSum".format(multMatrix), "{0}.inputMatrix".format(decompose), f=True);
quatToEular = cmds.shadingNode("quatToEuler", au=True);

# connection
cmds.connectAttr("{0}.outputQuat".format(decompose), "{0}.inputQuat".format(quatToEular), f=True);
for axis in axisList:
    cmds.connectAttr("{0}.outputRotate{1}".format(quatToEular, axis), "{0}.rotate{1}".format(driven, axis), f=True);


            
