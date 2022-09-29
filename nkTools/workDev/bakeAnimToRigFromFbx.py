# -*- coding: utf-8 -*-
"""
    要件定義
    ・FBXの骨アニメーションをキャラリグに戻し、アニメーションをベイクするToolを作成してください。

    処理
    ・骨から、コントローラへコンストレイントしてから、ベイクしてFBX

    処理フロー
    ・複数ファイル選択
    ・選択ファイルに対し、それぞれ以下の処理を実行
    ・シーン上のコントローラを取得
    ・コントローラ名に該当するボーンを取得し、ボーン：コントローラDictで格納
    ・各ボーンからコントローラへペアレントコンストレイント
    ・コントローラにベイク処理
    ・作成したコンストレイントノードを全て削除(ベイクに伴って削除される？)
    ・各ボーンに接続されているAnimCurveノードを全て削除
    ・各コントローラから対応するボーンへ対しコンストレイント(このコンストレイントは全てペアレントでよいのか？)
"""
# ------------------------------------------------------------------------------
from __future__ import absolute_import, division, generators, print_function, unicode_literals
from fileinput import filename
from hashlib import new
from tabnanny import check
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

# ------------------------------------------------------------------------------
# constant var
WINDOW_TITLE = "Bake Animation Tool";
ANIMCURVE_TYPES = ["animCurveTL", "animCurveTA", "animCurveTU"];
TRANSLATION_ATTRS = ["tx", "ty", "tz"];
ROTATE_ATTRS = ["rx", "ry", "rz"];
SCALE_ATTRS = ["sx", "sy", "sz"];
FILE_FILTER = "*.fbx";
FILE_EXTENSION = [".mb", ".ma", ".fbx"];
FILE_SUFFIX = "Test1";
CTRL_SUFFIX = "_c";
EXCEPTION_CONST_TABLE = {
    "L_arm" : ["L_arm_pole", True],
    "R_arm" : ["R_arm_pole", True],
    "L_leg" : ["L_leg_pole", True],
    "R_leg" : ["R_leg_pole", True],
    "L_foot" : ["L_foot_c", False],
    "R_foot" : ["R_foot_c", False],
}

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

# TODO: input text window
# class ModalWindow(QtWidgets.QDialog):
    
#     def __init__(self, parent=getMayaWindow()):
#         super(ModalWindow, self).__init__(parent)

#         self.setWindowTitle("Input NewFileName")

#         self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

#         self.createWidgets()
#         self.createLayout()
#         self.createConnection()

#     def createWidgets(self):
#         self.textBox = QtWidgets.QLineEdit(self);
#         self.okButton = QtWidgets.QPushButton(self);
#         self.okButton.setText("OK");

#     def createLayout(self):
#         mainLayout = QtWidgets.QVBoxLayout(self);
#         subLayout = QtWidgets.QFormLayout(self);
#         subLayout.addRow("NewFileName:", self.textBox);

#         mainLayout.addLayout(subLayout);
#         mainLayout.addWidget(self.okButton);

#     def createConnection(self):
#         self.okButton.clicked.connect(self.accept);

#     def getText(self):
#         return self.textBox.text();
    
class ConfirmWindow(QtWidgets.QDialog):
    
    def __init__(self, parent=getMayaWindow()):
        super(ConfirmWindow, self).__init__(parent)

        self.setWindowTitle("Confirm")

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.createWidgets()
        self.createLayout()
        self.createConnection()

    def createWidgets(self):
        self.confirmText = QtWidgets.QLabel(self);
        self.confirmText.setText("Done");

        self.okButton = QtWidgets.QPushButton(self);
        self.okButton.setText("OK");

    def createLayout(self):
        mainLayout = QtWidgets.QVBoxLayout(self);
        
        mainLayout.addWidget(self.confirmText);
        mainLayout.addWidget(self.okButton);

    def createConnection(self):
        self.okButton.clicked.connect(self.accept);

