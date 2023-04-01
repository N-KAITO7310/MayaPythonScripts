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
from functools import partial;
import maya.api.OpenMayaAnim as oma;

"""

switchModelingPoseTool

要件：
UI
・APose(modeling)Setボタン
・APose(modeling)Applyボタン
・APose(modeling)Deleteボタン
・TPose(modified)Setボタン
・TPose(modified)Applyボタン
・TPose(modified)Deleteボタン

・上書き確認ウィンドウ
・削除確認ウィンドウ

必要情報
・worldMatrix
・localMatrix
・parent node(,区切りStrでよい)

フロー
・最上位ジョイントノードの選択→実行
・選択された最上位ジョイントに情報を格納
・＊ノードツリー変更のチェック処理→差分ありの際はエラー処理でよい

名称
・modeling_matrix(Apose)
・Tstanse_matrix(Tpose)


import switchModelingPoseTool as switchModelingPoseTool;
reload(switchModelingPoseTool);
switchModelingPoseTool.showUi();

last updated: 2023/02/20

"""
# constant var
WINDOW_TITLE = "SwitchModelingPoseTool";
WORLD_EXIST = "world";
POSE_OPTION = ["modeling", "tPose"];
CONFIRM_WINDOW_OPTION = ["Overwrite", "Delete"];
mainUi = None;

# ------------------------------
# UI
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
        # modeling pose
        self.__aSetButton = QtWidgets.QPushButton(self);
        self.__aSetButton.setText("Modeling Pose(Astanse) Set");

        self.__aApplyButton = QtWidgets.QPushButton(self);
        self.__aApplyButton.setText("Modeling Pose(Astanse) Apply");

        self.__aDeleteButton = QtWidgets.QPushButton(self);
        self.__aDeleteButton.setText("Modeling Pose(Astanse) Delete");

        # Tstanse pose
        self.__tSetButton = QtWidgets.QPushButton(self);
        self.__tSetButton.setText("Tstanse Set");

        self.__tApplyButton = QtWidgets.QPushButton(self);
        self.__tApplyButton.setText("Tstanse Apply");

        self.__tDeleteButton = QtWidgets.QPushButton(self);
        self.__tDeleteButton.setText("Tstanse Delete");

    def createLayout(self):
        """レイアウト設定関数
        
        生成したWidgetクラスをレイアウトに設定する

        Args:
            None
        Returns:
            None
        
        """
        mainLayout = QtWidgets.QVBoxLayout(self);

        mainLayout.addWidget(self.__aSetButton);
        mainLayout.addWidget(self.__aApplyButton);
        mainLayout.addWidget(self.__aDeleteButton);
        mainLayout.addWidget(self.__tSetButton);
        mainLayout.addWidget(self.__tApplyButton);
        mainLayout.addWidget(self.__tDeleteButton);

    def createConnections(self):
        """スロット設定関数
        
        各ウィジェットのスロットに関数を設定する

        Args:
            None
        Returns:
            None
        """
        self.__aSetButton.clicked.connect(aPoseSet);
        self.__aApplyButton.clicked.connect(aPoseApply);
        self.__aDeleteButton.clicked.connect(aPoseDelete);

        self.__tSetButton.clicked.connect(tPoseSet);
        self.__tApplyButton.clicked.connect(tPoseApply);
        self.__tDeleteButton.clicked.connect(tPoseDelete);

