# -*- coding: utf-8 -*-
"""

FixRotByFbxTool

import fixRotByFbxTool as fixRotByFbxTool;
reload(fixRotByFbxTool);
fixRotByFbxTool.showUi();

lastUpdated: 2022/12/09

"""

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
import copy;
import datetime;
import json;

WINDOW_TITLE = "FixRotByFbxTool";
FILE_EXTENSIONS = ["*.ma", "*.fbx"];
SPECIFIC_NAMESPACE = "CR_NAMESPACE";
TARGET_BODY_PART = ["index", "middle", "ring", "pinky", "thumb"];
AXIS_LIST = ["X", "Y", "Z"];
ROTATE_ATTRS = ["rx", "ry", "rz"];
RSIDE_PREFIX = "R_";
OPEN_SCENE = "open scene";
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
    nameSpaceText = ":";
    saveDirectoryText = "";

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
        self.__nameSpaceSetButton.setText("Set NameSpace");
        self.__saveDirText = QtWidgets.QLineEdit(self);
        self.__saveDirSetButton = QtWidgets.QPushButton(self);
        self.__saveDirSetButton.setText("Set SaveDirectory");

        self.__applyFixButton = QtWidgets.QPushButton(self);
        self.__applyFixButton.setText("Apply This SceneFile");
        self.__multipleApplyButton = QtWidgets.QPushButton(self);
        self.__multipleApplyButton.setText("Apply Multiple Files");

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
        mainLayout.addWidget(self.__saveDirText, 1, 0);
        mainLayout.addWidget(self.__saveDirSetButton, 1, 1);
        mainLayout.addWidget(self.__applyFixButton, 2, 0, 1, 2);
        mainLayout.addWidget(self.__multipleApplyButton, 3, 0, 1, 2);

    def createConnections(self):
        """スロット設定関数
        
        各ウィジェットのスロットに関数を設定する

        Args:
            None
        Returns:
            None
        """

        self.__nameSpaceSetButton.clicked.connect(self.setNameSpace);
        self.__saveDirSetButton.clicked.connect(self.setSaveDir);
        self.__applyFixButton.clicked.connect(doItSingle);
        self.__multipleApplyButton.clicked.connect(doItMulti);

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
            nameSpace = nameSpace[0];

        self.__nameSpaceText.setText(nameSpace);
        self.nameSpaceText = nameSpace;

    def setSaveDir(self):
        """保存先ディレクトリをUIにセットする関数

        保存先ディレクトリをUIにセットする

        Args:
            None
        Returns:
            None
        
        """

        saveDir = getSaveDir();
        self.__saveDirText.setText(saveDir);
        self.saveDirectoryText = saveDir;

def doItSingle():
    """現在開いているシーンファイルに対し本処理とファイル保存処理を実行する関数
    
    現在開いているシーンファイルに対し、本ツールの本処理を実行する。

    Args:
        None
    Returns:
        None

    """
    global mainUi;

    refFile = getRefFile();
    if refFile is None:
        om.MGlobal.displayError("Please Select reference file");
        return;

    targetNameSpace = mainUi.nameSpaceText;
    saveDirectory = mainUi.saveDirectoryText;

    result = applyFix(targetNameSpace, refFile);
    if result == True:
        fileName = getFileName(refFile);
        fileName = fileName.replace(FILE_EXTENSIONS[1], FILE_EXTENSIONS[0])
        saveFile(saveDirectory, fileName);

def doItMulti():
    """複数ファイルを選択し、本ツールの本処理とファイル保存処理を実行する関数
    
    複数ファイルを選択し、本ツールの本処理を実行する。各ファイル処理においてエラーが発生した場合、ログ出力を行う。

    Args:
        None
    Returns:
        None

    """
    global mainUi;

    targetFiles = getTargetFiles();
    refFiles = getRefFiles();
    if targetFiles is None or refFiles is None:
        om.MGlobal.displayError("Please Select files");
        return;

    targetNameSpace = mainUi.nameSpaceText;
    saveDirectory = mainUi.saveDirectoryText;

    errorLogs = {};
    for i, targetFile in enumerate(targetFiles):
        try:
            cmds.file(targetFile, open=True, force=True);
            result = applyFix(targetNameSpace, refFiles[i]);

        except Exception as e:
            errorDict = {"errorType": str(type(e)), "error": str(e)};
            errorLogs[targetFile] = errorDict;
            continue;

        if result == True:
            fileName = getFileName(refFiles[i]);
            fileName = fileName.replace(FILE_EXTENSIONS[1], FILE_EXTENSIONS[0])
            saveFile(saveDirectory, fileName);

    if len(errorLogs) > 0:
        # エラー出力処理
        writeErrorLog(saveDir=saveDirectory, errorLogs=errorLogs);

