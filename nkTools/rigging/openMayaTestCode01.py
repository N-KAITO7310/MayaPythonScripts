import maya.cmds as cmds;
import maya.api.OpenMaya as om;

# Maya Python API test code

# select list
sList = om.MSelectionList();
sList.add("pSphere*");
if not sList.isEmpty():
    for i in range(sList.length()):
        depNode = om.MObject();
        sList.getDependNode(i, depNode);
        print(i, om.MFnDependencyNode(depNode).name());

# select plug
sList = om.MSelectionList();
sList.add("pSphere1.tx");
plug = om.Mplug();
plug.getPlug(0, plug);
print(plug.name());

"""
MSelectionListから実際のオブジェクトを抜き出す方法２つ
Mstatus getDependNode(unsigned int index, MObject &depNode) const
Mstatus getDagPath(unsigned int index, MDagPath &dagpath, , MObject &component=MObject::kNullObj) const

"""

# 選択をリスト取得。APIではMSelectionListというタイプのリストになる
selList = om.MGlobal.getActiveSelectionList();

for i in range(selList.length()):
    # 指定した番号のMDagPathをリストから取り出し、そのfullPathName関数でノード名を得る
    print(selList.getDagPath(i).fullPathName());

    # getDependNode(i)で指定した番号のMObjectを取り出す。MFnDependencyNodeにそのまま設定
    dnFn = om.MFnDependencyNode(selList.getDependNode(i));

    # findPlug関数にアトリビュート名を指定して、プラグを取得
    # ２つ目の引数はとりあえずFalse
    translatePlug = dnFn.findPlug("translate", False);

    # translatePlug(MPlug)には、translateという
    # tx,ty,tzの親となるアトリビュートが記録されています。
    # tx, ty, tzの値を取り出すには、plugの子のプラグを得て、その値を出力します。
    txPlug = translatePlug.child(0);
    tyPlug = translatePlug.child(1);
    tzPlug = translatePlug.child(2);

    # APIでは取得する値の型を正確に指定する必要があります。
    print("translateX:", txPlug.asDouble());
    print("translateY:", tyPlug.asDouble());
    print("translateZ:", tzPlug.asDouble());


# meshの取得
selList = om.MGlobal.getActiveSelectionList();
dagPath = selList.getDagPath(0);
# extendToShape()で、dagPathの中身がメッシュへのパスへ変更される
dagPath.extendToShape();

# プラグを取り出すためにMFnDependencyNodeを作成。
dnFn = om.MFnDependencyNode(dagPath.node());

# findPlug関数に、メッシュのアトリビュート名を指定
plug = dnFn.findPlug("outMesh", False);

# プラグの値をMObjectとして取得
# MFnMeshに渡して、MFnMesh経由でメッシュデータを取る
obj = plug.asMObject();
meshFn = om.MFnMesh(obj);

print("num of polygons:", meshFn.numPolygons);


#----------------------------------------
# 最近接頂点スナップ
def getClosestVertexPoint(inPos, inMesh):
    # 選択リストを作成、ターゲットメッシュを追加
    sl = om.MSelectionList();
    sl.add(inMesh);

    # 選択リストの０番目の要素をMDagPathで取得する
    dagPath = sl.getDagPath(0);

    # 取得したMDagPathをMFnMeshに入れる
    mesh = om.MFnMesh(dagPath);

    # MFnMeshのコマンドが使えるようになったので、最近接頂点取得コマンドを利用
    polyPt, polyId =  mesh.getClosestPoint(om.MPoint(inPos), om.MSpace.kWorld);

    # 指定したポリゴン内の頂点IDを取得する
    polyIds = mesh.getPolygonVertices(polyId);

    # 入力頂点から最も近い頂点IDの位置を取得する
    closestVtxPos = None;
    tempLength = None;
    for i in range(len(polyIds)):
        tempPos = mesh.getPoint(polyIds[i], om.MSpace.kWorld);
        delta = (tempPos - om.MPoint(inPos)).length();
        if tempLength is None or delta < tempLength:
            closestVtxPos = tempPos;
            tempLength = delta;

    print(list(closestVtxPos)[:3]);
    return list(closestVtxPos)[:3];

# スナップ先のポリゴンメッシュ名
target = "";

# 選択頂点でリストを作ってくれる。cmds.ls(sl=True)に近い
sl = om.MGlobal.getActiveSelectionList();

# メッシュのDagPathと頂点といったコンポーネント情報を取得
dagPath, obj = sl.getComponent(0);

# 頂点のインデックス情報を取得できるのがMFnSingleIndexedComponent
fnComp = om.MFnSingleIndexedComponent(obj);
ids = fnComp.getElements();

# 以上で作った関数を利用してスナップまで行う。引数は指定メッシュ頂点のインデックス＆メッシュ
fnMesh = om.MFnMesh(dagPath);
for i in range(len(ids)):
    vtxPoint = fnMesh.getPoint(ids[i], om.MSpace.kWorld);
    closestPoint = getClosestVertexPoint(vtxPoint, target);
    cmds.xform("{0}.vtx[{1}]".format(dagPath.fullPathName(), ids[i]), t=closestPoint, ws=True);
# --------------------------------------------------------

# ray cast
selection_list = om.MSelectionList()
selection_list.add("projection_srfShape") # 仮想のNurbsSurfaceを入れる
dag = selection_list.getDagPath(0)
nurbs_srf = om.MFnNurbsSurface(dag) # MFnNurbsSurfaceの機能を使うための関数セット

ray_source = om.MPoint() #レイを打ちはじめるポイント、始点、MPointを引数なし指定 = 原点(0,0,0)
ray_dir = cmds.getAttr("rayDirection.translate")[0] # レイを打つ方向、rayDirectionは方向を持つロケーター
ray_dir = om.MVector(ray_dir) 
hit_point, hit_u, hit_v = nurbs_srf.intersect(ray_source, ray_dir)
cmds.setAttr("hit_point.translate", *list(hit_point)[:3]) # hit_pointというロケーターにセット