# ------------------------------
# main methods
def aPoseSet():
    """Aposeにおける各ジョイントのMatrix情報を選択ルートジョイントに格納するメソッド

    Aposeにおける各ジョイントのMatrix情報を選択ルートジョイントに格納する。

    処理フロー
    ・選択チェック
    ・既存情報チェック(上書きの場合一部の処理をのぞいた削除メソッドを実行)
    ・階層の差分チェック
    ・Matrix情報の取得
    ・各ジョイントの親ノード名の取得
    ・選択ルートジョイントへの情報格納(compound→matrix, str)
    
    Args:
        None
    Returns:
        None

    """

    cmds.undoInfo(openChunk=True);

    # TODO: check処理を含めたセットの前段階処理も全て一つのメソッドでまとめて共通化する？
    selectedJnt = checkSelected();
    if not selectedJnt:
        return;

    allJnts = getHierarchyDescendingOrder(selectedJnt);

    # check information exists
    checkExistInformationsResult = checkExistInformations(selectedJnt, POSE_OPTION[0]);
    if checkExistInformationsResult:
        # confirm window
        response = showConfirmWindow(CONFIRM_WINDOW_OPTION[0]);

        # 上書きする場合は、全て削除する
        if response:
            aPoseDelete(useOverwrite=True);
        else:
            om.MGlobal.displayInfo("processing interrupted");
            return;

    # check hierarchyDiff
    hierarchyCheckResult = checkHierarchyDiff(allJnts, POSE_OPTION[0]);
    if not hierarchyCheckResult:
        om.MGlobal.displayError("do not match hierarchy.");
        return;

    # get world and local matrix
    jntInfoLists = returnMatrixAndParentLists(allJnts);

    # set Attrs to topJnt
    setJntInformations(targetJnt=selectedJnt, jntInfoLists=jntInfoLists, poseOption=POSE_OPTION[0]);

    om.MGlobal.displayInfo("Set successfully!");

    cmds.undoInfo(closeChunk=True);

def aPoseApply():
    """AposeのMatrix情報をセットするメソッド

    Aposeにおける各ジョイントのMatrix情報を選択ルートジョイントから取得し、ルート以下のジョイント全てにセットを行う

    処理フロー
    ・選択チェック
    ・既存情報チェック(上書きの場合一部の処理をのぞいた削除メソッドを実行)
    ・階層の差分チェック
    ・ルートジョイントからセットされているMatrix情報、各階層化ジョイントの親ノード名の取得
    ・各ジョイントへMatrixをセット
    
    Args:
        None
    Returns:
        None

    """
    cmds.undoInfo(openChunk=True);

    selectedJnt = checkSelected();
    if not selectedJnt:
        return;

    allJnts = getHierarchyDescendingOrder(selectedJnt);

    # check information exists
    checkExistInfoResult =  checkExistInformations(selectedJnt, POSE_OPTION[0]);
    if not checkExistInfoResult:
        om.MGlobal.displayError("do not exist info.");
        return;
    checkHierarchyResult = checkHierarchyDiff(allJnts, POSE_OPTION[0]);
    if not checkHierarchyResult:
        om.MGlobal.displayError("do not match hierarchy.");
        return;
    
    jntInfoLists = getJntInformations(allJnts=allJnts, poseOption=POSE_OPTION[0]);

    applyJntInformations(jntInfoLists);

    om.MGlobal.displayInfo("Apply successfully!");

    cmds.undoInfo(closeChunk=True);

def aPoseDelete(useOverwrite):
    """AposeのMatrix情報を削除するメソッド

    Aposeにおける各ジョイントのMatrix情報、親情報を削除する
    
    処理フロー
    ・選択チェック
    ・既存情報チェック(既に情報が存在する場合は上書き確認ウィンドウの表示)
    ・格納情報の削除
    
    Args:
        useOverwrite: (bool): pysideのslotによって呼び出される場合基本引数はFalseとなる。上書きの際の削除の際にTrueを指定することで不要な確認処理を回避する。
    Returns:
        None

    """

    cmds.undoInfo(openChunk=True);
    
    selectedJnt = checkSelected();

    if not useOverwrite:
        # check information exists
        checkExistInformationsResult = checkExistInformations(selectedJnt, POSE_OPTION[0]);
        if checkExistInformationsResult:
            response =  showConfirmWindow(CONFIRM_WINDOW_OPTION[1]);
            if not response:
                om.MGlobal.displayInfo("processing interrupted");
                return;
        else:
            om.MGlobal.displayError("Do not exist informations");
            return;

    deleteAttrs(selectedJnt, poseOption=POSE_OPTION[0]);

    om.MGlobal.displayInfo("Delete successfully!");

    cmds.undoInfo(closeChunk=True);

