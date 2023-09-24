# -*- coding: utf-8 -*-
"""
    FixPvCtrlPosTool

    created: 2022/01/16
    lastUpdated: 2023/09/16
    updateContent 2023/09/16: pvCtrlがフリーズされたものである場合のズレを修正。
    updateContent 2023/09/17: 複数選択した場合に1度のフレームイテレーションで完了するよう修正。また、それに伴い1つ目に選択したオブジェクトのキーを参照してレンジを決定するように変更。

    要件定義
    概要:
    PoleVectorコントローラーの位置を調整するスクリプト
    例:足IKの例
    脚の付け根(hipジョイント)A点・膝B点・くるぶしC点の三点ABCで定義される三角形で、
    底辺ACから点Bを通る垂線ベクトルVを定義する。

    依頼:
    PoleVectorコントローラーは、このベクトルV上になる様に位置を調整する。
    しかし、あまり遠くに行きすぎても困るので、現状の点A⇒poleVectorコントローラーの位置で定義されるベクトルV2とベクトルVの交点部分に移動させるか、
    ベクトルV2の長さと同じ長さの距離になる、点AからベクトルV上の点上に移動するのが良い。

    恐らく見た目は後者の、ベクトルV2の長さと同じ距離の点AからベクトルV上の点に移動する方がよさそう。

    python2
    import nkTools.animation.fixPvCtrlPosTool as fixPv;
    reload(fixPv);
    fixPv.showUi();

    python3
    import nkTools.animation.fixPvCtrlPosTool as fixPv;
    import importlib;
    importlib.reload(fixPv);
    fixPv.showUi();

"""

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

WINDOW_TITLE = "FixPvController Tool Window";
TARGET_JNTS = ["hip", "knee", "foot"];
LEFT_PREFIX = "L_"
RIGHT_PREFIX = "R_"
NAMESPACE_SEPARATOR = ":";
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
    """メインウィンドウクラス
    
    本ツールのメインウィンドウクラス

    Attributes:
        UI_NAME: 表示されるウィンドウ名

    """
    
    UI_NAME = "FixPvController Tool Window";
    nameSpaceText = ":";


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
        self.setMinimumSize(200, 50);
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

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

        self.__nameSpaceText = QtWidgets.QLineEdit(self);
        self.__nameSpaceSetButton = QtWidgets.QPushButton(self);
        self.__nameSpaceSetButton.setText("Set NameSpace");

        self._applyButton = QtWidgets.QPushButton(self);
        self._applyButton.setText("Fix Pv Controller");

    def createLayout(self):
        """レイアウト設定関数
        
        生成したWidgetクラスをレイアウトに設定する

        Args:
            None
        Returns:
            None
        
        """

        mainLayout = QtWidgets.QGridLayout(self);
        mainLayout.addWidget(self.__nameSpaceText, 0, 0);
        mainLayout.addWidget(self.__nameSpaceSetButton, 0, 1);
        mainLayout.addWidget(self._applyButton, 1, 0, 1, 2);
        
    def createConnections(self):
        """スロット設定関数
        
        各ウィジェットのスロットに関数を設定する

        Args:
            None
        Returns:
            None
        """

        self._applyButton.clicked.connect(fixPvCtrlPos);
        self.__nameSpaceSetButton.clicked.connect(self.setNameSpace);

    def setNameSpace(self):
        """テキストボックスへnameSpaceをセットする関数
        
        選択オブジェクトからnameSpaceを抽出し、テキストボックスへ入力する

        Args:
            None
        Returns:
            None
        
        """
        sel = cmds.ls(sl=True);
        if sel is None or len(sel) == 0:
            om.MGlobal.displayError("Please Select Object");
            return;

        sel = sel[0];

        nameSpace = sel.rpartition(":");
        if nameSpace[1] == "":
            nameSpace = ":";
        else:
            nameSpace = nameSpace[0] + NAMESPACE_SEPARATOR;

        self.__nameSpaceText.setText(nameSpace);
        self.nameSpaceText = nameSpace;

