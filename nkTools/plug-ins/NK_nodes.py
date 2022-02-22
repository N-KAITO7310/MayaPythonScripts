# -*- coding: utf-8 -*-
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import math, sys

# Maya API 2.0を使用するために必要な関数
def maya_useNewAPI():
    pass

# 実際のクラス
class NK_Sin(om.MPxNode):
    kPluginNodeTypeName = "NK_Sin";
    
    kPluginNodeId = om.MTypeId(0x7f001);
    
    input1Attr = om.MObject()
    kInput1AttrName = "timing";
    kInput1AttrLongName = "timing";
    
    input2Attr = om.MObject()
    kInput2AttrName = "size";
    kInput2AttrLongName = "size";

    input3Attr = om.MObject()
    kInput3AttrName = "speed";
    kInput3AttrLongName = "speed";

    input4Attr = om.MObject()
    kInput4AttrName = "offset";
    kInput4AttrLongName = "offset";
    
    output = om.MObject()
    kOutputAttrName = 'out'
    kOutputAttrLongName = 'output'

    # インスタンスを返すメソッド
    @staticmethod
    def creator():
        return NK_Sin()

    # 初期化時にMayaから呼ばれるメソッド
    # アトリビュートの設定を行う
    @staticmethod
    def initialize():
        # アトリビュートはMFnAttributeクラスのサブクラスのcreateメソッドを使い定義する
        nAttr = om.MFnNumericAttribute()
        NK_Sin.input1Attr = nAttr.create(
            NK_Sin.kInput1AttrLongName, NK_Sin.kInput1AttrName, om.MFnNumericData.kDouble, 0.0)
        nAttr.storable = True
        nAttr.writable = True
        nAttr.keyable = True;
        
        NK_Sin.input2Attr = nAttr.create(
            NK_Sin.kInput2AttrLongName, NK_Sin.kInput2AttrName, om.MFnNumericData.kDouble, 0.0)
        nAttr.storable = True
        nAttr.writable = True
        nAttr.keyable = True;
        
        NK_Sin.input3Attr = nAttr.create(
            NK_Sin.kInput3AttrLongName, NK_Sin.kInput3AttrName, om.MFnNumericData.kDouble, 0.0)
        nAttr.storable = True
        nAttr.writable = True
        nAttr.keyable = True;
        
        NK_Sin.input4Attr = nAttr.create(
            NK_Sin.kInput4AttrLongName, NK_Sin.kInput4AttrName, om.MFnNumericData.kDouble, 0.0)
        nAttr.storable = True
        nAttr.writable = True
        nAttr.keyable = True;

        nAttr = om.MFnNumericAttribute()
        NK_Sin.output = nAttr.create(NK_Sin.kOutputAttrLongName, NK_Sin.kOutputAttrName, om.MFnNumericData.kDouble, 0.0)
        nAttr.storable = False;
        nAttr.writable = False;

        # 定義した後はMPxNodeのaddAttributeを実行する
        NK_Sin.addAttribute(NK_Sin.input1Attr)
        NK_Sin.addAttribute(NK_Sin.input2Attr)
        NK_Sin.addAttribute(NK_Sin.input3Attr)
        NK_Sin.addAttribute(NK_Sin.input4Attr)
        NK_Sin.addAttribute(NK_Sin.output)
        # また、inputが変更された際にoutputを再計算するように設定する
        NK_Sin.attributeAffects( NK_Sin.input1Attr, NK_Sin.output)
        NK_Sin.attributeAffects( NK_Sin.input2Attr, NK_Sin.output)
        NK_Sin.attributeAffects( NK_Sin.input3Attr, NK_Sin.output)
        NK_Sin.attributeAffects( NK_Sin.input4Attr, NK_Sin.output)

    # コンストラクタは親のコンストラクタを呼ぶ
    def __init__(self):
        om.MPxNode.__init__(self)

    # アトリビュートの値が計算される際にMayaから呼び出されるメソッド
    def compute(self, plug, dataBlock):
        if(plug == NK_Sin.output):
            # get the incoming data
            # timing
            dataHandle = dataBlock.inputValue(NK_Sin.input1Attr)
            timing = dataHandle.asDouble()
            # size
            dataHandle = dataBlock.inputValue(NK_Sin.input2Attr)
            size = dataHandle.asDouble()
            # speed
            dataHandle = dataBlock.inputValue(NK_Sin.input3Attr)
            speed = dataHandle.asDouble();
            # offset
            dataHandle = dataBlock.inputValue(NK_Sin.input4Attr)
            offset = dataHandle.asDouble();

            # compute output sin
            result = math.sin(timing * speed - offset) * size;
            
            # set the outgoing plug
            dataHandle = dataBlock.outputValue(NK_Sin.output)
            dataHandle.setDouble(result)
            dataBlock.setClean(plug)

    
