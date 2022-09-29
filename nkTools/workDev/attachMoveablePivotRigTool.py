# -*- coding: utf-8 -*-
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

"""

ピボットコントローラー参考：
https://lesterbanks.com/2017/10/2-ways-create-movable-pivot-maya/

要件定義
・ロケーター生成ボタン
    ・選択オブジェクト箇所にロケーターを生成
・作成ボタン
    ・選択ロケーター位置にコントローラを生成
    ・指定コントローラの上位にコントローラを階層化。offsetグループと、negグループをはさむ
    ・pivot_ctrl.Translate→composeMatrix→inverseMatrix→decomposeMatrix→nega.Translate
・ベイクボタン
    ・ベイクした後に削除
・削除ボタン
    ・生成したコントローラを削除
・(更新ボタンは恐らく不要)

import nkTools.workDev.attachMoveablePivotRigTool.py as pivotRig;
reload(pivotRig);
pivotRig.showUi();

"""

WINDOW_TITLE = "AttachMoveablePivotRigToolWindow";
PIVOT_CTRL_SUFFIX = "_pivot_ctrl";
OFFSET_GRP_SUFFIX = "_offset_grp";
NEGA_GRP_SUFFIX = "_nega_grp";
LOCATOR_SUFFIX = "_loc";
TRANSLATION_ATTRS = ["tx", "ty", "tz"];
ROTATE_ATTRS = ["rx", "ry", "rz"];

def getMayaWindow():
    ptr = OpenMayaUI.MQtUtil.mainWindow();
    if sys.version_info.major >= 3:
        # python3
        return shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget);
    else:
        # python2
        return shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget);

