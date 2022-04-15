# -*- coding: utf-8 -*-
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import math, sys
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

# Maya API 2.0を使用するために必要な関数
def maya_useNewAPI():
    pass

class NK_TFDriver(om.MPxNode):
    kPluginNodeTypeName = "NK_TFDriver";
    
    kPluginNodeId = om.MTypeId(0x7f001);
    
    input1Attr = om.MObject()
    kInput1AttrName = "ti";
    kInput1AttrLongName = "timing";
    
    input2Attr = om.MObject()
    kInput2AttrName = "si";
    kInput2AttrLongName = "size";

    input3Attr = om.MObject()
    kInput3AttrName = "sp";
    kInput3AttrLongName = "speed";

    input4Attr = om.MObject()
    kInput4AttrName = "of";
    kInput4AttrLongName = "offset";
    
    input5Attr = om.MObject()
    kInput5AttrName = "op";
    kInput5AttrLongName = "operation";
    
    output = om.MObject()
    kOutputAttrName = 'out'
    kOutputAttrLongName = 'output'

    # インスタンスを返すメソッド
    @staticmethod
    def creator():
        return NK_TFDriver()

    # 初期化時にMayaから呼ばれるメソッド
    # アトリビュートの設定を行う
    @staticmethod
    def initialize():
        # アトリビュートはMFnAttributeクラスのサブクラスのcreateメソッドを使い定義する
        nAttr = om.MFnNumericAttribute()
        
        # input timing
        NK_TFDriver.input1Attr = nAttr.create(
            NK_TFDriver.kInput1AttrLongName, NK_TFDriver.kInput1AttrName, om.MFnNumericData.kDouble, 0.0)
        nAttr.storable = True
        nAttr.writable = True
        nAttr.keyable = True;
        
        # input size
        NK_TFDriver.input2Attr = nAttr.create(
            NK_TFDriver.kInput2AttrLongName, NK_TFDriver.kInput2AttrName, om.MFnNumericData.kDouble, 0.0)
        nAttr.storable = True
        nAttr.writable = True
        nAttr.keyable = True;
        
        # input speed
        NK_TFDriver.input3Attr = nAttr.create(
            NK_TFDriver.kInput3AttrLongName, NK_TFDriver.kInput3AttrName, om.MFnNumericData.kDouble, 0.0)
        nAttr.storable = True
        nAttr.writable = True
        nAttr.keyable = True;
        
        # offset
        NK_TFDriver.input4Attr = nAttr.create(
            NK_TFDriver.kInput4AttrLongName, NK_TFDriver.kInput4AttrName, om.MFnNumericData.kDouble, 0.0)
        nAttr.storable = True
        nAttr.writable = True
        nAttr.keyable = True;
        
        # input operation
        enumAttr = om.MFnEnumAttribute();
        NK_TFDriver.input5Attr = enumAttr.create(
            NK_TFDriver.kInput5AttrLongName, NK_TFDriver.kInput5AttrName
        );
        enumAttr.addField("Sin", 0);
        enumAttr.addField("Cos", 1);
        enumAttr.addField("Tan", 2);
        enumAttr.writable = True;
        enumAttr.keyable = True;

        nAttr = om.MFnNumericAttribute()
        NK_TFDriver.output = nAttr.create(NK_TFDriver.kOutputAttrLongName, NK_TFDriver.kOutputAttrName, om.MFnNumericData.kDouble, 0.0)
        nAttr.storable = False;
        nAttr.writable = False;

        # 定義した後はMPxNodeのaddAttributeを実行する
        NK_TFDriver.addAttribute(NK_TFDriver.input1Attr)
        NK_TFDriver.addAttribute(NK_TFDriver.input2Attr)
        NK_TFDriver.addAttribute(NK_TFDriver.input3Attr)
        NK_TFDriver.addAttribute(NK_TFDriver.input4Attr)
        NK_TFDriver.addAttribute(NK_TFDriver.input5Attr)
        NK_TFDriver.addAttribute(NK_TFDriver.output)
        # また、inputが変更された際にoutputを再計算するように設定する
        NK_TFDriver.attributeAffects( NK_TFDriver.input1Attr, NK_TFDriver.output)
        NK_TFDriver.attributeAffects( NK_TFDriver.input2Attr, NK_TFDriver.output)
        NK_TFDriver.attributeAffects( NK_TFDriver.input3Attr, NK_TFDriver.output)
        NK_TFDriver.attributeAffects( NK_TFDriver.input4Attr, NK_TFDriver.output)
        NK_TFDriver.attributeAffects( NK_TFDriver.input5Attr, NK_TFDriver.output)

    # コンストラクタは親のコンストラクタを呼ぶ
    def __init__(self):
        om.MPxNode.__init__(self)

    # アトリビュートの値が計算される際にMayaから呼び出されるメソッド
    def compute(self, plug, dataBlock):
        if(plug == NK_TFDriver.output):
            # get the incoming data
            # timing
            dataHandle = dataBlock.inputValue(NK_TFDriver.input1Attr)
            timing = dataHandle.asDouble()
            # size
            dataHandle = dataBlock.inputValue(NK_TFDriver.input2Attr)
            size = dataHandle.asDouble()
            # speed
            dataHandle = dataBlock.inputValue(NK_TFDriver.input3Attr)
            speed = dataHandle.asDouble();
            # offset
            dataHandle = dataBlock.inputValue(NK_TFDriver.input4Attr)
            offset = dataHandle.asDouble();
            # operation
            dataHandle = dataBlock.inputValue(NK_TFDriver.input5Attr);
            operation = dataHandle.asInt();
            
            # fork output option by operation
            result = None;
            print(operation)
            # compute output
            if operation == 0:
                print("sin")
                result = math.sin(timing * speed - offset) * size;
            elif operation == 1:
                print("cos")
                result = math.cos(timing * speed - offset) * size;
            elif operation == 2:
                print("tan")
                result = math.tan(timing * speed - offset) * size;
            else:
                # default sin
                result = math.sin(timing * speed - offset) * size;
            
            # set the outgoing plug
            dataHandle = dataBlock.outputValue(NK_TFDriver.output)
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
            

