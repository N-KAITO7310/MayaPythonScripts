# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, generators, print_function, unicode_literals
try:
    from future_builtins import *
except:
    pass
import sys
sys.dont_write_bytecode = True
from maya import OpenMayaUI, cmds;
import maya.mel as mel;
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

import attachMoveablePivotRigTool.py as pivotRig;
reload(pivotRig);
pivotRig.showUi();

last updated: 2022/10/31

"""

WINDOW_TITLE = "AttachMoveablePivotRigToolWindow";
PIVOT_CTRL_GRP = "pivot_ctrl_grp";
PIVOT_CTRL_SUFFIX = "_pivot_ctrl";
OFFSET_GRP_SUFFIX = "_offset_grp";
NEGA_GRP_SUFFIX = "_nega_grp";
LOCATOR_SUFFIX = "_loc";
AXIS_LIST = ["X", "Y", "Z"];
TRANSLATION_ATTRS = ["tx", "ty", "tz"];
ROTATE_ATTRS = ["rx", "ry", "rz"];

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
        return shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget);
    else:
        # python2
        return shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget);

class MainWindow(QtWidgets.QDialog):
    """メインウィンドウクラス
    
    本ツールのメインウィンドウクラス

    Attributes:
        UI_NAME: 表示されるウィンドウ名

    """

    def __init__(self, parent=getMayaWindow()):
        """ウィンドウクラスのinit

        この関数で行っていること
        ・ウィンドウタイトル設定
        ・UIサイズ設定
        ・ウィジェットオブジェクトの作成
        ・レイアウト設定
        ・スロットの設定

        Args:
            parent: (QtWidgets.QWidget): 親ウィンドウとして設定するインスタンス。デフォルトでMayaのウィンドウを指定。
        Returns:
            None
        
        """

        super(MainWindow, self).__init__(parent);
        self.setWindowTitle(WINDOW_TITLE);
        self.setObjectName(WINDOW_TITLE);
        self.setMinimumSize(200, 100);
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint);

        self.createWidgets();
        self.createLayout();
        self.createConnections();

    def createWidgets(self):
        """Widgetクラスの生成

        ボタン等各Widgetクラスを生成する

        Args:
            None
        Returns:
            None

        """

        self.__createLocatorButton = QtWidgets.QPushButton(self);
        self.__createLocatorButton.setText("Create Locator");

        self.__shapeCombo = QtWidgets.QComboBox(self);
        self.__shapeCombo.addItem("Cross");
        self.__shapeCombo.addItem("Sphere");
        self.__shapeCombo.addItem("Octahedron");

        self.__createCtrlButton = QtWidgets.QPushButton(self);
        self.__createCtrlButton.setText("Create Controller");

        self.__bakeButton = QtWidgets.QPushButton(self);
        self.__bakeButton.setText("Bake Apply");

        self.__deleteButton = QtWidgets.QPushButton(self);
        self.__deleteButton.setText("Delete");

    def createLayout(self):
        """レイアウト設定関数
        
        生成したWidgetクラスをレイアウトに設定する

        Args:
            None
        Returns:
            None
        
        """
        mainLayout = QtWidgets.QFormLayout(self);

        mainLayout.addRow(self.__createLocatorButton);
        mainLayout.addRow("CurveShape", self.__shapeCombo);
        mainLayout.addRow(self.__createCtrlButton);
        mainLayout.addRow(self.__bakeButton);
        mainLayout.addRow(self.__deleteButton);

    def createConnections(self):
        """スロット設定関数
        
        各ウィジェットのスロットに関数を設定する

        Args:
            None
        Returns:
            None
        """
        self.__createLocatorButton.clicked.connect(self.createLocator);
        self.__createCtrlButton.clicked.connect(self.attachMoveablePivotRig);
        self.__bakeButton.clicked.connect(self.bakeApply);
        self.__deleteButton.clicked.connect(self.deleteRig);

    def createLocator(self):
        """ロケーター生成関数

        選択されているオブジェクトと同一にロケーターを生成する

        Args:
            None
        Returns:
            None
        """

        cmds.undoInfo(openChunk=True);

        selectedObjs = cmds.ls(sl=True);

        if selectedObjs is None or len(selectedObjs) == 0:
            om.MGlobal.displayError("Please select controller");
            return;

        for selected in selectedObjs:
            pos = cmds.xform(selected, q=True, translation=True, ws=True);
            loc = cmds.spaceLocator(n="{}{}".format(selected, LOCATOR_SUFFIX));
            cmds.delete(cmds.parentConstraint(selected, loc, mo=False));

        cmds.undoInfo(closeChunk=True);

    def attachMoveablePivotRig(self):
        """外付けPivotリグをロケーター名に対応したコントローラに対しアタッチする関数

        外付けPivotコントローラを生成し、対象となるコントローラへ接続を行う

        Args:
            None
        Returns:
            None
        """

        cmds.undoInfo(openChunk=True);
        sel = cmds.ls(sl=True);

        # check pivot ctrl grp
        pivotCtrlGrp = cmds.ls(PIVOT_CTRL_GRP);
        if pivotCtrlGrp is None or len(pivotCtrlGrp) == 0:
            pivotCtrlGrp = cmds.group(em=True, n=PIVOT_CTRL_GRP);
        else:
            pivotCtrlGrp = pivotCtrlGrp[0];
        cmds.select(cl=True);

        # create ctrl and grp
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
        currentTrans = cmds.getAttr("{}.translate".format(targetCtrlName));
        currentRot = cmds.getAttr("{}.rotate".format(targetCtrlName))
        cmds.xform(targetCtrlName, ws=True, translation=[0, 0, 0], rotation=[0, 0, 0]);
        # オフセットグループをターゲットコントロールのデフォルト位置にスナップ
        cmds.delete(cmds.parentConstraint(targetCtrlName, targetOffsetGrp, mo=False));
        # オフセットグループをターゲットの上位ノード下にペアレント
        cmds.parent(targetOffsetGrp, parentObj);
        # ターゲットコントロールを元あった位置に戻す
        cmds.delete(cmds.parentConstraint(tempPosLoc, targetCtrlName));
        cmds.delete(tempPosLoc);

        # ピボットコントローラ、オフセットを作成
        pivotCtrlOffsetGrp = cmds.group(em=True, n="{}{}".format(pivotCtrlName, OFFSET_GRP_SUFFIX));
        shapeNum = self.__shapeCombo.currentIndex();
        pivotCtrl = self.createCtrlCurve(targetCtrlName, shapeNum);
        cmds.parent(pivotCtrl, pivotCtrlOffsetGrp);

        negaGrp = cmds.group(em=True, parent=pivotCtrl, n="{}{}".format(targetCtrlName, NEGA_GRP_SUFFIX));
        cmds.xform(pivotCtrlOffsetGrp, matrix=pivotMat, ws=True);

        cmds.parent(pivotCtrlOffsetGrp, pivotCtrlGrp);

        # create pivot system
        composeMat =  cmds.createNode("composeMatrix", n="{}_composeMatrix".format(targetCtrlName));
        inverseMat = cmds.createNode("inverseMatrix", n="{}_inverseMatrix".format(targetCtrlName));
        decomposeMat = cmds.createNode("decomposeMatrix", n="{}_decomposeMatrix".format(targetCtrlName));

        cmds.connectAttr("{}.translate".format(pivotCtrl), "{}.inputTranslate".format(composeMat));
        cmds.connectAttr("{}.outputMatrix".format(composeMat), "{}.inputMatrix".format(inverseMat));
        cmds.connectAttr("{}.outputMatrix".format(inverseMat), "{}.inputMatrix".format(decomposeMat));
        cmds.connectAttr("{}.outputTranslate".format(decomposeMat), "{}.translate".format(negaGrp));

        cmds.parent(targetOffsetGrp, negaGrp);

        # connect targetRig pivotRigSystem
        cmds.parentConstraint(parentObj, pivotCtrlOffsetGrp, mo=True);
        multMat = cmds.createNode("multMatrix", n=pivotCtrlName + "_multMat");
        rotatePivot = cmds.getAttr("{}.rotatePivot".format(targetCtrlName))[0];
        compoMat = cmds.createNode("composeMatrix", n=pivotCtrl + "_rotatePivot_composeMatrix");
        for i, rp in enumerate(rotatePivot):
            cmds.setAttr("{}.inputTranslate{}".format(compoMat, AXIS_LIST[i]), rp);
        inverseMat = cmds.createNode("inverseMatrix", n=pivotCtrl + "_rotatePivot_inverseMatrix");
        cmds.connectAttr("{}.outputMatrix".format(compoMat), "{}.inputMatrix".format(inverseMat));
        cmds.connectAttr("{}.outputMatrix".format(inverseMat), "{}.matrixIn[0]".format(multMat));

        topParentCtrl = self.getTopParentCtrl(targetCtrlName);
        cmds.connectAttr("{}.worldInverseMatrix[0]".format(topParentCtrl), "{}.matrixIn[1]".format(multMat));
        cmds.connectAttr("{}.worldMatrix[0]".format(targetOffsetGrp), "{}.matrixIn[2]".format(multMat));
        cmds.connectAttr("{}.matrixSum".format(multMat), "{}.offsetParentMatrix".format(targetCtrlName));

        cmds.setAttr("{}.translate".format(targetCtrlName), currentTrans[0][0], currentTrans[0][1], currentTrans[0][2], type="float3");
        cmds.setAttr("{}.rotate".format(targetCtrlName), currentRot[0][0], currentRot[0][1], currentRot[0][2], type="double3");
        cmds.delete(pivotPosLoc);
        cmds.select(cl=True);

        cmds.undoInfo(closeChunk=True);

    def getTopParentCtrl(self, targetCtrl):
        checkTarget = targetCtrl;
        checkFlag = True;

        while checkFlag:
            parent = cmds.listRelatives(checkTarget, parent=True, type="transform");
            if (not parent is None) and len(parent) > 0:
                shape = cmds.listRelatives(parent[0], shapes=True, type="nurbsCurve");
                if (not shape is None) and len(shape) > 0:
                    checkTarget = parent[0];
                else:
                    checkFlag = False;
            else:
                checkFlag = False;
        
        return checkTarget;

    def bakeApply(self):
        cmds.undoInfo(openChunk=True);

        sel = cmds.ls(sl=True);
        # ベイクしたいpivotCtrlを選択して実行。ベイク、アンペアレント＆りペアレント、不要になったコントローラ群を削除
        pivotCtrl, targetCtrl = self.getPivotCtrlAndTargetCtrl();

        # check keyframe
        keyCount = cmds.keyframe(pivotCtrl, q=True, keyframeCount=True);
        if keyCount < 1:
            om.MGlobal.displayError("Please keyframe pivotCtrl");
            return;

        # bake frame targetにキーがある場合はその範囲、キーがない場合はピボットコントローラのキーフレーム範囲を参照する
        startF = cmds.findKeyframe(targetCtrl, which="first");
        endF = cmds.findKeyframe(targetCtrl, which="last");
        if startF == endF:
            startF = cmds.findKeyframe(pivotCtrl, which="first");
            endF = cmds.findKeyframe(pivotCtrl, which="last");

        # ready source
        tempLoc = cmds.spaceLocator();
        tempConst = cmds.parentConstraint(targetCtrl, tempLoc);
        cmds.bakeResults(tempLoc, t=(startF, endF), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False);
        cmds.bakeResults(targetCtrl, t=(startF, endF), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False);
        cmds.delete(tempConst);

        # delete pivot rig
        self.deleteRig(pivotCtrl, targetCtrl);

        # tempLocのsourceとして対象となるキーフレームでtargetを位置合わせする
        currentTime = cmds.currentTime(q=True);
        for frame in range(int(startF), int(endF) + 1):
            cmds.currentTime(frame);
            cmds.matchTransform(targetCtrl, tempLoc, pos=True, rot=True);
            cmds.setKeyframe(targetCtrl, breakdown=0, preserveCurveShape=0, hierarchy="none", controlPoints=0, shape=0, attribute="translate");
            cmds.setKeyframe(targetCtrl, breakdown=0, preserveCurveShape=0, hierarchy="none", controlPoints=0, shape=0, attribute="rotate");

        cmds.currentTime(currentTime);
        cmds.delete(tempLoc);

        cmds.undoInfo(closeChunk=True);

    def delete(self):
        cmds.undoInfo(openChunk=True);

        self.deleteRig();

        cmds.undoInfo(closeChunk=True);

    def deleteRig(self, pivotCtrl=None, targetCtrl=None):
        if pivotCtrl is None and targetCtrl is None:
            pivotCtrl, targetCtrl = self.getPivotCtrlAndTargetCtrl();

        # breakConnection
        tempNull = cmds.group(em=True);
        cmds.matchTransform(tempNull, targetCtrl, pos=True, rot=True);
        cmds.disconnectAttr("{}.matrixSum".format(pivotCtrl + "_multMat"), "{}.offsetParentMatrix".format(targetCtrl));

        # reset offsetParentMatrix
        defaultMat = om.MMatrix();
        cmds.setAttr("{}.offsetParentMatrix".format(targetCtrl), defaultMat, type="matrix");
        tempConst = cmds.parentConstraint(tempNull, targetCtrl, mo=False);

        # delete
        cmds.delete(pivotCtrl + "_multMat", tempNull, tempConst, pivotCtrl + OFFSET_GRP_SUFFIX);

        # check pivotCtrlGrp
        pivotCtrlGrp = cmds.ls(PIVOT_CTRL_GRP);
        if (not pivotCtrlGrp is None) and len(pivotCtrlGrp) > 0:
            pivotCtrlGrp = pivotCtrlGrp[0];
            children = cmds.listRelatives(pivotCtrlGrp, c=True);
            if children is None:
                cmds.delete(pivotCtrlGrp);

    def getPivotCtrlAndTargetCtrl(self):
        pivotCtrl = cmds.ls(sl=True);
        if pivotCtrl is None or len(pivotCtrl) == 0:
            om.MGlobal.displayError("Please Select pivot controller");
            return None;
        else:
            pivotCtrl = pivotCtrl[0];
        if not PIVOT_CTRL_SUFFIX in pivotCtrl:
            om.MGlobal.displayError("Please Select pivot controller");
            return None;
        targetCtrl = pivotCtrl.split(PIVOT_CTRL_SUFFIX)[0];

        return pivotCtrl, targetCtrl;

    def createCtrlCurve(self, targetName, shapeNum):
        if shapeNum == 0:
            ctrlCurve = cmds.curve(name="{}{}".format(targetName, PIVOT_CTRL_SUFFIX),d=1,
            p=[(-1.0, 0.0, 0.0), (1.0, 0.0, 0.0),(0.0, 0.0, 0.0),(0.0, 0.0, 1.0),(0.0, 0.0, -1.0),(0.0, 0.0, 0.0),(0.0, 1.0, 0.0), (0.0, -1.0, 0.0)],
            k=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]);

        elif shapeNum == 1:
            ctrlCurve = cmds.curve(name="{}{}".format(targetName, PIVOT_CTRL_SUFFIX), d=1,
            p=[(0.0, 1.0, 0.0), (0.0, 0.92388, 0.382683), (0.0, 0.707107, 0.707107), (0.0, 0.382683, 0.92388), (0.0, 0.0, 1.0),
                (0.0, -0.382683, 0.92388), (0.0, -0.707107, 0.707107), (0.0, -0.92388, 0.382683), (0.0, -1.0, 0.0), (0.0, -0.92388, -0.382683),
                (0.0, -0.707107, -0.707107), (0.0, -0.382683, -0.92388), (0.0, 0.0, -1.0), (0.0, 0.382683, -0.92388), (0.0, 0.707107, -0.707107),
                (0.0, 0.92388, -0.382683), (0.0, 1.0, 0.0), (0.382683, 0.92388, 0.0), (0.707107, 0.707107, 0.0), (0.92388, 0.382683, 0.0),
                (1.0, 0.0, 0.0), (0.92388, -0.382683, 0.0), (0.707107, -0.707107, 0.0), (0.382683, -0.92388, 0.0), (0.0, -1.0, 0.0),
                (-0.382683, -0.92388, 0.0), (-0.707107, -0.707107, 0.0), (-0.92388, -0.382683, 0.0), (-1.0, 0.0, 0.0), (-0.92388, 0.382683, 0.0),
                (-0.707107, 0.707107, 0.0), (-0.382683, 0.92388, 0.0), (0.0, 1.0, 0.0), (0.0, 0.92388, -0.382683), (0.0, 0.707107, -0.707107),
                (0.0, 0.382683, -0.92388), (0.0, 0.0, -1.0), (-0.382683, 0.0, -0.92388), (-0.707107, 0.0, -0.707107), (-0.92388, 0.0, -0.382683),
                (-1.0, 0.0, 0.0), (-0.92388, 0.0, 0.382683), (-0.707107, 0.0, 0.707107), (-0.382683, 0.0, 0.92388), (0.0, 0.0, 1.0),
                (0.382683, 0.0, 0.92388), (0.707107, 0.0, 0.707107), (0.92388, 0.0, 0.382683), (1.0, 0.0, 0.0), (0.92388, 0.0, -0.382683),
                (0.707107, 0.0, -0.707107), (0.382683, 0.0, -0.92388), (0.0, 0.0, -1.0)],
            k=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0,
                23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0,
                44.0, 45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0])
        
        elif shapeNum == 2:
           ctrlCurve = cmds.curve(name="{}{}".format(targetName, PIVOT_CTRL_SUFFIX),d=1,
            p=[(0.0, 1.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), 
                (0.0, -1.0, 0.0), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (1.0, 0.0, 0.0)],
            k=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0])

        return ctrlCurve;

# show ui
def showUi():
    mainUi = MainWindow();
    mainUi.show();