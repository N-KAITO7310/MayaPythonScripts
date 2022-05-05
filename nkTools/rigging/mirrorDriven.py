import maya.cmds as cmds;
import maya.api.OpenMaya as om;
import sys;

def main():
    driverList = cmds.ls(sl=True);
    
    for driver in driverList:
        driver = str(driver);
        side = driver.split("_")[0] + "_";
        cmds.select(cl=True)
        
        mirrorSide = "";
        if side == "l_":
            mirrorSide = "r_";
        elif side == "r_":
            mirrorSide = "l_";
        elif side == "L_":
            mirrorSide == "R_";
        elif side == "R_":
            mirrorSide = "L_";
        else:
            sys.stderr.write("Please Select L or R side Ctrl")
        
        mirrorSideDriver = mirrorSide + driver[driver.find(side)+2:];
        drivenList = cmds.listConnections(driver, d=True, et=True, type="animCurveUA");
        
        etcNodeList = [];
        for driven in drivenList:
            existNext = True;
            copyTarget = cmds.listConnections("{}.output".format(driven), d=True);
            while existNext:
                if len(copyTarget) > 0:
                    if cmds.objectType(copyTarget[0]) == "joint":
                        # this is driven
                        drivenJnt = copyTarget[0];
                        existNext = False;
                        
                        mirror_driven_key(driven, mirrorSideDriver, drivenJnt, etcNodeList, side, mirrorSide);
                        
                    else:
                        etcNodeList.append(copyTarget[0]);
                        copyTarget = cmds.listConnections("{}.output".format(copyTarget[0]), d=True);
                else:
                    existNext = False;
                
def mirror_driven_key(driven, mirrorSideDriver,  drivenJnt, etcNodeList, side, mirrorSide):
    mirrorSideDrivenJnt = drivenJnt.replace(side, mirrorSide)
    
    # duplicate copy target nodes
    copyTargetList = [driven] + etcNodeList;
    duplicatedList = cmds.duplicate(copyTargetList, ic=True);
    outputNode = duplicatedList[-1];
    
    # get input source plug
    omList = om.MSelectionList();
    omList.add(driven);
    drivenDepend = omList.getDependNode(0);
    drivenMFnDepend = om.MFnDependencyNode(drivenDepend);
    drivenInputPlug = drivenMFnDepend.findPlug("input", False);
    drivenSourcePlug = drivenInputPlug.source();
    drivenSourcePlugName = drivenSourcePlug.partialName();
    
    # get output destination plug
    omList = om.MSelectionList();
    omList.add(copyTargetList[-1]);
    outputDepend = omList.getDependNode(0);
    outputMFnDepend = om.MFnDependencyNode(outputDepend);
    outputPlug = outputMFnDepend.findPlug("output", False);
    outputDestPlug = outputPlug.destinations()[0];
    outputDestPlugName = outputDestPlug.partialName();
    
    # connect mirrorSide
    cmds.connectAttr("{}.{}".format(mirrorSideDriver, drivenSourcePlugName), "{}.input".format(duplicatedList[0]), force=True);
    cmds.connectAttr("{}.output".format(outputNode), "{}.{}".format(mirrorSideDrivenJnt, outputDestPlugName), force=True);
    
    # scale -1 TODO: add scale -1 option widget
    cmds.bufferCurve(duplicatedList[0], animation="keys", overwrite=False);
    cmds.scaleKey(duplicatedList[0], scaleSpecifiedKeys=1, autoSnap=1, timeScale=1, timePivot=0, floatScale=1, floatPivot=0, valueScale=1, valuePivot=0, hierarchy="none", controlPoints=0, shape=1);


main();