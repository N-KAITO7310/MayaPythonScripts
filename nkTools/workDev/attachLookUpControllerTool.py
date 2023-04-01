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

attachLookUpControllerTool

import attachLookUpControllerTool as attachLookUpControllerTool;
reload(attachLookUpControllerTool);
attachLookUpControllerTool.showUi();

last updated: 2023/02/06

"""

WINDOW_TITLE = "attachLookUpControllerTool";
AXIS_LIST = ["X", "Y", "Z"];
AIM_UP = ["Aim", "Up"];
TOOL_GRP_NAME = "attachLookUpCtrl_grp";
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

    # default settings
    currentAimAxisIndex = 2;
    currentUpAxisIndex = 1;
    distance = 10;

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

        self.__distanceDouble = QtWidgets.QDoubleSpinBox(self);
        self.__distanceDouble.setMinimum(0);
        self.__distanceDouble.setMaximum(10000000);
        self.__distanceDouble.setDecimals(2);
        self.__distanceDouble.setValue(10.0);
        
        # aim axis
        self.__xOption = QtWidgets.QRadioButton("x", self);
        self.__yOption = QtWidgets.QRadioButton("y", self);
        self.__zOption = QtWidgets.QRadioButton("z", self);
        self.__zOption.setChecked(True);

        # up axis
        self.__upXOption = QtWidgets.QRadioButton("x", self);
        self.__upYOption = QtWidgets.QRadioButton("y", self);
        self.__upZOption = QtWidgets.QRadioButton("z", self);

        self.__applyButton = QtWidgets.QPushButton(self);
        self.__applyButton.setText("Apply");

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
        aimRadioLayout = QtWidgets.QHBoxLayout(self);
        upRadioLayout = QtWidgets.QHBoxLayout(self);

        mainLayout.addRow("Distance", self.__distanceDouble);

        self.__axisOption = QtWidgets.QButtonGroup(self);
        self.__axisOption.addButton(self.__xOption, 0);
        self.__axisOption.addButton(self.__yOption, 1);
        self.__axisOption.addButton(self.__zOption, 2);

        aimRadioLayout.addWidget(self.__xOption, True);
        aimRadioLayout.addWidget(self.__yOption, True);
        aimRadioLayout.addWidget(self.__zOption, True);

        mainLayout.addRow("AimAxisSetting", aimRadioLayout);

        self.__upAxisOption = QtWidgets.QButtonGroup(self);
        self.__upAxisOption.addButton(self.__upXOption, 0);
        self.__upAxisOption.addButton(self.__upYOption, 1);
        self.__upAxisOption.addButton(self.__upZOption, 2);

        upRadioLayout.addWidget(self.__upXOption, True);
        upRadioLayout.addWidget(self.__upYOption, True);
        upRadioLayout.addWidget(self.__upZOption, True);
        # createWidget関数内で設定した場合、aimのoptionが設定されなくなる問題がみられたためこちらの関数で行う
        self.__upYOption.setChecked(True);

        mainLayout.addRow("UpAxisSetting", upRadioLayout);

        mainLayout.addRow("Apply", self.__applyButton);
        mainLayout.addRow("Delete", self.__deleteButton);

    def createConnections(self):
        """スロット設定関数
        
        各ウィジェットのスロットに関数を設定する

        Args:
            None
        Returns:
            None
        """
        self.__distanceDouble.valueChanged.connect(self.setDistanceDouble);
        self.__xOption.toggled.connect(self.setAimAxis);
        self.__yOption.toggled.connect(self.setAimAxis);
        self.__zOption.toggled.connect(self.setAimAxis);
        self.__upXOption.toggled.connect(self.setUpAxis);
        self.__upYOption.toggled.connect(self.setUpAxis);
        self.__upZOption.toggled.connect(self.setUpAxis);

        self.__applyButton.clicked.connect(attach);
        self.__deleteButton.clicked.connect(delete);

    def setDistanceDouble(self):
        """コントローラ配置距離設定関数
        
        コントローラ配置距離を設定する

        Args:
            None
        Returns:
            None
        """

        self.distance = self.__distanceDouble.value();

    def setAimAxis(self):
        """aimConstraintのaim軸設定関数
        
        aimConstraintのaim軸を設定する

        Args:
            None
        Returns:
            None
        """
        self.currentAimAxisIndex = self.__axisOption.checkedId();
        if self.currentAimAxisIndex == self.currentUpAxisIndex:
            newIndex = self.currentUpAxisIndex;
            if newIndex == 2:
                newIndex = 0;
            else:
                newIndex = newIndex + 1;

            if newIndex == 0:
                self.__upXOption.setChecked(True);
                self.currentUpAxisIndex = newIndex;
            elif newIndex == 1:
                self.__upYOption.setChecked(True);
                self.currentUpAxisIndex = newIndex;
            elif newIndex == 2:
                self.__upZOption.setChecked(True);
                self.currentUpAxisIndex = newIndex;

    def setUpAxis(self):
        """aimConstraintのup軸設定関数
        
        aimConstraintのup軸を設定する

        Args:
            None
        Returns:
            None
        """

        self.currentUpAxisIndex = self.__upAxisOption.checkedId();

        if self.currentAimAxisIndex == self.currentUpAxisIndex:
            newIndex = self.currentAimAxisIndex;
            if newIndex == 2:
                newIndex = 0;
            else:
                newIndex = newIndex + 1;

            if newIndex == 0:
                self.__xOption.setChecked(True);
                self.currentAimAxisIndex = newIndex;
            elif newIndex == 1:
                self.__yOption.setChecked(True);
                self.currentAimAxisIndex = newIndex;
            elif newIndex == 2:
                self.__zOption.setChecked(True);
                self.currentAimAxisIndex = newIndex;

def attach():
    """aimコントローラアタッチ関数
    
    aimコントローラをアタッチする本処理

    Args:
        None
    Returns:
        None
    """

    cmds.undoInfo(openChunk=True);

    global mainUi;

    targetCtrl = cmds.ls(sl=True)[0];
    if cmds.objectType == "transform":
        om.MGlobal.displayError("Please Select Controller");
        return;

    # get settings
    distance = mainUi.distance;
    aimAxisIndex = mainUi.currentAimAxisIndex;
    upAxisIndex = mainUi.currentUpAxisIndex;

    aimSetting = [];
    upSetting = [];
    if aimAxisIndex == 0:
        aimSetting = [1, 0, 0];
    elif aimAxisIndex == 1:
        aimSetting = [0, 1, 0];
    elif aimAxisIndex == 2:
        aimSetting = [0, 0, 1];

    if upAxisIndex == 0:
            upSetting = [1, 0, 0];
    elif upAxisIndex == 1:
        upSetting = [0, 1, 0];
    elif upAxisIndex == 2:
        upSetting = [0, 0, 1];


    aimAxis = AXIS_LIST[aimAxisIndex];
    upAxis = AXIS_LIST[upAxisIndex];

    # create ctrl
    parentProxy = cmds.createNode("transform", n="parentProxy");

    # check
    aimCtrlOffsetName = "{}_aim_offset".format(targetCtrl);
    upCtrlOffsetName = "{}_up_offset".format(targetCtrl);
    aimCtrlOffset = cmds.ls(aimCtrlOffsetName);
    if (not aimCtrlOffset is None) and len(aimCtrlOffset) > 0:
        aimCtrlOffset = aimCtrlOffset[0];
        aimCtrl = cmds.listRelatives(aimCtrlOffset, c=True)[0];
    else:
        aimCtrlOffset = cmds.createNode("transform", n="{}_aim_offset".format(targetCtrl));
        aimCtrl = cmds.spaceLocator(n="{}_aim_ctrl".format(targetCtrl))[0];
        cmds.parent(aimCtrl, aimCtrlOffset);

    upCtrlOffset = cmds.ls(upCtrlOffsetName);
    if (not upCtrlOffset is None) and len(upCtrlOffset) > 0:
        upCtrlOffset = upCtrlOffset[0];
        upCtrl = cmds.listRelatives(upCtrlOffset, c=True)[0];
    else:
        upCtrlOffset = cmds.createNode("transform", n="{}_up_offset".format(targetCtrl))
        upCtrl = cmds.spaceLocator(n="{}_up_ctrl".format(targetCtrl))[0];
        cmds.parent(upCtrl, upCtrlOffset);

    aimConst = cmds.listConnections(targetCtrl, source=True, type="aimConstraint");
    if (not aimConst is None) and (aimConst > 0):
        cmds.delete(aimConst);

    # translation
    cmds.matchTransform(parentProxy, targetCtrl, pos=True, rot=True);
    cmds.matchTransform(aimCtrlOffset, targetCtrl, pos=True, rot=True);
    cmds.matchTransform(upCtrlOffset, targetCtrl, pos=True, rot=True);

    cmds.parent(aimCtrlOffset, parentProxy);
    cmds.parent(upCtrlOffset, parentProxy);

    # transle from distance
    cmds.setAttr("{}.translate{}".format(aimCtrlOffset, aimAxis), distance);
    cmds.setAttr("{}.translate{}".format(upCtrlOffset, upAxis), distance);

    # aimConstraint
    aimConst = cmds.aimConstraint(aimCtrl, targetCtrl, aimVector=aimSetting, upVector=upSetting, worldUpObject=upCtrl, worldUpType="object", offset=[0, 0, 0]);
    
    # grouping
    toolGrp = cmds.ls(TOOL_GRP_NAME);
    if toolGrp is None or len(toolGrp) == 0:
        toolGrp = cmds.group(n=TOOL_GRP_NAME, em=True);
    else:
        toolGrp = toolGrp[0];
    
    cmds.parent(aimCtrlOffset, toolGrp);
    cmds.parent(upCtrlOffset, toolGrp);

    cmds.delete(parentProxy);

    # annotation
    for i, ctrl in enumerate([aimCtrl, upCtrl]):
        setAnnotation(targetCtrl, ctrl, AIM_UP[i]);

    cmds.select(cl=True);

    cmds.undoInfo(closeChunk=True);

def delete():
    """aimコントローラ削除関数
    
    aimコントローラを削除する処理

    Args:
        None
    Returns:
        None
    """
    cmds.undoInfo(openChunk=True);
    print("test")

    targetCtrl = cmds.ls(sl=True)[0];
    if cmds.objectType == "transform":
        om.MGlobal.displayError("Please Select Controller");
        return;

    aimConst = cmds.listConnections(targetCtrl, source=True, type="aimConstraint")[0];
    if aimConst is None or len(aimConst) == 0:
        om.MGlobal.displayError("AimConstraint not Connected");
        return;

    aimCtrl = cmds.listConnections("{}.target[0].targetTranslate".format(aimConst), source=True, type="transform",destination=False);
    upCtrl = cmds.listConnections("{}.worldUpMatrix".format(aimConst), source=True, type="transform",destination=False);

    aimCtrlOffset = cmds.listRelatives(aimCtrl[0], p=True);
    upCtrlOffset = cmds.listRelatives(upCtrl[0], p=True);

    cmds.delete(aimCtrlOffset, upCtrlOffset);

    toolGrp = cmds.ls(TOOL_GRP_NAME);
    if not (toolGrp is None) and (not len(toolGrp) == 0):
        toolCtrl = cmds.listRelatives(toolGrp, c=True);
        if toolCtrl is None or len(toolCtrl) == 0:
            cmds.delete(toolGrp);
    
    # delete annotations
    for aimUp in AIM_UP:
        cmds.delete("{}_{}_annotation_loc".format(targetCtrl, aimUp));

    cmds.undoInfo(closeChunk=True);

def setAnnotation(target, ctrl, aimUp):
    """
    targetに対しannotationを作成
    annotationLocatorとtargetとを位置を確かに合わせる
    annotationノードをctrlにペアレントコンストレイントする
    annotationをtemplateにする

    ＊削除時にannotatioinLocatorを削除する処理を追加する必要あり
    
    """
    anLoc = cmds.spaceLocator(n="{}_{}_annotation_loc".format(target, aimUp))[0];
    cmds.matchTransform(anLoc, target);
    cmds.parent(anLoc, target);

    annotationShape = cmds.annotate(anLoc, text=aimUp);
    annotation = cmds.listRelatives(annotationShape, p=True, type="transform")[0];
    annotation = cmds.rename(annotation, "{}_{}_annotation".format(target, aimUp));
    cmds.parent(annotation, anLoc);

    cmds.parentConstraint(ctrl, annotation, mo=False);

    for an in [anLoc, annotation]:
        cmds.setAttr("{}.template".format(an), True);

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