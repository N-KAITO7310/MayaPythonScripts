import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx;# maya python api 1.0
import maya.cmds as cmds

class BasicDeformerNode(ommpx.MPxDeformerNode):
    
    TYPE_NAME = "basicdeformernode";
    TYPE_ID = om.MTypeId(0x0007F7FC);
    
    def __init__(self):
        super(BasicDeformerNode, self).__init__();
        
    def deform(self, data_block, geo_iter, matrix, multi_index):
        
        envelope = data_block.inputValue(self.envelope).asFloat();
        
        if envelope == 0:
            return;
            
        geo_iter.reset();
        while not geo_iter.isDone():
            
            if geo_iter.index() % 2 == 0:
                pt = geo_iter.position();
                # pt.y += 0.2 * envelope;
                pt = pt * matrix;
                
                geo_iter.setPosition(pt);
            
            geo_iter.next()
        
    @classmethod
    def creator(cls):
        return BasicDeformerNode();
        
    @classmethod
    def initialize(cls):
        pass;
        
    
def initializePlugin(plugin):
    vendor = "Chris Zurbrigg"
    version = "1.0.0"

    # maya python api 1.0
    plugin_fn = ommpx.MFnPlugin(plugin, vendor, version);
    try:
        plugin_fn.registerNode(BasicDeformerNode.TYPE_NAME, BasicDeformerNode.TYPE_ID, BasicDeformerNode.creator,BasicDeformerNode.initialize,ommpx.MPxNode.kDeformerNode);
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(BasicDeformerNode.TYPE_NAME));

def uninitializePlugin(plugin):
    plugin_fn = ommpx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(BasicDeformerNode.TYPE_ID);
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(BasicDeformerNode.TYPE_NAME));


if __name__ == "__main__":
    """
    For Development Only

    Specialized code that can be executed through the script editor to speed up the development process.

    For example: scene cleanup, reloading the plugin, loading a test scene
    """

    # Any code required before unloading the plug-in (e.g. creating a new scene)
    cmds.file(new=True, force=True);
    
    # Reload the plugin
    plugin_name = "basic_deformer_node.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))


    # Any setup code to help speed up testing (e.g. loading a test scene)N
    cmds.evalDeferred('cmds.nurbsPlane(u=10, v=10, p=[0, 0, 0], ax=[0, 1, 0], w=True, d=3);')
    cmds.evalDeferred('cmds.select("nurbsPlane1"); cmds.deformer(type="basicdeformernode")');