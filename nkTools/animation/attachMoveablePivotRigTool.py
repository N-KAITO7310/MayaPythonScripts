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
import math;

"""

AttachMoveablePivotRigTool

created: 2023/01/30
last updated: 2023/09/16
updateContent: ベイク処理を高速化(ogsコマンド等追加)

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

import nkTools.animation.attachMoveablePivotRigTool as pivotRig;
reload(pivotRig);
pivotRig.showUi();

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

mainUi = None;

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

    shapeComboIndex = 0;

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
        self.__createLocatorButton.clicked.connect(createLocator);
        self.__createCtrlButton.clicked.connect(attachMoveablePivotRig);
        self.__bakeButton.clicked.connect(bakeApply);
        self.__deleteButton.clicked.connect(deleteRig);
        self.__shapeCombo.currentIndexChanged.connect(self.setShapeComboCurrentIndex);

    def setShapeComboCurrentIndex(self):
        self.shapeComboIndex = self.__shapeCombo.currentIndex();


def createLocator():
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

def attachMoveablePivotRig():
    """外付けPivotリグをロケーター名に対応したコントローラに対しアタッチする関数

    外付けPivotコントローラノード群を生成し、階層変更は行わず対象となるコントローラへ接続を行う

    01/23 FBによる修正
    ・元アニメーション保持ロケータを作成しペアレント
    ・ターゲットと原点位置が同一になるようフリーズ
    ・ターゲットを親としてロケータにベイク

    Args:
        None
    Returns:
        None
    """

    global mainUi;

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
    shapeNum = mainUi.shapeComboIndex;
    pivotCtrl = createCtrlCurve(targetCtrlName, shapeNum);
    cmds.parent(pivotCtrl, pivotCtrlOffsetGrp);

    # loc scale attr
    cmds.setAttr("{}.scale".format(pivotCtrl), lock=True);

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
    # ＊matrixで取得しxformでセットするとターゲットの０位置がずれる現象があったためtranslation, rotationでそれぞれ取得
    # om.MTransformationMatrixを使用した場合translationの値が同一にならない現象があったため以下で実装
    targetCurrentTrans = cmds.xform(targetCtrlName, q=True, translation=True);
    targetCurrentRot = cmds.xform(targetCtrlName, q=True, rotation=True);
    zeroMat = om.MMatrix();
    cmds.xform(targetCtrlName, matrix=zeroMat);
    cmds.matchTransform(animPreserveLoc, targetCtrlName, pos=True, rot=True);
    cmds.makeIdentity(animPreserveLoc, translate=True, rotate=True, apply=True);
    cmds.xform(targetCtrlName, translation=targetCurrentTrans);
    cmds.xform(targetCtrlName, rotation=targetCurrentRot);

    tempPConst = cmds.parentConstraint(targetCtrlName, animPreserveLoc, mo=False);
    targetStartF, targetEndF = checkKeyframeRange(targetCtrlName);

    if not(targetStartF is None) and not(targetEndF is None):
        cmds.evaluationManager(mode="off");
        cmds.ogs(pause=True);
        cmds.bakeResults(animPreserveLoc, t=(targetStartF, targetEndF), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False);
        cmds.ogs(pause=True);
        cmds.evaluationManager(mode="parallel");

    cmds.delete(tempPConst);
    cmds.setAttr("{}.visibility".format(animPreserveLoc), 0);

    # connect targetRig pivotRigSystem
    cmds.parentConstraint(parentObj, pivotCtrlOffsetGrp, mo=True);

    # cmds.connectAttr("{}.matrixSum".format(multMat), "{}.offsetParentMatrix".format(targetCtrlName));
    pConst = cmds.parentConstraint(targetOffsetGrp, targetCtrlName, mo=True);

    cmds.delete(pivotPosLoc);
    cmds.select(cl=True);

    cmds.undoInfo(closeChunk=True);

def getTopParentCtrl(targetCtrl):
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

def bakeApply():
    """対象のコントローラにベイク処理を行い、Pivotコントローラを削除する関数
    
    対象コントローラへpivotCtrlからの座標変換をベイクする。
    
    01/23 FBによる修正
    ・元アニメーション保持ロケータとpivotCtrlのキーフレーム範囲から保持する範囲を決定
    ・ロケータを親としてターゲットに必要範囲でベイク

    Args:
        None
    Returns:
        None
    """

    cmds.undoInfo(openChunk=True);

    # ベイクしたいpivotCtrlを選択して実行
    pivotCtrl, targetCtrl = getPivotCtrlAndTargetCtrl();

    # アニメーション保持用ロケータを取得
    animPreserveLoc = cmds.ls("{}_animPreserve_loc".format(targetCtrl))[0];

    # キーフレーム範囲の取得。pivotCtrlからbakeを行うframe範囲の決定。
    targetStartF, targetEndF = checkKeyframeRange(animPreserveLoc);
    pivotStartF, pivotEndF = checkKeyframeRange(pivotCtrl);

    # check pivotCtrl keyframe
    if pivotStartF is None and pivotEndF is None:
        om.MGlobal.displayError("Please keyframe pivotController 2 or more");
        return;
    # bake
    cmds.evaluationManager(mode="off");
    cmds.ogs(pause=True);
    cmds.bakeResults(targetCtrl, t=(pivotStartF, pivotEndF), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False);
    cmds.ogs(pause=True);
    cmds.evaluationManager(mode="parallel");

    # 保持したアニメーションを再適用
    bakePreservedAnimation(targetCtrl=targetCtrl, animPreserveLoc=animPreserveLoc, targetStartF=targetStartF, targetEndF=targetEndF, pivotStartF=pivotStartF, pivotEndF=pivotEndF);
    
    # delete pivot rig
    deleteRig(pivotCtrl, targetCtrl);

    cmds.undoInfo(closeChunk=True);

def delete():
    """生成したpivotCtrlを削除する関数

    pivotCtrlを削除する。
    ウィジェットでのスロット設定、undoInfoコマンド、他の関数からの呼び出しの都合上実処理は切り出し。        

    Args:
        None
    Returns:
        None
    """

    cmds.undoInfo(openChunk=True);

    deleteRig();

    cmds.undoInfo(closeChunk=True);

def deleteRig(pivotCtrl=None, targetCtrl=None):
    """生成したpivotCtrlを削除する関数

    pivotCtrlを削除する。
    ウィジェットでのスロット設定、undoInfoコマンド、他の関数からの呼び出しの都合上実処理は切り出し。        

    Args:
        pivotCtrl: (string): このツールにより生成されるピボットコントローラ名文字列。
        targetCtrl: (string): pivotCtrl下で操作したいターゲットとなるコントローラ名文字列。
    Returns:
        None
    """

    selected = cmds.ls(sl=True)[0];
    selectedShape = cmds.listRelatives(s=True)[0];
    if cmds.objectType(selectedShape) == "locator":
        cmds.delete(selected);
        return;
    else:
        if pivotCtrl is None and targetCtrl is None:
            pivotCtrl, targetCtrl = getPivotCtrlAndTargetCtrl();

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

def getPivotCtrlAndTargetCtrl():
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

def checkKeyframeRange(target):
    """引数オブジェクトにセットされているキーフレーム範囲を取得する関数

    引数オブジェクトにセットされているキーフレームの開始値、終了値を取得し返す

    Args:
        target: (string): キーフレーム範囲を取得したい対象となるオブジェクト名
    Returns:
        startF: (int): キーフレーム開始値
        endF: (int): キーフレーム終了値
    """

    # check this obj has keyframe
    notExistKeyFrame = True if cmds.keyframe(target, q=True, keyframeCount=True) == 0 else False;
    if notExistKeyFrame:
        return None, None;

    startF = cmds.findKeyframe(target, which="first");
    endF = cmds.findKeyframe(target, which="last");

    # キーフレームが一つの場合はサポートせず、０と同一とみなす
    if startF == endF:
        return None, None;

    return int(startF), int(endF);

def bakePreservedAnimation(targetCtrl, animPreserveLoc, targetStartF, targetEndF, pivotStartF, pivotEndF):
    """pivotCtrlのキーフレーム取得した範囲をもとに保持アニメーションを再適用する関数

        pivotCtrlのキーフレーム取得した範囲をもとに保持アニメーションを再適用する

    Args:
        targetCtrl: (string): このツールにより生成されるピボットコントローラ名文字列。
        animPreserveLoc: (string): アニメーションを保持したロケーターオブジェクト
        targetStartF: (int): ターゲットコントローラのキーフレーム開始値
        targetEndF: (int): ターゲットコントローラのキーフレーム終了値
        pivotStartF: (int): ピボットコントローラのキーフレーム開始値
        pivotEndF: (int): ピボットコントローラのキーフレーム終了値
    Returns:
        None
    """

    # check(pivotCtrlについてはキーフレームがあることを前提)
    if targetStartF is None and targetEndF is None:
        # 元アニメーションが存在しなければ終了
        om.MGlobal.displayInfo("target Controller has not keyframe. skip bake preserved animation");
        return True;

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

    keyFrameDict = {};
    # 保持したアニメーションを再適用
    if not preservePreFrameRange is None:
        for i in range(preservePreFrameRange[0], preservePreFrameRange[1]):
            locTrans = cmds.getAttr("{}.translate".format(animPreserveLoc), time=i)[0];
            locRot = cmds.getAttr("{}.rotate".format(animPreserveLoc), time=i)[0];

            keyFrameDict[i] = [locTrans, locRot];

        om.MGlobal.displayInfo("baked preserved animation. pre range: {} to {}".format(preservePreFrameRange[0], preservePreFrameRange[1]-1));

    if not preserveAfterFrameRange is None:
        for i in range(preserveAfterFrameRange[0], preserveAfterFrameRange[1]):
            locTrans = cmds.getAttr("{}.translate".format(animPreserveLoc), time=i)[0];
            locRot = cmds.getAttr("{}.rotate".format(animPreserveLoc), time=i)[0];

            keyFrameDict[i] = [locTrans, locRot];

        om.MGlobal.displayInfo("baked preserved animation. afeter range: {} to {}".format(preserveAfterFrameRange[0], preserveAfterFrameRange[1]-1));

    if preservePreFrameRange is None and preserveAfterFrameRange is None:
        om.MGlobal.displayInfo("skip bake preserved animation");

    # set Preserved keyFrames
    for frame, values in keyFrameDict.items():
        for i, axis in enumerate(AXIS_LIST):
            cmds.setKeyframe(targetCtrl, value=values[0][i], time=frame, at="translate{}".format(axis));
            cmds.setKeyframe(targetCtrl, value=values[1][i], time=frame, at="rotate{}".format(axis));

def createCtrlCurve(targetName, shapeNum):
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
    global mainUi;

    mainUi = MainWindow();
    mainUi.show();