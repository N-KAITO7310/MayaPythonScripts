# -*- coding: utf-8 -*-
import maya.OpenMaya as om
import maya.OpenMayaMPx as ommpx

import maya.cmds as cmds



class BlendDeformerNode(ommpx.MPxDeformerNode):

    TYPE_NAME = "blenddeformernode"
    TYPE_ID = om.MTypeId(0x0007F7FD)

    def __init__(self):
        super(BlendDeformerNode, self).__init__()


    def deform(self, data_block, geo_iter, matrix, multi_index):

        envelope = data_block.inputValue(self.envelope).asFloat()
        if envelope == 0:
            return

        blend_weight = data_block.inputValue(BlendDeformerNode.blend_weight).asFloat();
        if blend_weight == 0:
            return;
            
        target_mesh = data_block.inputValue(BlendDeformerNode.blend_mesh).asMesh();
        if target_mesh.isNull():
            return;
            
        target_points = om.MPointArray();
        target_mesh_fn = om.MFnMesh(target_mesh);
        target_mesh_fn.getPoints(target_points);
        
        global_weight = blend_weight * envelope;

        geo_iter.reset();
        while not geo_iter.isDone():
            
            source_pt = geo_iter.position();
            target_pt = target_points[geo_iter.index()];
            
            source_weight = self.weightValue(data_block, multi_index, geo_iter.index());
            
            final_pt = source_pt + ((target_pt - source_pt) * global_weight * source_weight);
            
            geo_iter.setPosition(final_pt);
            
            geo_iter.next();

    @classmethod
    def creator(cls):
        return BlendDeformerNode()

    @classmethod
    def initialize(cls):
        typed_attr = om.MFnTypedAttribute();
        cls.blend_mesh = typed_attr.create("blendMesh", "bMesh", om.MFnData.kMesh);
        
        numeric_attr = om.MFnNumericAttribute();
        cls.blend_weight = numeric_attr.create("blendWeight", "bWeight", om.MFnNumericData.kFloat, 0.0);
        numeric_attr.setKeyable(True);
        numeric_attr.setMin(0.0);
        numeric_attr.setMax(1.0);
        
        cls.addAttribute(cls.blend_mesh);
        cls.addAttribute(cls.blend_weight);
        
        output_geom = ommpx.cvar.MPxGeometryFilter_outputGeom;
        
        cls.attributeAffects(cls.blend_mesh, output_geom);
        cls.attributeAffects(cls.blend_weight, output_geom);
        
def initializePlugin(plugin):
    vendor = "Chris Zurbrigg"
    version = "1.0.0"

    plugin_fn = ommpx.MFnPlugin(plugin, vendor, version)
    try:
        plugin_fn.registerNode(BlendDeformerNode.TYPE_NAME,
                               BlendDeformerNode.TYPE_ID,
                               BlendDeformerNode.creator,
                               BlendDeformerNode.initialize,
                               ommpx.MPxNode.kDeformerNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(BlendDeformerNode.TYPE_NAME))
        
    cmds.makePaintable(BlendDeformerNode.TYPE_NAME, "weights", attrType="multiFloat", shapeMode="deformer");


def uninitializePlugin(plugin):
    cmds.makePaintable(BlendDeformerNode.TYPE_NAME, "weights", remove=True);
    
    plugin_fn = ommpx.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(BlendDeformerNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(BlendDeformerNode.TYPE_NAME))


if __name__ == "__main__":
    """
    For Development Only

    Specialized code that can be executed through the script editor to speed up the development process.

    For example: scene cleanup, reloading the plugin, loading a test scene
    """

    # Any code required before unloading the plug-in (e.g. creating a new scene)
    cmds.file(new=True, force=True)

    # Reload the plugin
    plugin_name = "blend_deformer_node.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))


    # Any setup code to help speed up testing (e.g. loading a test scene)
    cmds.evalDeferred('cmds.file("C:\Users\kn_un\Documents\maya\projects\scriptTest\scenes/blend_test.ma", open=True, force=True)')
    cmds.evalDeferred('cmds.select("sourceSphere"); cmds.deformer(type="blenddeformernode")')
    cmds.evalDeferred('cmds.connectAttr("deformerTargetShape.outMesh", "blenddeformernode1.blendMesh", force=True);');

