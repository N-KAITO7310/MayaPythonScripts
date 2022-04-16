import maya.api.OpenMaya as om;
import maya.cmds as cmds;

def maya_useNewAPI():
    pass;
    
class NK_MatrixConstraint(om.MPxNode):
    TYPE_NAME = "NK_MatrixConstraint";
    TYPE_ID = om.MTypeId(0x0007f7f7);
    
    input1Attr = om.MObject()
    kInput1AttrName = "m";
    kInput1AttrLongName = "matrix";
    
    input2Attr = om.MObject()
    kInput2AttrName = "dm";
    kInput2AttrLongName = "drivenMatrix";

    input3Attr = om.MObject()
    kInput3AttrName = "o";
    kInput3AttrLongName = "operation";

    input4Attr = om.MObject()
    kInput4AttrName = "b";
    kInput4AttrLongName = "blender";
    
    outTranslate = om.MObject()
    kOutTranslateAttrName = 'ot'
    kOutTranslateAttrLongName = 'outTranslate'
    
    outRotate = om.MObject()
    kOutRotateAttrName = 'or'
    kOutRotateAttrLongName = 'outRotate'
    
    outScale = om.MObject()
    kOutScaleAttrName = 'os'
    kOutScaleAttrLongName = 'outScale'
    
    outShear = om.MObject()
    kOutShearAttrName = 'osh'
    kOutShearAttrLongName = 'outShear'
    
    driver_default_worldMatrix = None;
    driven_default_worldMatrix = None;
    offset_matrix = None;
    
    def __init__(self):
        super(NK_MatrixConstraint, self).__init__();
        
    @classmethod
    def creator(cls):
        return NK_MatrixConstraint();
        
    @classmethod
    def initialize(cls):
        # input Driver Matrix
        mAttr = om.MFnMatrixAttribute();
        NK_MatrixConstraint.input1Attr = mAttr.create(
            NK_MatrixConstraint.kInput1AttrLongName,
            NK_MatrixConstraint.kInput1AttrName,
            om.MFnMatrixAttribute.kDouble
        );
        mAttr.writable = True;
        mAttr.readable = False;
        mAttr.keyable = True;
        
        # input Driven Matrix
        mAttr = om.MFnMatrixAttribute();
        NK_MatrixConstraint.input2Attr = mAttr.create(
            NK_MatrixConstraint.kInput2AttrLongName,
            NK_MatrixConstraint.kInput2AttrName,
            om.MFnMatrixAttribute.kDouble
        );
        mAttr.writable = True;
        mAttr.readable = False;
        mAttr.keyable = True;
        
        # input Operation
        enumAttr = om.MFnEnumAttribute();
        NK_MatrixConstraint.input3Attr = enumAttr.create(
            NK_MatrixConstraint.kInput3AttrLongName,
            NK_MatrixConstraint.kInput3AttrName,
        )
        enumAttr.addField("Parent", 0);
        enumAttr.addField("Translate", 1);
        enumAttr.addField("Rotate", 2);
        enumAttr.addField("Scale", 3);
        enumAttr.writable = True;
        enumAttr.keyable = True;
        
        # input blender
        nAttr = om.MFnNumericAttribute();
        NK_MatrixConstraint.input4Attr = nAttr.create(
            NK_MatrixConstraint.kInput4AttrLongName,
            NK_MatrixConstraint.kInput4AttrName,
            om.MFnNumericData.k3Float,
            0.0
        );
        
        # output translate
        nAttr = om.MFnNumericAttribute()
        NK_MatrixConstraint.outTranslate = nAttr.create(
            NK_MatrixConstraint.kOutTranslateAttrLongName,
            NK_MatrixConstraint.kOutTranslateAttrName,
            om.MFnNumericData.k3Float,
            0.0
        );
        nAttr.storable = False;
        nAttr.writable = False;
        nAttr.keyable = False;
        
        # ouput rotate
        nAttr = om.MFnNumericAttribute()
        NK_MatrixConstraint.outRotate = nAttr.create(
            NK_MatrixConstraint.kOutRotateAttrLongName,
            NK_MatrixConstraint.kOutRotateAttrName,
            om.MFnNumericData.k3Double,
            0.0
        );
        nAttr.storable = False;
        nAttr.writable = False;
        nAttr.keyable = False;
        
        # output scale
        nAttr = om.MFnNumericAttribute()
        NK_MatrixConstraint.outScale = nAttr.create(
            NK_MatrixConstraint.kOutScaleAttrLongName,
            NK_MatrixConstraint.kOutScaleAttrName,
            om.MFnNumericData.k3Float,
            0.0
        );
        nAttr.storable = False;
        nAttr.writable = False;
        nAttr.keyable = False;
        
        # output shear
        nAttr = om.MFnNumericAttribute()
        NK_MatrixConstraint.outShear = nAttr.create(
            NK_MatrixConstraint.kOutShearAttrLongName,
            NK_MatrixConstraint.kOutShearAttrName,
            om.MFnNumericData.k3Float,
            0.0
        );
        nAttr.storable = False;
        nAttr.writable = False;
        nAttr.keyable = False;
        
        NK_MatrixConstraint.addAttribute(NK_MatrixConstraint.input1Attr);
        NK_MatrixConstraint.addAttribute(NK_MatrixConstraint.input2Attr);
        NK_MatrixConstraint.addAttribute(NK_MatrixConstraint.input3Attr);
        NK_MatrixConstraint.addAttribute(NK_MatrixConstraint.input4Attr);
        NK_MatrixConstraint.addAttribute(NK_MatrixConstraint.outTranslate);
        NK_MatrixConstraint.addAttribute(NK_MatrixConstraint.outRotate);
        NK_MatrixConstraint.addAttribute(NK_MatrixConstraint.outScale);
        NK_MatrixConstraint.addAttribute(NK_MatrixConstraint.outShear);
        
        
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input1Attr, NK_MatrixConstraint.outTranslate);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input1Attr, NK_MatrixConstraint.outRotate);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input1Attr, NK_MatrixConstraint.outScale);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input1Attr, NK_MatrixConstraint.outShear);
        
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input2Attr, NK_MatrixConstraint.outTranslate);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input2Attr, NK_MatrixConstraint.outRotate);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input2Attr, NK_MatrixConstraint.outScale);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input2Attr, NK_MatrixConstraint.outShear);
        
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input3Attr, NK_MatrixConstraint.outTranslate);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input3Attr, NK_MatrixConstraint.outRotate);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input3Attr, NK_MatrixConstraint.outScale);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input3Attr, NK_MatrixConstraint.outShear);
        
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input4Attr, NK_MatrixConstraint.outTranslate);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input4Attr, NK_MatrixConstraint.outRotate);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input4Attr, NK_MatrixConstraint.outScale);
        NK_MatrixConstraint.attributeAffects( NK_MatrixConstraint.input4Attr, NK_MatrixConstraint.outShear);
        
    def compute(self, plug, dataBlock):
        if plug == NK_MatrixConstraint.outTranslate or plug == NK_MatrixConstraint.outRotate or plug == NK_MatrixConstraint.outScale or plug == NK_MatrixConstraint.outShear:
            # driver matrix
            dataHandle = dataBlock.inputValue(NK_MatrixConstraint.input1Attr);
            driverMatrix = dataHandle.asMatrix();
            # print(driverMatrix)
            
            # driven matrix
            dataHandle = dataBlock.inputValue(NK_MatrixConstraint.input2Attr);
            drivenMatrix = dataHandle.asMatrix();
            # print(drivenMatrix)
            
            # operation
            dataHandle = dataBlock.inputValue(NK_MatrixConstraint.input3Attr);
            operation = dataHandle.asFloat();
            
            # blender
            dataHandle = dataBlock.inputValue(NK_MatrixConstraint.input4Attr);
            blender = dataHandle.asFloat();
            
            # culc
            """
            1. search common parent
                find plug
                get driverFullpath
                get drivenFullpath
                common parent
            2. confirm same matrix(use offset)
            3. mult matrix
            4. joint orient
            5. get each attr
            """
            
            selfName = self.name();
            # print(selfName)
            selection_list = om.MSelectionList();
            selection_list.add(selfName);
            self_mobject = selection_list.getDependNode(0);
            self_depend_fn = om.MFnDependencyNode(self_mobject);
            
            # get driver
            self_matrix_plug = self_depend_fn.findPlug("matrix", False);
            self_matrix_plug_source = self_matrix_plug.source();
            self_matrix_plug_source_mo = self_matrix_plug_source.node();
            self_matrix_plug_source_dag = om.MFnDagNode(self_matrix_plug_source_mo);
            # print(self_matrix_plug_source_dag.fullPathName());
            driver_fullPath = self_matrix_plug_source_dag.fullPathName();
            
            # get driven
            self_driven_matrix_plug = self_depend_fn.findPlug("drivenMatrix", False);
            self_driven_matrix_plug_source = self_driven_matrix_plug.source();
            self_driven_matrix_plug_source_mo = self_driven_matrix_plug_source.node();
            self_driven_matrix_plug_source_dag = om.MFnDagNode(self_driven_matrix_plug_source_mo);
            # print(self_driven_matrix_plug_source_dag.fullPathName());
            driven_fullPath = self_driven_matrix_plug_source_dag.fullPathName();
            
            # constract hierarchy list
            driver_hierarchy_list = driver_fullPath.split("|")[1:];
            driven_hierarchy_list = driven_fullPath.split("|")[1:];
            # print(driver_hierarchy_list)
            # print(driven_hierarchy_list)
            
            # check common parent and its index
            common_parent = set(driver_hierarchy_list) & set(driven_hierarchy_list);
            if len(common_parent) > 0:
                # exist common parent
                common_parent = list(common_parent)[0];
                # print(common_parent)
                
                driver_common_index = driver_hierarchy_list.index(common_parent);
                driven_common_index = driver_hierarchy_list.index(common_parent);
            
                driver_mult_targets = driver_hierarchy_list[driven_common_index+1:];
                driven_mult_targets = driven_hierarchy_list[driven_common_index+1:];
                # print(driven_common_index, driver_common_index);
                
            else:
                # dont exist common parent
                driver_mult_targets = driver_hierarchy_list;
                driven_mult_targets = driven_hierarchy_list;
            
            # remove driven itself
            driven_mult_targets.remove(self_driven_matrix_plug_source_dag.partialPathName())
            
            # print(driver_mult_targets, driven_mult_targets)
            
            # compare worldMatrix
            if self.driver_default_worldMatrix is None and self.driven_default_worldMatrix is None:
                driver_mdagPath = self_matrix_plug_source_dag.getPath();
                driven_mdgPath = self_driven_matrix_plug_source_dag.getPath();
                self.driver_default_worldMatrix = driver_mdagPath.inclusiveMatrix();
                self.driven_default_worldMatrix = driven_mdgPath.inclusiveMatrix();
                # print(driver_world_matrix, driven_world_matrix)
            
            sameWorldMatrix = False;
            if self.driver_default_worldMatrix == self.driven_default_worldMatrix:
                sameWorldMatrix = True;
            
            # mult matrix
            driver_target_matrix_list = [];
            driven_target_inverseMatrix_list = [];
            
            # Whether it is the same matrix
            if not sameWorldMatrix:
                # add offset matrix
                if self.offset_matrix is None:
                    self.offset_matrix = self.driven_default_worldMatrix * self.driver_default_worldMatrix.inverse();
                    driver_target_matrix_list.append(self.offset_matrix);
                else:
                    driver_target_matrix_list.append(self.offset_matrix)
                
            # driverTargetList reverse
            if len(driver_mult_targets) > 0:
                driver_mult_targets.reverse();
                
            # construct matrix list
            for driver in driver_mult_targets:
                driver_matrix = om.MMatrix(cmds.getAttr("{}.matrix".format(driver)));
                driver_target_matrix_list.append(driver_matrix);
                
            for driven in driven_mult_targets:
                driven_matrix = om.MMatrix(cmds.getAttr("{}.inverseMatrix".format(driven)));
                driven_target_inverseMatrix_list.append(driven_matrix);
                
            # print("driverMatrixes: {}".format(driver_target_matrix_list));
            # print("drivenMatirxes {}".format(driven_target_inverseMatrix_list));
            
            # culc result matrix
            result_matrix = None;
            for i, driver_matrix in enumerate(driver_target_matrix_list):
                if i == 0:
                    result_matrix = om.MMatrix(driver_matrix);
                    # print("driver first matrxix: {}".format(result_matrix));
                else:
                    result_matrix = result_matrix * driver_matrix;
                    # print("driver multed matrix: {}".format(result_matrix))
            for i, driven_matrix in enumerate(driven_target_inverseMatrix_list):
                result_matrix = result_matrix * driven_matrix;
                # print("driven multed matrix: {}".format(result_matrix))
                
            # print("result_matrix: {}".format(result_matrix))
            
            # joint orient
            # drivenObjType = cmds.objectType(self_driven_matrix_plug_source_dag.partialPathName());
            # if drivenObjType == "joint":
            #     jointOrient = cmds.getAttr("{}.jointOrient".format(self_driven_matrix_plug_source_dag.partialPathName()));
            #     jointOrientEuler = om.MEulerRotation(*jointOrient);
            #     print(jointOrientEuler)
            
            # get transform attr
            transformMatrix = om.MTransformationMatrix(result_matrix);
            translation = transformMatrix.translation(om.MSpace.kTransform);
            rotation = transformMatrix.rotation(False);
            scale = transformMatrix.scale(om.MSpace.kTransform);
            shear = transformMatrix.shear(om.MSpace.kTransform);
            
            # print(translation[0], translation[1], translation[2]);
            # print(rotation.x, rotation.y, rotation.z);
            
            # set output
            outDataHandle = dataBlock.outputValue(NK_MatrixConstraint.outTranslate);
            outDataHandle.set3Float(translation[0], translation[1], translation[2])
            
            outDataHandle = dataBlock.outputValue(NK_MatrixConstraint.outRotate);
            outDataHandle.set3Float(rotation.x, rotation.y, rotation.z);
            
            outDataHandle = dataBlock.outputValue(NK_MatrixConstraint.outScale);
            outDataHandle.set3Float(scale[0], scale[1], scale[2]);
            
            outDataHandle = dataBlock.outputValue(NK_MatrixConstraint.outShear);
            outDataHandle.set3Float(shear[0], shear[1], shear[2]);
            
            dataBlock.setClean(plug);
                
            
