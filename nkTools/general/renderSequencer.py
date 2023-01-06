# -*- coding: utf-8 -*-
"""
    RenderSequencer

    lastUpdated: 2022/12/30
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
import math;

WINDOW_TITLE = "Render Sequencer";
FILE_FILTER = "*.mb";

# UI ------------------------------------------------------------------------------
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
    
class ConfirmWindow(QtWidgets.QDialog):
    """処理完了通知ウィンドウクラス
    
    出力処理の完了をユーザーに通知するためのクラス

    Attributes:
        None

    """

    def __init__(self, parent=getMayaWindow()):
        """処理完了通知ウィンドウクラスのinit

        ・ウィンドウタイトルの設定
        ・ウィンドウのレイアウトに関する設定
        ・ウィジェットクラスの生成
        ・レイアウトの設定
        ・シグナルへの関数設定

        Args:
            parent: (QtWidgets.QWidget): 親ウィンドウとして設定するインスタンス。デフォルトでMayaのウィンドウを指定。
        Returns:
            None
        
        """

        super(ConfirmWindow, self).__init__(parent)

        self.setWindowTitle("Confirm")

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.createWidgets()
        self.createLayout()
        self.createConnection()

    def createWidgets(self):
        """Widgetクラスの生成

        ボタン等各Widgetクラスを生成する

        Args:
            None
        Returns:
            None

        """

        self.confirmText = QtWidgets.QLabel(self);
        self.confirmText.setText("Completed!");

        self.okButton = QtWidgets.QPushButton(self);
        self.okButton.setText("OK");

    def createLayout(self):
        """レイアウト設定関数
        
        生成したWidgetクラスをレイアウトに設定する

        Args:
            None
        Returns:
            None
        
        """

        mainLayout = QtWidgets.QVBoxLayout(self);
        
        mainLayout.addWidget(self.confirmText);
        mainLayout.addWidget(self.okButton);

    def createConnection(self):
        """スロット設定関数
        
        各ウィジェットのスロットに関数を設定する

        Args:
            None
        Returns:
            None

        """

        self.okButton.clicked.connect(self.accept);

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

        self._applyButton = QtWidgets.QPushButton(self);
        self._applyButton.setText("Render Sequence");

    def createLayout(self):
        """レイアウト設定関数
        
        生成したWidgetクラスをレイアウトに設定する

        Args:
            None
        Returns:
            None
        
        """

        mainLayout = QtWidgets.QVBoxLayout(self);
        mainLayout.addWidget(self._applyButton);
        
    def createConnections(self):
        """スロット設定関数
        
        各ウィジェットのスロットに関数を設定する

        Args:
            None
        Returns:
            None
        """

        self._applyButton.clicked.connect(self.renderSequence);


    def renderSequence(self):
        """
        ・ファイルダイアログの表示と複数選択
        ・選択されたシーンファイルを強制で開く
        ・レンダーシークエンスコマンドの実行
        ・プログレスバーの更新
        ・処理のイテレーション
        ・完了ダイアログの表示
        """
        paths = self.getFiles();
        fileCount = len(paths);
        progressDialog = self.showProgressDialog();
        
        for i, path in enumerate(paths):

            amount = 0;
            cmds.progressWindow(title='Rendering ...', progress=amount, status='Processing: 0%', isInterruptable=True);

            result = self.openFile(path);
            if not result:
                om.MGlobal.displayError("Error!")
                return;

            # do render sequence
            startF = int(cmds.playbackOptions(q=True, min=True));
            endF = int(cmds.playbackOptions(q=True, max=True));

            frameLength = endF - startF + 1;
            progressCounter = 0;

            for f in range(startF, endF + 1):
                if  cmds.progressWindow(query = True, isCancelled = True) :
                    break;

                cmds.currentTime(f);
                # TODO: 出力先の指定(現状tmpフォルダに出力される問題がある)
                mel.eval('renderWindowRender redoPreviousRender renderView;');

                progressCounter += 1;
                amount = int(math.floor(f+1 / frameLength));
                cmds.progressWindow(e=True, progress=amount, status="Processing: {}% ({}/{})".format(amount, progressCounter, frameLength));

            progressValue = self.culcProgressValue(fileCount, i);
            self.updateProgressDialog(progressDialog, progressValue);

            cmds.progressWindow(endProgress=True);

        self.showConfirmWindow();
            
    
    def getFiles(self):
        """ファイル選択ダイアログを表示する関数

        ファイル選択ダイアログを表示する

        Args:
            None
        Returns:
            None

        """

        try:
            paths = cmds.fileDialog2(fileFilter=FILE_FILTER, fileMode=4, dialogStyle=2, caption="Select import fbx files");
        except:
            om.MGlobal.displayError("Error File Dialog");
            
        return paths;

    def openFile(self, path):
        try:
            cmds.file(path, open=True, force=True);
            return True;
        except:
            om.MGlobal.displayError("Fail Open File");
            return False;
    
    def showProgressDialog(self):
        """プログレスバーの表示関数
        
        プログレスバーを表示する

        Args:
            None
        Returns:
            None
        
        """

        progress = QtWidgets.QProgressDialog(self);
        progress.setWindowTitle("File Progress...");
        progress.setCancelButton(None);
        progress.setWindowFlags(progress.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        progress.show();

        return progress;

    def updateProgressDialog(self, progressDialog, value):
        """プログレスバーの更新処理

        プログレスバーの表示進捗率を更新する

        Args:
            progressDialog: プログレスバーのインスタンス
            value: 進捗率
        Returns:
            None
        
        """
        progressDialog.setValue(value);
        # QtWidgets.qApp.processEvents();
        QtWidgets.QApplication.processEvents();# maya2022

    def culcProgressValue(self, fileCount, index):
        """プログレスバーに表示する進捗率を計算する関数

        ファイルに対する繰り返し処理のindexと選択ファイルの全体数から進捗率を計算する

        Args:
            fileCount: 選択ファイルの数
            index: ファイルに対する繰り返し処理のindex
        Returns:
            int: 進捗率

        """
        return int(((index+1) / fileCount) * 100);

    def showConfirmWindow(self):
        """処理完了通知ウィンドウを表示する関数

        Args:
            None
        Returns:
            bool: ウィンドウインスタンスのexecの返り値
        
        """

        confirmWindow = ConfirmWindow();
        result = confirmWindow.exec_();

        return result;


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