def tPoseSet():
    """Tposeにおける各ジョイントのMatrix情報を選択ルートジョイントに格納するメソッド

    Tposeにおける各ジョイントのMatrix情報を選択ルートジョイントに格納する。

    処理フロー
    ・選択チェック
    ・既存情報チェック(上書きの場合一部の処理をのぞいた削除メソッドを実行)
    ・階層の差分チェック
    ・Matrix情報の取得
    ・各ジョイントの親ノード名の取得
    ・選択ルートジョイントへの情報格納(compound→matrix, str)
    
    Args:
        None
    Returns:
        None

    """

    cmds.undoInfo(openChunk=True);
    
    selectedJnt = checkSelected();
    if not selectedJnt:
        return;

    allJnts = getHierarchyDescendingOrder(selectedJnt);

    # check information exists
    checkExistInformationsResult = checkExistInformations(selectedJnt, POSE_OPTION[1]);
    if checkExistInformationsResult:
        # confirm window
        response = showConfirmWindow(CONFIRM_WINDOW_OPTION[0]);

        # 上書きする場合は、全て削除する
        if response:
            tPoseDelete(useOverwrite=True);
        else:
            om.MGlobal.displayInfo("processing interrupted");
            return;

    # check hierarchyDiff
    hierarchyCheckResult = checkHierarchyDiff(allJnts, POSE_OPTION[1]);
    if not hierarchyCheckResult:
        om.MGlobal.displayError("do not match hierarchy.");
        return;

    # get world and local matrix
    jntInfoLists = returnMatrixAndParentLists(allJnts);

    # set Attrs to topJnt
    setJntInformations(targetJnt=selectedJnt, jntInfoLists=jntInfoLists, poseOption=POSE_OPTION[1]);

    om.MGlobal.displayInfo("Set successfully!");

    cmds.undoInfo(closeChunk=True);

def tPoseApply():
    """TposeのMatrix情報をセットするメソッド

    Tposeにおける各ジョイントのMatrix情報を選択ルートジョイントから取得し、ルート以下のジョイント全てにセットを行う

    処理フロー
    ・選択チェック
    ・既存情報チェック(上書きの場合一部の処理をのぞいた削除メソッドを実行)
    ・階層の差分チェック
    ・ルートジョイントからセットされているMatrix情報、各階層化ジョイントの親ノード名の取得
    ・各ジョイントへMatrixをセット
    
    Args:
        None
    Returns:
        None

    """
    cmds.undoInfo(openChunk=True);

    selectedJnt = checkSelected();
    if not selectedJnt:
        return;

    allJnts = getHierarchyDescendingOrder(selectedJnt);

    # check information exists
    checkExistInfoResult =  checkExistInformations(selectedJnt, POSE_OPTION[1]);
    if not checkExistInfoResult:
        om.MGlobal.displayError("do not exist info.");
        return;
    checkHierarchyResult = checkHierarchyDiff(allJnts, POSE_OPTION[1]);
    if not checkHierarchyResult:
        om.MGlobal.displayError("do not match hierarchy.");
        return;
    
    jntInfoLists = getJntInformations(allJnts=allJnts, poseOption=POSE_OPTION[1]);

    applyJntInformations(jntInfoLists);

    om.MGlobal.displayInfo("Apply successfully!");

    cmds.undoInfo(closeChunk=True);

