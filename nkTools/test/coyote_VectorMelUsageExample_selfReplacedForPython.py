import maya.cmds as cmds;
import maya.api.OpenMaya as om;
import math;

selection = cmds.ls(sl=True);
start = str(selection[0]);
end = str(selection[1]);
target = str(selection[2]);

startVec = om.MVector();
endVec = om.MVector();
postVec = om.MVector();

space = 2;
startTrans = cmds.getAttr("{0}.translate".format(start))[0];
startVec = om.MVector(startTrans);
endTrans = cmds.getAttr("{0}.translate".format(end))[0];
endVec = om.MVector(endTrans);

postVec = endVec - startVec;
sepNum = postVec.length() / space;
num = 0;

while(num < sepNum):
    vec = startVec + (postVec / math.floor(sepNum) * num);
    obj = cmds.duplicate(str(target));
    cmds.setAttr("{}.tx".format(obj[0]), vec.x);
    cmds.setAttr("{}.ty".format(obj[0]), vec.y);
    cmds.setAttr("{}.tz".format(obj[0]), vec.z);
    num = num + 1;
    