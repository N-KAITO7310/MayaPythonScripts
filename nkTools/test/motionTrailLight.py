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
    import motionTrailLight.motionTrailLight as mtl;
    reload(mtl);
    mtl.showUi();

Attributes:
    WINDOW_TITLE(str):A title string of this tool window.
    CURVE_SUFFIX(str):Suffix of motion trail curve name.
    HELP_DOCUMENT_DIR_NAME = A dir name of document.
    HELP_DOCUMENT_FILE_NAME = A name of document file.

TODO:
    ・ツールを再度開いた際に前回閉じた際の位置情報を取得する
    ・ScriptJobによる自動更新機能
    ・UIドッキング

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
# import maya.OpenMayaUI as omui;
import shiboken2;
import maya.api.OpenMaya as om;
import os;
import subprocess;
from functools import partial

# ------------------------------------------------------------------------------
# constant var
WINDOW_TITLE = "Motion Trail Light";
CURVE_SUFFIX = "motionTrail_curve";
HELP_DOCUMENT_DIR_NAME = "\\helpDoc\\";
HELP_DOCUMENT_FILE_NAME = "motionTrailLight_helpDocument.txt"
# ------------------------------------------------------------------------------
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

# main tool Widget Class
class MainWindow(QtWidgets.QDialog):
    """メインウィンドウクラス

    UI作成、レイアウトと各ボタンへのメソッドを設定するためのクラス

    Attributes:
        None
    
    """

    def __init__(self, parent=getMayaWindow()):
        """ウィンドウクラスのinit

        この関数で行っていること
        ・ウィンドウタイトル設定
        ・UIサイズ設定
        ・縦並びレイアウト設定
        ・各ボタンと押下時のメソッド設定、レイアウトへのセット

        Args:
            parent: (QtWidgets.QWidget): 親ウィンドウとして設定するインスタンス
        Returns:
            None
        
        """
        super(MainWindow, self).__init__(getMayaWindow());
        self.setWindowTitle(WINDOW_TITLE);
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)
        self.resize(200, 100);

        # self.geometry = None;
        self.scriptJobsDict = {};
        
        self.create_actions();
        self.create_widgets();
        self.create_layout();
        self.create_connections();

    def create_actions(self):
        """Qアクションの生成関数

        QMenuBarクラスのメニューボタンに設定するためのQActionクラスインスタンスを生成する
        ＊拡張性のため関数化
        
        """

        # opent document action on menubar
        self.document_action = QtWidgets.QAction("Open Document", self);

    def create_widgets(self):
        """Widgetクラスの生成

        ボタン等Widgetクラスを生成する

        """

        # menubar
        self.menu_bar = QtWidgets.QMenuBar();
        help_menu = self.menu_bar.addMenu("Help");
        help_menu.addAction(self.document_action);
        
        # create btn
        self.__createBtn = QtWidgets.QPushButton(self);
        self.__createBtn.setText("Create");
        
        # update btn
        self.__updateBtn = QtWidgets.QPushButton(self);
        self.__updateBtn.setText("Update");

        # delete btn
        self.__deleteBtn = QtWidgets.QPushButton(self);
        self.__deleteBtn.setText("Delete");
        
    def create_layout(self):
        """レイアウト設定関数
        
        生成したWidgetクラスをレイアウトに設定する
        
        """

        # mainLayout
        mainLayout = QtWidgets.QVBoxLayout(self);
        
        # add btn widgets
        mainLayout.addWidget(self.__createBtn);
        mainLayout.addWidget(self.__updateBtn);
        mainLayout.addWidget(self.__deleteBtn);
        
        # add menubar
        mainLayout.setMenuBar(self.menu_bar);
        
    def create_connections(self):
        """スロット設定関数
        
        スロットに関数を設定する

        """

        # menubar connections
        self.document_action.triggered.connect(self.openDocument);
        
        # btn connections
        self.__createBtn.clicked.connect(self.createMotionTrail);
        self.__updateBtn.clicked.connect(self.updateMotionTrail);
        self.__deleteBtn.clicked.connect(self.deleteMotionTrail);
        
    # ------------------------------------------------------------------------------
    # main methods
    # create motion trail curve
    def createMotionTrail(self):
        """モーショントレイル作成メソッド

        選択された各オブジェクトについて移動を追跡するカーブを作成する
        Create処理とundoInfoを分けるため関数を切り出し
        
        """
        cmds.undoInfo(openChunk=True);

        self.createMotionTrailExecute();

        cmds.undoInfo(closeChunk=True);

    def createMotionTrailExecute(self):
        """モーショントレイル作成実行メソッド

        作成処理を実行。Updateでの使用、Undoを考慮し処理を切り出し
        
        """
        #Find selected transform nodes
        sel = cmds.ls(sl=True, type='transform')
        #Get playback start time
        start = int(cmds.playbackOptions(q=True, min=True));
        #Get playback end time
        end = int(cmds.playbackOptions(q=True, max=True));

        # Get worldMatrix
        #For Loop - iterate on timeRange, each selected objects
        # curveBuildDict = {curveName : [worldMatrix...]}
        curveBuildDict = {};
        for frame in range(start, end + 1):
            for each in sel:
                # define curveName
                curveName = str("{}_{}".format(each, CURVE_SUFFIX));

                # get worldMatrix in specified frame
                wMatrix = cmds.getAttr("{}.worldMatrix[0]".format(each), time=frame);
                
                # add curveBuildDict worldMatrix
                if curveBuildDict.get(curveName):
                    curveBuildDict[curveName].append(wMatrix);
                else:
                    curveBuildDict[curveName] = [wMatrix];
                
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
            cmds.setAttr("{}.overrideDisplayType".format(renamedCurve), 2);

            # lock attributes
            lockAttr(renamedCurve, ["translate", "rotate", "scale"]);

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
                
        for each in sel: 
            self.create_script_jobs(each);

        # if not "playBack" in self.scriptJobsDict:
        #     self.scriptJobsDict["playBack"] = cmds.scriptJob(event=["playbackRangeSliderChanged", self.updateMotionTrail]);

    # create and delete motion trail curve
    def updateMotionTrail(self):
        """モーショントレイル更新メソッド

        現在シーン上に存在するこのモジュールによるトレイルカーブをすべて最新に更新する

        """
        cmds.undoInfo(openChunk=True);

        alreadyExistsCurves = findAlreadyExistCurves();
       
        # カーブから追跡するオブジェクト名を取得。既存カーブの削除処理。
        animTargets = [];
        for curve in alreadyExistsCurves:
            targetName = curve[:curve.rfind(CURVE_SUFFIX)-1];
            animTargets.append(targetName);
        cmds.delete(alreadyExistsCurves);
        
        self.delete_script_jobs();

        # 追跡オブジェクトを選択し、再度作成処理を実行
        cmds.select(animTargets, r=True);
        self.createMotionTrailExecute();

        cmds.undoInfo(closeChunk=True);

    # delete all motion trail curve
    def deleteMotionTrail(self):
        """モーショントレイル削除メソッド

        現在シーン上に存在するトレイルカーブを全て削除する。

        """
        cmds.undoInfo(openChunk=True);

        alreadyExistsCurves = findAlreadyExistCurves();
        cmds.delete(alreadyExistsCurves);
        
        self.delete_script_jobs();

        cmds.undoInfo(closeChunk=True);

    # open help document file
    def openDocument(self):
        """ヘルプドキュメントファイルを開くメソッド

        所定のディレクトリに存在するヘルプドキュメントファイルを開く。

        """
        absPath = os.path.abspath(__file__);
        path, filename = os.path.split(absPath);

        filePath = path + HELP_DOCUMENT_DIR_NAME +  HELP_DOCUMENT_FILE_NAME;

        subprocess.Popen(filePath,shell=True);
        
        
    def create_script_jobs(self, objName):
        self.scriptJobsDict[objName] = cmds.scriptJob(attributeChange=["{}.translate".format(objName), partial(self.on_trailTarget_moved)]);
        #self.scriptJobsDict["playBack"] = cmds.scriptJob(event=["playbackRangeSliderChanged", self.updateMotionTrail]);

    def delete_script_jobs(self):
        for objName in self.scriptJobsDict.keys():
            cmds.scriptJob(kill=self.scriptJobsDict[objName]);
            
        self.scriptJobsDict = {};

    def on_trailTarget_moved(self):
        movedObjs = cmds.ls(sl=True, type="transform");

        updateTargets = {};
        for movedObj in movedObjs:
            curveName = str("{}_{}".format(movedObj, CURVE_SUFFIX));
            cmds.ls(curveName);
            if len(curveName) > 0:
                updateTargets[movedObj] = curveName;

        for movedObj in updateTargets.keys():
            curveName = updateTargets[movedObj];

            cmds.delete(curveName);
            cmds.evalDeferred("cmds.scriptJob(kill={})".format(self.scriptJobsDict[movedObj]));

            cmds.select(movedObj, r=True);
            self.createMotionTrailExecute();

        cmds.select(movedObjs, r=True);
        
        print("scriptjob test");
        
