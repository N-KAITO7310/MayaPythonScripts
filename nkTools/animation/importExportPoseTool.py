# -*- coding: utf-8 -*-

import maya.api.OpenMayaUI as omUI;
import maya.api.OpenMaya as om;
import maya.cmds as cmds;
import json, time;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN;
import glob


"""
version: 1.0
created Date: 2022/02/01

import nkTools.animation.importExportPoseTool as importExportPoseTool;
reload(importExportPoseTool);
reload(importExportPoseTool.qt);
importExportPoseTool.option();

要件定義
・画像のキャプチャ機能
・コントローラ情報の取得とJSONデータ化
・JSON書き出し

ポイント
・Json書き出し処理
・コントローラの情報をどうJsonの形に成型するか
・ファイルパスの指定
・汎用的なものにするかどうか

UI必要項目
・import or export チェックボックス
・import元またはexport先ファイルパス
新規
・表示ウィジェットによる指定画像表示(Qlabel)
・import export でタブを分ける(QtabWidget)*v2での追加項目として
・ファイル表示をリストし、選択することでインタラクティブに画像を表示する
・プログレスバーの表示

スケジュール
・まずは、最小単位、エクスポートから開発をはじめる
・次にインポート機能の追加
・UIを凝るのは最後の工程とする(特に画像表示など)
"""

def saveImg(filePass):
    # アクティブなviewportを取得
    view = omUI.M3dView.active3dView();
    # 空の画像を作成
    image = om.MImage();
    view.readColorBuffer(image, True);
    image.resize(960, 540, preserveAspectRatio=True);

    try:
        temp = filePass.split(".");
        format = temp[-1];
        image.writeToFile(filePass, format);
    except:
        return False;

    return True;

def exportJson(data, filePass):
    jsonName = filePass[:filePass.rfind(".")] + ".json";
    
    writeJsonFile(data, jsonName);
    
def writeJsonFile(dataToWrite, fileName):
    if ".json" not in fileName:
        fileName += ".json"

    print "> write to json file is seeing: {0}".format(fileName)

    with open(fileName, "w") as jsonFile:
        json.dump(dataToWrite, jsonFile, indent=4, separators=(',', ': '))

    print "Data was successfully written to {0}".format(fileName)

    return fileName

def getSceneCtrlInfo():
    ctrls = cmds.ls( '*_ctrl');
    ctrls = map(lambda ctrl: str(ctrl), ctrls);
    
    ctrlsDict = {};
    for ctrl in ctrls:
        
        attrList = cmds.listAttr(ctrl, keyable=True, unlocked = True, connectable=True);
        attrList = map(lambda attr: str(attr), attrList);
        
        ctrlInfoDict = {};
        for attr in attrList:
            connectExist = cmds.listConnections("{0}.{1}".format(ctrl, attr), s=True, d=False);
            if not connectExist is None:
                continue;
            
            value = cmds.getAttr("{0}.{1}".format(ctrl, attr));
            if type(value) is float:
                # 余計な少数の丸め処理。float型ではなく文字列str型を指定すると正確にその値のDecimal型として扱われる
                value = float(Decimal(str(value)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP));
            ctrlInfoDict[attr] = value;
    
        ctrlsDict[ctrl] = ctrlInfoDict;
    
    return ctrlsDict;
    

def exportPose():
    filePass = settings.filePass
    # capture image
    imgResult = saveImg(filePass);
    
    if not imgResult:
        om.MGlobal.displayError("Failed to save picture.");
        return;
        
    # get controller info
    fileName = filePass[filePass.rfind("/"):];
    exportData = {"time": time.time(), "filePass": settings.filePass, "fileName": fileName};
    
    ctrlsData = getSceneCtrlInfo();
    exportData["controllerInfo"] = ctrlsData;
    
    # write json
    exportJson(exportData, filePass);
        
