import maya.api.OpenMaya as om;
import maya.cmds as cmds;

def maya_useNewAPI():
    pass;
    
class HellowWorldCmd(om.MPxCommand):
    COMMAND_NAME = "HelloWorld";
    
    def __init__(self):
        super(HellowWorldCmd, self).__init__();
        
    def doIt(self, args):
        print("Hello World");
        
    @classmethod
    def creator(cls):
        return HellowWorldCmd();
    
def initializePlugin(plugin):
    vendor = "Kaito Nakamura";
    version = "1.0.0";
    
    plugin_fn = om.MFnPlugin(plugin, vendor, version);
    
    try:
        plugin_fn.registerCommand(HellowWorldCmd.COMMAND_NAME, HellowWorldCmd.creator);
    except:
        om.MGlobal.displayError("Failed to register command: {}".format(HellowWorldCmd));
    
def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin);
    try:
        plugin_fn.deregisterCommand(HellowWorldCmd.COMMAND_NAME);
    except:
        om.MGlobal.displayError("Failed to deregister command: {}".format(HellowWorldCmd));
    
if __name__ == "__main__":
    plugin_name = "hello_world_cmd.py";
    cmds.evalDeferred("if cmds.pluginInfo('{0}', q=True, loaded=True): cmds.unloadPlugin('{0}')".format(plugin_name));
    cmds.evalDeferred("if not cmds.pluginInfo('{0}', q=True, loaded=True): cmds.loadPlugin('{0}')".format(plugin_name));