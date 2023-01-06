# -*- coding: utf-8 -*-

from maya import OpenMayaUI, cmds;
from PySide2 import QtWidgets, QtCore;
import maya.OpenMayaUI as omui;
import shiboken2;
import maya.api.OpenMaya as om;
import os;
import subprocess;
from functools import partial;
import maya.api.OpenMayaAnim as oma;
import maya.mel as mel;

"""
・prefix設定
・コントローラーシェイプ選択

前提
・実行するとメッシュは複製される。その複製されたメッシュがブレンドシェイプされる側となるメッシュとし、元のメッシュはスキン用と想定する。
・既にジョイントがスキンされている状態かどうか(ジョイントが法線と同じ向きになるかどうかの差異がでる)

参考URL
https://www.cgcircuit.com/workshop/face-rigging
"""

def autoCreateTweakers():
    mesh = cmds.ls(sl=True)[0];
    jnts = cmds.ls(sl=True, type="joint")[0:];
    blendShapeMesh = cmds.duplicate(mesh, n="{}_bs_geo".format(mesh))[0];
    meshShape = cmds.listRelatives(blendShapeMesh, s=True, type="mesh")[0];

    jntsNum = len(jnts);
    cmds.select(cl=True);
    cmds.select(blendShapeMesh);
    mel.eval("createHair {} 1 10 0 0 0 0 5 0 1 1 1;".format(jntsNum));
    
    # delete hair nodes
    deleteTargets = ["nucleus1", "hairSystem1", "pfxHair1"];
    cmds.delete(deleteTargets);
    
    follicles = cmds.listConnections(meshShape + ".worldMatrix[0]", type="follicle", d=True);
    
    bindPreMatrixGrps = [];
    renamedJnts = [];
    for i, jnt in enumerate(jnts):
        # rename
        follicle = cmds.rename(follicles[i], "{}_{}_follicle".format(mesh, i));
        follicleShape = cmds.listRelatives(follicle, s=True, type="follicle")[0];
        
        # uv
        closest = cmds.createNode("closestPointOnMesh", n="{}_closestPointOnMesh".format(mesh));
        cmds.connectAttr("{}.worldMatrix[0]".format(meshShape), "{}.inputMatrix".format(closest));
        cmds.connectAttr("{}.worldMesh[0]".format(meshShape), "{}.inMesh".format(closest));
        decomposeMat = cmds.createNode("decomposeMatrix", n="{}_decompose".format(jnt));
        cmds.connectAttr("{}.worldMatrix".format(jnt), "{}.inputMatrix".format(decomposeMat));
        cmds.connectAttr("{}.outputTranslate".format(decomposeMat), "{}.inPosition".format(closest));
        
        paramU = cmds.getAttr("{}.result.parameterU".format(closest));
        paramV = cmds.getAttr("{}.result.parameterV".format(closest));
        
        cmds.setAttr("{}.parameterU".format(follicleShape), paramU);
        cmds.setAttr("{}.parameterV".format(follicleShape), paramV);
        
        cmds.delete(closest, decomposeMat);
        
        follicleUnderGrp = cmds.rename(cmds.listRelatives(follicle, c=True, type="transform")[0], "{}_{}_grp".format(mesh, i));
        bindPreMatrixGrps.append(follicleUnderGrp);
        
        # ctrl
        ctrl = cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=1, d=3, ut=0, tol=0.01, s=8, ch=0, n="{}_{}_ctrl".format(mesh, i))[0];
        cmds.matchTransform(ctrl, follicleUnderGrp, pos=True, rot=True);
        cmds.parent(ctrl, follicleUnderGrp);
        
        # snap jnt
        jnt = cmds.rename(jnt, "{}_{}_jnt".format(mesh, i));
        renamedJnts.append(jnt);
        cmds.matchTransform(jnt, ctrl, pos=True, rot=True);
        cmds.parent(jnt, ctrl);
        
    bs = cmds.blendShape(blendShapeMesh, mesh, frontOfChain=True, n="{}_tweaker_bs".format(mesh))[0];
    cmds.setAttr("{}.{}".format(bs, blendShapeMesh), 1);
    cmds.setAttr("{}.visibility".format(blendShapeMesh), 0);
    
    # get skinCluster
    skinCluster = cmds.skinCluster(renamedJnts, mesh, bindMethod=1, normalizeWeights=1, skinMethod=0, weightDistribution=1, dr=4.0)[0];
    bindJnts = cmds.listConnections("{}.matrix".format(skinCluster));
    bindJntsNum = len(bindJnts);
    
    for i, jnt in enumerate(renamedJnts):
        matrixOrder = 0;
        for n in range(0, bindJntsNum):
            inputJnt = cmds.listConnections("{}.matrix[{}]".format(skinCluster, n))[0];
            if jnt == inputJnt:
                matrixOrder = n;
            else:
                continue;
        
        cmds.connectAttr("{}.worldInverseMatrix".format(bindPreMatrixGrps[i]), "{}.bindPreMatrix[{}]".format(skinCluster, matrixOrder));
        
autoCreateTweakers();