class MainWindow(QtWidgets.QDialog):
    
    UI_NAME = "Bake Animation Tool Window"

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
        self.setWindowTitle(WINDOW_TITLE);
        self.setObjectName(self.__class__.UI_NAME);
        self.setMinimumSize(200, 50);
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)


        self.createWidgets();
        self.createLayout();
        self.createConnections();

    def createWidgets(self):
        self._applyButton = QtWidgets.QPushButton(self);
        self._applyButton.setText("BakeAnimation");

    def createLayout(self):
        mainLayout = QtWidgets.QVBoxLayout(self);

        mainLayout.addWidget(self._applyButton);

    def createConnections(self):
        self._applyButton.clicked.connect(self.bakeAnimation);

    def bakeAnimation(self):
        """
        処理フロー
        ・複数ファイル選択
        ・選択ファイルに対し、それぞれ以下の処理を実行
        ・シーン上のコントローラを取得
        ・コントローラ名に該当するボーンを取得し、ボーン：コントローラDictで格納
        ・各ボーンからコントローラへペアレントコンストレイント
        ・コントローラにベイク処理
        ・作成したコンストレイントノードを全て削除(ベイクに伴って削除される？)
        ・各ボーンに接続されているAnimCurveノードを全て削除
        ・各コントローラから対応するボーンへ対しコンストレイント(このコンストレイントは全てペアレントでよいのか？)
        """
        # インポートファイル選択
        files = self.getFiles();
        if files is None:
            om.MGlobal.displayError("No file selected")
            return;

        # インポート元ファイルパス取得
        currentPath = cmds.file(q=True, exn=True);

        # 保存先ディレクトリ指定
        saveDirectory = self.specifyFilePath();
        if saveDirectory is None:
            om.MGlobal.displayError("No Directory selected")
            return;

        # progress bar
        progress = self.showProgressDialog();
        fileCount = len(files);

        for i, filePath in enumerate(files):
            # Import animation file
            imported = cmds.file(filePath, i=True, type="fbx", returnNewNodes=True, ignoreVersion=True, renameAll=True, mergeNamespacesOnClash=False, options="fbx", pr=True);
            
            importedJnts = self.extractJnts(imported);
            importedJnts = self.convertPartialPathName(importedJnts);
            if len(imported) < 1:
                cmds.delete(imported);
                continue;

            # リグ・ジョイント情報の取得
            jntCtrlTable = self.analyzeRig(importedJnts);
            jntCtrlTable = self.addExceptionToTable(jntCtrlTable);

            # ジョイントからコントローラーへ接続
            tempConsts = self.iterConnection(jntCtrlTable);

            # ベイク処理
            ctrlList = [];
            for key in jntCtrlTable:
                values = jntCtrlTable[key];
                for value in values:
                    ctrlList.append(value[0]);

            startF, endF = self.analyzeKeyfameRange(jntCtrlTable.keys());

            cmds.bakeResults(ctrlList, t=(startF, endF), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False);

            # インポートされたノードを削除
            cmds.delete(imported);

            # 保存処理
            # newFileName = self.showModalWindow();
            # if newFileName is None:
            #     om.MGlobal.displayError("Please Input New File Name");

            # oldFilePath ,newFilePath = self.saveAs(filePath, newFileName);
            fileName = self.getFileName(filePath);
            self.save(saveDirectory, fileName);

            progressValue = self.culcProgressValue(fileCount, i);
            self.updateProgressDialog(progress, progressValue);

            # 再度ファイルを開き直し処理を継続する
            cmds.file(currentPath, open=True, force=True);

        self.showConfirmWindow();

    def getFileName(self, path):
        return path.split("/")[-1];

    def getFiles(self):
        try:
            paths = cmds.fileDialog2(fileFilter=FILE_FILTER, fileMode=4, dialogStyle=2, caption="Select import fbx files");
        except:
            om.MGlobal.displayError("Error File Dialog");
            
        return paths;

    def specifyFilePath(self):
        # 保存先ディレクトリの指定
        try:
            path = cmds.fileDialog2(fileMode=3, dialogStyle=2, caption="Select save directory");
        except:
            om.MGlobal.displayError("Error File Dialog");
            
        if not path is None:
            return path[0];

        return path;

    def save(self, filePath, fileName):
        newFilePath = filePath + "/" + fileName;

        try:
            # ファイル保存処理
            cmds.file(rename=newFilePath);
            cmds.file(save=True, type='mayaBinary', force=True);

        except:
            om.MGlobal.displayError("Error save file");

        return True;

    # def saveAs(self, filePath, newFileName):
    #     oldFilePath = cmds.file(q=True, exn=True)
    #     newFilePath = "/".join(filePath.split("/")[:-1]) + "/" + newFileName;

    #     cmds.file(rename=newFilePath);
    #     cmds.file(save=True, type='mayaBinary', force=True);

    #     return oldFilePath, newFilePath;
        
    def extractJnts(self, objs):
        return [node for node in objs if cmds.objectType(node) == "joint"];
        
    def convertPartialPathName(self, objs):
        paths = [];
        
        for obj in objs:
            omSel = om.MSelectionList();
            omSel.add(obj);
            dagPath = omSel.getDagPath(0);
            path = dagPath.partialPathName();
            paths.append(path);
            
        return paths;

    def analyzeRig(self, importedJnts):
        """
        取得方法検討
        1. ジョイントとの接続から対応するコントローラーを特定
            ・s:のnamespaceがついていることを前提として、importしたジョイントと名前が一致するシーン内ジョイントを取得
            ・TranslateまたはRotateのプラグからたどる→基本は一つのペアレントコンストレイントと想定
            ・たどった先のコントローラーが対応コントローラとして保存
        2. ジョイントとコントローラーの対応表データをあらかじめハードコーディングまたはjsonで保存
            ・このサンプルデータ上では確実だが、名前の変更に際しての対応が煩雑になる
        """
        jntCtrlTable = {};
        nameSpace = "s:"
        
        mainJnts = [];
        for importedJnt in importedJnts:
            jntName = nameSpace + importedJnt;

            mainJnt = cmds.ls(jntName, type="joint");
            if not mainJnt is None and len(mainJnt) > 0:
                mainJnt = mainJnt[0];
                mainJnts.append(mainJnt);
            
        for mainJnt in mainJnts:
            doSearch = True;
            listConType = "parentConstraint"
            searchStartObj = mainJnt;

            while doSearch:
                # Translate, Rotateからコンストレイントノードを検索
                const = cmds.listConnections(searchStartObj, type=listConType, source=True, destination=False);
                if const is None:
                    break;
                else:
                    const = list(set(const))[0];

                # コンストレイントノードからコントローラを取得
                sourceCtrl = cmds.listConnections("{}.target[0].targetParentMatrix".format(const), source=True, destination=False);
                if sourceCtrl is None:
                    break;
                else:
                    sourceCtrl = sourceCtrl[0];

                # コントローラであれば、それを変数にセット
                if CTRL_SUFFIX in sourceCtrl and cmds.objectType(sourceCtrl) == "transform" :
                    # table{jntName: [{ctrlName: constraint maintainOffset}]}
                    jntCtrlTable[mainJnt[2:]] = [[sourceCtrl, False]];
                    doSearch = False;

                else:
                    searchStartObj = sourceCtrl;
                    listConType = "orientConstraint"

        return jntCtrlTable;

    def addExceptionToTable(self, dict):
        for key, value in EXCEPTION_CONST_TABLE.items():
            if key in dict:
                dict[key].append([value[0], value[1]]);
            else:
                dict[key] = [[value[0], value[1]]];

        return dict;

    def iterConnection(self, dict):
        createdConsts = [];

        for parent, children in dict.items():
            for child in children:
                isUnLockTrans = self.checkLockState(child[0], "tx");
                isUnLockRot = self.checkLockState(child[0], "rx");

                if isUnLockTrans:
                    createdConst = cmds.parentConstraint(parent, child[0], mo=child[1], skipRotate=["x", "y", "z"])[0];
                    createdConsts.append(createdConst);

                if isUnLockRot:
                    createdConst = cmds.orientConstraint(parent, child[0], mo=child[1]);
                    createdConsts.append(createdConst);

        return createdConsts;

    def checkLockState(self, obj, attr):
        result = cmds.getAttr("{}.{}".format(obj, attr), settable=True);
        return result;

    def analyzeKeyfameRange(self, targets):
        """ 渡された全てのオブジェクトのanimCurveNodeをチェックし、keyframeが打たれている範囲を求める関数
        
            bakeSimulationで利用するため、ジョイント群のkeyframeが打たれている範囲を取得する

                    Args:
                        targets: keyframe範囲を調べるオブジェクト群
                    Returns:
                        list: オブジェクト群に打たれたkeyframeのtimeの最小値、最大値


        """
        animCurves = [];
        startF = 0;
        endF = 0;
        animCurveFn = oma.MFnAnimCurve();

        for target in targets:
            for animCurveType in ANIMCURVE_TYPES:
                tempAnimCurves = cmds.listConnections(target, type=animCurveType);
                for tempAnimCurve in tempAnimCurves:
                    animCurves.append(tempAnimCurve);

            for animCurve in animCurves:
                MSel = om.MSelectionList();
                MSel.add(animCurve);
                MAnimCurve = MSel.getDependNode(0);

                if animCurveFn.hasObj(MAnimCurve):
                    animCurveFn.setObject(MAnimCurve);

                    tempStartF = animCurveFn.input(0).value;
                    if tempStartF < startF:
                        startF = tempStartF;

                    tempEndF = animCurveFn.input(int(animCurveFn.numKeys)-1).value;
                    if tempEndF > endF:
                        endF = tempEndF;

        return [startF, endF];

    # def showModalWindow(self):
    #     modalWindow = ModalWindow();
    #     result = modalWindow.exec_();

    #     if result == QtWidgets.QDialog.Accepted:
    #         return modalWindow.getText();
    #     else:
    #         return None;

    def showProgressDialog(self):
        progress = QtWidgets.QProgressDialog(self);
        progress.setCancelButton(None);
        progress.setWindowFlags(progress.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        progress.show();

        return progress;

    def updateProgressDialog(self, progressDialog, value):
        progressDialog.setValue(value);
        QtWidgets.qApp.processEvents();

    def culcProgressValue(self, fileCount, index):
        return int(((index+1) / fileCount) * 100);

    def showConfirmWindow(self):
        confirmWindow = ConfirmWindow();
        result = confirmWindow.exec_();

        return result;

def showUi():
    mainUi = MainWindow();
    mainUi.show();