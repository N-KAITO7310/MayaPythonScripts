import maya.api.OpenMaya as om;
import maya.cmds as cmds;

from PySide2 import QtCore;
from PySide2 import QtWidgets;
from PySide2 import QtGui;
from shiboken2 import wrapInstance;

import maya.OpenMayaUI as omui;


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow();
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget);

        
class OutputResolutionDialog(QtWidgets.QDialog):
    
    RESOLUTION_ITEMS = [
        ["1920*1000 (1080p)", 1920.0, 1080.0],
        ["1280*720 (720p)", 1280.0, 720.0],
        ["960*540 (540p)", 960.0, 540.0],
        ["640*480", 640.0, 480.0],
        ["320*240", 320.0, 240.0],
    ]
    
    def __init__(self, parent=maya_main_window()):
        super(OutputResolutionDialog, self).__init__(parent);
        
        self.setWindowTitle("Output Resolution");
        self.setMinimumWidth(220);
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint);
        
        self.create_widgets();
        self.create_layout();
        self.create_connections();
        
    def create_widgets(self):
        self.resolution_list_wdg = QtWidgets.QListWidget();
        for resolution_item in self.RESOLUTION_ITEMS:
            list_wdg_item = QtWidgets.QListWidgetItem(resolution_item[0]);
            list_wdg_item.setData(QtCore.Qt.UserRole, [resolution_item[1], resolution_item[2]]);
            self.resolution_list_wdg.addItem(list_wdg_item)
            
        self.close_btn = QtWidgets.QPushButton("Close");
        
    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout();
        button_layout.addStretch();
        button_layout.addWidget(self.close_btn);
        
        main_layout = QtWidgets.QVBoxLayout(self);
        main_layout.setContentsMargins(2, 2, 2, 2);
        main_layout.setSpacing(2);
        main_layout.addWidget(self.resolution_list_wdg);
        main_layout.addStretch();
        main_layout.addLayout(button_layout);
        
        
    def create_connections(self):
        self.resolution_list_wdg.itemClicked.connect(self.set_output_resolution);
        
        self.close_btn.clicked.connect(self.close);
        
    def set_output_resolution(self, item):
        resoluttion = item.data(QtCore.Qt.UserRole);
        
        print("Resolutoin: {}".format(resoluttion));
        
        cmds.setAttr("defaultResolution.width", resoluttion[0]);
        cmds.setAttr("defaultResolution.height", resoluttion[1]);
        cmds.setAttr("defaultResolution.deviceAspectRatio", resoluttion[0]/resoluttion[1]);
        
if __name__ == "__main__":
    try:
        output_resolution_dialog.close();
        output_resolution_dialog.deleteLater();
    except:
        pass;
    
    output_resolution_dialog = OutputResolutionDialog();
    output_resolution_dialog.show();