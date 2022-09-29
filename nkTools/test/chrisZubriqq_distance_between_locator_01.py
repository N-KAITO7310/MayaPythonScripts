import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui

import maya.cmds as cmds


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class DistanceBetweenLocator(omui.MPxLocatorNode):

    TYPE_NAME = "distanceBetweenLocator"
    TYPE_ID = om.MTypeId(0x0007F7FD)
    DRAW_CLASSIFICATION = "drawdb/geometry/distancebetweenlocator"
    DRAW_REGISTRANT_ID = "DistanceBetweenLocator"
    
    point1_obj = None;
    point2_obj = None;
    distance_obj = None;


    def __init__(self):
        super(DistanceBetweenLocator, self).__init__()
        
    def compute(self, plug, data):
        point1 =om.MPoint(data.inputValue(self.point1_obj).asFloatVector());
        point2 = om.MPoint(data.inputValue(self.point2_obj).asFloatVector());
        
        distance = point1.distanceTo(point2);
        
        data.outputValue(self.distance_obj).setDouble(distance);
        
        data.setClean(plug);

    @classmethod
    def creator(cls):
        return DistanceBetweenLocator()

    @classmethod
    def initialize(cls):
        numeric_attr = om.MFnNumericAttribute();
        
        cls.point1_obj = numeric_attr.createPoint("point1", "p1");
        numeric_attr.readable = False;
        numeric_attr.keyable = True;
        
        cls.point2_obj = numeric_attr.createPoint("point2", "p2");
        numeric_attr.readable = False;
        numeric_attr.keyable = True;
        
        cls.distance_obj = numeric_attr.create("distance", "dist", om.MFnNumericData.kDouble, 0.0);
        numeric_attr.writable = False;
        
        cls.addAttribute(cls.point1_obj);
        cls.addAttribute(cls.point2_obj);
        cls.addAttribute(cls.distance_obj);
        
        cls.attributeAffects(cls.point1_obj, cls.distance_obj);
        cls.attributeAffects(cls.point2_obj, cls.distance_obj);
        
        
class DistanceBetweenUserData(om.MUserData):
    
    def __init__(self, deleteAfterUse=False):
        super(DistanceBetweenUserData, self).__init__(deleteAfterUse)
        
        self.distance = 0


class DistanceBetweenDrawOverride(omr.MPxDrawOverride):

    NAME = "DistanceBetweenDrawOverride"


    def __init__(self, obj):
        super(DistanceBetweenDrawOverride, self).__init__(obj, None, True)

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        data = old_data
        if not data:
            data = DistanceBetweenUserData()
            
        node_fn = om.MFnDependencyNode(obj_path.node());
        
        data.distance = node_fn.findPlug("distance", False).asDouble();
        
        return data

    def supportedDrawAPIs(self):
        return omr.MRenderer.kAllDevices

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        draw_manager.beginDrawable()

        draw_manager.setFontSize(20)
        draw_manager.setFontWeight(100)
        draw_manager.text2d(om.MPoint(100, 100), "Distance: {0}".format(data.distance))

        draw_manager.endDrawable()

    @classmethod
    def creator(cls, obj):
        return DistanceBetweenDrawOverride(obj)


def initializePlugin(plugin):

    vendor = "Chris Zurbrigg"
    version = "1.0.0"
    api_version = "Any"

    plugin_fn = om.MFnPlugin(plugin, vendor, version, api_version)
    try:
        plugin_fn.registerNode(DistanceBetweenLocator.TYPE_NAME,              # name of the node
                               DistanceBetweenLocator.TYPE_ID,                # unique id that identifies node
                               DistanceBetweenLocator.creator,                # function/method that returns new instance of class
                               DistanceBetweenLocator.initialize,             # function/method that will initialize all attributes of node
                               om.MPxNode.kLocatorNode,                       # type of node to be registered
                               DistanceBetweenLocator.DRAW_CLASSIFICATION)    # draw-specific classification string (VP2.0)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(DistanceBetweenLocator.TYPE_NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(DistanceBetweenLocator.DRAW_CLASSIFICATION,     # draw-specific classification
                                                      DistanceBetweenLocator.DRAW_REGISTRANT_ID,      # unique name to identify registration
                                                      DistanceBetweenDrawOverride.creator)         # function/method that returns new instance of class
    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(DistanceBetweenLocator.TYPE_NAME))


def uninitializePlugin(plugin):

    plugin_fn = om.MFnPlugin(plugin)
    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(DistanceBetweenLocator.DRAW_CLASSIFICATION, DistanceBetweenLocator.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError("Failed to deregister draw override: {0}".format(DistanceBetweenDrawOverride.NAME))

    try:
        plugin_fn.deregisterNode(DistanceBetweenLocator.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to unregister node: {0}".format(DistanceBetweenLocator.TYPE_NAME))


def cz_distance_between_test():
    cmds.setAttr("persp.translate", 3.5, 5.5, 10.0)
    cmds.setAttr("persp.rotate", -27.0, 19.0, 0.0)
    
    cube1 = cmds.polyCube()[0]
    cube2 = cmds.polyCube()[0]

    cmds.setAttr("{0}.translateX".format(cube1), -2.5)
    cmds.setAttr("{0}.translateX".format(cube2), 2.5)
    
    distance_locator = cmds.createNode("{0}".format(DistanceBetweenLocator.TYPE_NAME))
    cmds.select(distance_locator)


if __name__ == "__main__":

    cmds.file(new=True, force=True)

    plugin_name = "chrisZubrig_distance_between_locator_01.py"

    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('cz_distance_between_test()')
