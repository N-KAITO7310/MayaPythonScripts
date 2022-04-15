# -*- coding: utf-8 -*-
import os;
import maya.cmds as cmds;
from PySide2 import QtWidgets;
from PySide2.QtUiTools import QUiLoader;
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin;

# pathの取得と正規化処理
CURRENT_FILE = os.path.normpath(__file__);

# 拡張子とパスを切り分ける
path, ext = os.path.splitext(CURRENT_FILE);

# 同一パス上の同名uiファイルを取得
UI_FILE = path + ".ui";

class TRSConnectorWindow(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(TRSConnectorWindow, self).__init__(*args, **kwargs);
        
        self.widget = QUiLoader().load(UI_FILE);
        self.setCentralWidget(self.widget);
        self.setWindowTitle(self.widget.windowTitle());
        
        self.widget.pb_t.clicked.connect(self.clicked_connect_translate);
        self.widget.pb_r.clicked.connect(self.clicked_connect_rotate);
        self.widget.pb_s.clicked.connect(self.clicked_connect_scale);
        
    def clicked_connect_translate(self):
        src, dst = cmds.ls(os=True);
        cmds.connectAttr("{}.translate".format(src), "{}.translate".format(dst));
        
    def clicked_connect_rotate(self):
        src, dst = cmds.ls(os=True);
        cmds.connectAttr("{}.rotate".format(src), "{}.rotate".format(dst));
    
    def clicked_connect_scale(self):
        src, dst = cmds.ls(os=True);
        cmds.connectAttr("{}.scale".format(src), "{}.scale".format(dst));
    
    
# for test
import nkTools.test.techArt_test01 as test;
reload(test);
widget = test.TRSConnectorWindow();
widget.show();