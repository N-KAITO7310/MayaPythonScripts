# -*- coding: utf-8 -*-

"""
ModelCleanupTool

Description:
書籍「Mayaキャラクターリギング」のリギングにおける事前確認事項に沿い、シーン内のモデルに対し、以下の処理を実行する。またモデラー向けに簡易的なリネーム機能を付随させている。
・すべてのメッシュデータへのフリーズ
・ヒストリ削除
・メッシュのクリーンナップコマンド
・オプティマイズシーンサイズ、
・不要なトランスフォームノード削除＊現状特定の場合に一部のシェイプを持たないトランスフォームノードが残る場合を確認。

# python2
import nkTools.modeling.modelCleanupTool as mo;
reload(mo);
mo.showUi();

# python3
import nkTools.modeling.modelCleanupTool as mo;
import importlib;
importlib.reload(mo);
mo.showUi();

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

    UI_NAME = "Modeling Cleanup Tool";

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
        self.__renameButton = QtWidgets.QPushButton(self);
        self.__renameButton.setText("Rename Geometry");

        self.__cleannupButton = QtWidgets.QPushButton(self);
        self.__cleannupButton.setText("Cleanup");

    def createLayout(self):
        mainLayout = QtWidgets.QVBoxLayout(self);

        mainLayout.addWidget(self.__textbox);
        mainLayout.addWidget(self.__renameButton);
        mainLayout.addWidget(self.__cleannupButton);

    def createConnections(self):
        self.__renameButton.clicked.connect(self.renameGeometry);
        self.__cleannupButton.clicked.connect(self.modelCleanup);

    def renameGeometry(self):
        cmds.undoInfo(openChunk=True);
        # TODO: per obj

        targets =  cmds.ls(sl=True);

        prefix = self.__textbox.text();
        if prefix is None or prefix == "":
            om.MGlobal.displayError("Please Input Prefix Text");
            return;

        for i, target in enumerate(targets):
            newName = prefix + str(i+1) + "_geo";
            cmds.rename(target, newName);

        cmds.undoInfo(closeChunk=True);


    def modelCleanup(self):
        cmds.undoInfo(openChunk=True);

        meshDataList = cmds.ls(type="mesh");
        for mesh in meshDataList:
            try:
                transform = cmds.listRelatives(mesh, parent=True, fullPath=True);
            except:
                continue;

            if transform is None:
                continue;
            else:
                transform = transform[0];

            flag = True;
            while flag:
                parent = cmds.listRelatives(transform, parent=True, fullPath=True);
                if parent is None:
                    flag = False;
                else:
                    transform = parent[0];

            cmds.delete(mesh, constructionHistory = True);
            cmds.makeIdentity(transform, apply=True, t=1 ,r=1, s=1, n=0, pn=1);
            cmds.select(mesh);
            mel.eval('polyCleanupArgList 4 { "0","1","1","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","2","1","0" };');
            cmds.select(cl=True);
            cmds.delete(mesh, constructionHistory = True);

        allTransObj = cmds.ls(type="transform");
        for transform in allTransObj:
            shape = cmds.listRelatives(transform, s=True);
            children = cmds.listRelatives(transform, c=True);
            # TODO: 表示されないシェイプノードは削除できない
            if  children is None and shape is None:
                cmds.delete(transform);

        mel.eval("cleanUpScene 3");

        print("cleanup completed!");

        cmds.undoInfo(closeChunk=True);

def showUi():
    mainUi = MainWindow();
    mainUi.show();