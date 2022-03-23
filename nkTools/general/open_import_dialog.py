import maya.api.OpenMaya as om;
import maya.cmds as cmds;

from PySide2 import QtCore;
from PySide2 import QtWidgets;
from PySide2 import QtGui;
from shiboken2 import wrapInstance;

import maya.OpenMayaUI as omui;


"""
created: 2020/03/20

from nkTools.general import open_import_dialog;

if open_import_dialog.OpenImportDialog.dlg_instance:
	open_import_dialog.OpenImportDialog.show_dialog();
else:
	reload(open_import_dialog)
	open_import_dialog.OpenImportDialog.show_dialog()
"""


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow();
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget);
    
class OpenImportDialog(QtWidgets.QDialog):
    
    FILE_FILTER = "Maya (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)";
    
    selected_filter = "Maya (*.ma *.mb)";
    
    dlg_instance = None;
    
    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = OpenImportDialog();
            
        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show();
        else:
            cls.dlg_instance.raise_();
            cls.dlg_instance.activateWindow();
            
        cls.dlg_instance.show();
    
    def __init__(self, parent=maya_main_window()):
        super(OpenImportDialog, self).__init__(parent);
        
        self.setWindowTitle("Open/Import/Reference");
        self.setMinimumSize(300, 80);
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint);
        
        self.geometry = None;
        
        self.create_widgets();
        self.create_layout();
        self.create_connections();
        
    def create_widgets(self):
        self.filepath_le = QtWidgets.QLineEdit();
        self.select_file_path_btn = QtWidgets.QPushButton();
        self.select_file_path_btn.setIcon(QtGui.QIcon(":fileOpen.png"));
        self.select_file_path_btn.setToolTip("Select File");
        
        self.open_rb = QtWidgets.QRadioButton("Open");
        self.open_rb.setChecked(True);
        self.import_rb = QtWidgets.QRadioButton("Import");
        self.reference_rb = QtWidgets.QRadioButton("Reference");
        
        self.force_cb = QtWidgets.QCheckBox("Force");
        
        self.apply_btn = QtWidgets.QPushButton("Apply");
        self.close_btn = QtWidgets.QPushButton("close");
        
    def create_layout(self):
        file_path_layout = QtWidgets.QHBoxLayout();
        file_path_layout.addWidget(self.filepath_le);
        file_path_layout.addWidget(self.select_file_path_btn);
        
        radio_btn_layout = QtWidgets.QHBoxLayout();
        radio_btn_layout.addWidget(self.open_rb);
        radio_btn_layout.addWidget(self.import_rb);
        radio_btn_layout.addWidget(self.reference_rb);
        
        form_layout = QtWidgets.QFormLayout();
        form_layout.addRow("File:", file_path_layout);
        form_layout.addRow("", radio_btn_layout);
        form_layout.addRow("", self.force_cb);
        
        button_layout = QtWidgets.QHBoxLayout();
        button_layout.addStretch();
        button_layout.addWidget(self.apply_btn);
        button_layout.addWidget(self.close_btn);
        
        main_layout = QtWidgets.QVBoxLayout(self);
        main_layout.addLayout(form_layout);
        main_layout.addLayout(button_layout);
        
        
    def create_connections(self):
        self.select_file_path_btn.clicked.connect(self.show_file_select_dialog);
        
        self.open_rb.toggled.connect(self.update_force_visibility);
        
        self.apply_btn.clicked.connect(self.load_file);
        self.close_btn.clicked.connect(self.close);
        
    def show_file_select_dialog(self):
        file_path, selected_filter  = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", "", self.FILE_FILTER, self.selected_filter);
        if file_path:
            self.filepath_le.setText(file_path);
        
    def update_force_visibility(self, checked):
        self.force_cb.setVisible(checked);
        
    def load_file(self):
        file_path = self.filepath_le.text();
        if not file_path:
            return;
            
        file_info = QtCore.QFileInfo(file_path);
        if not file_info.exists():
            om.MGlobal.displayError("file does not exist: {}".format(file_path));
            return;
        
        if self.open_rb.isChecked():
            self.open_file(file_path);
        elif self.import_rb.isChecked():
            self.import_file(file_path);
        else:
            self.reference_file(file_path);
        
    def open_file(self, file_path):
        force = self.force_cb.isChecked();
        if not force and cmds.file(q=True, modified=True):
            result = QtWidgets.QMessageBox.question(self, "Modified", "Current Scene has unsaved Changed. Continue?");
            if result == QtWidgets.QMessageBox.StandardButton.Yes:
                force = True;
            else:
                return;
        
        cmds.file(file_path, open=True, ignoreVersion=True, force=force);
        
    def import_file(self, file_path):
        cmds.file(file_path, i=True, ignoreVersion=True);
        
    def reference_file(self, file_path):
        cmds.file(file_path, reference=True, ignoreVersion=True);
        
    def showEvent(self, e):
        super(OpenImportDialog, self).showEvent(e);
        
        if self.geometry:
            self.restoreGeometry(self.geometry);
        
    def closeEvent(self, e):
        if isinstance(self, OpenImportDialog):
            super(OpenImportDialog, self).closeEvent(e);
            
            self.geometry = self.saveGeometry();
        