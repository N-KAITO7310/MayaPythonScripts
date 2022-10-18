# -*- coding: utf-8 -*-
"""
    要件定義
    ・FBXの骨アニメーションをキャラリグに戻し、アニメーションをベイクするToolを作成
    ・ファイル名はfbxファイルから自動生成
    ・揺れものなどの追加パーツのアニメーションは対象外
    ・肘と膝のPoleVectorについては下記の通り
        ・・・肘PoleVector⇒肩（上腕）のparentConstraintの移動値を受け付ける
        ・・・膝Polevector⇒腿（大腿）のparentConstraintの移動値を受け付ける
    ・脚のSoftIKについて、微細なソフトIKの処理が実際対象のリグには組み込まれてはいるが、あまりにも微細なので、いったんは無視でよい
    ・出力ファイルのfps指定オプション

    import bakeAnimToRigFromFbx as bake;
    reload(bake);
    bake.showUi();

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
# jnt : [ctrl, maintainOffset, targetOffsetRotate]
EXCEPTION_CONST_TABLE = {
    "L_arm" : ["L_arm_pole", True, [0, 0, 0]],
    "R_arm" : ["R_arm_pole", True, [0, 0, 0]],
    "L_leg" : ["L_leg_pole", True, [0, 0, 0]],
    "R_leg" : ["R_leg_pole", True, [0, 0, 0]],
    "L_foot" : ["L_foot_c", False, [0, 0, 0]],
    "R_foot" : ["R_foot_c", False, [0, 0, 0]],
    "L_collar" : ["L_collar_c", True, [0, 0, 17]],# output用のボーンへのconstraintにセットされているための対応
    "R_collar" : ["R_collar_c", True, [180, 0, -17]],
    "center" : ["center_c", False, [0, 0, 0]]
}
FPS_TIME_OPTIONS = ["ntsc", "ntscf"];

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

# ファイル名入力モーダルウィンドウ＊要件にないためコメントアウト
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
    
    UI_NAME = "Bake Animation Tool Window"

    def __init__(self, parent=getMayaWindow()):
        """ウィンドウクラスのinit

        この関数で行っていること
        ・ウィンドウタイトル設定
        ・UIサイズ設定
        ・縦並びレイアウト設定
        ・各ボタンとスロットの設定

        Args:
            parent: (QtWidgets.QWidget): 親ウィンドウとして設定するインスタンス。デフォルトでMayaのウィンドウを指定。
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
        """Widgetクラスの生成

        ボタン等各Widgetクラスを生成する

        Args:
            None
        Returns:
            None

        """

        self._applyButton = QtWidgets.QPushButton(self);
        self._applyButton.setText("Bake and Export");

        self._fpsComboBox = QtWidgets.QComboBox(self);
        self._fpsComboBox.addItems(["30fps", "60fps"]);

    def createLayout(self):
        """レイアウト設定関数
        
        生成したWidgetクラスをレイアウトに設定する

        Args:
            None
        Returns:
            None
        
        """

        mainLayout = QtWidgets.QFormLayout(self);

        mainLayout.addRow("fps:", self._fpsComboBox);
        mainLayout.addWidget(self._applyButton);
        
    def createConnections(self):
        """スロット設定関数
        
        各ウィジェットのスロットに関数を設定する

        Args:
            None
        Returns:
            None
        """

        self._applyButton.clicked.connect(self.bakeAnimation);

    def bakeAnimation(self):
        """fbxファイルのインポート、コネクション、ベイク、ファイルの保存の一連の処理を行う関数

        主な処理フロー
        ・インポートを行うfbxファイルを選択
        ・選択ファイルに対し、それぞれ以下の処理を実行
            ・シーン上のコントローラを取得
            ・各コントローラに該当するボーンを取得するための解析処理を行い情報を保持
            ・各fbxボーンからコントローラへペアレントコンストレイント
            ・コントローラにベイク処理
            ・作成したコンストレイントノードを全て削除
            ・別ファイルとして出力
            ・再度リグファイルを開きなおす
        ・処理完了通知ウィンドウを表示

        Args:
            None
        Returns:
            None

        """
        # インポートファイル選択
        files = self.getFiles();
        if files is None:
            om.MGlobal.displayError("No file selected")
            return;

        # インポート元ファイルパス取得
        currentPath = cmds.file(q=True, exn=True);

        # 保存先ディレクトリ指定
        saveDirectory = self.specifySaveFilePath();
        if saveDirectory is None:
            om.MGlobal.displayError("No Directory selected")
            return;

        # progress bar
        progress = self.showProgressDialog();
        fileCount = len(files);

        for i, filePath in enumerate(files):
            # Import animation file
            imported = cmds.file(filePath, i=True, type="fbx", returnNewNodes=True, ignoreVersion=True, renameAll=True, mergeNamespacesOnClash=False, options="fbx", pr=True, force=True);
            
            # change fps setting
            cmds.currentUnit(time=FPS_TIME_OPTIONS[self._fpsComboBox.currentIndex()]);

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

            # ファイル名の入力処理
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
        """ファイルの絶対パスからファイル名を取得する関数

        ファイルの絶対パスからファイル名を取得する

        Args:
            path: ファイルの絶対パス
        Returns:
            str: ファイル名

        """
        return path.split("/")[-1];

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

    def specifySaveFilePath(self):
        """保存先ディレクトリの指定関数

        保存先ディレクトリの指定

        Args:
            None
        Returns:
            None
        
        """

        # 保存先ディレクトリの指定
        try:
            path = cmds.fileDialog2(fileMode=3, dialogStyle=2, caption="Select save directory");
        except:
            om.MGlobal.displayError("Error File Dialog");
            
        if not path is None:
            return path[0];

        return path;

    def save(self, filePath, fileName):
        """ファイルの保存処理を行う関数

        ファイルの保存処理を行う

        Args:
            filePath: 保存先のパス
            fileName: 保存ファイル名
        Returns:
            bool: 処理の完了

        """

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
        """オブジェクトリストからjointのみを抽出する関数

        オブジェクトリストからjointのみを抽出する関数

        Args:
            objs: オブジェクトのリスト
        Returns:
            [str]: 抽出されたjointのリスト

        """

        return [node for node in objs if cmds.objectType(node) == "joint"];
        
    def convertPartialPathName(self, objs):
        """オブジェクトのフルパスをオブジェクト名に変換する関数

        オブジェクトのフルパスをオブジェクト名に変換する
        
        Args:
            objs: オブジェクト名またはフルパスのリスト
        Returns:
            [str]: オブジェクト名のリスト
        
        """


        paths = [];
        
        for obj in objs:
            omSel = om.MSelectionList();
            omSel.add(obj);
            dagPath = omSel.getDagPath(0);
            path = dagPath.partialPathName();
            paths.append(path);
            
        return paths;

    def analyzeRig(self, importedJnts):
        """リグファイルのジョイントとコントローラ間の接続を解析する関数

        処理フロー
        ・インポートされたジョイントと対応する、ベイクの対象となるリグファイル(nameSpaceあり)のジョイントを取得
        ・コネクション検索からコンストレイントノードを取得
        ・コンストレイントノードからさらに接続元となるコントローラを取得
        ・ジョイント名、コントローラ名、コンストレイントノード、オフセットの情報を返す
        ・リグの構造上さらに接続元を検索する必要がある場合は、繰り返し処理を行う

        Args:
            importedJnts: インポートされたfbxファイルのジョイント名リスト
        Returns:
            {str: [{str: str, bool}]}: {jntName: [{ctrlName: constraint, maintainOffset}]}

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

                    # offsetを取得
                    if cmds.objectType(const) == "parentConstraint":
                        rotOffsets = cmds.getAttr("{}.target[0].targetOffsetRotate".format(const))[0];
                    elif cmds.objectType(const) == "orientConstraint":
                        rotOffsets = cmds.getAttr("{}.offset".format(const))[0];
                    else:
                        rotOffsets = [0, 0, 0];

                    jntCtrlTable[mainJnt.split(nameSpace)[1]] = [[sourceCtrl, False, rotOffsets]];
                    doSearch = False;
                else:
                    searchStartObj = sourceCtrl;
                    # リグの構造上、後の対象がorientConstraintのみとなるため取得タイプを変更
                    listConType = "orientConstraint"
        print(jntCtrlTable)
        return jntCtrlTable;

    def addExceptionToTable(self, dict):
        """ジョイントとコントローラ間の例外的な関係を辞書型に追加する

        要件から、poleVectorなど例外的なジョイント-コントローラ間の関係を情報に追加するための関数

        """
        for key, value in EXCEPTION_CONST_TABLE.items():
            if key in dict:
                dict[key].append([value[0], value[1], value[2]]);
            else:
                dict[key] = [[value[0], value[1], value[2]]];

        return dict;

    def iterConnection(self, dict):
        """接続処理の繰り返しを行う関数

        アトリビュートのロックをチェックし、適切なコンストレイントを行う

        Args:
            dict: {jntName: [{ctrlName: constraint, maintainOffset}]}
        Returns:
            [str]: この関数で作成されたコンストレイントノードのリスト
        
        """
        createdConsts = [];

        for parent, children in dict.items():
            for child in children:
                isUnLockTrans = self.checkLockState(child[0], "tx");
                isUnLockRot = self.checkLockState(child[0], "rx");
                print(child)
                if isUnLockTrans:
                    # 鎖骨のみparentConstraintオフセットなし&orientConstraintオフセットありとしたいため特例の対応
                    if "collar_c" in  child[0]:
                        createdConst = cmds.parentConstraint(parent, child[0], mo=False, skipRotate=["x", "y", "z"])[0];
                    else:
                        createdConst = cmds.parentConstraint(parent, child[0], mo=child[1], skipRotate=["x", "y", "z"])[0];
                    if child[1]:
                        cmds.setAttr("{}.target[0].targetOffsetRotate".format(createdConst), child[2][0], child[2][1], child[2][2], type="float3");
                    createdConsts.append(createdConst);

                if isUnLockRot:
                    createdConst = cmds.orientConstraint(parent, child[0], mo=child[1])[0]
                    if child[1]:
                        cmds.setAttr("{}.offset".format(createdConst), child[2][0], child[2][1], child[2][2], type="float3");
                    createdConsts.append(createdConst);

        return createdConsts;

    def checkLockState(self, obj, attr):
        """アトリビュートのロックをチェックする

        アトリビュートのロックをチェックするための関数

        Args:
            obj: チェック対象となるオブジェクト名
            attr: チェック対象となるアトリビュート名

        Returns:
            bool: ロック：True/非ロック：False
    

        """
        result = cmds.getAttr("{}.{}".format(obj, attr), settable=True);
        return result;

    def analyzeKeyfameRange(self, targets):
        """ 渡された全てのオブジェクトのkeyframe範囲をチェックし、最少と最大を返す関数
        
        bakeSimulationで利用するため、ジョイント群のkeyframeが打たれている範囲を取得する

        Args:
            targets: keyframe範囲を調べるオブジェクト群
        Returns:
            list: オブジェクト群に打たれたkeyframeのtimeの最小値、最大値

        """
        # animCurves = [];
        startF = 0;
        endF = 0;
        # animCurveFn = oma.MFnAnimCurve();

        for target in targets:
            tempStartF = cmds.findKeyframe(target, which="first");
            if tempStartF < startF:
                startF = tempStartF;
            
            tempEndF = cmds.findKeyframe(target, which="last");
            if tempEndF > endF:
                endF = tempEndF;

            # case of om
            # for animCurveType in ANIMCURVE_TYPES:
            #     tempAnimCurves = cmds.listConnections(target, type=animCurveType);
            #     for tempAnimCurve in tempAnimCurves:
            #         animCurves.append(tempAnimCurve);

            # for animCurve in animCurves:
            #     MSel = om.MSelectionList();
            #     MSel.add(animCurve);
            #     MAnimCurve = MSel.getDependNode(0);

            #     if animCurveFn.hasObj(MAnimCurve):
            #         animCurveFn.setObject(MAnimCurve);

            #         tempStartF = animCurveFn.input(0).value;
            #         if tempStartF < startF:
            #             startF = tempStartF;

            #         tempEndF = animCurveFn.input(int(animCurveFn.numKeys)-1).value;
            #         if tempEndF > endF:
            #             endF = tempEndF;

        return [startF, endF];

    # def showModalWindow(self):
    #     modalWindow = ModalWindow();
    #     result = modalWindow.exec_();

    #     if result == QtWidgets.QDialog.Accepted:
    #         return modalWindow.getText();
    #     else:
    #         return None;

    def showProgressDialog(self):
        """プログレスバーの表示関数
        
        プログレスバーを表示する

        Args:
            None
        Returns:
            None
        
        """

        progress = QtWidgets.QProgressDialog(self);
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
        QtWidgets.qApp.processEvents();

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