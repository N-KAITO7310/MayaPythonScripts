import maya.api.OpenMaya as om;
import maya.api.OpenMayaRender as omr;
import maya.api.OpenMayaUI as omui;
import maya.cmds as cmds;

def maya_useNewAPI():
    pass;
    
class HellowWorldNode(omui.MPxLocatorNode):
    TYPE_NAME = "helloworld";
    TYPE_ID = om.MTypeId(0x0007f7f7);
    DRAW_CLASSIFICATION = "drawdb/geometry/helloworld";
    DRAW_REGISTRANT_ID = "HelloWorld";
    
    def __init__(self):
        super(HellowWorldNode, self).__init__();
        
    @classmethod
    def creator(cls):
        return HellowWorldNode();
        
    @classmethod
    def initialize(cls):
        pass;
    
class HellowWorldDrawOverride(omr.MPxDrawOverride):
    NAME = "HelloWorldDrawOverride";
    
    def __init__(self, obj):
        super(HellowWorldDrawOverride, self).__init__(obj, None, False);
        
    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        pass;
        
    def supportedDrawAPIs(self):
        return omr.MRenderer.kAllDevices;
        
    def hasUIDrawables(self):
        return True;
        
    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        draw_manager.beginDrawable();
        draw_manager.text2d(om.MPoint(100, 100), "Hello World");
        draw_manager.endDrawable();
        
    @classmethod
    def creator(cls, obj):
        return HellowWorldDrawOverride(obj);
    
    
def initializePlugin(plugin):
    vendor = "Kaito Nakamura";
    version = "1.0.0";
    
    plugin_fn = om.MFnPlugin(plugin, vendor, version);
    try:
        plugin_fn.registerNode(HellowWorldNode.TYPE_NAME, 
        HellowWorldNode.TYPE_ID, 
        HellowWorldNode.creator, 
        HellowWorldNode.initialize,
        om.MPxNode.kLocatorNode,
        HellowWorldNode.DRAW_CLASSIFICATION);
    except:
        om.MGlobal.displayError("Failled to register node: {}".format(HellowWorldNode.TYPE_NAME));
        
    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(HellowWorldNode.DRAW_CLASSIFICATION,
        HellowWorldNode.DRAW_REGISTRANT_ID,
        HellowWorldDrawOverride.creator);
    except:
        om.MGlobal.displayError("Failled to register node: {}".format(HellowWorldDrawOverride.NAME));
    
def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin);
    
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(HellowWorldNode.DRAW_CLASSIFICATION, HellowWorldNode.DRAW_REGISTRANT_ID);
        pass;
    except:
        pass;
    
    try:
        plugin_fn.deregisterNode(HellowWorldNode.TYPE_ID);
    except:
        om.MGlobal.displayError("Failed to deregister node: {}".format(HellowWorldNode.TYPE_NAME));
    
if __name__ == "__main__":
    
    cmds.file(new=True, force=True);
    
    plugin_name = "hello_world_node.py";
    cmds.evalDeferred("if cmds.pluginInfo('{0}', q=True, loaded=True): cmds.unloadPlugin('{0}')".format(plugin_name));
    cmds.evalDeferred("if not cmds.pluginInfo('{0}', q=True, loaded=True): cmds.loadPlugin('{0}')".format(plugin_name));

    cmds.evalDeferred("cmds.createNode('helloworld')");