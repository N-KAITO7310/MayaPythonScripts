# -*- coding: utf-8 -*-
from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;
"""

Connect by Matrix

1.check driver and driven hierarchy
2.get commonParent
3.multMatrix driverSide: from driver to obj under commonParent
4.multInverseMatrix drivenSide: from obj under commonParent to obj on driven
5.not same axis: duplicate driven and parent under driver,this is first mult target
6.decomposeMatrix and connect driven

from nkTools.rigging import connectByMatrix_v1_1;
reload(connectByMatrix_v1_1);
connectByMatrix_v1_1.option();
"""
def revealHierarchyUp(obj):
    hierarchyList = [];
    p = cmds.listRelatives(obj, type="transform", p=True);
    while not p is None:
        hierarchyList.append(p[0]);
        p = cmds.listRelatives(p, type="transform", p=True);

    hierarchyList.reverse();

    return hierarchyList;

def connectByMatrx():
    driver = str(cmds.ls(sl=True)[0]);
    driven = str(cmds.ls(sl=True)[1]);

    sameAxis = settings.sameAxis;

    opmList = [];
    if settings.existOffsetParentMatrix:
        opmList = settings.opmList;

    prefix = driven;
    mult = cmds.shadingNode("multMatrix", au=True, n="{0}_multMatrix".format(prefix));
    decompose = cmds.shadingNode("decomposeMatrix", au=True, n="{0}_decomposeMatrix".format(prefix));

    # find common parent
    driverParentList = revealHierarchyUp(driver);
    drivenParentList = revealHierarchyUp(driven);

    commonParent = "";
    for driverP in driverParentList:
        for drivenP in drivenParentList:
            if driverP == drivenP:
                commonParent = driverP;

    isWorld = False;
    if commonParent == "":
        isWorld = True;

    # get mult matrix target
    driverSideMultTargetList = driverParentList;
    drivenSideMultTargetList = drivenParentList;
    if not isWorld:
        commonParentUpList = [commonParent];
        cp = cmds.listRelatives(commonParent, p=True);
        while not cp is None:
            commonParentUpList.append(cp[0]);
            cp = cmds.listRelatives(cp[0], p=True);

        for cp in commonParentUpList:
            driverSideMultTargetList.remove(cp);
            drivenSideMultTargetList.remove(cp);

    # connect mult
    # driverSide
    driverSideMultTargetList.reverse();
    driverSideMultTargetList.insert(0, driver);

    matrixInNum = 0;
    if not sameAxis:
        dup = cmds.duplicate(driven, po=True, n=driven + "_forMatrixCon")[0];
        cmds.setAttr(dup + ".visibility", 0);
        cmds.parent(dup, driver);
        cmds.setAttr(mult + ".matrixIn[{0}]".format(matrixInNum), *cmds.getAttr(dup + ".matrix"), type="matrix")
        matrixInNum += 1;
        cmds.delete(dup);

    for driverSide in driverSideMultTargetList:
        cmds.connectAttr(driverSide + ".matrix",mult + ".matrixIn[{0}]".format(matrixInNum), f=True);
        matrixInNum = matrixInNum + 1;

        if settings.existOffsetParentMatrix:
            if driverSide in opmList or driven in opmList:
                cmds.connectAttr(driverSide + ".offsetParentMatrix",mult + ".matrixIn[{0}]".format(matrixInNum), f=True);
                matrixInNum = matrixInNum + 1;
        

    # drivenSide
    for i, drivenSide in enumerate(drivenSideMultTargetList):
        cmds.connectAttr(drivenSide + ".inverseMatrix",mult + ".matrixIn[{0}]".format(matrixInNum), f=True);
        matrixInNum = matrixInNum + 1;

        if settings.existOffsetParentMatrix:
            if drivenSide in opmList:
                # offsetParentMatrixの逆地をどうやって得るか？
                tmpInverse = cmds.shadingNode("inverseMatrix", au=True, n=drivenSide + "_offsetParentMatrixInverse");
                cmds.connectAttr(drivenSide + ".offsetParentMatrix",tmpInverse + ".inputMatrix", f=True);
                cmds.connectAttr(tmpInverse + ".outputMatrix",mult + ".matrixIn[{0}]".format(matrixInNum), f=True);
                matrixInNum = matrixInNum + 1;
    # If the offsetParentMatrix is also applied to the driven itself
    if settings.existOffsetParentMatrix:
        if driven in opmList:
            tmpInverse = cmds.shadingNode("inverseMatrix", au=True, n=driven + "_offsetParentMatrixInverse");
            cmds.connectAttr(driven + ".offsetParentMatrix",tmpInverse + ".inputMatrix", f=True);
            cmds.connectAttr(tmpInverse + ".outputMatrix",mult + ".matrixIn[{0}]".format(matrixInNum), f=True);

    # connect decompose
    cmds.connectAttr(mult + ".matrixSum",decompose + ".inputMatrix", f=True);

    # connect driven
    attrList = [];
    if settings.useAttr == 1:
        attrList = ["translate"];
    elif settings.useAttr == 2:
        attrList = ["rotate"];
    else:
        attrList = ["translate", "rotate", "scale", "shear"];

    for attr in attrList:
        if cmds.objectType(driven) == "joint" and attr == "rotate":
            # create culiculate nodes
            eulerToQuat = cmds.createNode("eulerToQuat", n="{}_eulerToQuat".format(driven));
            quatInvert = cmds.createNode("quatInvert", n="{}_quatInvert".format(driven));
            quatProd = cmds.createNode("quatProd", n="{}_quatProd".format(driven));
            quatToEuler = cmds.createNode("quatToEuler", n="{}_quatToEuler".format(driven));
            
            # connect network
            cmds.connectAttr("{}.jointOrient".format(driven), "{}.inputRotate".format(eulerToQuat));
            cmds.connectAttr("{}.outputQuat".format(eulerToQuat), "{}.inputQuat".format(quatInvert));
            cmds.connectAttr("{}.outputQuat".format(decompose), "{}.input1Quat".format(quatProd));
            cmds.connectAttr("{}.outputQuat".format(quatInvert), "{}.input2Quat".format(quatProd));
            cmds.connectAttr("{}.outputQuat".format(quatProd), "{}.inputQuat".format(quatToEuler));
            cmds.connectAttr("{}.outputRotate".format(quatToEuler), "{}.rotate".format(driven));
            pass;
        else:
            cmds.connectAttr("{0}.output{1}".format(decompose, str.capitalize(attr)), "{0}.{1}".format(driven, attr), f=True);q

    # apply