# ------------------------------------------------------------------------------
# helper methods
def findAlreadyExistCurves(s=False):
    """シーン内のモーショントレイルカーブを取得するヘルパー関数

    シーン内のモーショントレイルカーブを取得する。対象カーブが取得できない場合エラー表示を行う。

    Args:
        s(bool): True:シーン内の該当するカーブのシェイプを返す。 False:シーン内の該当するカーブのトランスフォームを返す。

    Returns:
        [str]: 該当するオブジェクト名のリスト

    """
    # get targets
    if s:
        alreadyExistsCurve = cmds.ls("::*{}Shape".format(CURVE_SUFFIX), s=True, type="nurbsCurve");

    else:
        alreadyExistsCurve = cmds.ls("::*{}".format(CURVE_SUFFIX), s=False, type="transform");

    if len(alreadyExistsCurve) == 0:
        om.MGlobal.displayError("There are no motion trail curves in the scene. Please Create motion trail curve");

    return alreadyExistsCurve;

def lockAttr(object, attributes):
    """対象オブジェクトの指定したアトリビュートを全てロックするヘルパー関数

    対象オブジェクトの指定したアトリビュートを全てロックする
    
    """

    for attr in attributes:
        cmds.setAttr("{}.{}".format(object, attr), l=True);
        
# show ui
def showUi():
    """UI表示関数
    
    このツールにおけるUIを表示する

    """
    try:
        mainUi.close() # pylint: disable=E0601
        mainUi.delete_script_jobs();
        mainUi.deleteLater();
    except:
        pass;

    mainUi = MainWindow();
    mainUi.show();