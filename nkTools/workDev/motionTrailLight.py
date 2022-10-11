# -*- coding: utf-8 -*-
"""軽量版モーショントレイルツール

ツール概要
NurbsCurveを利用した軽量版モーショントレイルの作成、更新、削除ツール

基本要件：
Maya標準モーショントレイルの処理が重く多用するとフレームレートを落とす懸念があるため、処理の軽い廉価版を利用したい
1. 指定ノード（※複数可能）の軌跡をNurbsCurveで生成
2. カーブを編集することによってモーションが修正される必要はない
3. 簡単操作でカーブの生成・削除が行える

Example:
    py2:
    import motionTrailLight.motionTrailLight as mtl;
    reload(mtl);
    mtl.showUi();

    py3
    import motionTrailLight.motionTrailLight as mtl;
    import importlib;
    importlib.reload(mtl);
    mtl.showUi();

Attributes:
    WINDOW_TITLE(str):A title string of this tool window.
    CURVE_SUFFIX(str):Suffix of motion trail curve name.
    HELP_DOCUMENT_DIR_NAME = A dir name of document.
    HELP_DOCUMENT_FILE_NAME = A name of document file.
    LOC_SUFFIX = suffix of locator name
    CURVE_GROUP = name of top node
    SCRIPTNODENAME = name of scriptNode

lastUpdated: 2022/08/03
"""
# ------------------------------------------------------------------------------
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

# ------------------------------------------------------------------------------
# constant var
WINDOW_TITLE = "Motion Trail Light";
CURVE_SUFFIX = "motionTrail_curve";
HELP_DOCUMENT_DIR_NAME = "\\helpDoc\\";
HELP_DOCUMENT_FILE_NAME = "motionTrailLight_helpDocument.txt";
LOC_SUFFIX = "motionTrail_loc";
CURVE_GROUP = "motionTrailLight_grp"
SCRIPTNODENAME = "motionTrailLightScriptNode"
TRANSLATION_ATTRS = ["tx", "ty", "tz"];
ROTATE_ATTRS = ["rx", "ry", "rz"];
SCALE_ATTRS = ["sx", "sy", "sz"];
COLOR_RED_INDEX = 13;
CURVE_OPTION_NAME = "DisplayOption";
CURVE_DISPLAY_ENUM = ["Normal", "Template", "Reference"];
class CreateOption():
    REFERENCE_TARGET = 0;
    REFERENCE_LOCATOR = 1;
# ------------------------------------------------------------------------------
# global var
settings = None;
# callbackIds = {curveName: callbackId}
callbackIds = {};
# curveInfoDict = {curveName: {vtx: worldMat}}
curveInfoDict = {};
locList = [];

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

class WorkspaceControl(object):
    """workspaceControlメソッド利用クラス
    
    cmds.workspaceControlメソッド処理をまとめたクラス

    Attributes:
        None

    """

    def __init__(self, name):
        """WorkspaceControlクラスのinit

        name変数の初期化

        Args:
            name: ウィンドウ名 'Motion Trail Light WorkspaceControl'をセット
            widget: ウィンドウにはめ込むウィジェットオブジェクト
        Returns:
            None

        """
        self.name = name
        self.widget = None

    def create(self, label, widget, ui_script=None):
        """WorkspaceControlオブジェクトの作成と設定

        WorkspaceControlオブジェクトを作成し、渡されたウィジェットをMayaLayoutにセットする

        Args:
            label: ウィンドウ名
            widget: workSpacerControlで設定するウィジェットオブジェクト
            ui_script: cmds.workSpaceControlのフラグuiScriptに渡すスクリプト。必須フラグ。既定でNone。
        Returns:
            None

        """

        cmds.workspaceControl(self.name, label=label)

        if ui_script:
            cmds.workspaceControl(self.name, e=True, uiScript=ui_script)

        self.add_widget_to_layout(widget)
        self.set_visible(True)

    def restore(self, widget):
        """widgetオブジェクトに対して再度add_widget_to_layoutのみ実行する関数

        widgetオブジェクトに対して再度add_widget_to_layoutのみ実行する

        Args:
            widget: workSpacerControlで設定するウィジェットオブジェクト
        Returns:
            None

        """
        self.add_widget_to_layout(widget)

    def add_widget_to_layout(self, widget):
        """widgetオブジェクトをworkSpaceControlに追加する関数

        widgetとworkSpaceControlウィンドウのポインターを利用し、UIをworkSpaceControlに追加する

        Args:
            widget: workSpacerControlに追加するウィジェットオブジェクト
        Returns:
            None

        """
        if widget:
            self.widget = widget
            self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)

            if sys.version_info.major >= 3:
                workspace_control_ptr = int(omui.MQtUtil.findControl(self.name))
                widget_ptr = int(shiboken2.getCppPointer(self.widget)[0])
            else:
                workspace_control_ptr = long(omui.MQtUtil.findControl(self.name))
                widget_ptr = long(shiboken2.getCppPointer(self.widget)[0])

            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

    def exists(self):
        """workSpaceControlが既に存在するかを照会する関数

        workSpaceControlが既に存在するかを照会する

        Args:
            None
        Returns:
            None

        """
        return cmds.workspaceControl(self.name, q=True, exists=True)

    def is_visible(self):
        """workSpaceControlが既にvisible=Trueであるかを照会する関数

        workSpaceControlが既にvisible=Trueであるかを照会する

        Args:
            None
        Returns:
            None

        """
        return cmds.workspaceControl(self.name, q=True, visible=True)

    def set_visible(self, visible):
        """workSpaceControlのrestoreフラグをスイッチする関数

        workSpaceControlのrestoreフラグをスイッチする

        Args:
            None
        Returns:
            None

        """

        if visible:
            cmds.workspaceControl(self.name, e=True, restore=True)
        else:
            cmds.workspaceControl(self.name, e=True, visible=False)

    def set_label(self, label):
        """workSpaceControlのlabelフラグにテキストをセットする関数

        workSpaceControlのlabelフラグにテキストをセットする

        Args:
            None
        Returns:
            None

        """

        cmds.workspaceControl(self.name, e=True, label=label)

    def is_floating(self):
        """workSpaceControlのfloatingフラグを照会する関数

        workSpaceControlのfloatingフラグを照会する

        Args:
            None
        Returns:
            None

        """

        return cmds.workspaceControl(self.name, q=True, floating=True)

    def is_collapsed(self):
        """workSpaceControlのcollapseフラグを照会する関数

        workSpaceControlのcollapseフラグを照会する

        Args:
            None
        Returns:
            None

        """

        return cmds.workspaceControl(self.name, q=True, collapse=True)

