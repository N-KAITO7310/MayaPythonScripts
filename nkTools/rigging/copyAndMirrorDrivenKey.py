# -*- coding: utf-8 -*-

from maya import OpenMaya, cmds, mel;
from PySide2 import QtCore, QtWidgets, QtGui;
from ..lib import qt;
import pymel.core as pm;

"""
ドリブンキーのコピー、ペースト、反転ツール
create: 2021/09/13~

ドリブンキーについてのセットアップを効率化するためのツール

制作当時他の優先事項で時間が取れなくなったためUIのみで完全に未完

"""

def copyAndMirrorDrivenKey():
    pass;


# apply
def main():
    autoQuaternionDecomposition();
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

        # 接続する回転成分の選択ラジオボタン作成
        roll = QtWidgets.QRadioButton("Roll", self);
        bend = QtWidgets.QRadioButton("Bend", self);

        # ラジオボタンのレイアウト配置
        rotationLayout = QtWidgets.QHBoxLayout(self);
        rotationLayout.addWidget(roll, True);
        rotationLayout.addWidget(bend, True);
        mainLayout.addRow("Rotation Component", rotationLayout);

        # 各ボタンについての内部情報を作成
        self.__rotationComponent = QtWidgets.QButtonGroup(self);
        self.__rotationComponent.addButton(roll, 0);
        self.__rotationComponent.addButton(bend, 1);

        # QuatSlerp作成のONOFチェックボックス
        self.__quatSlerp = QtWidgets.QCheckBox("Create", self);
        mainLayout.addRow("QuatSlerp", self.__quatSlerp);

        self.initialize();

    # ウィンドウボタンの初期設定
    def initialize(self):
        self.__rotationComponent.button(settings.rotationComponent).setChecked(True);
        self.__quatSlerp.setChecked(settings.quatSlerp);

    # ウィンドウで入力された値を設定にセット
    def saveSettings(self):
        settings.rotationComponent = self.__rotationComponent.checkedId();
        settings.quatSlerp = self.__quatSlerp.isChecked();

    # ウィンドウ入力値をセットして処理を実行
    def apply(self):
        self.saveSettings();
        main();

# setting Window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent);
        self.setWindowTitle("Auto Quaternion Decomposition Tool");
        self.resize(400, 120);

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
        self.rotationComponent = 0;
        self.quatSlerp = True;

settings = Settings();