class NK_TransToRot(om.MPxNode):
    """
    input
    translate:float3
    diameter:float
    operation:enum
    
    output
    outputTranslate
    outputRotate
    """
    kPluginNodeTypeName = "NK_TransToRot";
    
    kPluginNodeId = om.MTypeId(0x7f005);
    
    # diameter point1 trans
    input1Attr = om.MObject()
    kInput1AttrName = "p1";
    kInput1AttrLongName = "point1";
    
    # diameter point2 trans
    input2Attr = om.MObject()
    kInput2AttrName = "p2";
    kInput2AttrLongName = "point2";
    
    # input translate
    input3Attr = om.MObject()
    kInput3AttrName = "t";
    kInput3AttrLongName = "translate";
    
    # input last translate
    input4Attr = om.MObject()
    kInput4AttrName = "lt";
    kInput4AttrLongName = "lastTranslate";
    
    # operation
    input5Attr = om.MObject()
    kInput5AttrName = "o";
    kInput5AttrLongName = "operation";
    
    # output Trans
    output1 = om.MObject()
    kOutput1AttrName = 'outTrans'
    kOutput1AttrLongName = 'outputTranslate'
    
    # output Rot
    output2 = om.MObject()
    kOutput2AttrName = 'outRot'
    kOutput2AttrLongName = 'outputRotate'
    
    # output lastTranslate
    output3 = om.MObject()
    kOutput3AttrName = 'outLastTrans'
    kOutput3AttrLongName = 'outputLastTranslate'
    
    kTempVector = om.MVector();
    kTempRot = om.MEulerRotation();

    # インスタンスを返すメソッド
    @staticmethod
    def creator():
        return NK_TransToRot()

    # 初期化時にMayaから呼ばれるメソッド
    # アトリビュートの設定を行う
    @staticmethod
    def initialize():
        # アトリビュートはMFnAttributeクラスのサブクラスのcreateメソッドを使い定義する
        # input1 point1
        NK_TransToRot.input1Attr = nAttr.create(
            NK_TransToRot.kInput1AttrLongName, NK_TransToRot.kInput1AttrName, om.MFnNumericData.k3Float, 0
        );
        nAttr.writable = True;
        nAttr.keyable = True;
        
        # input2 point2
        NK_TransToRot.input2Attr = nAttr.create(
            NK_TransToRot.kInput2AttrLongName, NK_TransToRot.kInput2AttrName, om.MFnNumericData.k3Float, 0
        );
        nAttr.writable = True;
        nAttr.keyable = True;
        
        # input3 driver translate
        nAttr = om.MFnNumericAttribute()
        NK_TransToRot.input1Attr = nAttr.create(
            NK_TransToRot.kInput3AttrLongName, NK_TransToRot.kInput3AttrName, om.MFnNumericData.k3Float, 0
        );
        nAttr.writable = True;
        nAttr.keyable = True;
        
        # input4 driver last translate
        NK_TransToRot.input4Attr = nAttr.create(
            NK_TransToRot.kInput4AttrLongName, NK_TransToRot.kInput4AttrName, om.MFnNumericData.k3Float, 0
        );
        nAttr.writable = True;
        nAttr.keyable = True;
        
        # input5 operation
        enumAttr = om.MFnEnumAttribute();
        NK_TransToRot.input5Attr = enumAttr.create(
            NK_TransToRot.kInput5AttrLongName, NK_TransToRot.kInput5AttrName
        );
        enumAttr.addField("XZ", 0);
        enumAttr.addField("XY", 1);
        enumAttr.addField("YZ", 2);
        nAttr.writable = True;
        nAttr.keyable = True;
        
        # output1 trans
        nAttr = om.MFnNumericAttribute()
        NK_TransToRot.output1 = nAttr.create(NK_TransToRot.kOutput1AttrLongName, NK_TransToRot.kOutput1AttrName, om.MFnNumericData.k3Float, 0.0)
        nAttr.storable = False;
        nAttr.writable = False;
        
        # output2 rot
        nAttr = om.MFnNumericAttribute()
        NK_TransToRot.output2 = nAttr.create(NK_TransToRot.kOutput2AttrLongName, NK_TransToRot.kOutput2AttrName, om.MFnNumericData.k3Float, 0.0)
        nAttr.storable = False;
        nAttr.writable = False;
        
        # output3 last translate
        nAttr = om.MFnNumericAttribute()
        NK_TransToRot.output3 = nAttr.create(NK_TransToRot.kOutput3AttrLongName, NK_TransToRot.kOutput3AttrName, om.MFnNumericData.k3Float, 0.0)
        nAttr.storable = False;
        nAttr.writable = False;
        
        # 定義した後はMPxNodeのaddAttributeを実行する
        NK_TransToRot.addAttribute(NK_TransToRot.input1Attr);
        NK_TransToRot.addAttribute(NK_TransToRot.input2Attr);
        NK_TransToRot.addAttribute(NK_TransToRot.input3Attr);
        NK_TransToRot.addAttribute(NK_TransToRot.input4Attr);
        NK_TransToRot.addAttribute(NK_TransToRot.input5Attr);
        NK_TransToRot.addAttribute(NK_TransToRot.output1);
        NK_TransToRot.addAttribute(NK_TransToRot.output2);
        NK_TransToRot.addAttribute(NK_TransToRot.output3);
        # また、inputが変更された際にoutputを再計算するように設定する
        NK_TransToRot.attributeAffects( NK_TransToRot.input1Attr, NK_TransToRot.output1);
        NK_TransToRot.attributeAffects( NK_TransToRot.input2Attr, NK_TransToRot.output1);
        NK_TransToRot.attributeAffects( NK_TransToRot.input3Attr, NK_TransToRot.output1);
        NK_TransToRot.attributeAffects( NK_TransToRot.input4Attr, NK_TransToRot.output1);
        NK_TransToRot.attributeAffects( NK_TransToRot.input5Attr, NK_TransToRot.output1);
        NK_TransToRot.attributeAffects( NK_TransToRot.input1Attr, NK_TransToRot.output2);
        NK_TransToRot.attributeAffects( NK_TransToRot.input2Attr, NK_TransToRot.output2);
        NK_TransToRot.attributeAffects( NK_TransToRot.input3Attr, NK_TransToRot.output2);
        NK_TransToRot.attributeAffects( NK_TransToRot.input4Attr, NK_TransToRot.output2);
        NK_TransToRot.attributeAffects( NK_TransToRot.input5Attr, NK_TransToRot.output2);
        NK_TransToRot.attributeAffects( NK_TransToRot.input1Attr, NK_TransToRot.output3);
        NK_TransToRot.attributeAffects( NK_TransToRot.input2Attr, NK_TransToRot.output3);
        NK_TransToRot.attributeAffects( NK_TransToRot.input3Attr, NK_TransToRot.output3);
        NK_TransToRot.attributeAffects( NK_TransToRot.input4Attr, NK_TransToRot.output3);
        NK_TransToRot.attributeAffects( NK_TransToRot.input5Attr, NK_TransToRot.output3);


    # コンストラクタは親のコンストラクタを呼ぶ
    def __init__(self):
        om.MPxNode.__init__(self)
    
    @staticmethod
    def clamp(num, min_value, max_value):
            return max(min(num, max_value), min_value);
    
    # アトリビュートの値が計算される際にMayaから呼び出されるメソッド
    def compute(self, plug, dataBlock):
        if plug == NK_TransToRot.output1 or plug == NK_TransToRot.output2:
            
            # get the incoming data
            # driver trans
            dataHandle = dataBlock.inputValue(NK_TransToRot.input1Attr);
            dTrans = dataHandle.asFloat3();
            dVec = om.MVector(dTrans[0], dTrans[1], dTrans[2]);
            
            # driven rot
            dataHandle = dataBlock.inputValue(NK_TransToRot.input5Attr);
            drivenRot = dataHandle.asFloat3();
            
            # pos 1
            dataHandle = dataBlock.inputValue(NK_TransToRot.input2Attr);
            pos1 = dataHandle.asFloat3();
            vec1 = om.MVector(pos1[0], pos1[1], pos1[2]);
            
            # pos 2
            dataHandle = dataBlock.inputValue(NK_TransToRot.input3Attr);
            pos2 = dataHandle.asFloat3();
            vec2 = om.MVector(pos2[0], pos2[1], pos2[2]);
            
            # operation TODO:
            dataHandle = dataBlock.inputValue(NK_TransToRot.input3Attr);
            operation = dataHandle.asFloat();
            
            # culc diameter
            subtract = vec1 - vec2;
            diameter = abs(subtract.length());# length() = magnitude of this vector
            
            # driven Circumference length
            drivenCircumlen = diameter * math.pi;
            
            # culc rot
            driverDistVec = dVec - NK_TransToRot.kTempVector
            driverDist = driverDistVec.length();
            distRatio = driverDist / drivenCircumlen;
            print(driverDist, distRatio, NK_TransToRot.kTempVector);
            
            rotRatio = 360 * distRatio;
            rot = float(Decimal(str(rotRatio)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            
            newRot = om.MEulerRotation();
            vec = driverDistVec.rotateBy(om.MEulerRotation(0, 90, 0))
            euler = newRot.incrementalRotateBy(vec, rot);
            
            eulerList = [euler.x, euler.y, euler.z];
            
            newEuler = [0, 0, 0];
            for i, new in enumerate(eulerList):
                if drivenRot[i]  != new:
                    newEuler[i] = new;
                else:
                    newEuler[i] = drivenRot[i];
                    
            
            print(rotRatio, rot, newRot, euler.x, euler.y, euler.z);
            
            # set the outgoing plug
            dataHandle1 = dataBlock.outputValue(NK_TransToRot.output1);
            dataHandle1.set3Float(dTrans[0], dTrans[1], dTrans[2]);
            dataHandle2 = dataBlock.outputValue(NK_TransToRot.output2);
            dataHandle2.set3Float(newEuler[0], newEuler[1], newEuler[2]);
            dataBlock.setClean(plug);
            
            """
            // 直径
            float $diameter = 1;
            // targetのY値
            nurbsSphere1.translateY = $diameter * 0.5 + 0;
            // driverの移動XZ
            float $tx = wireController1.translateX;
            float $tz = wireController1.translateZ;
            if( frame <= 1 ){
                float $rx = nurbsSphere1.startRotX;
                float $ry = nurbsSphere1.startRotY;
                float $rz = nurbsSphere1.startRotZ;
                setAttr nurbsSphere1.rx $rx;
                setAttr nurbsSphere1.ry $ry;
                setAttr nurbsSphere1.rz $rz;
               nurbsSphere1.lastX = $tx;
               nurbsSphere1.lastZ = $tz;
            } else {
                // get driver last translate x z
                float $lx = `getAttr "nurbsSphere1.ltx"`;
                float $lz = `getAttr "nurbsSphere1.ltz"`;
                // subtract translate - lastTranslate
                float $x = $tx-$lx;
                float $z = $tz-$lz;
                // squar root = distance(vector norm
                float $d = sqrt($x * $x + $z*$z);
                if( $d > 0.00001 ){
                    $x /= $d;
                    $z /= $d;
                    // 円周
                    float $piD = 3.14 * $diameter;
                    //　距離と円周の比率から回転値を計算
                    float $xrot = 360.0 * $d/$piD;
                    // 底辺、高さからタンジェントの逆関数を利用し、ラジアンを角度に変換
                    float $yrot =  rad_to_deg( atan2( $x, $z ));
                      rotate -ws -r 0 (-$yrot) 0 nurbsSphere1;
                      rotate -ws -r ($xrot) 0 0 nurbsSphere1;
                      rotate -ws -r 0 ($yrot) 0 nurbsSphere1;
                    nurbsSphere1.lastX = $tx;
                    nurbsSphere1.lastZ = $tz;
                }
            }
            """

# 新しいノードの登録を行うMayaから呼ばれる関数
def initializePlugin(obj):
    mplugin = om.MFnPlugin(obj)

    try:
        mplugin.registerNode('NK_TFDriver', NK_TFDriver.kPluginNodeId, NK_TFDriver.creator,
                            NK_TFDriver.initialize, om.MPxNode.kDependNode);
    except:
        sys.stderr.write('Faled to register node: %s' % 'NK_TFDriver')
        raise
        
    try:
        mplugin.registerNode("NK_TSHDriver", NK_TSHDriver.kPluginNodeId, NK_TSHDriver.creator,
                            NK_TSHDriver.initialize, om.MPxNode.kDependNode);
    except:
        sys.stderr.write('Faled to register node: %s' % 'NK_TSHDriver')
        raise
        
    try:
        mplugin.registerNode("NK_TransToRot", NK_TransToRot.kPluginNodeId, NK_TransToRot.creator,
                            NK_TransToRot.initialize, om.MPxNode.kDependNode);
    except:
        sys.stderr.write('Faled to register node: %s' % 'NK_TransToRot')
        raise

# プラグインを終了する際にMayaから呼ばれる関数
def uninitializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(NK_TFDriver.kPluginNodeId);
    except:
        sys.stderr.write('Faled to uninitialize node: %s' % 'NK_TFDriver')
        raise
    try:
        mplugin.deregisterNode(NK_TSHDriver.kPluginNodeId);
    except:
        sys.stderr.write('Faled to uninitialize node: %s' % 'NK_TSHDriver')
        raise
    try:
        mplugin.deregisterNode(NK_TransToRot.kPluginNodeId);
    except:
        sys.stderr.write('Faled to uninitialize node: %s' % 'NK_TransToRot')
        raise