def main():
    connectByMatrx();
    OpenMaya.MGlobal.displayInfo("Done");

# show Window
def option():
    window = MainWindow(qt.getMayaWindow());
    window.show();

# setting option Button
class OptionWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(OptionWidget, self).__init__(*args, **kwargs);

        # グリッドレイアウトを設定
        layout = QtWidgets.QGridLayout(self);

        # whitch use attr?
        parent = QtWidgets.QRadioButton("Parent", self);
        point = QtWidgets.QRadioButton("Point", self);
        orient = QtWidgets.QRadioButton("Orient", self);

        # set radio button
        layout.addWidget(parent, 0, 0);
        layout.addWidget(point, 0, 1);
        layout.addWidget(orient, 0, 2);

        self.__useAttr = QtWidgets.QButtonGroup(self);
        self.__useAttr.addButton(parent, 0);
        self.__useAttr.addButton(point, 1);
        self.__useAttr.addButton(orient, 2);

        # checkbox sameAxis
        axisLabel = QtWidgets.QLabel("SameAxis：", self);
        layout.addWidget(axisLabel, 1,0);
        self.__sameAxis = QtWidgets.QCheckBox("Same", self);
        layout.addWidget(self.__sameAxis, 1, 1);

        # checkbox selfexistOffsetParentMatrix
        switchLabel = QtWidgets.QLabel("ExistOffsetParentMatrx：", self);
        layout.addWidget(switchLabel, 2,0);
        self.__existOffsetParentMatrix = QtWidgets.QCheckBox("Exist", self);
        layout.addWidget(self.__existOffsetParentMatrix, 2, 1);

        # set stockerView
        stockerView = StockerView(self);
        layout.addWidget(stockerView, 3, 0, 1, 3);

        # set opm model
        self.__opmModel = StockItemModelOpm(self);
        stockerView.setModel(self.__opmModel);

        # opm load button
        button = QtWidgets.QPushButton("load", self);
        button.clicked.connect(self.loadOpms);
        layout.addWidget(button, 4, 0);
        
        
        self.initialize();

    # ウィンドウボタンの初期設定
    def initialize(self):
        self.__useAttr.button(settings.useAttr).setChecked(True);
        self.__sameAxis.setChecked(settings.sameAxis);
        self.__existOffsetParentMatrix.setChecked(settings.existOffsetParentMatrix);

    # ウィンドウで入力された値を設定にセット
    def saveSettings(self, opmModel):
        settings.useAttr = self.__useAttr.checkedId();
        settings.sameAxis = self.__sameAxis.isChecked();
        settings.existOffsetParentMatrix = self.__existOffsetParentMatrix.isChecked();
        
        settings.opmList = [];
        opmListRowCount = self.__opmModel.rowCount();
        for i in range(opmListRowCount):
            settings.opmList.append(self.__opmModel.rowData(i));

    # ウィンドウ入力値をセットして処理を実行
    def apply(self):
        self.saveSettings(self.__opmModel);
        main();

    def loadOpms(self):
        self.__opmModel.removeRows(0, self.__opmModel.rowCount());
        objList = cmds.ls(sl=True);
        if not objList:
            return;
        for obj in objList:
            self.__opmModel.appendItem(str(obj));
            print(obj);

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("ConnectByMatrix");
        self.resize(500, 500);

        # qt.pyで設定したウィジェット(下部実行ボタン＆スクロールエリア)をウィンドウに設定
        toolWidget = qt.ToolWidget(self);
        self.setCentralWidget(toolWidget);

        # スクロールエリアにオプションウィジェットを設定する
        optionWidget = OptionWidget(self);
        toolWidget.setOptionWidget(optionWidget);
        
        # 実行＆closeにウィンドウタイトルを設定
        toolWidget.setActionName(self.windowTitle());
        # appliedシグナルにslotを設定
        toolWidget.applied.connect(optionWidget.apply);# qt.Callback(optionWidget.apply) ←動作しないため削除
        # closedのスロットにQmainWindowのcloseメソッドを設定
        toolWidget.closed.connect(self.close);