def fixPvCtrlPos():
    """ 腿、膝、足ジョイント位置から算出した位置にPVコントローラーを移動しキーを打つ

        腿、膝、足ジョイント位置からPVコントローラーの位置を算出し、移動後に新しくキーをセットする

        処理フロー
        ・PVコントローラを選択させたうえで実行
            ・対象となる腿、膝、足首ジョイントの名前は決め打ち←こちらで対応
            ・or pvConstraintされているikHandleのstartから取得する
        ・選択各コントローラでfor
            ・PVコントローラーのキーフレームから計算範囲を決定
            ・各フレームにおける適切な位置を腿、膝、足首から計算して移動
            ・足が伸び切っている場合、算出されたベクトルが反対側となる場合が見られたため、チェックと対応処理
            ・キーフレームをセット

        Args:
            None
        Returns:
            None
    
    """
    global mainUi;

    cmds.undoInfo(openChunk=True);

    # selection check
    selected = cmds.ls(sl=True);
    if selected is None or len(selected) == 0:
        om.MGlobal.displayError("Please Select Pv Controller");
        return;

    nameSpace = mainUi.nameSpaceText;

    currentF = cmds.currentTime(q=True);
    # get frame range
    startF = cmds.findKeyframe(selected[0], which="first");
    endF = cmds.findKeyframe(selected[0], which="last");
        
    # take measures for fleeze pvCtrl＊コントローラーがフリーズされている場合xformによる適切なワールド位置情報を取得、セットできないため:23/09/16修正
    tempLoc = cmds.spaceLocator()[0];

    for frame in range(int(startF), int(endF) + 1):
        cmds.currentTime(frame);
        for pvCtrl in selected:
            # obj check
            shape = cmds.listRelatives(pvCtrl, shapes=True)[0];
            if not (cmds.objectType(pvCtrl) == "transform") or not (cmds.objectType(shape) == "nurbsCurve"):
                om.MGlobal.displayError("{} is not nurbsCurve Controller".format(pvCtrl));
                continue;

            # side check
            sidePrefix = "";
            if LEFT_PREFIX in pvCtrl:
                sidePrefix = LEFT_PREFIX;
            else:
                sidePrefix = RIGHT_PREFIX;

            # 対象ジョイントを定数ではなくpvConstから得られ、脚部のジョイント階層が3joint構成のリグに関しては以下を使用
            # get ikJoint hip to foot
            pvConst = cmds.listConnections(pvCtrl, type="poleVectorConstraint", source=False, destination=True)[0];
            ikHandle = cmds.listConnections(pvConst, type="ikHandle", source=False, destination=True)[0];

            hipJnt = cmds.ikHandle(ikHandle, q=True, startJoint=True);
            kneeJnt = cmds.listRelatives(hipJnt, c=True, typ="joint")[0];
            footJnt = cmds.listRelatives(kneeJnt, c=True, typ="joint")[0];

            # 対象ジョイントを定数で指定する場合はコメントアウトした以下を使用
            # hipJnt = nameSpace + sidePrefix + TARGET_JNTS[0];
            # kneeJnt = nameSpace + sidePrefix + TARGET_JNTS[1];
            # footJnt = nameSpace + sidePrefix + TARGET_JNTS[2];
            
            # ＊以下依頼のあったリグに対しての特殊対応を考慮した記述20230916
            # このikHandleから求められるik膝ジョイントはskin膝ジョイント位置が異なるための対応(例：位置においてDummy_R_knee＝R_knee)
            # kneeConst = cmds.listConnections(kneeJnt, type="orientConstraint")[0];
            # dummyKneeJnt = cmds.listConnections(kneeConst, type="joint")[0];
            # kneeJnt = cmds.listConnections(dummyKneeJnt, type="joint")[0];


            # 内積計算、底面～三角形上頂点までのベクトルを取得、正規化、pvCtrlまでの距離で乗算
            # culc pv position
            # get vec
            hipJntVec = om.MVector(cmds.xform(hipJnt, q=True, ws=True, t=True));
            kneeJntVec = om.MVector(cmds.xform(kneeJnt, q=True, ws=True, t=True));
            footJntVec = om.MVector(cmds.xform(footJnt, q=True, ws=True, t=True));
            cmds.matchTransform(tempLoc, pvCtrl)
            pvCtrlVec = om.MVector(cmds.xform(tempLoc, q=True, ws=True, t=True));

            # get length
            hipToKneeVec = kneeJntVec - hipJntVec;
            hipToFootVec = footJntVec - hipJntVec;

            # normalize
            hipToFootLenNormalized = hipToFootVec.normalize();

            # dot product
            dotProd = hipToKneeVec * hipToFootVec;
            dotProdVec = (hipToFootLenNormalized * dotProd) + hipJntVec;
            dotToKneeVec = kneeJntVec - dotProdVec;
            dotToKneeVecNormalized = dotToKneeVec.normalize();

            # vector hip to pvCtrl
            hipToPvCtrlVec = pvCtrlVec - hipJntVec;
            hipToPvCtrlVecLen = hipToPvCtrlVec.length();

            # check whether this vector is opposite
            # sideAdjust = 1;
            # kneeRotZ = cmds.getAttr("{}.rz".format(kneeJnt));
            # if kneeRotZ > 0:
            #     sideAdjust = -1;

            # culc result = 内積位置 + 内積位置からひざジョイントへのベクトル(正規化、ノルム１) * ももジョイントからpvCtrlへのベクトル長 * 配置する側を調整するための値
            resultPvPoint = dotProdVec + (dotToKneeVecNormalized * hipToPvCtrlVecLen*1.2)

            # move target ctrl and set keyframe
            cmds.xform(tempLoc, t=resultPvPoint, ws=True);
            cmds.matchTransform(pvCtrl, tempLoc);

            cmds.setKeyframe(pvCtrl, at="translate");

    cmds.currentTime(currentF);
    cmds.delete(tempLoc);

    cmds.undoInfo(closeChunk=True);

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