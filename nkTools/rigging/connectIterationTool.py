# -*- coding: utf-8 -*-

from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;


"""
ConnectIterationTool
要件：
・接続側と、被接続側のノードをそれぞれ複数読み込み
・それぞれの側で接続するアトリビュート名を入力する

必要入力情報
・接続オブジェクト名
・被接続側オブジェクトリスト
・それぞれのアトリビュートテキストデータ
←できたらアトリビュート一覧をリストに表示して選択できる仕様に今後変更したい

多＊多conection

"""

def connectIterationTool():
    # get input info
    driver = settings.driverList[0];
    driverAttr = settings.driverAttr;
    drivenList = settings.drivenList;
    drivenAttr = settings.drivenAttr;

    for driven in drivenList:
        driverAttrName = str(driven) + "." + str(drivenAttr);
        drivenAttrName = str(driver) + "." + str(driverAttr);
        cmds.connectAttr(drivenAttrName ,driverAttrName, lock=False, force=True);

        print(driverAttrName + ">>" + drivenAttrName);

# apply
def main():
    connectIterationTool();
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
        # ストッカービューを設定
        stockerView = StockerView(self);
        layout.addWidget(stockerView, 0, 0, 1, 3);

        # set driver model
        self.__driverModel = StockItemModelDriver(self);
        stockerView.setModel(self.__driverModel);

        # driver load button
        button = QtWidgets.QPushButton("load", self);
        button.clicked.connect(self.loadDrivers)
        layout.addWidget(button, 1, 0);

        # set stocker view
        stockerView = StockerView(self);
        layout.addWidget(stockerView, 2, 0, 1, 3);

        # set driven model
        self.__drivenModel = StockItemModelDriven(self);
        stockerView.setModel(self.__drivenModel);

        # driven load Button
        button = QtWidgets.QPushButton("load", self);
        button.clicked.connect(self.loadDrivens)
        layout.addWidget(button, 3, 0);

        # Input driverAttr
        driverLabel = QtWidgets.QLabel("DriverAttribute", self);
        layout.addWidget(driverLabel, 4,0);
        self.__driverAttr = QtWidgets.QLineEdit(self);
        layout.addWidget(self.__driverAttr, 4,1)

        # Input drivenAttr
        drivenLabel = QtWidgets.QLabel("DrivenAttribute", self);
        layout.addWidget(drivenLabel, 5,0);
        self.__drivenAttr = QtWidgets.QLineEdit(self);
        layout.addWidget(self.__drivenAttr, 5,1)
        
        self.initialize();

    # ウィンドウボタンの初期設定
    def initialize(self):
        pass;

    # ウィンドウで入力された値を設定にセット
    def saveSettings(self, driverModel, drivenModel):
        settings.driverAttr = str(self.__driverAttr.text());
        settings.drivenAttr = str(self.__drivenAttr.text());
        
        settings.driverList = [];
        driverRowCount = self.__driverModel.rowCount();
        for i in range(driverRowCount):
            settings.driverList.append(self.__driverModel.rowData(i));

        settings.drivenList = [];
        drivenRowCount = self.__drivenModel.rowCount();
        for i in range(drivenRowCount):
            settings.drivenList.append(self.__drivenModel.rowData(i));

    # ウィンドウ入力値をセットして処理を実行
    def apply(self):
        self.saveSettings(self.__drivenModel, self.__driverModel);
        main();

    def loadDrivers(self):
        self.__driverModel.removeRows(0, self.__driverModel.rowCount());
        objList = cmds.ls(sl=True);
        if not objList:
            return;
        for obj in objList:
            self.__driverModel.appendItem(str(obj));
            print(obj);

    def loadDrivens(self):
        self.__drivenModel.removeRows(0, self.__drivenModel.rowCount());
        objList = cmds.ls(sl=True);
        if not objList:
            return;
        for obj in objList:
            self.__drivenModel.appendItem(str(obj));

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("ConnectIterationTool");
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


class StockItemModelDriver(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(StockItemModelDriver, self).__init__(0, 1, parent);
        self.setHeaderData(0, QtCore.Qt.Horizontal, "Driver");

    def appendItem(self, driverName):
        # モデルに行を追加
        driverName = QtGui.QStandardItem(driverName);
        driverName.setEditable(False);

        self.appendRow([driverName]);

    def rowData(self, index):
        # 指定したインデックスの表示名を取得
        driverName = str(self.item(index, 0).text());

        return driverName;

class StockItemModelDriven(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(StockItemModelDriven, self).__init__(0, 1, parent);
        self.setHeaderData(0, QtCore.Qt.Horizontal, "Drivens");

    def appendItem(self, drivenName):
        # モデルに行を追加
        drivenName = QtGui.QStandardItem(drivenName);
        drivenName.setEditable(False);

        self.appendRow([drivenName]);

    def rowData(self, index):
        # 指定したインデックスの表示名を取得
        drivenName = str(self.item(index, 0).text());

        return drivenName;

class Settings(object):
    def __init__(self):
        self.driver = [];
        self.drivenList = [];
        self.driverAttr = "";
        self.drivenAttr ="";

settings = Settings();