def initializePlugin(plugin):
    vendor = "Kaito Nakamura";
    version = "1.0.0";
    
    plugin_fn = om.MFnPlugin(plugin, vendor, version);
    try:
        plugin_fn.registerNode(NK_MatrixConstraint.TYPE_NAME, 
        NK_MatrixConstraint.TYPE_ID, 
        NK_MatrixConstraint.creator, 
        NK_MatrixConstraint.initialize,
        om.MPxNode.kDependNode);
    except:
        om.MGlobal.displayError("Failled to register node: {}".format(NK_MatrixConstraint.TYPE_NAME));
        
def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin);
    
    try:
        plugin_fn.deregisterNode(NK_MatrixConstraint.TYPE_ID);
    except:
        om.MGlobal.displayError("Failed to deregister node: {}".format(NK_MatrixConstraint.TYPE_NAME));
    
# For Test
if __name__ == "__main__":
    
    cmds.file(new=True, force=True);
    
    plugin_name = "NK_MatrixConstraint_v1.py";
    cmds.evalDeferred("if cmds.pluginInfo('{0}', q=True, loaded=True): cmds.unloadPlugin('{0}')".format(plugin_name));
    cmds.evalDeferred("if not cmds.pluginInfo('{0}', q=True, loaded=True): cmds.loadPlugin('{0}')".format(plugin_name));

    cmds.evalDeferred('cmds.file("C:\Users\kn_un\Documents\maya\projects\scriptTest\scenes/MatrixConstraintNode_test06.mb", open=True, force=True)')
    cmds.evalDeferred("cmds.createNode('NK_MatrixConstraint')");
    cmds.evalDeferred('cmds.connectAttr("withOffset_driver.matrix", "NK_MatrixConstraint1.matrix");')
    
    cmds.evalDeferred('cmds.connectAttr("withOffset_driven.worldMatrix", "NK_MatrixConstraint1.drivenMatrix");')
    
    cmds.evalDeferred('cmds.connectAttr("NK_MatrixConstraint1.outTranslate", "withOffset_driven.translate");')
    cmds.evalDeferred('cmds.connectAttr("NK_MatrixConstraint1.outRotate", "withOffset_driven.rotate");')
    cmds.evalDeferred('cmds.connectAttr("NK_MatrixConstraint1.outScale", "withOffset_driven.scale");')
    cmds.evalDeferred('cmds.connectAttr("NK_MatrixConstraint1.outShear", "withOffset_driven.shear");')