def tPoseDelete(useOverwrite):
    """TposeのMatrix情報を削除するメソッド

    Tposeにおける各ジョイントのMatrix情報、親情報を削除する
    
    処理フロー
    ・選択チェック
    ・既存情報チェック(既に情報が存在する場合は上書き確認ウィンドウの表示)
    ・格納情報の削除
    
    Args:
        useOverwrite: (bool): pysideのslotによって呼び出される場合基本引数はFalseとなる。上書きの際の削除の際にTrueを指定することで不要な確認処理を回避する。
    Returns:
        None

    """
    cmds.undoInfo(openChunk=True);

    selectedJnt = checkSelected();

    if not useOverwrite:
        # check information exists
        checkExistInformationsResult = checkExistInformations(selectedJnt, POSE_OPTION[1]);
        if checkExistInformationsResult:
            response = showConfirmWindow(CONFIRM_WINDOW_OPTION[1]);
            if not response:
                om.MGlobal.displayInfo("processing interrupted");
                return;
        else:
            om.MGlobal.displayError("Do not exist informations");
            return;


    deleteAttrs(selectedJnt, poseOption=POSE_OPTION[1]);

    om.MGlobal.displayInfo("Delete successfully!");

    cmds.undoInfo(closeChunk=True);

# ------------------------------
# helper mothods
def getHierarchyDescendingOrder(targetJnt): 
    """選択されたルートジョイントから下の階層に向かってジョイントをリスト化し返すメソッド

    選択されたルートジョイントから下の階層に向かってジョイントをリスト化し返す
    
    Args:
        targetJnt: (string): ルートとなるターゲットジョイント
    Returns:
        list: ([string]): 階層降順リスト

    """

    list = [];
    selList = om.MSelectionList();
    selList.add(targetJnt);

    dag = selList.getDependNode(0);

    dagIterator = om.MItDag(om.MItDag.kBreadthFirst, om.MFn.kInvalid);
    dagIterator.reset(dag, om.MItDag.kBreadthFirst, om.MFn.kJoint);

    fDn = om.MFnDagNode();
    while ( not dagIterator.isDone()):
        currentObj = dagIterator.currentItem();
        fDn.setObject(currentObj);
        fName = fDn.name();
        list.append(fName); 

        dagIterator.next();

    return list;

def checkSelected():
    """選択されたオブジェクトがこのツールの用途において適切かどうかを判定するメソッド

    選択されたオブジェクトがこのツールの用途において適切かどうかを判定する
    ・選択数
    ・ジョイントであるか
    
    Args:
        None
    Returns:
        selectedJnt: (string): 選択された一つのジョイント

    """
    selected = cmds.ls(sl=True);
    selectedJnt = None;
    if (selected is None) or (len(selected) != 1):
        om.MGlobal.displayError("Please select one joint");
        return False;
    if not cmds.objectType(selected[0]) == "joint":
        om.MGlobal.displayError("Please select a joint");
        return False;
    else:
        selectedJnt = selected[0];

    return selectedJnt;

def checkExistInformations(targetJnt, poseOption):
    """選択されたルートジョイントに既にMatrix情報がセットされているかどうかを判定するメソッド

    選択されたルートジョイントに既にMatrix情報がセットされているかどうかを判定する
    
    Args:
        targetJnt: (string): ターゲットとなるルートジョイント
        poseOption: (str): アトリビュート名で利用しているT or Aスタンス情報を示す文字列
    Returns:
        attrExist: (bool): アトリビュートの有無

    """
    # 対象となるジョイントに既に情報があるかを判定する。T or Aの2パターン。再利用・拡張のためメソッド化。
    attrExist = cmds.attributeQuery("{}_world_matrixs".format(poseOption), node=targetJnt, exists=True);
    return attrExist;

def checkHierarchyDiff(allJnts, poseOption):
    """前回セット時とのジョイント階層差分があるかどうかを判定するメソッド

    前回セット時とのジョイント階層差分があるかどうかを判定する
    
    Args:
        allJnts: (string): 対象となる全てのジョイント
        poseOption: (str): アトリビュート名で利用しているT or Aスタンス情報を示す文字列
    Returns:
        (bool): 差分の有無

    """
    # check attr exist
    attrExist = cmds.attributeQuery("{}_parent_obj_info".format(poseOption), node=allJnts[0], exists=True);
    if attrExist:
        parentListStr = cmds.getAttr("{}.{}_parent_obj_info".format(allJnts[0], poseOption));
        parentList = parentListStr.split(",");
    else:
        # アトリビュートが存在しない場合はTrueとして返す
        return True;

    for i, jnt in enumerate(allJnts):
        parentObj = parentList[i];
        currentParentObj = cmds.listRelatives(jnt, p=True, type="joint");
        if currentParentObj is None or len(currentParentObj) == 0:
            if parentObj == WORLD_EXIST:
                continue;
            else:
                return False;
        else:
            match = True if parentObj == currentParentObj[0] else False;
            if match:
                continue;
            else:
                return False;
    
    return True;

