# -*- coding: utf-8 -*-
"""
始点終点を指定したベジェカーブの作成(終点-始点ベクトル、ベクトルのノルム取得、ノルムをジョイント数で割る、2点間ベクトルを割られたベクトル)

開始ジョイント～終了ジョイントを選択
フォームにトランスフォームコントローラ名を入力
IKSpline
plusMinusAverage、各ジョイント間の長さ取得
全長 割る 各ジョイント長さ = 各ジョイントまでの割合を算出
ジョイントの個数分pointOnCurveInfoノードを作成
ロケーターを作成し、poinOnCurveInfoのpositionを接続(実際は不要)
distanceBetweenで各ロケーターの間の長さを計算
計算結果をfloatMathのABに接続し、Bの接続を解除
割り算結果を各ジョイントのスケールに接続
トランスフォームコントローラでのスケール対策としてのシステムを構築＊入力がなければplulsMinusAverage

from nkTools.rigging import createFixedIkSplineSystem_v1;
import importlib
importlib.reload(createFixedIkSplineSystem_v1);
createFixedIkSplineSystem_v1.showUi();

"""
# ------------------------------------------------------------------------------
from __future__ import absolute_import, division, generators, print_function, unicode_literals
try:
    from future_builtins import *
except:
    pass
import sys
sys.dont_write_bytecode = True
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

AXIS_LIST = ["X", "Y", "Z"];

def maya_useNewAPI():
    """Maya Python API 2.0 の明示的な使用宣言

    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.

    Args:
        None
    Returns:
        None

    """
    pass;

# get  maya window to parent
def getMayaWindow():
    """Mayaウィンドウの取得メソッド

    Mayaウィンドウを取得

    Args:
        None
    Returns:
        QtWidgets.QWidget: Mayaウィンドウを取得し、Qtでアクセス可能なクラスとしてreturnする関数。

    """
    ptr = OpenMayaUI.MQtUtil.mainWindow();
    if sys.version_info.major >= 3:
        # python3
            return shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget)
    else:
        # python2
        return shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)

