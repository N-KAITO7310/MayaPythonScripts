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
SHAPE_ENUM_CROSS = 0;
SHAPE_ENUM_SPHERE = 1;
SHAPE_ENUM_OCTAHEDRON = 2;

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

        外付けPivotコントローラノード群を生成し、階層変更は行わず対象となるコントローラへ接続を行う

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

        # ターゲットコントロールのオフセットを持ったグループを作成
        targetOffsetGrp = cmds.group(em=True, n="{}{}".format(targetCtrlName, OFFSET_GRP_SUFFIX));

        # オフセットグループをターゲットコントロールのデフォルト位置にスナップ
        cmds.delete(cmds.parentConstraint(targetCtrlName, targetOffsetGrp, mo=False));
        
        # ピボットコントローラ、オフセットを作成
        pivotCtrlOffsetGrp = cmds.group(em=True, n="{}{}".format(pivotCtrlName, OFFSET_GRP_SUFFIX));
        shapeNum = self.__shapeCombo.currentIndex();
        pivotCtrl = self.createCtrlCurve(targetCtrlName, shapeNum);
        cmds.parent(pivotCtrl, pivotCtrlOffsetGrp);

        # pivotコントローラ移動とは逆の移動値をセットするnegaグループを作成
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

        # 元アニメーションを保持するためのロケータを作成しベイク処理
        animPreserveLoc = cmds.spaceLocator(n="{}_animPreserve_loc".format(targetCtrlName))[0];
        cmds.parent(animPreserveLoc, parentObj);

        # locatorの原点をコントローラ0位置に移動、フリーズしスペースを合わせる
        targetCurrentMat = cmds.xform(targetCtrlName, q=True, matrix=True);
        zeroMat = om.MMatrix();
        cmds.xform(targetCtrlName, matrix=zeroMat);
        cmds.matchTransform(animPreserveLoc, targetCtrlName, pos=True, rot=True);
        cmds.makeIdentity(animPreserveLoc, translate=True, rotate=True, apply=True);
        cmds.xform(targetCtrlName, matrix=targetCurrentMat);

        tempPConst = cmds.parentConstraint(targetCtrlName, animPreserveLoc, mo=False);
        targetStartF, targetEndF = self.checkKeyframeRange(targetCtrlName);
        cmds.bakeResults(animPreserveLoc, t=(targetStartF, targetEndF), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False);
        cmds.delete(tempPConst);
        cmds.setAttr("{}.visibility".format(animPreserveLoc), 0);

        # connect targetRig pivotRigSystem
        cmds.parentConstraint(parentObj, pivotCtrlOffsetGrp, mo=True);

        # cmds.connectAttr("{}.matrixSum".format(multMat), "{}.offsetParentMatrix".format(targetCtrlName));
        pConst = cmds.parentConstraint(targetOffsetGrp, targetCtrlName, mo=True);

        cmds.delete(pivotPosLoc);
        cmds.select(cl=True);

        cmds.undoInfo(closeChunk=True);

    def getTopParentCtrl(self, targetCtrl):
        """対象コントローラが存在する階層の最上位nurbsCurveオブジェクトを取得する関数

        引数に指定したオブジェクトからたどり、最上位のnurbsCurveオブジェクトを取得する
        ＊階層途中にnurbsCurve以外のノード(joint, nullなど)が存在する場合については未対応。

        Args:
            targetCtrl: (string): pivotCtrl下で操作したいターゲットとなるコントローラ名文字列。
        Returns:
            checkTarget: (string): 最上位階層のnurbsCurveオブジェクト
        """

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
        """対象のコントローラにベイク処理を行い、Pivotコントローラを削除する関数
        
        対象コントローラへpivotCtrlからの座標変換をベイクする。
        キーフレーム範囲は対象となるコントローラ>pivotCtrlで参照。
        実装時対象コントローラがフリーズを行った０位置に戻らなくなる現象がみられたため、
        実質的にはロケーターへベイク後、そのロケーターへ位置合わせ・キーを打つことによって実装。

        Args:
            None
        Returns:
            None
        """

        cmds.undoInfo(openChunk=True);

        # ベイクしたいpivotCtrlを選択して実行
        pivotCtrl, targetCtrl = self.getPivotCtrlAndTargetCtrl();

        # アニメーション保持用ロケータを取得
        animPreserveLoc = cmds.ls("{}_animPreserve_loc".format(targetCtrl))[0];

        # check keyframe
        keyCount = cmds.keyframe(pivotCtrl, q=True, keyframeCount=True);
        if keyCount < 1:
            om.MGlobal.displayError("Please keyframe pivotCtrl");
            return;

        # bakeを行うframe範囲の決定。targetCtrl、pivotCtrlがもつキーフレーム範囲のうち大きい(小さい)方を参照する
        targetStartF, targetEndF = self.checkKeyframeRange(animPreserveLoc);
        pivotStartF, pivotEndF = self.checkKeyframeRange(pivotCtrl);

        # 元アニメーションを保持する範囲を決定
        preservePreFrameRange = [];
        if targetStartF >= pivotStartF:
            # フレームが同じ場合 or ピボットコントロールのキーフレームがターゲットよりも小さい場合＝前範囲の元アニメーションを維持する必要のない場合
            preservePreFrameRange = None;
        else:
            # ピボットコントロールのキーフレームがターゲットよりも大きい場合＝前範囲の元アニメーションを維持する必要がある場合
            preservePreFrameRange = [targetStartF, pivotStartF];

        preserveAfterFrameRange = [];
        if targetEndF <= pivotEndF:
            preserveAfterFrameRange = None;
        else:
            preserveAfterFrameRange = [pivotEndF+1, targetEndF+1];

        # bake
        cmds.bakeResults(targetCtrl, t=(pivotStartF, pivotEndF), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False);

        keyFrameDict = {};
        # 保持したアニメーションを再適用
        if not preservePreFrameRange is None:
            for i in range(preservePreFrameRange[0], preservePreFrameRange[1]):
                locTrans = cmds.getAttr("{}.translate".format(animPreserveLoc), time=i)[0];
                locRot = cmds.getAttr("{}.rotate".format(animPreserveLoc), time=i)[0];

                keyFrameDict[i] = [locTrans, locRot];

        if not preserveAfterFrameRange is None:
            for i in range(preserveAfterFrameRange[0], preserveAfterFrameRange[1]):
                locTrans = cmds.getAttr("{}.translate".format(animPreserveLoc), time=i)[0];
                locRot = cmds.getAttr("{}.rotate".format(animPreserveLoc), time=i)[0];

                keyFrameDict[i] = [locTrans, locRot];

        # set Preserved keyFrames
        for frame, values in keyFrameDict.items():
            for i, axis in enumerate(AXIS_LIST):
                cmds.setKeyframe(targetCtrl, value=values[0][i], time=frame, at="translate{}".format(axis));
                cmds.setKeyframe(targetCtrl, value=values[1][i], time=frame, at="rotate{}".format(axis));

        # delete pivot rig
        self.deleteRig(pivotCtrl, targetCtrl);

        cmds.undoInfo(closeChunk=True);

    def delete(self):
        """生成したpivotCtrlを削除する関数

        pivotCtrlを削除する。
        ウィジェットでのスロット設定、undoInfoコマンド、他の関数からの呼び出しの都合上実処理は切り出し。        

        Args:
            None
        Returns:
            None
        """

        cmds.undoInfo(openChunk=True);

        self.deleteRig();

        cmds.undoInfo(closeChunk=True);

    def deleteRig(self, pivotCtrl=None, targetCtrl=None):
        """生成したpivotCtrlを削除する関数

        pivotCtrlを削除する。
        ウィジェットでのスロット設定、undoInfoコマンド、他の関数からの呼び出しの都合上実処理は切り出し。        

        Args:
            pivotCtrl: (string): このツールにより生成されるピボットコントローラ名文字列。
            targetCtrl: (string): pivotCtrl下で操作したいターゲットとなるコントローラ名文字列。
        Returns:
            None
        """

        if pivotCtrl is None and targetCtrl is None:
            pivotCtrl, targetCtrl = self.getPivotCtrlAndTargetCtrl();

        animPreserveLoc = cmds.ls("{}_animPreserve_loc".format(targetCtrl))[0];
        cmds.delete(animPreserveLoc);

        # breakConnection
        tempNull = cmds.group(em=True);
        cmds.matchTransform(tempNull, targetCtrl, pos=True, rot=True);

        # delete
        cmds.delete(pivotCtrl + OFFSET_GRP_SUFFIX);

        cmds.matchTransform(targetCtrl, tempNull, pos=True, rot=True);

        cmds.delete(tempNull);

        # check pivotCtrlGrp
        pivotCtrlGrp = cmds.ls(PIVOT_CTRL_GRP);
        if (not pivotCtrlGrp is None) and len(pivotCtrlGrp) > 0:
            pivotCtrlGrp = pivotCtrlGrp[0];
            children = cmds.listRelatives(pivotCtrlGrp, c=True);
            if children is None:
                cmds.delete(pivotCtrlGrp);

    def getPivotCtrlAndTargetCtrl(self):
        """選択からピボットコントローラ、その名称からターゲットとなるコントローラ名を取得する関数

        選択からピボットコントローラ、その名称からターゲットとなるコントローラ名を取得し、それぞれをリストで返す。

        Args:
            None
        Returns:
            pivotCtrl: (string): ピボットコントローラ名文字列
            targetCtrl: (string): ピボットコントローラ下の対象となるコントローラ名文字列
        """

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

    def checkKeyframeRange(self, target):
        startF = cmds.findKeyframe(target, which="first");
        endF = cmds.findKeyframe(target, which="last");

        return int(startF), int(endF);

    def createCtrlCurve(self, targetName, shapeNum):
        """カーブオプション引数から、指定のシェイプを持ったコントローラカーブを作成する

        カーブオプション引数から、指定のシェイプを持ったコントローラカーブを作成する
        1031時点。十字、球形、八面体。


        Args:
            pivotCtrl: (string): このツールにより生成されるピボットコントローラ名文字列。
            targetCtrl: (string): pivotCtrl下で操作したいターゲットとなるコントローラ名文字列。
        Returns:
            ctrlCurve: (string): この関数により作成したコントローラカーブ名文字列。
        """

        if shapeNum == SHAPE_ENUM_CROSS:
            ctrlCurve = cmds.curve(name="{}{}".format(targetName, PIVOT_CTRL_SUFFIX),d=1,
            p=[(-1.0, 0.0, 0.0), (1.0, 0.0, 0.0),(0.0, 0.0, 0.0),(0.0, 0.0, 1.0),(0.0, 0.0, -1.0),(0.0, 0.0, 0.0),(0.0, 1.0, 0.0), (0.0, -1.0, 0.0)],
            k=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]);

        elif shapeNum == SHAPE_ENUM_SPHERE:
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
        
        elif shapeNum == SHAPE_ENUM_OCTAHEDRON:
           ctrlCurve = cmds.curve(name="{}{}".format(targetName, PIVOT_CTRL_SUFFIX),d=1,
            p=[(0.0, 1.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), 
                (0.0, -1.0, 0.0), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (1.0, 0.0, 0.0)],
            k=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0])

        return ctrlCurve;

# show ui
def showUi():
    """本ツールのメインウィンドウを表示する関数

    本ツールのメインウィンドウを表示する関数

    Args:
        None
    Returns:
        None

    """
    mainUi = MainWindow();
    mainUi.show();