def importPose():
    print("start import");
    filePass = settings.filePass
    # json parse
    with open(filePass) as jsonFile:
        importData = json.load(jsonFile);
    
    # set attr iteration
    ctrlsDict = importData["controllerInfo"];
    for ctrl in ctrlsDict.keys():
        # 各コントローラ毎に、持っているアトリビュートでイテレート
        attrDict = ctrlsDict[ctrl];
        for attr in attrDict.keys():
            value = attrDict[attr];
            cmds.setAttr("{0}.{1}".format(ctrl, attr), value);
    
        
def maya_useNewAPI():
    pass
    
# apply
def main():
    if settings.operation == 0:
        exportPose();
    else:
        importPose();
    om.MGlobal.displayInfo("Done");

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
        
        # TODO:　以下のレイアウトはv１としての仮。あとでUIをアプデする際に大幅に変更するが、まずはメイン処理を優先する。
        # operation radioButton
        export = QtWidgets.QRadioButton("Export", self);
        imp = QtWidgets.QRadioButton("Import", self);

        # ラジオボタンのレイアウト配置
        layout.addWidget(export, 0, 0);
        layout.addWidget(imp, 0, 1);

        # 各ボタンについての内部情報を作成
        self.__operation = QtWidgets.QButtonGroup(self);
        self.__operation.addButton(export, 0);
        self.__operation.addButton(imp, 1);

        # Input filePass
        filePassLabel = QtWidgets.QLabel("FilePass", self);
        layout.addWidget(filePassLabel, 1,0);
        self.__filePass = QtWidgets.QLineEdit(self);
        layout.addWidget(self.__filePass, 1,1);
        
        # fillePass ref button
        filePassButton = QtWidgets.QPushButton("Input FilePass", self);
        filePassButton.clicked.connect(self.refFileSet);
        layout.addWidget(filePassButton, 2, 0);
        
        # view img selected
        self.__poseImgLabel = QtWidgets.QLabel(self);
        self.__poseImgLabel.setPixmap(QtGui.QPixmap(settings.filePass));
        layout.addWidget(self.__poseImgLabel, 3, 0, 1, 2);
        
        self.initialize();

    # ウィンドウボタンの初期設定
    def initialize(self):
        self.__operation.button(settings.operation).setChecked(True);
        self.__filePass.setText(settings.filePass);

    # ウィンドウで入力された値を設定にセット
    def saveSettings(self):
        settings.operation = self.__operation.checkedId();
        settings.filePass = str(self.__filePass.text());
        
    # set fille pass
    def refFileSet(self):
        operation = self.__operation.checkedId();
        if operation == 0:
            ffSetting = "*.jpeg;;*.png;;*.bmp;;*.tif;;*.gif;;*.iff;;*.psd;;*.json";
        else:
            ffSetting = "*.json";
        # ds2:Mayaスタイルダイアログ, cap:ダイアログタイトル, fm;0=保存モード1=開く, ff:ファイル形式指定
        filename = str(cmds.fileDialog2(
            ds=2, cap="Save Image", fm=0, ff=ffSetting
        )[0]);
        settings.filePass = filename;
        self.__filePass.setText(filename);
        
        if operation == 1 and ".json" in filename:
            json = filename[filename.rfind("/") + 1:];
            fname = json[:json.rfind(".json")];
            files = glob.glob("C:/Users/kn_un/Documents/maya/scripts/nkTools/importExport/{0}.*".format(fname));
            print(json, fname, files);
            if len(files) > 0:
                filename = files[0].replace("\\", "/");
            else:
                print("not found selected json img");
                return;
            self.__poseImgLabel.setPixmap(QtGui.QPixmap(filename));
        else:
            self.__poseImgLabel.setPixmap(QtGui.QPixmap(""));
            
    # Do mainMethod
    def apply(self):
        self.saveSettings();
        main();

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("importExportPoseTool");
        self.resize(1100, 700);

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


class Settings(object):
    def __init__(self):
        self.operation = 0;
        self.filePass = "";

settings = Settings();