class MainWindow(QtWidgets.QDialog):

    UI_NAME = "Create Fixed IkSpline System";

    def __init__(self, parent=getMayaWindow()):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle(self.UI_NAME);
        self.setObjectName(self.__class__.UI_NAME);
        self.setMinimumSize(200, 50);
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.createWidgets();
        self.createLayout();
        self.createConnections();

    def createWidgets(self):
        self.__textbox = QtWidgets.QLineEdit(self);
        self.__curveName = QtWidgets.QLineEdit(self);

        self.__createButton = QtWidgets.QPushButton(self);
        self.__createButton.setText("Create");

    def createLayout(self):
        mainLayout = QtWidgets.QFormLayout(self);

        mainLayout.addRow("TransformCtrlName", self.__textbox);
        mainLayout.addRow("CurveName", self.__curveName);
        mainLayout.addRow(self.__createButton);

    def createConnections(self):
        self.__createButton.clicked.connect(self.crateFixedIkSplineSystem);

    def crateFixedIkSplineSystem(self):
        cmds.undoInfo(openChunk=True);

        selectedJnts = cmds.ls(sl=True);
        duplicatedJnts = cmds.duplicate(selectedJnts, parentOnly=True, renameChildren=True);

        fixedIkSplineSystemGrp = cmds.ls("fixedIkSplineSystem_grp");
        if fixedIkSplineSystemGrp is None or len(fixedIkSplineSystemGrp) == 0:
            fixedIkSplineSystemGrp = cmds.group(em=True, n="fixedIkSplineSystem_grp", world=True);
        else:
            fixedIkSplineSystemGrp = fixedIkSplineSystemGrp[0];

        # rename jnts
        ikJnts = [];
        for duplicatedJnt in duplicatedJnts:
            newJntName = duplicatedJnt.split("_jnt")[0] + "_ik_jnt";
            newIkJnt = cmds.rename(duplicatedJnt, newJntName);
            ikJnts.append(newIkJnt);
        
        startJnt = ikJnts[0];
        endJnt = ikJnts[-1];

        curve = self.__curveName.text();
        if curve is None or curve == "":
            # get jnt positions
            jntPointList = [];
            for ikJnt in ikJnts:
                position = cmds.xform(ikJnt, q=True, translation=True, worldSpace=True);
                jntPointList.append(position);

            # create curve and clsuter and ikHandle
            curve = cmds.curve(bezier=True, d=3, p=jntPointList);
        
        # clusterList = [];
        # for i in range(len(ikJnts)):
        #     cluster = cmds.cluster("{}.cv[{}]".format(curve, i))[1];
        #     clusterList.append(cluster);

        ikHandle = cmds.ikHandle(sj=startJnt, ee=endJnt, curve=curve, sol="ikSplineSolver", ccv=False)[0];

        # culc length
        orgLength = cmds.createNode("plusMinusAverage", n="orgLength");

        pma = None;
        pmaList = [];
        locList = [];
        curveShape = cmds.listRelatives(curve, shapes=True)[0];

        for i, jnt in enumerate(ikJnts):
            if i == 0:
                poci = cmds.createNode("pointOnCurveInfo", n="{}_pointOnCurveInfo".format(jnt));
                cmds.setAttr("{}.turnOnPercentage".format(poci), 1);
                cmds.connectAttr("{}.local".format(curveShape), "{}.inputCurve".format(poci));
                posLoc = cmds.spaceLocator(n="{}_loc".format(jnt))[0];
                cmds.connectAttr("{}.position".format(poci), "{}.translate".format(posLoc));
                locList.append(posLoc);
                continue;
            
            # create plusMinusAverage and connection
            jnt = str(jnt);
            cmds.connectAttr("{}.translateX".format(jnt), "{}.input1D[{}]".format(orgLength, i));
            pma = cmds.createNode("plusMinusAverage", n="{}_PMA".format(jnt));
            if len(pmaList) != 0:
                # if previous pma exists connect it to current pma input1D[0]
                cmds.connectAttr("{}.output1D".format(pmaList[-1]), "{}.input1D[{}]".format(pma, 0));
                cmds.connectAttr("{}.translateX".format(jnt), "{}.input1D[{}]".format(pma, 1));
            else:
                cmds.connectAttr("{}.translateX".format(jnt), "{}.input1D[{}]".format(pma, 0));
                
            fm = cmds.createNode("floatMath", n="{}_FM".format(jnt));
            # operation divide
            cmds.setAttr("{}.operation".format(fm), 3);
            # each jnt length / orgLength
            cmds.connectAttr("{}.output1D".format(pma), "{}.floatA".format(fm));
            cmds.connectAttr("{}.output1D".format(orgLength), "{}.floatB".format(fm));
            
            # create pointOnCurveInfo and connect to its local
            poci = cmds.createNode("pointOnCurveInfo", n="{}_pointOnCurveInfo".format(jnt));
            cmds.setAttr("{}.turnOnPercentage".format(poci), 1);
            cmds.connectAttr("{}.local".format(curveShape), "{}.inputCurve".format(poci));
            
            cmds.connectAttr("{}.outFloat".format(fm), "{}.parameter".format(poci));

            # create position locator
            posLoc = cmds.spaceLocator(n="{}_loc".format(jnt))[0];
            locList.append(posLoc);
            cmds.connectAttr("{}.position".format(poci), "{}.translate".format(posLoc));

            pmaList.append(pma);
        
        # create groups
        # cGrp = cmds.ls("fixedIkSplineSystem_cluster_grp");
        # if cGrp is None or len(cGrp) == 0:
        #     cGrp = cmds.group(em=True, n="fixedIkSplineSystem_cluster_grp", world=True);
        #     cmds.parent(clusterList, cGrp);
        # else:
        #     cGrp = cGrp[0];
        #     cmds.parent(clusterList, cGrp, world=True);

        locGrp = cmds.ls("fixedIkSplineSystem_loc_grp");
        if locGrp is None or len(locGrp) == 0:
            locGrp = cmds.group(em=True, n="fixedIkSplineSystem_loc_grp", world=True);
            cmds.parent(locList, locGrp);
        else:
            locGrp = locGrp[0];
            cmds.parent(locList, locGrp, world=True);

        ikGrp = cmds.ls("fixedIkSplineSystem_ikHandle_grp");
        if ikGrp is None or len(ikGrp) == 0:
            ikGrp = cmds.group(em=True, n="fixedIkSplineSystem_ikHandle_grp", world=True);
            cmds.parent(ikHandle, ikGrp);
        else:
            ikGrp = ikGrp[0];
            cmds.parent(ikHandle, ikGrp, world=True);

        curveGrp = cmds.ls("fixedIkSplineSystem_curve_grp");
        if curveGrp is None or len(curveGrp) == 0:
            curveGrp = cmds.group(em=True, n="fixedIkSplineSystem_curve_grp", world=True);
            cmds.parent(curve, curveGrp);
        else:
            curveGrp = curveGrp[0];
            cmds.parent(curve, curveGrp, world=True);

        cmds.parent(cGrp, locGrp, ikGrp, curveGrp, fixedIkSplineSystemGrp);

        # crate stretch factor
        scaleFactorFMList = [];
        for i in range(len(locList) - 1):
            # each distance
            dist = cmds.createNode("distanceBetween");
            cmds.connectAttr("{}.translate".format(locList[i]), "{}.point1".format(dist));
            cmds.connectAttr("{}.translate".format(locList[i+1]), "{}.point2".format(dist));
            
            scaleFactorFM = cmds.createNode("floatMath", n="scaleFactor_{}_FM".format(i));
            # divide
            cmds.setAttr("{}.operation".format(scaleFactorFM), 3);
            cmds.connectAttr("{}.distance".format(dist), "{}.floatA".format(scaleFactorFM));
            # set default value
            cmds.connectAttr("{}.distance".format(dist), "{}.floatB".format(scaleFactorFM));
            cmds.disconnectAttr("{}.distance".format(dist), "{}.floatB".format(scaleFactorFM));
            
            scaleFactorFMList.append(scaleFactorFM);
        
        for i, fm in enumerate(scaleFactorFMList):
            cmds.connectAttr("{}.outFloat".format(fm), "{}.scaleX".format(ikJnts[i]));
    
        # transform ctrl scale
        transformCtrl = self.__textbox.text();
        if not transformCtrl == "":
            transformScalePMA = cmds.ls("{}_scale_PMA".format(transformCtrl));
            if transformScalePMA is None:
                transformScalePMA = cmds.createNode("plusMinusAverage", n="{}_scale_PMA".format(transformCtrl));
                cmds.setAttr("{}.operation".format(transformScalePMA), 3);
            for i, axis in enumerate(AXIS_LIST):
                cmds.connectAttr("{}.scale{}".format(transformCtrl, axis), "{}.input1D[{}]".format(transformScalePMA, i));

            for scaleFActorFm in scaleFactorFMList:
                multiFm = cmds.createNode("floatMath", n="{}_transformRatio_FM".format(scaleFActorFm.split("_FM")[0]));
                cmds.setAttr("{}.operation".format(multiFm), 2);
                cmds.connectAttr("{}.output1D".format(transformScalePMA), "{}.floatA".format(multiFm));
                defaultAttr = cmds.getAttr("{}.floatB".format(scaleFActorFm));
                cmds.setAttr("{}.floatB".format(multiFm), defaultAttr);
                cmds.connectAttr("{}.outFloat".format(multiFm), "{}.floatB".format(scaleFActorFm));

        cmds.scaleConstraint(transformCtrl, cGrp, mo=False);

        cmds.undoInfo(closeChunk=True);

def showUi():
    mainUi = MainWindow();
    mainUi.show();