def applyFix(targetNameSpace, refFile):
    """本ツールの本処理関数

    本ツールの本処理を実行する。
    修正したいアニメーションシーンを開いた状態で実行。
    出力済みの回転軸修正前FBXデータを参照し、アニメーションをコンストレイント・ノード接続で修正する
    ネームスペースを指定した場合その指定したものに処理を限る

    Args:
        None
    Returns:
        boolean: result
    """
    errorLog = None;

    importedData = refNodes(refFile);
    importedJnts = [getPartialName(x) for x in importedData if cmds.objectType(x) == "joint"];

    corTable = {}; 
    for bodyPart in TARGET_BODY_PART:
        targetBodyPartJnts = [x for x in importedJnts if bodyPart in x];

        for fbxJnt in targetBodyPartJnts:
            jntName = fbxJnt.split(":")[-1];
            targetCtrlName = jntName + "_ctrl";
            targetCtrl = cmds.ls("{}:{}".format(targetNameSpace, targetCtrlName), type="transform");
            if (not targetCtrl is None) and len(targetCtrl) == 1:
                corTable[fbxJnt] = targetCtrl[0];

    startF = 0;
    endF = 0;
    # right side orient reverse source
    null = cmds.createNode("transform", n="{}:rSide_minusScale_null".format(SPECIFIC_NAMESPACE, fbxJnt));# or rotateZ -180
    cmds.setAttr("{}.scaleX".format(null), -1);
    cmds.setAttr("{}.scaleY".format(null), -1);
    # cmds.setAttr("{}.rotateZ".format(null), -180);

    isRight = False;

    for fbxJnt, targetCtrl in corTable.items():
        # check skip attr
        skipAtts = checkLockedAttrs(targetCtrl, ROTATE_ATTRS);
        skipAxis = [x[-1] for x in skipAtts];

        connectAttrs = copy.deepcopy(ROTATE_ATTRS);
        for skipAttr in skipAtts:
            connectAttrs.remove(skipAttr);
        
        # TODO: 削除予定。実行されるアニメーションファイルはリファレンスされていない条件を想定。＝animCurveNodeは接続解除ではなくcutKeyで削除可能のみを想定。
        # for connectAttr in connectAttrs:
        #     destAttr = targetCtrl + "." + connectAttr;
        #     sourceAttr = cmds.connectionInfo(destAttr, sourceFromDestination=True);
        #     if sourceAttr == "":
        #         continue;
        #     cmds.disconnectAttr(sourceAttr, destAttr);

        cmds.cutKey(targetCtrl, attribute="rotate");
        tempConst = cmds.orientConstraint(fbxJnt, targetCtrl, mo=False, skip=skipAxis)[0]

        isRight = RSIDE_PREFIX in fbxJnt and RSIDE_PREFIX in targetCtrl;
        if isRight:
            # 右側ジョイントにおいてrotZ-180のオフセットが挟まっているため対応
            # constraint接続を解除
            for attr in connectAttrs:
                cmds.disconnectAttr("{}.constraintRotate.constraintRotate{}".format(tempConst, attr[-1].upper()), "{}.{}".format(targetCtrl, attr));

            composeMat = cmds.createNode("composeMatrix", n="{}:{}_composeMatrix".format(SPECIFIC_NAMESPACE, tempConst));
            multMat = cmds.createNode("multMatrix", n="{}:{}_multMat".format(SPECIFIC_NAMESPACE, fbxJnt));
            decomposeMat = cmds.createNode("decomposeMatrix", n="{}:{}_decomposeMat".format(SPECIFIC_NAMESPACE, fbxJnt));
            quatToEuler = cmds.createNode("quatToEuler", n="{}:{}_quatToEuler".format(SPECIFIC_NAMESPACE, fbxJnt));

            cmds.connectAttr("{}.constraintRotate".format(tempConst), "{}.inputRotate".format(composeMat));
            cmds.connectAttr("{}.matrix".format(null), "{}.matrixIn[0]".format(multMat));
            cmds.connectAttr("{}.outputMatrix".format(composeMat), "{}.matrixIn[1]".format(multMat));
            cmds.connectAttr("{}.matrixSum".format(multMat), "{}.inputMatrix".format(decomposeMat));
            cmds.connectAttr("{}.outputQuat".format(decomposeMat), "{}.inputQuat".format(quatToEuler));

            # targetと接続
            for axis in connectAttrs:
                cmds.connectAttr("{}.outputRotate{}".format(quatToEuler, axis[-1].upper()), "{}.{}".format(targetCtrl, axis), f=True);

    # check keyframeRange
    sf = cmds.findKeyframe(fbxJnt, which="first");
    ef = cmds.findKeyframe(fbxJnt, which="last");

    if sf < startF:
        startF = sf;
    if ef > endF:
        endF = ef;
            
    # bake
    cmds.bakeResults(corTable.values(), t=(startF, endF), at=ROTATE_ATTRS, simulation=False);

    # cleanup
    deleteTargets = cmds.ls("{}:*".format(SPECIFIC_NAMESPACE));
    cmds.delete(deleteTargets);

    return True;