class NK_TSHDriver(om.MPxNode):
    kPluginNodeTypeName = "NK_TSHDriver";
    
    kPluginNodeId = om.MTypeId(0x7f004);

    # input1
    input1Attr = om.MObject()
    kInput1AttrName = "p1";
    kInput1AttrLongName = "Position1";
    
    input2Attr = om.MObject()
    kInput2AttrName = "p2";
    kInput2AttrLongName = "Position2";
    
    input3Attr = om.MObject()
    kInput3AttrName = "w";
    kInput3AttrLongName = "Weight";
    
    output = om.MObject()
    kOutputAttrName = 'out'
    kOutputAttrLongName = 'output'

    # インスタンスを返すメソッド
    @staticmethod
    def creator():
        return NK_TSHDriver()

    # 初期化時にMayaから呼ばれるメソッド
    # アトリビュートの設定を行う
    @staticmethod
    def initialize():
        # アトリビュートはMFnAttributeクラスのサブクラスのcreateメソッドを使い定義する
        # pos input 1
        nAttr = om.MFnNumericAttribute()
        NK_TSHDriver.input1Attr = nAttr.create(
            NK_TSHDriver.kInput1AttrLongName, NK_TSHDriver.kInput1AttrName, om.MFnNumericData.k3Float, 0
        );
        nAttr.writable = True;
        nAttr.keyable = True;
        
        # pos input2
        NK_TSHDriver.input2Attr = nAttr.create(
            NK_TSHDriver.kInput2AttrLongName, NK_TSHDriver.kInput2AttrName, om.MFnNumericData.k3Float, 0
        );
        nAttr.writable = True;
        nAttr.keyable = True;
        
        # weight
        NK_TSHDriver.input3Attr = nAttr.create(
            NK_TSHDriver.kInput3AttrLongName, NK_TSHDriver.kInput3AttrName, om.MFnNumericData.kFloat, 1
        );
        nAttr.writable = True;
        nAttr.keyable = True;
        
        
        # output
        nAttr = om.MFnNumericAttribute()
        NK_TSHDriver.output = nAttr.create(NK_TSHDriver.kOutputAttrLongName, NK_TSHDriver.kOutputAttrName, om.MFnNumericData.kDouble, 0.0)
        nAttr.storable = False;
        nAttr.writable = False;

        # 定義した後はMPxNodeのaddAttributeを実行する
        NK_TSHDriver.addAttribute(NK_TSHDriver.input1Attr);
        NK_TSHDriver.addAttribute(NK_TSHDriver.input2Attr);
        NK_TSHDriver.addAttribute(NK_TSHDriver.input3Attr);
        NK_TSHDriver.addAttribute(NK_TSHDriver.output)
        # また、inputが変更された際にoutputを再計算するように設定する
        NK_TSHDriver.attributeAffects( NK_TSHDriver.input1Attr, NK_TSHDriver.output)
        NK_TSHDriver.attributeAffects( NK_TSHDriver.input2Attr, NK_TSHDriver.output)
        NK_TSHDriver.attributeAffects( NK_TSHDriver.input3Attr, NK_TSHDriver.output)

    # コンストラクタは親のコンストラクタを呼ぶ
    def __init__(self):
        om.MPxNode.__init__(self)
    
    @staticmethod
    def clamp(num, min_value, max_value):
            return max(min(num, max_value), min_value);
    
    # アトリビュートの値が計算される際にMayaから呼び出されるメソッド
    def compute(self, plug, dataBlock):
        if plug == NK_TSHDriver.output:
            
            # get the incoming data
            # pos 1
            dataHandle = dataBlock.inputValue(NK_TSHDriver.input1Attr);
            pos1 = dataHandle.asFloat3();
            vec1 = om.MVector(pos1[0], pos1[1], pos1[2]);
            
            # pos 2
            dataHandle = dataBlock.inputValue(NK_TSHDriver.input2Attr);
            pos2 = dataHandle.asFloat3();
            vec2 = om.MVector(pos2[0], pos2[1], pos2[2]);
            
            # weight
            dataHandle = dataBlock.inputValue(NK_TSHDriver.input3Attr);
            weight = dataHandle.asFloat();
            
            # distance
            subtract = vec1 - vec2;
            dist = subtract.length();
            distClamped = NK_TSHDriver.clamp(dist, 0, 1);
            calculatedResult = 1.0 - distClamped;
            result = calculatedResult * weight;
            
            """
            resource expression code
            vector $t = <<front_armor_down_ik_l_driven_loc.translateX, front_armor_down_ik_l_driven_loc.translateY, front_armor_down_ik_l_driven_loc.translateZ>>;
            float $dist = mag($t);
            float $clamp_dist = clamp(0.0, 1.0, $dist);
            float $oneminus_clamp_dist = 1.0 - $clamp_dist;
            float $weight = $oneminus_clamp_dist;
            front_armor_down_A_ik_ctrl_jnt_rotZ_condition.colorIfTrueR = $weight * 80;
            front_armor_down_A_ik_ctrl_jnt_rotZ_condition.firstTerm = $weight;

            front_armor_down_B_ik_ctrl_jnt_rotZ_condition.colorIfTrueR = $weight * 60;
            front_armor_down_B_ik_ctrl_jnt_rotZ_condition.firstTerm = $weight;

            front_armor_down_ikHandle_twistZ_condition.colorIfTrueR = $weight * 120;
            front_armor_down_ikHandle_twistZ_condition.firstTerm = $weight;
            """
            
            # set the outgoing plug
            dataHandle = dataBlock.outputValue(NK_TSHDriver.output);
            dataHandle.setDouble(result);
            dataBlock.setClean(plug);
            

# 新しいノードの登録を行うMayaから呼ばれる関数
def initializePlugin(obj):
    mplugin = om.MFnPlugin(obj)

    try:
        mplugin.registerNode('NK_Sin', NK_Sin.kPluginNodeId, NK_Sin.creator,
                            NK_Sin.initialize, om.MPxNode.kDependNode);
    except:
        sys.stderr.write('Faled to register node: %s' % 'NK_Sin')
        raise
        
    try:
        mplugin.registerNode("NK_TSHDriver", NK_TSHDriver.kPluginNodeId, NK_TSHDriver.creator,
                            NK_TSHDriver.initialize, om.MPxNode.kDependNode);
    except:
        sys.stderr.write('Faled to register node: %s' % 'NK_TSHDriver')
        raise

# プラグインを終了する際にMayaから呼ばれる関数
def uninitializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(NK_Sin.kPluginNodeId);
    except:
        sys.stderr.write('Faled to uninitialize node: %s' % 'NK_Sin')
        raise
    try:
        mplugin.deregisterNode(NK_TSHDriver.kPluginNodeId);
    except:
        sys.stderr.write('Faled to uninitialize node: %s' % 'NK_TSHDriver')
        raise