# main tool Widget Class
class MainWindow(QtWidgets.QDialog):
    """メインウィンドウクラス

    ・UI作成、レイアウトと各ボタンへバインドされるメソッドの設定
    ・自動更新処理を目的としたコールバック、スクリプトノード作成関連処理
    ・作成、更新、削除処理

    Attributes:
        uiInstance: MainWindowインスタンスを保持
        UI_NAME: MainWindowクラスの名前
    
    """

    uiInstance = None;
    UI_NAME = "Motion Trail Light"

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
        super(MainWindow, self).__init__();
        self.setWindowTitle(WINDOW_TITLE);
        self.setObjectName(self.__class__.UI_NAME);
        self.setMinimumSize(350, 250);

        self.create_actions();
        self.create_widgets();
        self.create_layout();
        self.create_connections();
        self.create_workspace_control()

        self.settingInitialize()

    def settingInitialize(self):
        """ウィジェットプロパティへデフォルト値をセットする関数

        settings変数よりデフォルト値を取得し、各ウィジェットへセットする

        Args:
            None
        Returns:
            None
        
        """
        
        global settings;

        self.__locSizeSpinBox.setValue(settings.locSize);
        self.__autoUpdateCheckBox.setChecked(settings.autoUpdateEnable);

    def saveSettings(self):
        """UIから取得した情報でsettings変数を更新する関数

        UIから取得した情報でsettings変数を更新する

        Args:
            None
        Returns:
            None
        
        """

        settings.autoUpdateEnable = self.__autoUpdateCheckBox.isChecked();
        settings.locSize = self.__locSizeSpinBox.value();

    @classmethod
    def display(cls):
        """UIの表示クラス関数

        uiInstanceが既に存在すればUIを表示する関数を実行。ない場合はMainWindowクラスを作成。

        Args:
            None
        Returns:
            None
        
        """

        if cls.uiInstance:
            cls.uiInstance.show_workspace_control()
        else:
            cls.uiInstance = MainWindow()

    def show_workspace_control(self):
        """UIの表示関数
        
        UIを表示する

        Args:
            None
        Returns:
            None

        """

        self.workspace_control_instance.set_visible(True)

    @classmethod
    def get_workspace_control_name(cls):
        """MainWindowクラスのワークスペースコントロール名を返すクラス関数

        MainWindowクラスのUI_NAME末尾にWorkspaceControlを追加したテキストを返す

        Args:
            None
        Returns:
            string: MainWindowクラスのUI_NAME末尾にWorkspaceControlを追加したテキスト
        
        """

        return "{0}WorkspaceControl".format(cls.UI_NAME)

    def create_actions(self):
        """Qアクションの生成関数

        QMenuBarクラスのメニューボタンに設定するためのQActionクラスインスタンスを生成する
        ＊拡張性のため関数化

        Args:
            None
        Returns:
            None
        
        """

        # opent document action on menubar
        self.document_action = QtWidgets.QAction("Open Document", self);

    def create_widgets(self):
        """Widgetクラスの生成

        ボタン等各Widgetクラスを生成する

        Args:
            None
        Returns:
            None

        """

        # menubar
        self.menu_bar = QtWidgets.QMenuBar();
        help_menu = self.menu_bar.addMenu("Help");
        help_menu.addAction(self.document_action);
        
        # create btn
        self.__createBtn = QtWidgets.QPushButton(self);
        self.__createBtn.setText("Create");

        # auto update checkBox
        self.__autoUpdateCheckBox = QtWidgets.QCheckBox("AutoUpdate Enable", self)

        # locator size label
        self.__locSizseLabel = QtWidgets.QLabel("Locator Size", self);

        # locator size spinBox
        self.__locSizeSpinBox = QtWidgets.QDoubleSpinBox(self);
        self.__locSizeSpinBox.setMinimum(0);
        self.__locSizeSpinBox.setMaximum(100);
        self.__locSizeSpinBox.setDecimals(1);
        
        # update btn
        self.__updateBtn = QtWidgets.QPushButton(self);
        self.__updateBtn.setText("Update");

        # delete btn
        self.__deleteBtn = QtWidgets.QPushButton(self);
        self.__deleteBtn.setText("Delete");
        
    def create_layout(self):
        """レイアウト設定関数
        
        生成したWidgetクラスをレイアウトに設定する

        Args:
            None
        Returns:
            None
        
        """

        # mainLayout
        mainLayout = QtWidgets.QVBoxLayout(self);

        # subLayout
        locSizeLayout = QtWidgets.QHBoxLayout(self);
        locSizeLayout.addWidget(self.__locSizseLabel);
        locSizeLayout.addWidget(self.__locSizeSpinBox);
        
        # add btn widgets
        mainLayout.addWidget(self.__createBtn);
        mainLayout.addWidget(self.__autoUpdateCheckBox);
        mainLayout.addLayout(locSizeLayout);
        mainLayout.addWidget(self.__updateBtn);
        mainLayout.addWidget(self.__deleteBtn);
        
        # add menubar
        mainLayout.setMenuBar(self.menu_bar);
        
    def create_connections(self):
        """スロット設定関数
        
        各ウィジェットのスロットに関数を設定する

        Args:
            None
        Returns:
            None

        """

        # menubar connections
        self.document_action.triggered.connect(self.openDocument);
        
        # btn connections
        self.__createBtn.clicked.connect(self.createMotionTrail);
        self.__updateBtn.clicked.connect(self.updateMotionTrail);
        self.__deleteBtn.clicked.connect(self.deleteMotionTrail);
        self.__autoUpdateCheckBox.stateChanged.connect(self.switchAutoUpdateEnable);
        
    def create_workspace_control(self):
        """workSpaceControlインスタンスを作成する関数
        
        workSpaceControlインスタンスを作成し、既に存在すればリストア、なければ作成し、ウィンドウを表示する

        Args:
            None
        Returns:
            None

        """

        self.workspace_control_instance = WorkspaceControl(self.get_workspace_control_name())
        if self.workspace_control_instance.exists():
            self.workspace_control_instance.restore(self)
        else:
            self.workspace_control_instance.create(WINDOW_TITLE, self, ui_script="from workspace_control import MainWindow\MainWindow.display()");

    # ------------------------------------------------------------------------------
    # Callback
    def setKeyFrameCallback(self, curveName, animCurve, targetObj=None, option=0):
        """指定したアニメーションカーブノードにコールバックを設定する
        
        アニメーションカーブノードにMAnimMessageクラスによるコールバックを設定する

        Args:
            curveName: 作成したモーションパスカーブの名前
            animCurve: キー変更を検知する対象となるanimCurveノード
            targetObj: translationを検知する対象となるMayaシーン上のオブジェクト名※現在はコメントアウトのため不要
        Returns:
            None

        """

        cmds.select(animCurve);
        animNodeMObjectList = om.MGlobal.getActiveSelectionList();
        animNodeMObject = animNodeMObjectList.getDependNode(0);

        # cmds.select(targetObj);
        # targetMObjectList = om.MGlobal.getActiveSelectionList();
        # targetMObject = targetMObjectList.getDependNode(0);
        if option == 0:
            if curveName in callbackIds:
                callbackIds[curveName].append(oma.MAnimMessage.addNodeAnimKeyframeEditedCallback(animNodeMObject, self.callbackOnTrailTargetMoved));
            else:
                callbackIds[curveName] = [oma.MAnimMessage.addNodeAnimKeyframeEditedCallback(animNodeMObject, self.callbackOnTrailTargetMoved)];
        elif option == 1:
            if curveName in callbackIds:
                    callbackIds[curveName].append(oma.MAnimMessage.addNodeAnimKeyframeEditedCallback(animNodeMObject, self.callbackOnLocatorMoved));
            else:
                callbackIds[curveName] = [oma.MAnimMessage.addNodeAnimKeyframeEditedCallback(animNodeMObject, self.callbackOnLocatorMoved)];

        
    def setPreRemoveCallback(self, curveName):
        """指定したモーションパスカーブが削除された際のコールバックを設定する関数
        
        指定したモーションパスカーブが削除された際に実行されるコールバックを設定する

        Args:
            curveName: コールバックを設定する対象となるモーションパスカーブオブジェクト名
        Returns:
            None

        """

        cmds.select(curveName);
        curveMObjectList = om.MGlobal.getActiveSelectionList();
        curveMObject = curveMObjectList.getDependNode(0);
        callbackIds[curveName].append(om.MNodeMessage.addNodePreRemovalCallback(curveMObject, self.callbackOnTargetDeleted));

    # addNodeAnimKeyframeEditedCallbackなどに渡す際にエラーがでるためコメントアウト
    # def undoChunk(func):
    #         def wrapper(*args, **kwargs):
    #             cmds.undoInfo(swf = False)
    #             func(*args, **kwargs)
    #             cmds.undoInfo(swf = True)
    #             return wrapper

    def callbackOnTrailTargetMoved(self, *args, **kwargs):
        """モーションパス対象オブジェクトが移動した際に実行されるコールバック関数
        
        モーションパス対象オブジェクトが移動した際に実行されるコールバック処理。
        移動時の選択オブジェクトから追跡対象となるオブジェクトかを確認し、
        該当する場合は、そのカーブを削除し、再度作成処理を行う。
        *args, **kwargs指定はコールバック関数として呼び出される際に必要となるため記述

        Args:
            None
        Returns:
            None

        """

        global curveInfoDict, locList;

        cmds.undoInfo(swf=False);

        if settings.autoUpdateEnable:

            selectedObjs = cmds.ls(sl=True);

            for s in selectedObjs:
                curveName = "{}_{}".format(s, CURVE_SUFFIX);

                if curveName in curveInfoDict:
                    locName = "{}_{}".format(s, LOC_SUFFIX);

                    if locName in locList:
                        # delete curve, delete callbacks, recreate curve
                        cmds.delete(curveName);
                            
                        self.deleteCallback(curveName);
                                                
                        cmds.select(s);
                        self.createMotionTrailExecute();
                        
                        # 移動させたフレームに対応した頂点のみを移動させる。
                        # ＊該当フレーム付近のカーブの形状がパスとずれるためコメントアウト。
                        # update vtx
                        # cmds.select(cl=True);
                        # cmds.select(curveName);
                        # omCurve = om.MGlobal.getActiveSelectionList();
                        # dagPath = omCurve.getDagPath(0);
                        # curveFn = om.MFnNurbsCurve(dagPath);

                        # mMat = om.MMatrix(movedObjMat);
                        # tMat = om.MTransformationMatrix(mMat);
                        # trans = tMat.translation(om.MSpace.kWorld);
                        # point = om.MPoint([trans.x, trans.y, trans.z])
                        # curveFn.setCVPosition(culcVtxNum, point, space=om.MSpace.kWorld);

                        # curveFn.updateCurve();

                        # if curveName in curveInfoDict:
                        #     curveInfo = curveInfoDict[curveName]
                        #     if vtxNum in curveInfo:
                        #         curveInfo[culcVtxNum] = movedObjMat;
                        #     else:
                        #         curveInfoDict[curveName] = {vtxNum: movedObjMat};
                        # else:
                        #     curveInfoDict[curveName] = {vtxNum: movedObjMat};

                cmds.select(selectedObjs);

        # print("callback triggered!")
        cmds.undoInfo(swf=True);

    def callbackOnLocatorMoved(self, *args, **kwargs):
        """ロケーターがユーザーによって移動された際に実行されるコールバック関数

        ロケーターがユーザーによって移動された際に実行された際に、
        対応するモーションパスカーブを更新する処理を行う
        *args, **kwargs指定はコールバック関数として呼び出される際に必要となるため記述

        Args:
            None;
        Returns:
            None:
        
        """
        global curveInfoDict, locList;
        cmds.undoInfo(swf=False);

        if settings.autoUpdateEnable:

            selectedObjs = cmds.ls(sl=True);

            for locName in selectedObjs:
                # get curveName from locName
                targetName = locName.split("_" + LOC_SUFFIX)[0];
                curveName = "{}_{}".format(targetName, CURVE_SUFFIX);

                if curveName in curveInfoDict:

                    if locName in locList:
                        # delete curve, delete callbacks, recreate curve
                        try:
                            cmds.delete(curveName);
                            self.deleteCallback(curveName);
                        except:
                            pass;
                        
                        cmds.select(targetName);
                        self.createMotionTrailExecute(option=CreateOption.REFERENCE_LOCATOR);
                        
                cmds.select(selectedObjs);

        # print("callback triggered!")
        cmds.undoInfo(swf=True);

    def callbackOnTargetDeleted(self, *args, **kwargs):
        """モーションパスカーブがユーザーによって削除された際に実行されるコールバック関数
        
        モーションパスカーブがユーザーによって削除された際に実行されるコールバック処理。
        そのカーブに関する保持された情報を削除する。
        グループノード以下にロケーターのみが残っている場合を想定し、グループノードを削除。
        *args, **kwargs指定はコールバック関数として呼び出される際に必要となるため記述

        Args:
            None
        Returns:
            None

        """
        global callbackIds;
        
        aboutToDeleteCurves = cmds.ls("::*{}".format(CURVE_SUFFIX), sl=True, type="transform");
        
        for curve in aboutToDeleteCurves:
            targetName = curve[:curve.rfind(CURVE_SUFFIX)-1];

            # delete locator
            locName = str("{}_{}".format(targetName, LOC_SUFFIX));
            existLoc = cmds.ls(locName);
            if existLoc is None or len(existLoc) < 1:
                return;
            cmds.delete(locName);
            locList.remove(locName);

            # delete callback
            self.deleteCallback(curve);

            # delete paret grp
            grpChildren = cmds.listRelatives(CURVE_GROUP, c=True);
            if len(grpChildren) < 2:
                cmds.delete(CURVE_GROUP);

    def deleteCallback(self, curveName):
        """特定のモーショントレイルカーブを指定し、対応するコールバックをすべて削除する関数
        
       特定のモーショントレイルカーブを指定し、対応するコールバックをすべて削除する

        Args:
            curveName: モーショントレイルカーブ名文字列
        Returns:
            None

        """

        global curveInfoDict, locList, callbackIds;

        cmds.evalDeferred("maya.api.OpenMaya.MMessage.removeCallbacks({})".format(callbackIds[curveName]));
        callbackIds.pop(curveName);

    def deleteAllCallbacks(self):
        """作成されているコールバックを全て削除する関数
        
       作成されているコールバックを全て削除し、格納している変数を初期化する

        Args:
            None
        Returns:
            None

        """
        global curveInfoDict, locList, callbackIds; 

        for curveName in callbackIds.keys():
                om.MMessage.removeCallbacks(callbackIds[curveName]);
        callbackIds = {};

    def switchAutoUpdateEnable(self):
        """自動更新処理の有効/無効チェックボックス切り替えに応じた処理を行う関数
        
        自動更新処理の有効/無効チェックボックス切り替えに応じ、以下の処理を行う
        オン
        ・カーブの取得
        ・カーブのオブジェクトを取得し、animCurveを取得
        ・animCurveに対しコールバックを設定し、情報をDictに保存
        オフ
        ・全てのコールバックを削除

        Args:
            None
        Returns:
            None

        """

        cmds.undoInfo(swf=False);

        # enableのチェック切り替えに対する処理
        self.saveSettings();

        sl = cmds.ls(sl=True);

        if settings.autoUpdateEnable:
            # callbackの作成処理
            """
           
            """
            alreadyExistsCurves = findAlreadyExistCurves(error=False);

            if len(alreadyExistsCurves) > 0:
                # カーブから追跡するオブジェクト名を取得。既存カーブの削除処理。
                for curve in alreadyExistsCurves:
                    targetName = curve[:curve.rfind(CURVE_SUFFIX)-1];

                    isExistTarget = cmds.ls(targetName);
                    if len(isExistTarget) > 0:
                        # get animnode
                        animNodes = cmds.listConnections(targetName, type="animCurveTL");
                        if not animNodes is None and len(animNodes) > 0:
                            # create callbacks
                            for animNode in animNodes:
                                self.setKeyFrameCallback(curve, animNode, targetName);
                            self.setPreRemoveCallback(curve)

                    # callback for locator
                    locName = str("{}_{}".format(targetName, LOC_SUFFIX));
                    if locName in locList:
                        # loc get animnode
                        locAnimNodes = cmds.listConnections(locName, type="animCurveTL");
                        for locAnimNode in locAnimNodes:
                            self.setKeyFrameCallback(curve, locAnimNode, locName, option=1)

        else:
            # 全てのcallbackを削除
            if len(callbackIds) > 0:
                for curveName in callbackIds.keys():
                    om.MMessage.removeCallbacks(callbackIds[curveName]);
                callbackIds.clear();

        cmds.select(sl);

        cmds.undoInfo(swf=True);

    def createScriptNode(self):
        """ScriptNodeを作成する関数
        
        ScriptNodeが既に存在するかどうかを照会し、なければ作成処理を行う

        Args:
            None
        Returns:
            None

        """
        executeCode = "import motionTrailLight.motionTrailLight as mtl;reload(mtl);ui = mtl.showUi();ui.setCallbackByScriptNode();"

        isExist = cmds.ls(SCRIPTNODENAME)
        if not isExist:
            cmds.scriptNode(scriptType=1, bs=executeCode, sourceType="python", n=SCRIPTNODENAME);

    def setCallbackByScriptNode(self):
        """ScriptNodeによって実行される関数
        
        以下の処理を行う
        ・シーン上のカーブを検索
        ・カーブが存在する場合、ターゲットのオブジェクトを名前から割り出す
        ・そのオブジェクトのanimCurveを利用してコールバックを作成
        ・カーブ情報の保持
        ・ロケーター情報の保持
        ・コールバック情報の保持

        Args:
            None
        Returns:
            None

        """
        global locList, curveInfoDict, callbackIds;

        alreadyExistsCurves = findAlreadyExistCurves();

        if len(alreadyExistsCurves) > 0:
            
            # reset callbacks
            self.deleteAllCallbacks();

            for curve in alreadyExistsCurves:
                targetName = curve[:curve.rfind(CURVE_SUFFIX)-1];

                # search locator
                locName = str("{}_{}".format(targetName, LOC_SUFFIX));
                thisTargetLoc = cmds.ls(locName);
                if len(thisTargetLoc) > 0:
                    locList.append(locName);
                else:
                    continue;

                # analyze curve info
                cmds.select(cl=True);
                cmds.select(curve);
                omCurve = om.MGlobal.getActiveSelectionList();
                dagPath = omCurve.getDagPath(0);
                curveFn = om.MFnNurbsCurve(dagPath);

                # {vtx:worldMat, ... }
                vtxAndWorldMats = {};

                cvTotalNum = curveFn.numSpans;

                for cvNum in range(cvTotalNum):
                    cvPos = curveFn.cvPosition(cvNum, om.MSpace.kWorld);
                    vtxAndWorldMats[cvNum] = cvPos;

                curveInfoDict[curve] = vtxAndWorldMats;

                # create callbacks
                animNodes = cmds.listConnections(targetName, type="animCurveTL");
                for  animNode in animNodes:
                    self.setKeyFrameCallback(curve, animNode, targetName);
                    self.setPreRemoveCallback(curve);
                    
                # callback for locator
                if locName in locList:
                    # loc get animnode
                    locAnimNodes = cmds.listConnections(locName, type="animCurveTL");
                    for locAnimNode in locAnimNodes:
                        self.setKeyFrameCallback(curve, locAnimNode, locName, option=1)

        cmds.select(cl=True);
        # for Deubug
        # print("setCallbackByScriptNode--------------------------------------------------------------------------")
        # print(curveInfoDict, locList, callbackIds)

    # ------------------------------------------------------------------------------
    # main methods
    # create motion trail curve
    def createMotionTrail(self):
        """モーショントレイル作成メソッド

        選択された各オブジェクトについて移動を追跡するカーブを作成する
        Create処理とundoInfoを分けるため関数を切り出し

        Args:
            None
        Returns:
            None
        
        """
        self.saveSettings();

        cmds.undoInfo(openChunk=True);

        self.createMotionTrailExecute();

        cmds.undoInfo(closeChunk=True);

    def createMotionTrailExecute(self, option=CreateOption.REFERENCE_TARGET):
        """モーショントレイル作成実行メソッド

        作成処理を実行。Update等での再利用、Undoを考慮し処理を切り出し

        Args:
            option: REFERENCE_TARGET=ターゲットにコンストレインされるnullを作成し、そのworldMatrixを参照する
                    REFERENCE_LOCATOR=カーブ作成時に生成されるロケーターを参照する(初回作成時のみコンストレイン、ベイク処理)
        Returns:
            None
        
        """
        global settings, curveInfoDict;

        #Find selected transform nodes
        sel = cmds.ls(sl=True, type='transform')
        if len(sel) == 0:
            om.MGlobal.displayError("Please select tracking targets");
            return;

        #Get playback start time
        start = int(cmds.playbackOptions(q=True, min=True));
        #Get playback end time
        end = int(cmds.playbackOptions(q=True, max=True));

        curveGroup = cmds.ls(CURVE_GROUP);
        if len(curveGroup) == 0:
            cmds.select(cl=True);
            curveGroup = cmds.group(n=CURVE_GROUP, empty=True);

        # Get worldMatrix
        #For Loop - iterate on timeRange, each selected objects
        # curveBuildDict = {curveName : [worldMatrix...]}
        curveBuildDict = {};
        targetAnimNodeDict = {};
        tempNullList = [];
        for frame in range(start, end + 1):
            for each in sel:
                # define curveName
                curveName = str("{}_{}".format(each, CURVE_SUFFIX));

                # create target locator
                locName = str("{}_{}".format(each, LOC_SUFFIX));
                
                existLoc = cmds.ls(locName);
                if len(existLoc) < 1:
                    loc = cmds.spaceLocator(n=locName)[0];
                    locList.append(locName);
                    locConst = cmds.parentConstraint(each, locName, mo=False);

                    # bake and delete constraint
                    cmds.bakeSimulation(locName, t=(start, end), at=TRANSLATION_ATTRS, simulation=False);
                    cmds.delete(locConst);

                    # 0824 FBによりoverride設定を削除
                    # cmds.setAttr("{}.overrideEnabled".format(locName), 1);
                    # cmds.setAttr("{}.overrideDisplayType".format(locName), 1);

                    locShape = cmds.listRelatives(locName, s=True)[0];
                    localScaleSize = settings.locSize;

                    for axis in ["X", "Y", "Z"]:
                        cmds.setAttr("{}.localScale{}".format(locShape, axis), localScaleSize);

                nullName = str("{}_{}".format(each, "null"));
                existNull = cmds.ls(nullName);
                if len(existNull) < 1:
                    tempNull = cmds.group(n=nullName, em=True);
                    tempNullList.append(tempNull);
                    tempConst = cmds.parentConstraint(each, tempNull);

                # get worldMatrix in specified frame
                if option == CreateOption.REFERENCE_TARGET:
                    wMatrix = cmds.getAttr("{}.worldMatrix[0]".format(nullName), time=frame);
                elif option == CreateOption.REFERENCE_LOCATOR:
                    wMatrix = cmds.getAttr("{}.worldMatrix[0]".format(locName), time=frame);

                # add curveBuildDict worldMatrix
                if curveBuildDict.get(curveName):
                    curveBuildDict[curveName].append(wMatrix);
                else:
                    curveBuildDict[curveName] = [wMatrix];
                    
                # get animnode
                animNodes = cmds.listConnections(each, type="animCurveTL");
                if not animNodes is None and len(animNodes) > 0:
                    targetAnimNodeDict[curveName] = [animNodes, each];

        cmds.delete(tempNullList);
                
        # Build curve
        # For Loop - iterate on curveName
        for curveName in curveBuildDict.keys():
            # check
            isExist = cmds.ls(curveName, type="transform");
            if isExist:
                cmds.delete(isExist[0]);

            #Create Curve
            curve = cmds.curve(d=1, p=[(0, 0, 0), (0, 0, 1)])
            #Rebuild the curve to create the new curve we will align to our motion trail
            rebuilded = cmds.rebuildCurve(curve, ch=False, rpo=True, rt=0, end=0, s=end - start, d=1)
            # rename obj name + suffix
            renamedCurve = cmds.rename(rebuilded, curveName);

            # change display type
            cmds.setAttr("{}.overrideEnabled".format(renamedCurve), 1);
            # cmds.setAttr("{}.overrideDisplayType".format(renamedCurve), 1);

            # change color
            cmds.setAttr("{}.overrideColor".format(renamedCurve), COLOR_RED_INDEX);

            # lock attributes
            lockAttr(renamedCurve, TRANSLATION_ATTRS + ROTATE_ATTRS + SCALE_ATTRS, hide=True);

            # add attr
            cmds.addAttr(renamedCurve, longName=CURVE_OPTION_NAME, attributeType="enum", enumName=":".join(CURVE_DISPLAY_ENUM));
            cmds.setAttr("{}.{}".format(renamedCurve, CURVE_OPTION_NAME), 0, e=True, keyable=True);
            cmds.connectAttr("{}.{}".format(renamedCurve, CURVE_OPTION_NAME), "{}.overrideDisplayType".format(renamedCurve));

            # ready MFnNubrsCurve
            cmds.select(cl=True);
            cmds.select(renamedCurve);
            omCurve = om.MGlobal.getActiveSelectionList();
            dagPath = omCurve.getDagPath(0);
            curveFn = om.MFnNurbsCurve(dagPath);
            cmds.select(cl=True);

            # CurveShape deformation
            # For Loop - iterate on worldMatrix
            for i, wMatrix in enumerate(curveBuildDict[curveName]):
                mMat = om.MMatrix(wMatrix);
                tMat = om.MTransformationMatrix(mMat);
                trans = tMat.translation(om.MSpace.kWorld);
                point = om.MPoint([trans.x, trans.y, trans.z])
                curveFn.setCVPosition(i, point, space=om.MSpace.kWorld);

                # shape update
                curveFn.updateCurve();

                if curveName in curveInfoDict:
                        curveInfoDict[curveName][i] = wMatrix;

                else:
                    curveInfoDict[curveName] = {i: wMatrix};

            # create callbacks
            if settings.autoUpdateEnable:
                if curveName in curveInfoDict:
                    if curveName in targetAnimNodeDict:
                        animNodes = targetAnimNodeDict[curveName][0];
                        target = targetAnimNodeDict[curveName][1];
                        for  animNode in animNodes:
                            self.setKeyFrameCallback(curveName, animNode, target);
                        self.setPreRemoveCallback(curveName);
                    # callback for locator
                    if locName in locList:
                        # loc get animnode
                        locAnimNodes = cmds.listConnections(locName, type="animCurveTL");
                        for locAnimNode in locAnimNodes:
                            self.setKeyFrameCallback(curveName, locAnimNode, locName, option=1)

            # organize
            for loc in locList:
                locParentGrp = cmds.listRelatives(loc, p=True);
                if locParentGrp is None:
                    cmds.parent(loc, CURVE_GROUP);
            for curve in curveInfoDict.keys():
                curveParentGrp = cmds.listRelatives(curve, p=True);
                if curveParentGrp is None:
                    cmds.parent(curveName, CURVE_GROUP);
            
        self.createScriptNode();
        cmds.select(sel);

    # create and delete motion trail curve
    def updateMotionTrail(self):
        """モーショントレイル更新メソッド

        現在シーン上に存在するこのモジュールによるトレイルカーブをすべて最新に更新する

        Args:
            None
        Returns:
            None

        """
        global callbackIds, locList, curveInfoDict;

        self.saveSettings();

        cmds.undoInfo(openChunk=True);

        selected = cmds.ls(sl=True);

        alreadyExistsCurves = findAlreadyExistCurves();

        if len(alreadyExistsCurves) > 0:
       
            # カーブから追跡するオブジェクト名を取得。既存カーブの削除処理。
            animTargets = [];
            for curve in alreadyExistsCurves:
                targetName = curve[:curve.rfind(CURVE_SUFFIX)-1];
                animTargets.append(targetName);
            cmds.delete(alreadyExistsCurves);
            curveInfoDict = {};
            
            # 全てのコールバックを削除
            self.deleteAllCallbacks();

            # 追跡オブジェクトを選択し、再度作成処理を実行
            cmds.select(animTargets, r=True);
            self.createMotionTrailExecute();

            cmds.select(selected);

        cmds.undoInfo(closeChunk=True);

    # delete all motion trail curve
    def deleteMotionTrail(self):
        """モーショントレイル削除メソッド

        現在シーン上に存在するトレイルカーブを全て削除する。

        Args:
            None
        Returns:
            None

        """
        global callbackIds, locList, curveInfoDict;

        self.saveSettings();

        cmds.undoInfo(openChunk=True);

        # alreadyExistsCurves = findAlreadyExistCurves();
        # cmds.delete(alreadyExistsCurves);

        curveGroup = cmds.ls(CURVE_GROUP);
        if len(curveGroup) > 0:
            cmds.delete(CURVE_GROUP);
            curveInfoDict = {};
            locList = [];
        else:
            om.MGlobal.displayError("There are no motion trail curves in the scene. Please Create motion trail curve");
            return;
        
        self.deleteAllCallbacks();

        scriptNode = cmds.ls(SCRIPTNODENAME);
        if len(scriptNode) > 0:
            cmds.delete(scriptNode);

        cmds.undoInfo(closeChunk=True);

    # open help document file
    def openDocument(self):
        """ヘルプドキュメントファイルを開くメソッド

        所定のディレクトリに存在するヘルプドキュメントファイルを開く。

        Args:
            None
        Returns:
            None

        """
        absPath = os.path.abspath(__file__);
        path, filename = os.path.split(absPath);

        filePath = path + HELP_DOCUMENT_DIR_NAME +  HELP_DOCUMENT_FILE_NAME;

        subprocess.Popen(filePath,shell=True);
                