def getTargetFiles():
    """本処理適用するターゲットファイルを指定する関数

    本処理適用するターゲットファイルを指定する

    Args:
        None
    Returns:
        [str]: 指定されたファイルパス

    """

    try:
        paths = cmds.fileDialog2(fileFilter=FILE_EXTENSIONS[0], fileMode=4, dialogStyle=2, caption="Select target files");
    except:
        om.MGlobal.displayError("Error File Dialog");
        return None;
        
    if paths is None or len(paths) < 1:
        om.MGlobal.displayError("No fbx file selected");
        return None;

    return paths;


def getRefFile():
    """単一のリファレンスファイルの指定関数

    単一のリファレンスファイルの指定

    Args:
        None
    Returns:
        str: 指定されたファイルパス

    """

    try:
        paths = cmds.fileDialog2(fileFilter=FILE_EXTENSIONS[1], fileMode=1, dialogStyle=2, caption="Select a reference fbx file");
    except:
        om.MGlobal.displayError("Error File Dialog");
        
    if paths is None or len(paths) < 1:
        om.MGlobal.displayError("No file selected");
        return None;

    path = paths[0];

    return path;

def getRefFiles():
    """リファレンスファイルの指定関数

    リファレンスファイルの指定

    Args:
        None
    Returns:
        [str]: 指定されたリファレンスファイルパス
    
    """

    try:
        paths = cmds.fileDialog2(fileFilter=FILE_EXTENSIONS[1], fileMode=4, dialogStyle=2, caption="Select reference fbx files");
    except:
        om.MGlobal.displayError("Error File Dialog");
        return None;
        
    if paths is None or len(paths) < 1:
        om.MGlobal.displayError("No file selected");
        return None;

    return paths;

def getSaveDir():
    """保存先ディレクトリの指定関数

    保存先ディレクトリの指定

    Args:
        None
    Returns:
        str: 指定された保存先ファイルパス
    
    """

    # 保存先ディレクトリの指定
    try:
        path = cmds.fileDialog2(fileMode=3, dialogStyle=2, caption="Select save directory");
    except:
        om.MGlobal.displayError("Error File Dialog");
        return None;
        
    if not path is None:
        return path[0];

def refNodes(filePath):
    """指定ファイルをnameSpaceを指定しリファレンスする関数

    指定ファイルをnameSpaceを指定しリファレンスする

    Args:
        filePath: リファレンス先ファイルパス
    Returns:
        [str]: リファレンスされたノードリスト

    """

    currentNs = cmds.namespaceInfo(cur=True)
    if not cmds.namespace(ex="{}".format(SPECIFIC_NAMESPACE)):
        cmds.namespace(add="{}".format(SPECIFIC_NAMESPACE))
    cmds.namespace(set=":{}".format(SPECIFIC_NAMESPACE))

    # Import animation file
    cmds.file(filePath, i=True, type="fbx", returnNewNodes=True, ignoreVersion=True, renameAll=True, mergeNamespacesOnClash=False, options="fbx", pr=True);
    # 一時的に変更したカレントnameSpaceをもとに戻す
    cmds.namespace(set=currentNs);

    # get referenced nodes
    referenced = cmds.ls("{}::*".format(SPECIFIC_NAMESPACE));
    return referenced;


def getPartialName(name):
    """オブジェクトのフルパスをオブジェクト名に変換する関数

    オブジェクトのフルパスをオブジェクト名に変換する

    Args:
        name: オブジェクトのフルパス
    Returns:
        str: オブジェクト名

    """

    return name.split("|")[-1];

def checkLockedAttrs(obj, attrs):
    """引数に指定したアトリビュートのうちロックされているもののみを返す関数

    引数に指定したアトリビュートのうちロックされているもののみを返す

    Args:
        obj: オブジェクト名
        attrs: ロックをチェックしたいアトリビュートリスト
    Returns:
        [str]: ロックされているアトリビュートリスト

    """

    lockedAttrs = [];
    for attr in attrs:
        isLocked = cmds.getAttr("{}.{}".format(obj, attr), lock=True);
        if isLocked:
            lockedAttrs.append(attr);
    return lockedAttrs;

def getFileName(path):
    """ファイルの絶対パスからファイル名を取得する関数

    ファイルの絶対パスからファイル名を取得する

    Args:
        path: ファイルの絶対パス
    Returns:
        str: ファイル名

    """
    return path.split("/")[-1];

def saveFile(filePath, fileName):
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
        cmds.file(save=True, type='mayaAscii', force=True);

    except:
        om.MGlobal.displayError("Error save file");

    return True;

def writeErrorLog(saveDir, errorLogs):
    """エラーログ出力処理関数

    エラーログの出力処理を行う

    Args:
        saveDir: 保存先のパス
        errorLogs: エラーログdict
    Returns:
        None
    """

    dt = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S");
    path = saveDir + "/" + "errorLog_" + dt + ".json";

    tf = open(path, "w");
    json.dump(errorLogs, tf, indent=2);
    tf.close();

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