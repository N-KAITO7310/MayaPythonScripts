# -*- coding: utf-8 -*-

from maya import cmds, OpenMaya;
from PySide2 import QtWidgets;
from ..lib import qt;

"""

SelectHierarchyJoints
create: 2021/08/11

自前リグ用制作当時仕様のためのオプション付きジョイント階層自動選択ツール

基本動作：選択したグループノード以下のジョイントから末端のジョイントを除いた
ジョイントをすべて選択状態にする
オプション：
チェックでvolジョイントを含める or 含めない or volのみかの選択
選択したジョイントをセットにするかの選択

from nkTools.rigging import selectHierarchyJointsTool;
reload(selectHierarchyJointsTool);
reload(selectHierarchyJointsTool.qt);
selectHierarchyJointsTool.option();

"""

# main logic
def selectHierarchyJoints():
    targetList = [];

    # 選択ノードを取得
    selected = cmds.ls(sl=True);
    if not selected or len(selected) > 1:
        OpenMaya.MGlobal.displayError("Select one object");
        return;
    else:
        selected = selected[0];

    # 選択ノード以下のジョイントを全て取得
    descendentsList = cmds.listRelatives(selected, allDescendents=True, type="joint");

    if not descendentsList:
        OpenMaya.MGlobal.displayError("This node do not have joint");
        return;

    print(descendentsList);

    # ジョイントの最下層をリストから除外(ただしvolを除く)
    for descendent in descendentsList:
        children = cmds.listRelatives(descendent, c=True, type="joint");

        # 以下オプション毎の条件分け
        # 子要素がなくvolジョイントでもない場合は末端のジョイントとしてリストから除外
        if not children and not "_vol_jnt" in descendent:
           continue;

        # volジョイントを含まないオプションの場合で、この要素がvolジョイントの場合スキップ
        if settings.selectOption == 1 and "_vol_jnt" in descendent:
            continue;

        # volジョイントのみの場合で、この要素がvolジョイントでない場合スキップ
        if settings.selectOption == 2 and not "_vol_jnt" in descendent:
            continue;

        # fkikジョイントを含める設定がオフである場合(既定)で、この要素がfkikならスキップ
        if not settings.fkik and ("fk" in descendent or "ik" in descendent):
            continue;

        # ターゲットとしてリストに追加
        targetList.append(descendent);

    # ジョイントリストのノードを全て選択状態にする
    cmds.select(targetList, replace=True);

    # 選択ジョイントからsetを作成
    if settings.createSet:
        if settings.selectOption == 2:
             cmds.sets(name=selected + "_vol_set");
        else:
            cmds.sets(name=selected + "_set");
       

# apply
def main():
    selectHierarchyJoints();
    OpenMaya.MGlobal.displayInfo("Done");

# show Window
def option():
    window = MainWindow(qt.getMayaWindow());
    window.show();

# setting option Button
class OptionWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(OptionWidget, self).__init__(*args, **kwargs);

        # 左にラベル、右にコントローラの配置レイアウトを設定
        mainLayout = QtWidgets.QFormLayout(self);

        # ラジオボタン
        exceptEnd = QtWidgets.QRadioButton("Except end", self);
        exceptEndAndVol = QtWidgets.QRadioButton("Except end and vol", self);
        onlyVol = QtWidgets.QRadioButton("Only vol", self);

        # ラジオボタンを横並びに設定(見た目の設定)
        acrossLayout = QtWidgets.QHBoxLayout(self);
        acrossLayout.addWidget(exceptEnd, True);
        acrossLayout.addWidget(exceptEndAndVol, True);
        acrossLayout.addWidget(onlyVol, True);
        mainLayout.addRow("Select Option", acrossLayout);

        # 各ボタンについての内部情報を作成
        self.__selectOption = QtWidgets.QButtonGroup(self);
        self.__selectOption.addButton(exceptEnd, 0);
        self.__selectOption.addButton(exceptEndAndVol, 1);
        self.__selectOption.addButton(onlyVol, 2);

        # セット作成のONOFチェックボックス
        self.__createSet = QtWidgets.QCheckBox("Create", self);
        mainLayout.addRow("Joint Set", self.__createSet);

         # FKIKジョイントを含めるかのONOFチェックボックス
        self.__fkik = QtWidgets.QCheckBox("Include", self);
        mainLayout.addRow("FKIK Joint", self.__fkik);

        self.initialize();

    # ウィンドウボタンの初期設定
    def initialize(self):
        self.__selectOption.button(settings.selectOption).setChecked(True);
        self.__createSet.setChecked(settings.crateSet);
        self.__fkik.setChecked(settings.fkik);

    # ウィンドウで入力された値を設定にセット
    def saveSettings(self):
        settings.selectOption = self.__selectOption.checkedId();
        settings.createSet = self.__createSet.isChecked();
        settings.fkik = self.__fkik.isChecked();

    # ウィンドウ入力値をセットして処理を実行
    def apply(self):
        self.saveSettings();
        main();

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("Select Hierarchy Joints");
        self.resize(400, 200);

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
        self.selectOption = 0;
        self.crateSet = False;
        self.fkik = False;

settings = Settings();