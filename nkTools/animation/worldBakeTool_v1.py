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

WINDOW_TITLE = "SimpleWorldBakeTool";
TRANSLATION_ATTRS = ["tx", "ty", "tz"];
ROTATE_ATTRS = ["rx", "ry", "rz"];
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
    ptr = OpenMayaUI.MQtUtil.mainWindow();
    if sys.version_info.major >= 3:
        # python3
        return shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget);
    else:
        # python2
        return shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget);

class MainWindow(QtWidgets.QDialog):
    # default settings
    currentAimAxisIndex = 2;
    currentUpAxisIndex = 1;
    distance = 10;

    def __init__(self, parent=getMayaWindow()):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle(WINDOW_TITLE);
        self.setObjectName(WINDOW_TITLE);
        self.setMinimumSize(200, 50);
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint);

        self.createWidgets();
        self.createLayout();
        self.createConnections();

    def createWidgets(self):
        self.__applyButton = QtWidgets.QPushButton(self);
        self.__applyButton.setText("Apply WorldBake");

    def createLayout(self):
        mainLayout = QtWidgets.QHBoxLayout(self);

        mainLayout.addWidget(self.__applyButton, True);

    def createConnections(self):
        self.__applyButton.clicked.connect(apply);


def apply():
    cmds.undoInfo(openChunk=True);

    currentF = cmds.currentTime(q=True);

    rootObjs = cmds.ls(sl=True, type="transform")[0];
    targetObjs = cmds.ls(sl=True, type="transform")[1:];

    targetLocs = [];
    for target in targetObjs:
        loc = cmds.spaceLocator(n="{}_loc".format(target));
        targetLocs.append(loc);

        cmds.parentConstraint(target, loc, mo=False);

    startF = cmds.findKeyframe(target, which="first");
    endF = cmds.findKeyframe(target, which="last");

    cmds.bakeResults(targetLocs, t=(startF, endF), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False);

    # rootのキーと値を削除
    cmds.cutKey(rootObjs);
    cmds.xform(rootObjs, t=[0.0, 0.0, 0.0], r=[0.0, 0.0, 0.0]);

    # ロケーターからターゲットオブジェクトへコンストレイント
    for i, target in enumerate(targetObjs):
        cmds.parentConstraint(targetLocs[i], mo=False);

    # ターゲットオブジェクトに対しベイク処理
    cmds.bakeResults(targetObjs, t=(startF, endF), at=TRANSLATION_ATTRS+ROTATE_ATTRS, simulation=False)

    # ロケーターの削除
    cmds.delete(targetLocs);

    cmds.currentTime(currentF);

    cmds.undoInfo(closeChunk=True);

# show ui
def showUi():
    global mainUi;

    if cmds.window(WINDOW_TITLE, exists=True):
        cmds.deleteUI(WINDOW_TITLE);

    mainUi = MainWindow();
    mainUi.show();

if __name__ == "__main__":
    global mainUi;

    if cmds.window(WINDOW_TITLE, exists=True):
        cmds.deleteUI(WINDOW_TITLE);

    mainUi = MainWindow();
    mainUi.show();