# ------------------------------------------------------------------------------
# helper methods
def findAlreadyExistCurves(s=False, error=True):
    """シーン内のモーショントレイルカーブを取得するヘルパー関数

    シーン内のモーショントレイルカーブを取得する。対象カーブが取得できない場合エラー表示を行う。

    Args:
        s(bool): False:シーン内の該当するカーブのシェイプを返す。 False:シーン内の該当するカーブのトランスフォームを返す。
        error(bool): True: カーブが見つからなかった場合にエラー表示を行うかどうかの可否。汎用化のため。

    Returns:
        [str]: 該当するオブジェクト名のリスト

    """
    # get targets
    if s:
        alreadyExistsCurve = cmds.ls("::*{}Shape".format(CURVE_SUFFIX), s=True, type="nurbsCurve");

    else:
        alreadyExistsCurve = cmds.ls("::*{}".format(CURVE_SUFFIX), s=False, type="transform");
    
    if error:
        if len(alreadyExistsCurve) == 0:
            om.MGlobal.displayError("There are no motion trail curves in the scene. Please Create motion trail curve");

    return alreadyExistsCurve;

def lockAttr(object, attributes, hide=False):
    """対象オブジェクトの指定したアトリビュートを全てロックするヘルパー関数

    対象オブジェクトの指定したアトリビュートを全てロックする

    Args:
        object: ロックする対象となるオブジェクト名
        attributes: ロックする対象となるアトリビュート名
    Returns:
        None
    
    """

    for attr in attributes:
        if hide:
            cmds.setAttr("{}.{}".format(object, attr), l=True, channelBox=False, keyable=False);
        else:
            cmds.setAttr("{}.{}".format(object, attr), l=True);
        
class Settings(object):
    def __init__(self):
        self.locSize = 1.0;
        self.autoUpdateEnable = True;

# show ui
def showUi():
    """UI表示関数
    
    このツールにおけるUIを表示する

    Args:
        None
    Returns:
        MainWindow: 作成されたMainWindowインスタンス

    """
    global settings;
    
    workspace_control_name = MainWindow.get_workspace_control_name()
    if cmds.window(workspace_control_name, exists=True):
        cmds.deleteUI(workspace_control_name)

    settings = Settings();
    mainUi = MainWindow();
    return mainUi;