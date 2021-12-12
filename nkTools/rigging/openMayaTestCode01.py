import maya.cmds as cmds;
import maya.OpenMaya as OM;

# Maya Python API test code

# select list
sList = OM.MSelectionList();
sList.add("pSphere*");
if not sList.isEmpty():
    for i in range(sList.length()):
        depNode = OM.MObject();
        sList.getDependNode(i, depNode);
        print(i, OM.MFnDependencyNode(depnode).name());

# select plug
sList = OM.MSelectionList();
sList.add("pSphere1.tx");
plug.getPlug(0, plug);
print plug.name();

"""
MSelectionListから実際のオブジェクトを抜き出す方法２つ
Mstatus getDependNode(unsigned int index, MObject &depNode) const
Mstatus getDagPath(unsigned int index, MDagPath &dagpath, , MObject &component=MObject::kNullObj) const

"""
