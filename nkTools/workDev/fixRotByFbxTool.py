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

FixRotByFbxTool

import fixRotByFbxTool as fixRotByFbxTool;
reload(fixRotByFbxTool);
fixRotByFbxTool.showUi();

"""

WINDOW_TITLE = "FixRotByFbxTool";
FILE_FILTER = "*.fbx";
SPECIFIC_NAMESPACE = "CR_NAMESPACE";
TARGET_BODY_PART = ["thumb"];
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

        self.__nameSpaceText = QtWidgets.QLineEdit(self);
        self.__nameSpaceSetButton = QtWidgets.QPushButton(self);
        self.__nameSpaceSetButton.setText("NameSpace Set");

        self.__applyFixButton = QtWidgets.QPushButton(self);
        self.__applyFixButton.setText("Apply Fix");

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
        mainLayout.addWidget(self.__applyFixButton, 1, 0, 1, 2);

    def createConnections(self):
        """スロット設定関数
        
        各ウィジェットのスロットに関数を設定する

        Args:
            None
        Returns:
            None
        """

        self.__nameSpaceSetButton.clicked.connect(self.setNameSpace);
        self.__applyFixButton.clicked.connect(self.applyFix);

    def setNameSpace(self):
        sel = cmds.ls(sl=True);
        if sel is None or len(sel) == 0:
            om.MGlobal.displayError("Please Select Object");
            return;

        sel = sel[0];

        nameSpace = sel.rpartition(":");
        if not nameSpace[1] == ":":
            nameSpace = ":"

        self.__nameSpaceText.setText(nameSpace);

    def applyFix(self):
        """
        アニメーションシーンデータに対し実行
        出力済みのFBXデータを参照し、アニメーションをコンストレイントなどで修正する
        ネームスペースを指定した場合その指定したものに処理を限る

        ・ファイルダイアログ表示
        ・指定ファイルをリファレンスで読み込み＊既定のネームスペース
        ・修正処理
            ・リファレンスしたジョイントと、対応するコントローラを取得
            ・アニメーションデータが存在する範囲を取得
            ・対応するジョイントからコントローラへオリエントコンストレイント
            ・ベイク処理
            ・リファレンスの解除
            ・出力 or ベイクして終了？
        ・リファレンスデータを削除

        """
        targetNameSpace = self.__nameSpaceText.text();

        filePath = self.getFile();
        referencedData = cmds.file(filePath, reference=True, returnNewNodes=True, type="fbx", namespace=SPECIFIC_NAMESPACE);
        referencedJnts = [self.getPartialName(x) for x in referencedData if cmds.objectType(x) == "joint"];

        print(referencedJnts)

        corTable = {}; 
        for bodyPart in TARGET_BODY_PART:
            targetBodyPartJnts = [x for x in referencedJnts if bodyPart in x];
            print(targetBodyPartJnts)
            for fbxJnt in targetBodyPartJnts:
                jntName = fbxJnt.split(":")[-1];
                targetCtrlName = jntName + "_ctrl";
                targetCtrl = cmds.ls("{}:{}".format(targetNameSpace, targetCtrlName), type="transform");
                if (not targetCtrl is None) and len(targetCtrl) == 1:
                    corTable[fbxJnt] = targetCtrl[0];

        tempConstList = [];
        startF = 0;
        endF = 0;
        print(corTable)
        for fbxJnt, targetCtrl in corTable.items():
            cmds.cutKey(targetCtrl, attribute="rotate");
            skipAtts = self.checkLockedAttrs(targetCtrl, ROTATE_ATTRS);
            skipAxis = [x[-1] for x in skipAtts];
            tempConstList.append(cmds.orientConstraint(fbxJnt, targetCtrl, mo=False, skip=skipAxis)[0]);
            # TODO: 右側コントローラへの接続について回転値の反転が必要な可能性高
            """
            ・何をもって右側と判断するか
            ・スケール-1を利用した反転接続処理
            ・削除処理における適切なコネクション切断とノード削除

            composeMatrix, multMatrix, decomposeMatrix, quatToEuler, xyMinusScaleNull
            ＊ジョイントの位置自体が違う？該当するジョイント同士で直接コネクションすると明らかに位置が異なることがわかる＆回転と合わせぴったりする
            また、他のジョイントでもずれが顕著に確認できる？
            """

            # check keyframeRange
            sf = cmds.findKeyframe(fbxJnt, which="first");
            ef = cmds.findKeyframe(fbxJnt, which="last");

            if sf < startF:
                startF = sf;
            if ef > endF:
                endF = ef;
                
        return;
        # bake
        cmds.bakeResults(corTable.values(), t=(startF, endF), at=ROTATE_ATTRS, simulation=False);

        # cleanup
        cmds.delete(tempConstList);
        cmds.file(filePath, removeReference=True);

    def getFile(self):
        """ファイル選択ダイアログを表示する関数

        ファイル選択ダイアログを表示する

        Args:
            None
        Returns:
            None

        """

        try:
            paths = cmds.fileDialog2(fileFilter=FILE_FILTER, fileMode=4, dialogStyle=2, caption="Select a reference fbx file");
        except:
            om.MGlobal.displayError("Error File Dialog");
            
        if paths is None or len(paths) < 1:
                om.MGlobal.displayError("No file selected");

        path = paths[0];

        return path;

    def getPartialName(self, name):
            return name.split("|")[-1];

    def checkLockedAttrs(self, obj, attrs):
        lockedAttrs = [];
        for attr in attrs:
            isLocked = cmds.getAttr("{}.{}".format(obj, attr), lock=True);
            if isLocked:
                lockedAttrs.append(attr);
        return lockedAttrs;

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