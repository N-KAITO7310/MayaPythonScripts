# -*- coding: utf-8 -*-

from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;


"""
JointSnapGenerateTool

create:
2021/10/30~

選択頂点と同一座標にジョイントを複数生成するスクリプト

現在未着手

"""

def jointSnapGenerateTool:
    selectedList = cmds.ls(sl=True);
    objList =  [];
    vertexList = [];
    for s in selectedList:
        if ".vtx" in str(s):
            vertexList.append(str(s));
        else:
            objList.append(str(s));

    for v in vertexList:
        cluster = cmds.cluster(v);
        


    pass;