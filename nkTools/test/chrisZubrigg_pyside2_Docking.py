from PySide2 import QtWidgets
from shiboken2 import getCppPointer

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMayaUI import MQtUtil

import maya.cmds as cmds;


class MyDockableButton(MayaQWidgetDockableMixin, QtWidgets.QPushButton):
    
    UI_NAME = "MyDockableButtonStatic";

    def __init__(self, workspace_control_name=None):
        super(MyDockableButton, self).__init__()

        self.setWindowTitle("Dockable Window")

        self.setText("My Button")
        
        if workspace_control_name:
            workspace_control_ptr = long(MQtUtil.findControl(workspace_control_name));
            widget_ptr = long(getCppPointer(self)[0]);
            
            MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr);


if __name__ == "__main__":
    
    try:
        if button and button.parent(): # pylint: disable=#0601
            workspace_control_name = button.parent().objectName();
            
            if cmds.window(workspace_control_name, exists=True):
                cmds.deleteUI(workspace_control_name);
    except:
        pass;
    
    button = MyDockableButton()
    
    workspace_control_name = "{0}WorkspaceControl".format(button.objectName());
    ui_script = "from my_dockable_button import MyDockableButton\nbutton = MyDockableButton('{0}')".format(workspace_control_name);
    
    button.show(dockable=True, uiScript="pass");