def returnMatrixAndParentLists(allJnts):
    """対象となるジョイントからMatrix情報、親ノード情報を取得しリストで返すメソッド

    対象となるジョイントからMatrix情報、親ノード情報を取得しリストで返す
    
    Args:
        allJnts: ([string]): ターゲットとなる全てのジョイント
    Returns:
        jntInfoLists: ([[worldMatrix], [localMatrix], string]]): worldMatrix, localMatrix, 親オブジェクト名文字列を含むリスト

    """
    jntInfoLists = [];
    for jnt in allJnts:
        worldMat = cmds.xform(jnt, q=True, matrix=True, ws=True);
        localMat = cmds.xform(jnt, q=True, matrix=True, ws=False);
        parentObj = cmds.listRelatives(jnt, p=True, type="joint");
        if parentObj is None or len(parentObj) == 0:
            parentObj = WORLD_EXIST;
        else:
            parentObj = parentObj[0];
    
        jntInfoLists.append([worldMat, localMat, jnt, parentObj]);
    
    return jntInfoLists;

def setJntInformations(targetJnt, jntInfoLists, poseOption):
    """格納された情報から、対象となる各ジョイントにMatrix情報をセットするメソッド

    格納された情報から、対象となる各ジョイントにMatrix情報をセットする
    
    Args:
        targetJnt: (string): ターゲットとなるルートジョイント
        jntInfoLists: ([[worldMatrix], [localMatrix], string]]): worldMatrix, localMatrix, 親オブジェクト名文字列を含むリスト
        poseOption: (string): アトリビュート名で利用しているT or Aスタンス情報を示す文字列
    Returns:
        None

    """

    numOfList = len(jntInfoLists);
    parentObjList = [];

    # matrixs
    cmds.addAttr(targetJnt, longName="{}_world_matrixs".format(poseOption), numberOfChildren=numOfList, attributeType="compound");
    cmds.addAttr(longName='{}_local_matrixs'.format(poseOption), numberOfChildren=numOfList, attributeType='compound');

    for i, info in enumerate(jntInfoLists):
        worldMat, localMat, jnt, parentObj = info;

        # worldMat
        worldMatAttrName = "{}_{}_{}_world_matrix".format(jnt, i, poseOption);
        cmds.addAttr(longName=worldMatAttrName, attributeType='matrix', parent="{}_world_matrixs".format(poseOption));
    
        # localMat
        localMatAttrName = "{}_{}_{}_local_matrix".format(jnt, i, poseOption);
        cmds.addAttr(longName=localMatAttrName, attributeType='matrix', parent='{}_local_matrixs'.format(poseOption));

        # add parentObjName
        parentObjList.append(parentObj);
    
    # addAttrが全て完了して以降でなければセットできないため再度イテレート
    for i, info in enumerate(jntInfoLists):
        worldMat, localMat, jnt, parentObj = info;

        worldMatAttrName = "{}_{}_{}_world_matrix".format(jnt, i, poseOption)
        cmds.setAttr("{}.{}_world_matrixs.{}".format(targetJnt, poseOption, worldMatAttrName), worldMat, type="matrix");
        localMatAttrName = "{}_{}_{}_local_matrix".format(jnt, i, poseOption);
        cmds.setAttr("{}.{}_local_matrixs.{}".format(targetJnt, poseOption, localMatAttrName), localMat, type="matrix");
    
    # parents
    parentObjStr = ",".join(parentObjList);
    cmds.addAttr(longName="{}_parent_obj_info".format(poseOption), dt="string");
    cmds.setAttr("{}.{}_parent_obj_info".format(targetJnt, poseOption), parentObjStr, type="string");

