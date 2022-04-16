import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui

import maya.cmds as cmds


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass
    
    
class JointCreateContext(omui.MPxContext):
    
    TITLE = "Joint Create Context"
    
    HELP_TEXT = ["Select first joint location",
				 "Select second joint location",
                 "Select final joint location",
                 "Press Enter to complete"]
    
    
    def __init__(self):
        super(JointCreateContext, self).__init__()

        self.setTitleString(JointCreateContext.TITLE)
        self.setImage("C:\Users\kn_un\Documents\maya\2020\plug-ins/context_image.png", omui.MPxContext.kImage1)
        
        self.state = 0;
        self.context_selection = om.MSelectionList();
        
    def helpStateHasChanged(self, event):
        self.update_help_string();
        
    def update_help_string(self):
        self.setHelpString(JointCreateContext.HELP_TEXT[self.state]);
        
    def toolOnSetup(self, event):
        om.MGlobal.selectCommand(om.MSelectionList());
        self.reset_state();
        
    def toolOffCleanup(self):
        self.reset_state();
        
    def doRelease(self, event, draw_manager, frame_context):
        if self.state >= 0 and self.state < 3:
            om.MGlobal.selectFromScreen(event.position[0], event.position[1],
                                        event.position[0], event.position[1],
                                        om.MGlobal.kReplaceList);
                                        
        active_selection = om.MGlobal.getActiveSelectionList();
        if active_selection.length() == 1:
            self.context_selection.merge(active_selection);
            
        om.MGlobal.setActiveSelectionList(self.context_selection);
        
        self.update_state();
        
    def completeAction(self):
        selection_count = self.context_selection.length();
        if selection_count == 3:
            om.MGlobal.setActiveSelectionList(om.MSelectionList());
            
            for i in range(selection_count):
                transform_fn = om.MFnTransform(self.context_selection.getDependNode(i));
                
                cmds.joint(position=transform_fn.translation(om.MSpace.kTransform));
                cmds.delete(transform_fn.name());
                
            cmds.select(clear=True);
            self.reset_state();
        else:
            om.MGlobal.displayError("Three objects must be selected");
        
    def deleteAction(self):
        selection_count = self.context_selection.length();
        if selection_count > 0:
            self.context_selection.remove(selection_count - 1);
            
            om.MGlobal.setActiveSelectionList(self.context_selection);
            
            self.update_state();
        
    def abortAction(self):
        self.reset_state();
        
    def update_state(self):
        self.state = self.context_selection.length();
        
        self.update_help_string();
        
    def reset_state(self):
        om.MGlobal.setActiveSelectionList(om.MSelectionList());
        
        self.context_selection.clear();
        self.update_state();
        

class JointCreateContextCmd(omui.MPxContextCommand):
    
    COMMAND_NAME = "czJointCreateCtx"
    
    
    def __init__(self):
        super(JointCreateContextCmd, self).__init__()
        
    def makeObj(self):
        return JointCreateContext()
    
    @classmethod
    def creator(cls):
        return JointCreateContextCmd()
        
    

def initializePlugin(plugin):
    """
    """
    vendor = "Chris Zurbrigg"
    version = "1.0.0"

    plugin_fn = om.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerContextCommand(JointCreateContextCmd.COMMAND_NAME, JointCreateContextCmd.creator)
    except:
        om.MGlobal.displayError("Failed to register context command: {0}".format(JointCreateContextCmd.COMMAND_NAME))
    

def uninitializePlugin(plugin):
    """
    """
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterContextCommand(JointCreateContextCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister context command: {0}".format(JointCreateContextCmd.COMMAND_NAME))


if __name__ == "__main__":
    """
    For Development Only

    Specialized code that can be executed through the script editor to speed up the development process.

    For example: scene cleanup, reloading the plugin, loading a test scene
    """

    # Any code required before unloading the plug-in (e.g. creating a new scene)
    cmds.file(new=True, force=True)

    # Reload the plugin
    plugin_name = "joint_create_context.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))


    # Any setup code to help speed up testing (e.g. loading a test scene)
    cmds.evalDeferred('cmds.file("C:\Users\kn_un\Documents\maya\projects\scriptTest\scenes/polygons.ma", open=True, force=True)')
    cmds.evalDeferred('context = cmds.czJointCreateCtx(); cmds.setToolTo(context)')