# 選択オブジェクトの表示ビュー
class StockerView(QtWidgets.QTreeView):
    mimeType = "application/x-mytool-copyattribute-data";

    def __init__(self, *args, **kwargs):
        super(StockerView, self).__init__(*args, **kwargs);
        # Ctrl,Shiftで選択可能設定
        self.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection);
        # リストで交互に色を変更
        self.setAlternatingRowColors(True);
        # ルート表示不可に設定
        self.setRootIsDecorated(False);

    def removeSelectedItem(self):
        model = self.model();
        selModel = self.selectModel();

        while selModel.selectedIndexes():
            indexes = selModel.selectedIndexes();
            model.removeRow(indexes[0].row());

class StockItemModelOpm(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(StockItemModelOpm, self).__init__(0, 1, parent);
        self.setHeaderData(0, QtCore.Qt.Horizontal, "offsetParentMatrixObj");

    def appendItem(self, opm):
        # モデルに行を追加
        opm = QtGui.QStandardItem(opm);
        opm.setEditable(False);

        self.appendRow([opm]);

    def rowData(self, index):
        # 指定したインデックスの表示名を取得
        opm = str(self.item(index, 0).text());

        return opm;

class Settings(object):
    def __init__(self):
        self.useAttr = 0;
        self.sameAxis = True;
        self.existOffsetParentMatrix = False;
        self.opmList = [];

settings = Settings();