class MainWindow(QtWidgets.QDialog):

    def __init__(self, parent=getMayaWindow()):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle(WINDOW_TITLE);
        self.setObjectName(WINDOW_TITLE);
        self.setMinimumSize(300, 200);
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint);

        self.createWidgets();
        self.createLayout();
        self.createConnections();

    def createWidgets(self):
        self.__createLocatorButton = QtWidgets.QPushButton(self);
        self.__createLocatorButton.setText("Create Locator");

        self.__createCtrlButton = QtWidgets.QPushButton(self);
        self.__createCtrlButton.setText("Create Controller");

        self.__bakeButton = QtWidgets.QPushButton(self);
        self.__bakeButton.setText("Bake Apply");

        self.__deleteButton = QtWidgets.QPushButton(self);
        self.__deleteButton.setText("Delete");

    def createLayout(self):
        mainLayout = QtWidgets.QVBoxLayout(self);

        mainLayout.addWidget(self.__createLocatorButton);
        mainLayout.addWidget(self.__createCtrlButton);
        mainLayout.addWidget(self.__bakeButton);
        mainLayout.addWidget(self.__deleteButton);

    def createConnections(self):
        self.__createLocatorButton.clicked.connect(self.createLocator);
        self.__createCtrlButton.clicked.connect(self.attachMoveablePivotRig);
        self.__bakeButton.clicked.connect(self.bakeApply);
        self.__deleteButton.clicked.connect(self.deleteRig);

    def createLocator(self):
        selectedObjs = cmds.ls(sl=True);

        if selectedObjs is None or len(selectedObjs) == 0:
            om.MGlobal.displayError("Please select controller");
            return;

        for selected in selectedObjs:
            pos = cmds.xform(selected, q=True, translation=True, ws=True);
            loc = cmds.spaceLocator(n="{}{}".format(selected, LOCATOR_SUFFIX));
            cmds.delete(cmds.parentConstraint(selected, loc, mo=False));

    def attachMoveablePivotRig(self):
        """
        ・選択ロケーター位置に、offset＆Pivotコントローラを生成
        ・指定コントローラの上位にコントローラを階層化。offsetグループと、negグループをはさむ
        ・pivot_ctrl.Translate→composeMatrix→inverseMatrix→decomposeMatrix→nega.Translate
        """

        # create ctrl and grp
        sel = cmds.ls(sl=True);
        if sel is None or len(sel) == 0:
            om.MGlobal.displayError("Please Select Pivot Position Locator");
            return;
        
        pivotPosLoc = sel[0];

        targetCtrlName = pivotPosLoc.split(LOCATOR_SUFFIX)[0];
        pivotCtrlName = targetCtrlName + PIVOT_CTRL_SUFFIX;
        pivotMat = cmds.xform(pivotPosLoc, q=True, matrix=True, ws=True);

        parentObj = cmds.listRelatives(targetCtrlName, p=True)[0];
        if parentObj is None or len(parentObj) == 0:
            om.MGlobal.displayError("Error! target ctrl dont have parent");

        # ターゲットコントロールにオフセットを作成
        targetOffsetGrp = cmds.group(em=True, n="{}{}".format(targetCtrlName, OFFSET_GRP_SUFFIX));
        # ターゲットコントロールの移動値を保持、matrixを0にし、デフォルト位置に戻す。フリーズがかかっているためロケーターを利用して保持
        tempPosLoc = cmds.spaceLocator();
        cmds.delete(cmds.parentConstraint(targetCtrlName, tempPosLoc));
        cmds.xform(targetCtrlName, ws=True, translation=[0, 0, 0], rotation=[0, 0, 0]);
        # オフセットグループをターゲットコントロールのデフォルト位置にスナップ
        cmds.delete(cmds.parentConstraint(targetCtrlName, targetOffsetGrp, mo=False));
        # オフセットグループをターゲットの上位ノード下にペアレント
        cmds.parent(targetOffsetGrp, parentObj);
        # フリーズをかける
        cmds.makeIdentity(targetOffsetGrp, apply=True, t=True, r=True, s=True, n=False, pn=True);
        # ターゲットコントロールを元あった位置に戻す
        cmds.delete(cmds.parentConstraint(tempPosLoc, targetCtrlName));
        cmds.delete(tempPosLoc);
        # オフセットにターゲットコントロールをペアレント
        cmds.parent(targetCtrlName, targetOffsetGrp);

        # ピボットコントローラ、オフセットを作成
        pivotCtrlOffsetGrp = cmds.group(em=True, n="{}{}".format(pivotCtrlName, OFFSET_GRP_SUFFIX));
        pivotCtrl = self.createCtrlCurve(targetCtrlName);
        cmds.parent(pivotCtrl, pivotCtrlOffsetGrp);

        negaGrp = cmds.group(em=True, parent=pivotCtrl, n="{}{}".format(targetCtrlName, NEGA_GRP_SUFFIX));
        cmds.xform(pivotCtrlOffsetGrp, matrix=pivotMat, ws=True);

        cmds.parent(pivotCtrlOffsetGrp, parentObj);
        cmds.makeIdentity(pivotCtrlOffsetGrp, apply=True, t=True, r=True, s=True, n=False, pn=True);

        # create pivot system
        composeMat =  cmds.createNode("composeMatrix", n="{}_composeMatrix".format(targetCtrlName));
        inverseMat = cmds.createNode("inverseMatrix", n="{}_inverseMatrix".format(targetCtrlName));
        decomposeMat = cmds.createNode("decomposeMatrix", n="{}_decomposeMatrix".format(targetCtrlName));

        cmds.connectAttr("{}.translate".format(pivotCtrl), "{}.inputTranslate".format(composeMat));
        cmds.connectAttr("{}.outputMatrix".format(composeMat), "{}.inputMatrix".format(inverseMat));
        cmds.connectAttr("{}.outputMatrix".format(inverseMat), "{}.inputMatrix".format(decomposeMat));
        cmds.connectAttr("{}.outputTranslate".format(decomposeMat), "{}.translate".format(negaGrp));

        cmds.parent(targetOffsetGrp, negaGrp);

        cmds.delete(pivotPosLoc);

    def bakeApply(self):
        sel = cmds.ls(sl=True);
        # ベイクしたいpivotCtrlを選択して実行。ベイク、アンペアレント＆りペアレント、不要になったコントローラ群を削除
        pivotCtrl, targetCtrl = self.getPivotCtrlAndTargetCtrl();
        print(pivotCtrl, targetCtrl)

        # bake frame TODO: 範囲はターゲットorピボットコントロール？ユーザーに入力させるかタイムスライダ―？
        startF = cmds.findKeyframe(targetCtrl, which="first");
        endF = cmds.findKeyframe(targetCtrl, which="last");

        # ready source
        tempLoc = cmds.spaceLocator();
        cmds.parentConstraint(targetCtrl, tempLoc);
        cmds.bakeResults(tempLoc, t=(startF, endF), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False);

        # ターゲットを元の階層に。キーを削除したうえでベイク処理。不要なノードを削除。
        parentObj = cmds.listRelatives(pivotCtrl + OFFSET_GRP_SUFFIX, parent=True)[0];
        cmds.parent(targetCtrl, parentObj);

        for attr in TRANSLATION_ATTRS + ROTATE_ATTRS:
            source = cmds.listConnections("{}.{}".format(targetCtrl, attr));
            if source is None:
                continue;
            source = source[0];
            cmds.delete(source);

        tempPConst = cmds.parentConstraint(tempLoc, targetCtrl);
        cmds.bakeResults(targetCtrl, t=(startF, endF), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False);
        cmds.delete(tempLoc, tempPConst, pivotCtrl + OFFSET_GRP_SUFFIX);

    def deleteRig(self):
        pivotCtrl, targetCtrl = self.getPivotCtrlAndTargetCtrl();

        negaGrp = targetCtrl + NEGA_GRP_SUFFIX;

        # breakConnection
        tConSource = cmds.listConnections("{}.translate".format(negaGrp), source=True)[0];
        cmds.disconnectAttr("{}.outputTranslate".format(tConSource), "{}.translate".format(negaGrp));

        # delete
        pivotCtrlOffsetGrp = pivotCtrl + OFFSET_GRP_SUFFIX;
        parentObj = cmds.listRelatives(pivotCtrlOffsetGrp, parent=True)[0];
        cmds.parent(pivotCtrlOffsetGrp, w=True);
        cmds.parent(targetCtrl, parentObj);

        cmds.delete(pivotCtrlOffsetGrp);

    def getPivotCtrlAndTargetCtrl(self):
        pivotCtrl = cmds.ls(sl=True);
        if pivotCtrl is None:
            om.MGlobal.displayError("Please Select pivot controller");
            return;
        else:
            pivotCtrl = pivotCtrl[0];
        if not PIVOT_CTRL_SUFFIX in pivotCtrl:
            om.MGlobal.displayError("Please Select pivot controller");
            return;
        targetCtrl = pivotCtrl.split(PIVOT_CTRL_SUFFIX)[0];

        return pivotCtrl, targetCtrl;

    def createCtrlCurve(self, targetName):
        ctrlCurve = cmds.curve(d=1, p=[[0, 0, 1] ,[0 ,0.5 ,0.866025], [0, 0.866025, 0.5], [0, 1, 0] ,[0, 0.866025, -0.5], [0, 0.5, -0.866025], [0, 0, -1], [0, -0.5, -0.866025], [0, -0.866025, -0.5], [0, -1, 0], [0, -0.866025, 0.5], [0, -0.5, 0.866025], [0, 0, 1], [0.707107, 0, 0.707107], [1, 0, 0], [0.707107, 0, -0.707107], [0, 0, -1], [-0.707107, 0, -0.707107], [-1, 0, 0], [-0.866025, 0.5, 0], [-0.5, 0.866025, 0], [0, 1, 0], [0.5, 0.866025, 0], [0.866025, 0.5, 0], [1, 0, 0], [0.866025, 0.5, 0], [0.5, -0.866025, 0] ,[0, -1, 0], [-0.5, -0.866025, 0], [-0.866025, -0.5, 0], [-1, 0, 0], [-0.707107, 0, 0.707107], [0, 0, 1]], k=[0 ,1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32], n="{}{}".format(targetName, PIVOT_CTRL_SUFFIX));

        return ctrlCurve;

# show ui
def showUi():
    mainUi = MainWindow();
    mainUi.show();