import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui

import maya.cmds as cmds


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass
    
    
class CustomSelectContext(omui.MPxContext):
    
    TITLE = "Custom Select Context"
    
    HELP_TEXT = "Ctrl to select only meshes. Ctrl+Shift to select only lights."
    
    def __init__(self):
        super(CustomSelectContext, self).__init__()
        
        self.setTitleString(CustomSelectContext.TITLE)
        self.setImage("C:\Users\kn_un\Documents\maya\2020\plug-ins\context_image.png", omui.MPxContext.kImage1)
        
    def helpStateHasChanged(self, event):
        self.setHelpString(CustomSelectContext.HELP_TEXT)
        
    def doPress(self, event, draw_manager, frame_context):
        self.viewport_start_pos = event.position;
        
        self.light_only = False;
        self.meshes_only = False;
        
        if event.isModifierControl():
            if event.isModifierShift():
                self.light_only = True;
            else:
                self.meshes_only = True;
            
    def doRelease(self, event, draw_manager, frame_context):
        self.viewport_end_pos = event.position;
        
        initial_selection = om.MGlobal.getActiveSelectionList();
        
        om.MGlobal.selectFromScreen(self.viewport_start_pos[0], self.viewport_start_pos[1],
                                    self.viewport_end_pos[0], self.viewport_end_pos[1],
                                    om.MGlobal.kReplaceList)
                                    
        selection_list = om.MGlobal.getActiveSelectionList();
        
        if self.light_only or self.meshes_only:
            for i in reversed(range(selection_list.length())):
                obj = selection_list.getDependNode(i);
                shape = om.MFnDagNode(obj).child(0);
                
                if self.light_only and not shape.hasFn(om.MFn.kLight):
                    selection_list.remove(i);
                elif self.meshes_only and not shape.hasFn(om.MFn.kMesh):
                    selection_list.remove(i);
        
        om.MGlobal.setActiveSelectionList(initial_selection, om.MGlobal.kReplaceList);
        om.MGlobal.selectCommand(selection_list, om.MGlobal.kReplaceList);
        
    def doDrag(self, event, draw_manager, frame_context):
        self.viewport_end_pos = event.position;
        
        self.draw_selection_rectangle(draw_manager, self.viewport_start_pos[0], self.viewport_start_pos[1],
                                        self.viewport_end_pos[0], self.viewport_start_pos[1],
                                        self.viewport_end_pos[0], self.viewport_end_pos[1],
                                        self.viewport_start_pos[0], self.viewport_end_pos[1])
        
    def draw_selection_rectangle(self, draw_manager, x0, y0,  x1, y1,  x2, y2,  x3, y3):
        draw_manager.beginDrawable();
        draw_manager.setLineWidth(1.0);
        draw_manager.setColor(om.MColor([1.0, 0.0, 0.0]));
        
        draw_manager.line2d(om.MPoint(x0, y0), om.MPoint(x1, y1));
        draw_manager.line2d(om.MPoint(x1, y1), om.MPoint(x2, y2));
        draw_manager.line2d(om.MPoint(x2, y2), om.MPoint(x3, y3));
        draw_manager.line2d(om.MPoint(x3, y3), om.MPoint(x0, y0));
        
        
        draw_manager.endDrawable();
        

class CustomSelectContextCmd(omui.MPxContextCommand):
    
    COMMAND_NAME = "czCustomSelectCtx"
    
    
    def __init__(self):
        super(CustomSelectContextCmd, self).__init__()
        
    def makeObj(self):
        return CustomSelectContext()
    
    @classmethod
    def creator(cls):
        return CustomSelectContextCmd()
        
    

def initializePlugin(plugin):
    """
    """
    vendor = "Chris Zurbrigg"
    version = "1.0.0"

    plugin_fn = om.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerContextCommand(CustomSelectContextCmd.COMMAND_NAME, CustomSelectContextCmd.creator)
    except:
        om.MGlobal.displayError("Failed to register context command: {0}".format(CustomSelectContextCmd.COMMAND_NAME))
    

def uninitializePlugin(plugin):
    """
    """
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterContextCommand(CustomSelectContextCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister context command: {0}".format(CustomSelectContextCmd.COMMAND_NAME))


if __name__ == "__main__":
    """
    For Development Only

    Specialized code that can be executed through the script editor to speed up the development process.

    For example: scene cleanup, reloading the plugin, loading a test scene
    """

    # Any code required before unloading the plug-in (e.g. creating a new scene)
    cmds.file(new=True, force=True)

    # Reload the plugin
    plugin_name = "custom_select_context.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))


    # Any setup code to help speed up testing (e.g. loading a test scene)
    cmds.evalDeferred('cmds.file("C:\Users\kn_un\Documents\maya\projects\scriptTest\scenes/meshes_and_lights.ma", open=True, force=True)')
    cmds.evalDeferred('context = cmds.czCustomSelectCtx(); cmds.setToolTo(context)')