def getJntInformations(allJnts, poseOption):
    """ルートジョイントから、格納された情報を取得する

    対象となるジョイントからMatrix情報、親ノード情報を取得しリストで返す
    
    Args:
        allJnts: ([string]): ターゲットとなる全てのジョイント
        poseOption: (string): アトリビュート名で利用しているT or Aスタンス情報を示す文字列
    Returns:
        jntInfoLists: ([[worldMatrix], [localMatrix], string]]): worldMatrix, localMatrix, 親オブジェクト名文字列を含むリスト

    """
    jntInfoLists = [];
    targetJnt = allJnts[0];

    for i, jnt in enumerate(allJnts):
        worldMatAttrName = "{}_{}_{}_world_matrix".format(jnt, i, poseOption)
        localMatAttrName = "{}_{}_{}_local_matrix".format(jnt, i, poseOption);

        worldMat = cmds.getAttr("{}.{}_world_matrixs.{}".format(targetJnt, poseOption, worldMatAttrName));
        localMat = cmds.getAttr("{}.{}_local_matrixs.{}".format(targetJnt, poseOption, localMatAttrName));

        jntInfoLists.append([worldMat, localMat, jnt]);

    return jntInfoLists;

def applyJntInformations(jntInfoLists):
    """取得されたMatrix情報を用いて、対象となるジョイント群に値をセットするメソッド

    取得されたMatrix情報を用いて、対象となるジョイント群に値をセットする
    現状の実装ではlocalMatrixの値を用いている。worldMatrixの使用については下記コード内コメント参照ください
    
    Args:
        jntInfoLists: ([[worldMatrix], [localMatrix], string]]): worldMatrix, localMatrix, 親オブジェクト名文字列を含むリスト
    Returns:
        None

    """
    for info in jntInfoLists:
        worldMat, localMat, jnt = info;

        # localMatrixを標準で使用しているが、階層を上から取得しているため、worldMatrixでも可能。その場合以下のコードに変更してください。
        # cmds.xform(jnt, matrix=worldMat, ws=True);
        cmds.xform(jnt, matrix=localMat, ws=False);

def deleteAttrs(targetJnt, poseOption):
    """ルートジョイントにセットされたアトリビュート情報を削除するメソッド

    ルートジョイントにセットされたアトリビュート情報を削除する。
    compound型に親子付けされているため、compound型アトリビュート、文字列アトリビュートのみ削除する

    Args:
        targetJnt: string: ルートジョイント名
        poseOption: (string): アトリビュート名で利用しているT or Aスタンス情報を示す文字列

    Returns:
        (bool): 処理が正常に行われたかどうか

    """

    attrExist = cmds.attributeQuery("{}_world_matrixs".format(poseOption), node=targetJnt, exists=True);
    if not attrExist:
        om.MGlobal.displayError("do not exist attributes");
        # 現状削除処理はこのメソッド以降処理がないためFalseを返す意味は薄いが、アップデートを考慮。
        return False;

    cmds.deleteAttr(targetJnt, at="{}_world_matrixs".format(poseOption));
    cmds.deleteAttr(targetJnt, at="{}_local_matrixs".format(poseOption));

    # delete parent obj list str
    cmds.deleteAttr(targetJnt, at="{}_parent_obj_info".format(poseOption));

    return True;

# confirm window
def showConfirmWindow(confirmOption):
    """確認ウィンドウを表示するメソッド

    確認ウィンドウを表示する。引数により削除or上書き表示を切り替える。

    Args:
        confirmOption: string: オプションを表す文字列

    Returns:
        (bool): ユーザーからのレスポンスからboolを返す
        
    """
    response = cmds.confirmDialog( title=confirmOption, message='Are you sure you want to {}?'.format(confirmOption), button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
    
    if response == "Yes":
        return True;
    else:
        return False;

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

    if cmds.window(WINDOW_TITLE, exists=True):
        cmds.deleteUI(WINDOW_TITLE);

    mainUi = MainWindow();
    mainUi.show();