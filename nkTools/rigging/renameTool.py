# -*- coding: utf-8 -*-
"""
RenameTool
version.1.0
created: 2022/10/23

UIに入力したPrefixと、対象オブジェクトのオブジェクトタイプからリネームを行う簡易ツール。
オプションとして対象を階層か選択かを付随。

ScriptEditorUse:
from nkTools.rigging import renameTool;
reload(renameTool);
renameTool.showUi();

"""

from __future__ import absolute_import, division, generators, print_function, unicode_literals
try:
    from future_builtins import *
except:
    pass
import sys
sys.dont_write_bytecode = True

from maya import OpenMayaUI, cmds, mel;
from PySide2 import QtWidgets, QtCore;
import maya.OpenMayaUI as omui;
import shiboken2;
import maya.api.OpenMaya as om;
import os;
import subprocess;
from functools import partial;
import maya.api.OpenMayaAnim as oma;

# constants
SUFFIX_JNT = "_jnt";
SUFFIX_CTRL = "_ctrl";
SUFFIX_GEO = "_geo";
SUFFIX_GRP = "_grp";
SUFFIX_LOCATOR = "_loc";
OBJECTTYPE_TRANSFORM = "transform";
OBJECTTYPE_JOINT = "joint";
OBJECTTYPE_CURVE = "nurbsCurve";
OBJECTTYPE_GEO = "mesh";
OBJECTTYPE_LOCATOR = "locator"
FKIK_PREFIX = ["_fk", "_FK", "_IK", "_fk"];


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

    UI_NAME = "Rename Tool V1";

    def __init__(self, parent=getMayaWindow()):
        """ウィンドウクラスのinit

        この関数で行っていること
        ・ウィンドウタイトル設定
        ・UIサイズ設定
        ・縦並びレイアウト設定
        ・各ボタンと押下時のメソッドバインド、レイアウトへのセット
        ・workspaceControlを利用したウィンドウ設定

        Args:
            parent: (QtWidgets.QWidget): 親ウィンドウとして設定するインスタンス
        Returns:
            None
        
        """
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
        self.__OperationComboBox = QtWidgets.QComboBox(self);
        self.__OperationComboBox.addItems(["Selected", "Hierarchy"]);

        self.__renameButton = QtWidgets.QPushButton(self);
        self.__renameButton.setText("Rename");

    def createLayout(self):
        mainLayout = QtWidgets.QFormLayout(self);

        mainLayout.addRow("Prefix", self.__textbox);
        mainLayout.addRow("Operation", self.__OperationComboBox);
        mainLayout.addRow(self.__renameButton);

    def createConnections(self):
        self.__renameButton.clicked.connect(self.rename);

    def rename(self):
        cmds.undoInfo(openChunk=True);

        selected =  cmds.ls(sl=True);
        target = selected[0];
        if len(selected) < 1:
            om.MGlobal.displayError("Please select rename target");
            return;
        else:
            target = selected[0];

        prefix = self.__textbox.text();
        if prefix is None or prefix == "":
            om.MGlobal.displayError("Please Input Prefix Text");
            return;

        targets = [];
        if self.__OperationComboBox.currentIndex() == 0:
            # selected
            targets = selected;
            
        elif self.__OperationComboBox.currentIndex() == 1:
            # hierarchy
            targets = [target];
            objType = cmds.objectType(targets[0]);
            childExist = True;

            while childExist:
                children = cmds.listRelatives(target, c=True, s=False);
                print(children)
                if (not children is None) and len(children) == 1:
                    child = children[0];

                    # check object type and children
                    childObjType = cmds.objectType(child);
                    if not objType == childObjType:
                        childExist = False;
                        break;

                    targets.append(child);
                    target = child;
                
                else:
                    childExist = False;
                    break;

        for i, target in enumerate(targets):
            index = str(i + 1);
            suffix = "";

            objType = cmds.objectType(target);
            if objType == OBJECTTYPE_JOINT:
                suffix = SUFFIX_JNT;
            elif objType == OBJECTTYPE_TRANSFORM:
                shape = cmds.listRelatives(target, s=True)[0];
                shapeType = cmds.objectType(shape);
                if shapeType == OBJECTTYPE_GEO:
                    suffix = SUFFIX_GEO;
                elif shapeType == OBJECTTYPE_CURVE:
                    suffix = SUFFIX_CTRL;
            elif objType == OBJECTTYPE_LOCATOR:
                suffix = SUFFIX_LOCATOR;

            newName = prefix + str(i+1) + suffix;
            
            for fkikPrefix in FKIK_PREFIX:
                if fkikPrefix in prefix:
                    newName = prefix.split(fkikPrefix)[0] + str(i+1) + fkikPrefix + suffix;

            cmds.rename(target, newName);
        cmds.undoInfo(closeChunk=True);


def showUi():
    mainUi = MainWindow();
    mainUi.show();