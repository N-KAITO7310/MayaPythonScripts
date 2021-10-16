# -*- coding: utf-8 -*-
from maya import OpenMayaUI, cmds;
from PySide2 import QtWidgets, QtCore;
import shiboken2;

def getMayaWindow():
    print("run qt.py")
    ptr = OpenMayaUI.MQtUtil.mainWindow();
    widget = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget);
    return widget;

# p117 ボタンのクリックイベントで利用するも、引数違い？で動作せず
class Callback(object):
    def __init__(self, func, *args, **kwards):
        # 今後の実装への備えとしての記述
        self.__func = func;
        self.__args = args;
        self.__kwards = kwards;

        # 特殊メソッド、インスタンスを作成し、関数として実行することで処理が行われる
        def __call__(self):
            cmds.undoInfo(openChunk=True);
            try:
                return self.__func(*self.__args, **self.__kwards);

            except:
                raise;

            finally:
                cmds.undoInfo(closeChunk=True);

# 下部実行ボタンとオプション配置のためのスクロールエリアの設定
class ToolWidget(QtWidgets.QWidget):
    # シグナル設定
    applied = QtCore.Signal();
    closed = QtCore.Signal();

    def __init__(self, *args, **kwargs):
        super(ToolWidget, self).__init__(*args, **kwargs);

        # 下部グリッドレイアウトを設定
        mainLayout = QtWidgets.QGridLayout(self);
        self.setLayout(mainLayout);

        # オプション配置部分スクロールエリアの設定
        self.__scrollWidget = QtWidgets.QScrollArea(self);
        self.__scrollWidget.setWidgetResizable(True);
        self.__scrollWidget.setFocusPolicy(QtCore.Qt.NoFocus);
        self.__scrollWidget.setMinimumHeight(1);# px
        # セル指定(縦方向, 横方向, 縦方向結合, 横方向結合)
        mainLayout.addWidget(self.__scrollWidget, 0, 0, 1, 3);

        # 下部ボタン配置(実行＆閉じる)
        self.__actionBtn = QtWidgets.QPushButton(self);
        self.__actionBtn.setText("Apply and Close");
        # slotの設定
        self.__actionBtn.clicked.connect(self.action);
        mainLayout.addWidget(self.__actionBtn, 1, 0);

        # 下部ボタン配置(実行)
        applyBtn = QtWidgets.QPushButton(self);
        applyBtn.setText("Apply");
        # slotの設定
        applyBtn.clicked.connect(self.apply);
        mainLayout.addWidget(applyBtn, 1, 1);

        # 下部ボタン配置(閉じる)
        closeBtn = QtWidgets.QPushButton(self);
        closeBtn.setText("Close");
        # slotの設定
        closeBtn.clicked.connect(self.close);
        mainLayout.addWidget(closeBtn, 1, 2);

    # 中ボタンスロット
    def apply(self):
        # appliedに接続されたスロットを実行
        self.applied.emit();

     # 右ボタンスロット
    def close(self):
        # closedに接続されたスロットを実行
        self.closed.emit();

     # 左ボタンスロット
    def action(self):
        # applied&closedに接続されたスロットを実行
        self.apply();
        self.close();

    # スクロールエリアにsetWidget()でウィジェットを設定する
    def setOptionWidget(self, widget):
        self.__scrollWidget.setWidget(widget);

    # 左実行ボタンの名前を変更するメソッド
    def setActionName(self, name):
        self.__actionBtn.setText(name);