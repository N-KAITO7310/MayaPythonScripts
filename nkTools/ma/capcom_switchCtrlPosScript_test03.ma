//Maya ASCII 2020 scene
//Name: capcom_switchCtrlPosScript_test03.ma
//Last modified: Wed, Jun 07, 2023 11:15:20 PM
//Codeset: 932
requires maya "2020";
requires "mtoa" "4.1.1";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2020";
fileInfo "version" "2020";
fileInfo "cutIdentifier" "202011110415-b1e20b88e2";
fileInfo "osv" "Microsoft Windows 10 Technical Preview  (Build 19044)\n";
fileInfo "UUID" "3A73A59C-45D4-4005-4473-C78CAE5C9B54";
createNode transform -s -n "persp";
	rename -uid "8425DACD-4A0A-DF79-1CBF-23B94A265314";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -22.124850385004216 13.006501033268595 93.176863413214448 ;
	setAttr ".r" -type "double3" -7.5383527296042869 -16.200000000001364 0 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "D274FBB8-4553-55F0-DB93-FBA761782CA3";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 98.74775724069454;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" 13.776394844055176 -6.2172489379008766e-15 0 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
	setAttr ".ai_translator" -type "string" "perspective";
createNode transform -s -n "top";
	rename -uid "DFB9A13C-4DF6-5F2F-A5FD-0FA39F0BB33D";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "A2FCBC1E-40BE-6C99-787A-EA9203478D6D";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -s -n "front";
	rename -uid "755B69AB-4AA3-5BD8-F5D2-2682A2111781";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "BE02EC76-4323-A2A4-0519-B0B8AC2FE70D";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -s -n "side";
	rename -uid "E845D335-45FB-0D1D-8141-55AAAA256F32";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "E76FCFD8-4058-2AC9-D037-8C81447C228D";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -n "test";
	rename -uid "88B0C940-490D-73F9-B0F3-A8B56D759647";
createNode transform -n "geo_grp" -p "test";
	rename -uid "DE05AB33-4ADC-0F26-ACEE-9899D1B8DE4D";
createNode transform -n "pCylinder1" -p "geo_grp";
	rename -uid "9795C673-44D2-0316-23F3-37AC4B2585BF";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" 0 0 -90.000000000000028 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr ".s" -type "double3" 1 13.776395222766416 1 ;
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode mesh -n "pCylinderShape1" -p "pCylinder1";
	rename -uid "F31AF0B2-459A-83AF-0A64-88A0104D5E59";
	setAttr -k off ".v";
	setAttr -s 4 ".iog[0].og";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".db" yes;
	setAttr ".bw" 4;
	setAttr ".vcs" 2;
	setAttr ".ai_translator" -type "string" "polymesh";
createNode mesh -n "pCylinderShape1Orig" -p "pCylinder1";
	rename -uid "EE62D1DB-4B34-D3D1-94F5-E98EC3B4A705";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".db" yes;
	setAttr ".bw" 4;
	setAttr ".ai_translator" -type "string" "polymesh";
createNode transform -n "jnt_grp" -p "test";
	rename -uid "138E7032-4004-AF0E-2B8C-4BAEC1031D65";
createNode joint -n "bind_jnt" -p "jnt_grp";
	rename -uid "8B1694B0-460F-2EA7-3BE5-11BB4F619270";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".uoc" 1;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
createNode parentConstraint -n "bind_jnt_parentConstraint1" -p "bind_jnt";
	rename -uid "A2273FF7-4C4B-2C10-C6F4-66BF65FDD3C5";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "main_ctrlW0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 0 -6.1179483008789396e-15 0 ;
	setAttr -k on ".w0";
createNode joint -n "bot_jnt" -p "jnt_grp";
	rename -uid "8C0625D0-4808-CA97-BBA7-FE80DAC13FD3";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
createNode parentConstraint -n "joint2_parentConstraint1" -p "bot_jnt";
	rename -uid "E0211AC5-4397-6CEB-280E-F29114AFFA56";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "wireController1W0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" -13.776394844055176 6.1179483008789396e-15 0 ;
	setAttr -k on ".w0";
createNode joint -n "bind_jnt_bot" -p "bot_jnt";
	rename -uid "86328BAF-4D96-91ED-AA4D-FABF213112C4";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".uoc" 1;
	setAttr ".t" -type "double3" 13.776394844055176 -6.1179483008789396e-15 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
createNode joint -n "up_jnt_bot" -p "bot_jnt";
	rename -uid "75199220-4BBA-A01D-0E96-9E953571D859";
	setAttr ".t" -type "double3" 27.552789688110352 -1.2235896601757879e-14 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
createNode joint -n "up_jnt" -p "jnt_grp";
	rename -uid "82E2A459-4AC2-FEFF-9B7C-988162CEC344";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
createNode parentConstraint -n "joint3_parentConstraint1" -p "up_jnt";
	rename -uid "60D43A77-4A2B-1D52-B610-5DBD2D7632BF";
	addAttr -dcb 0 -ci true -k true -sn "w0" -ln "wireController2W0" -dv 1 -min 0 -at "double";
	setAttr -k on ".nds";
	setAttr -k off ".v";
	setAttr -k off ".tx";
	setAttr -k off ".ty";
	setAttr -k off ".tz";
	setAttr -k off ".rx";
	setAttr -k off ".ry";
	setAttr -k off ".rz";
	setAttr -k off ".sx";
	setAttr -k off ".sy";
	setAttr -k off ".sz";
	setAttr ".erp" yes;
	setAttr ".rst" -type "double3" 13.776394844055176 -6.1179483008789396e-15 0 ;
	setAttr -k on ".w0";
createNode joint -n "bind_jnt_up" -p "up_jnt";
	rename -uid "D8B3F8A5-4F42-A903-16BE-6EB9CC049097";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".uoc" 1;
	setAttr ".t" -type "double3" -13.776394844055176 6.1179483008789396e-15 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
createNode joint -n "bot_jnt_up" -p "up_jnt";
	rename -uid "1950FE2F-40BF-FFEE-763D-F382C441B7F2";
	setAttr ".t" -type "double3" -27.552789688110352 1.2235896601757879e-14 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
createNode transform -n "ctrl_grp" -p "test";
	rename -uid "6F2A02CF-492B-4A39-F92F-47B577113163";
createNode transform -n "bot_offset_grp" -p "ctrl_grp";
	rename -uid "FBE7C017-45A3-E361-1AFD-989C31C9D30A";
	setAttr ".t" -type "double3" -13.776394844055176 6.1179483008789396e-15 0 ;
createNode transform -n "bot_constraint_grp" -p "bot_offset_grp";
	rename -uid "02858081-49FA-C222-C41B-90A1BB5AAF28";
createNode transform -n "bot_ctrl" -p "bot_constraint_grp";
	rename -uid "77B72DF8-4ACF-C5F6-C3A4-AB8247C7C2E6";
createNode nurbsCurve -n "bot_ctrlShape" -p "bot_ctrl";
	rename -uid "CAFC2047-4AC5-14D9-EEEA-96BD84CB56C6";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		-7.1085698923775775e-17 2.0069329784975585 -2.0069329784975589
		-1.7379157671886973e-16 1.7379157671886978e-16 -2.8382318369650799
		-7.1085698923775775e-17 -2.0069329784975585 -2.0069329784975585
		-1.4217139784755155e-16 -2.8382318369650803 -1.4713443962245383e-16
		7.1085698923775775e-17 -2.0069329784975585 2.0069329784975585
		1.7379157671886988e-16 -2.8430762426442775e-16 2.8382318369650803
		7.1085698923775775e-17 2.0069329784975585 2.0069329784975585
		1.4217139784755155e-16 2.8382318369650803 3.8704867349019777e-16
		-7.1085698923775775e-17 2.0069329784975585 -2.0069329784975589
		-1.7379157671886973e-16 1.7379157671886978e-16 -2.8382318369650799
		-7.1085698923775775e-17 -2.0069329784975585 -2.0069329784975585
		;
createNode transform -n "up_offset_grp" -p "ctrl_grp";
	rename -uid "EC4D7085-4300-77DC-78D3-74AA744FAF78";
	setAttr ".t" -type "double3" 13.776394844055176 -6.1179483008789396e-15 0 ;
createNode transform -n "up_constraint_grp" -p "up_offset_grp";
	rename -uid "305F2CA6-4CAE-E0D1-B1FD-C6BB11F1D109";
	setAttr ".t" -type "double3" 0 6.1179483008789396e-15 0 ;
createNode transform -n "up_ctrl" -p "up_constraint_grp";
	rename -uid "229F1C4D-4484-27B8-EB52-2298F66345FB";
	setAttr ".r" -type "double3" 0 0 0 ;
	setAttr -av ".rx";
	setAttr -av ".ry";
	setAttr -av ".rz";
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999989 1 ;
createNode nurbsCurve -n "curveShape1" -p "up_ctrl";
	rename -uid "4BCB6285-4990-14F6-C4AA-BC8CCD0748EB";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		4.2651419354265505e-16 2.5611322174759024 -2.5611322174759028
		-4.2651419354265505e-16 -2.5611322174759024 -2.5611322174759028
		-4.2651419354265505e-16 -2.5611322174759024 2.5611322174759028
		4.2651419354265505e-16 2.5611322174759024 2.5611322174759028
		4.2651419354265505e-16 2.5611322174759024 -2.5611322174759028
		;
createNode transform -n "main_offset_grp" -p "ctrl_grp";
	rename -uid "85D89240-4532-B6C1-31F6-0B83CBA592CB";
createNode transform -n "main_ctrl" -p "main_offset_grp";
	rename -uid "CED2DD03-46E7-1410-6041-14A212B37A4D";
	addAttr -ci true -sn "change" -ln "change" -min 0 -max 1 -at "double";
	addAttr -ci true -sn "lastSwitchFrame" -ln "lastSwitchFrame" -at "double";
	setAttr -k on ".change" 1;
	setAttr -k on ".lastSwitchFrame" 80;
createNode nurbsCurve -n "curveShape2" -p "main_ctrl";
	rename -uid "C506BB5B-4E40-24CC-F443-4E89C0D31A73";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 3 0 no 3
		4 0 1 2 3
		4
		-1.1981383338287022e-15 -5.6076178976976134 3.2375612122615491
		1.1981383338287022e-15 5.6076178976976134 3.2375612122615491
		0 0 -6.4751224245230983
		-1.1981383338287022e-15 -5.6076178976976134 3.2375612122615491
		;
createNode transform -n "dontTouch_grp" -p "test";
	rename -uid "77C1809C-4E0E-E4F7-CD27-4FA25AA472F5";
createNode transform -n "source_loc" -p "dontTouch_grp";
	rename -uid "E2AD0AEF-4669-A0BA-6D6B-5CB90F480E26";
	setAttr -av ".tx";
	setAttr -av ".ty";
	setAttr -av ".tz";
	setAttr -av ".rx";
	setAttr -av ".ry";
	setAttr -av ".rz";
createNode locator -n "source_locShape" -p "source_loc";
	rename -uid "439D8AC3-4874-4287-A791-09845BF11DD7";
	setAttr -k off ".v";
createNode lightLinker -s -n "lightLinker1";
	rename -uid "27B2007A-47F3-7C13-E435-B9B8158E9311";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "D9F6C0FE-4034-5DEE-A228-A4B89B935047";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "5D2FAC76-417F-7C16-BCFF-C5843D04A26E";
createNode displayLayerManager -n "layerManager";
	rename -uid "E8ED5BA7-40CF-F58E-D62F-76AA7AEC13AE";
createNode displayLayer -n "defaultLayer";
	rename -uid "1E219766-4AC8-6665-1181-F3B5DBB39E8F";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "E1AF5535-4A01-D7D0-68CE-65AA193923C1";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "8F54DA39-4F2E-95E1-23A7-F5A29E8B46EA";
	setAttr ".g" yes;
createNode polyCylinder -n "polyCylinder1";
	rename -uid "4F1A2F4B-451F-4903-410A-92B5204E6C07";
	setAttr ".sh" 2;
	setAttr ".sc" 2;
	setAttr ".cuv" 3;
createNode tweak -n "tweak1";
	rename -uid "91B7273E-46ED-E3E7-6483-FAA6E9993A19";
createNode objectSet -n "tweakSet1";
	rename -uid "CD727FEB-4B62-54E5-1A2C-D49DB38DAF69";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "groupId2";
	rename -uid "1AE9E148-4036-B57B-66DA-ADB0099CBEE0";
	setAttr ".ihi" 0;
createNode groupParts -n "groupParts2";
	rename -uid "638443FF-40FD-6131-C1DF-25A32DD1E31D";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode skinCluster -n "skinCluster1";
	rename -uid "5FD90720-4396-4900-B70D-45A4076D2FB0";
	setAttr -s 102 ".wl";
	setAttr ".wl[0:101].w"
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1
		1 0 1;
	setAttr ".pm[0]" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".gm" -type "matrix" -4.4408920985006262e-16 -1 0 0 13.776395222766416 -6.117948469060515e-15 0 0
		 0 0 1 0 0 0 0 1;
	setAttr ".dpf[0]"  4;
	setAttr ".mi" 5;
	setAttr ".bm" 1;
	setAttr ".ucm" yes;
	setAttr ".wd" 1;
createNode objectSet -n "skinCluster1Set";
	rename -uid "433AB98A-415F-A0A0-8C13-939853FBFA54";
	setAttr ".ihi" 0;
	setAttr ".vo" yes;
createNode groupId -n "skinCluster1GroupId";
	rename -uid "FDD14EA2-4C56-F97E-FA27-54A2A07D6A4B";
	setAttr ".ihi" 0;
createNode groupParts -n "skinCluster1GroupParts";
	rename -uid "781FE24C-48A0-4936-A871-0884AECB4814";
	setAttr ".ihi" 0;
	setAttr ".ic" -type "componentList" 1 "vtx[*]";
createNode dagPose -n "bindPose1";
	rename -uid "282E80C8-4854-7665-17F9-AA800343E216";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".bp" yes;
createNode blendMatrix -n "blendMatrix1";
	rename -uid "41411099-42F5-E61A-BC55-FD87DAC97D94";
createNode decomposeMatrix -n "decomposeMatrix1";
	rename -uid "13D3B44F-4C12-5D9D-1B7F-C78D6DE49C10";
createNode multMatrix -n "multMatrix1";
	rename -uid "618B4C61-4E67-EAB8-61D6-5CBAFADD22C7";
	setAttr -s 2 ".i";
createNode multMatrix -n "multMatrix2";
	rename -uid "1A110707-41D5-E1A3-CE39-918B672FDC46";
	setAttr -s 2 ".i";
createNode reverse -n "reverse1";
	rename -uid "EB6BC7EE-4467-C6D0-AB1E-0D8FA6C5E4BD";
createNode animCurveTL -n "bot_ctrl_translateX";
	rename -uid "E3564D15-4978-73B5-1B37-6B9F6C558373";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 42 ".ktv[0:41]"  0 0 40 -7.1054273576010019e-15 41 -0.0088702361224157755
		 42 -0.034693959296685506 43 -0.07604793700551582 44 -0.13123200477360086 45 -0.19832414586113245
		 46 -0.27523207467094934 47 -0.35974183945777227 48 -0.44956384783660397 49 -0.54237660267333609
		 50 -0.63586832163768392 51 -0.72777650550876416 52 -0.81592542193331496 53 -0.89826138569680225
		 54 -0.97288564593658222 55 -1.0380846366926306 56 -1.0923573106822992 57 -1.1344392574710973
		 58 -1.1633233059149042 59 -1.1782763258622388 60 -1.1788519740288308 61 -1.1648991715458337
		 62 -1.1365661533273652 63 -1.0942999891113097 64 -1.0388415395415542 65 -0.97121587457292335
		 66 -0.89271824236741892 67 -0.80489573140435766 68 -0.70952481368723852 69 -0.60858499000931943
		 70 -0.50422877703899971 71 -0.3987482788934571 72 -0.29453857194678434 73 -0.19405810067450346
		 74 -0.099786234977909061 75 -0.014178077120369892 76 0.060383468500791793 77 0.12163843372800542
		 78 0.16750349334397896 79 0.19612888909982118 80 0.2059589019645216;
createNode animCurveTL -n "bot_ctrl_translateY";
	rename -uid "01CCFA08-482D-DFD9-D8AD-A781D2491AD7";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 42 ".ktv[0:41]"  0 0 40 -6.1179483008789396e-15 41 -0.027538238286138116
		 42 -0.10835876638047716 43 -0.23986312819576028 44 -0.41955282347326939 45 -0.6449991315032183
		 46 -0.91381338394252853 47 -1.2236186341087345 48 -1.5720235081115801 49 -1.9565988762015563
		 50 -2.3748578469283754 51 -2.8242394590602364 52 -3.3020963244987236 53 -3.8056863582490483
		 54 -4.3321686182753831 55 -4.8786031689061025 56 -5.4419547770863739 57 -6.0191001524322107
		 58 -6.6068383513022084 59 -7.2019038837677432 60 -7.8009819922983032 61 -8.400725513988597
		 62 -8.997772695852408 63 -9.588765306415576 64 -10.170366377501418 65 -10.739276918232958
		 66 -11.292250968944417 67 -11.826108405524655 68 -12.337744963933098 69 -12.82413902913264
		 70 -13.282354821135831 71 -13.709541711807562 72 -14.102929518068029 73 -14.45981973889945
		 74 -14.777572834067938 75 -15.053591781119462 76 -15.285302293895457 77 -15.470130241016859
		 78 -15.605476967595839 79 -15.688693399534415 80 -15.717053999354238;
createNode animCurveTL -n "bot_ctrl_translateZ";
	rename -uid "0CF2B3EB-4613-F53D-61BE-619C58A70258";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 42 ".ktv[0:41]"  0 0 40 -5.3290705182007514e-15 41 0.0039403019385364502
		 42 0.015495834734009506 43 0.034270834456940236 44 0.05987212123754837 45 0.091908525939734531
		 46 0.12999034649483932 47 0.17372883642543435 48 0.22273572762428628 49 0.27662278901912707
		 50 0.33500142234904473 51 0.39748229590299466 52 0.46367501672294154 53 0.5331878414554172
		 54 0.60562742574240858 55 0.680598611778926 56 0.75770425342664538 57 0.83654507806418721
		 58 0.91671958417210142 59 0.99782397349703444 60 1.0794521165139539 61 1.1611955498080757
		 62 1.2426435039308039 63 1.3233829602452492 64 1.4029987352687261 65 1.4810735910418735
		 66 1.5571883701064593 67 1.6309221537581511 68 1.7018524423561026 69 1.7695553566178113
		 70 1.8336058590073918 71 1.893577994536253 72 1.9490451505384563 73 1.999580335258818
		 74 2.0447564753989447 75 2.0841467331062358 76 2.1173248432615743 77 2.1438654723238475
		 78 2.1633446004224517 79 2.1753399288518125 80 2.1794313156144653;
createNode animCurveTA -n "bot_ctrl_rotateX";
	rename -uid "EF6D548B-4CFE-EE70-EFD7-5BA5B1EBA61F";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 42 ".ktv[0:41]"  0 0 40 -0.72542736288316134 41 -0.7567586617514408
		 42 -0.84087199711923388 43 -0.97498408743380216 44 -1.1563116511424019 45 -1.3820714066923045
		 46 -1.6494800725307612 47 -1.9557543671050375 48 -2.2981110088623948 49 -2.6737667162500918
		 50 -3.0799382077153981 51 -3.5138422017055566 52 -3.9726954166678454 53 -4.4537145710495265
		 54 -4.9541163832978556 55 -5.4711175718600877 56 -6.0019348551834941 57 -6.5437849517153319
		 58 -7.0938845799028538 59 -7.6494504581933347 60 -8.2076993050340263 61 -8.7658478388722063
		 62 -9.321112778155122 63 -9.8707108413300304 64 -10.411858746844201 65 -10.941773213144893
		 66 -11.457670958679364 67 -11.956768701894887 68 -12.436283161238711 69 -12.893431055158096
		 70 -13.325429102100323 71 -13.729494020512613 72 -14.102842528842279 73 -14.442691345536542
		 74 -14.746257189042687 75 -15.010756777807963 76 -15.233406830279637 77 -15.411424064904958
		 78 -15.542025200131201 79 -15.622426954405618 80 -15.649846046175476;
createNode animCurveTA -n "bot_ctrl_rotateY";
	rename -uid "2EC78DB3-48D0-B864-0B7B-E6AF0DE3671F";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 42 ".ktv[0:41]"  0 0 40 -26.046461578439388 41 -26.037341860143972
		 42 -26.010600991243848 43 -25.967166400718199 44 -25.907965517546259 45 -25.833925770707211
		 46 -25.745974589180243 47 -25.645039401944501 48 -25.532047637979264 49 -25.407926726263657
		 50 -25.273604095776946 51 -25.130007175498207 52 -24.978063394406789 53 -24.81870018148177
		 54 -24.65284496570245 55 -24.48142517604791 56 -24.305368241497387 57 -24.125601591030108
		 58 -23.943052653625212 59 -23.758648858261967 60 -23.573317633919491 61 -23.387986409577024
		 62 -23.203582614213779 63 -23.021033676808887 64 -22.841267026341612 65 -22.665210091791124
		 66 -22.493790302136542 67 -22.327935086357204 68 -22.168571873432207 69 -22.01662809234076
		 70 -21.873031172062092 71 -21.738708541575324 72 -21.614587629859741 73 -21.501595865894473
		 74 -21.400660678658774 75 -21.312709497131799 76 -21.238669750292722 77 -21.179468867120772
		 78 -21.13603427659514 79 -21.109293407695027 80 -21.100173689399611;
createNode animCurveTA -n "bot_ctrl_rotateZ";
	rename -uid "6934B980-488A-9DA1-85AA-E8B4C768520A";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 42 ".ktv[0:41]"  0 0 40 -14.071649533680667 41 -14.004836670977113
		 42 -13.808927768473442 43 -13.490717354580214 44 -13.056999957707951 45 -12.514570106267188
		 46 -11.870222328668437 47 -11.130751153322247 48 -10.302951108639153 49 -9.3936167230296661
		 50 -8.4095425249043405 51 -7.3575230426736971 52 -6.2443528047482815 53 -5.07682633953858
		 54 -3.8617381754551876 55 -2.6058828409086057 56 -1.3160548643093481 57 0.000951225932021657
		 58 1.3383409014049874 59 2.6893196336990313 60 4.0470928944035878 61 5.4048661551081461
		 62 6.755844887402195 63 8.0932345628751587 64 9.4102406531165244 65 10.700068629715796
		 66 11.955923964262364 67 13.171012128345762 68 14.338538593555439 69 15.451708831480872
		 70 16.503728313711523 71 17.487802511836843 72 18.397136897446323 73 19.224936942129411
		 74 19.964408117475617 75 20.608755895074363 76 21.151185746515139 77 21.584903143387407
		 78 21.903113557280648 79 22.099022459784287 80 22.165835322487876;
createNode animCurveTU -n "bot_ctrl_scaleX";
	rename -uid "1835BE46-4901-78F4-058A-48A44772D860";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr ".ktv[0]"  0 1;
createNode animCurveTU -n "bot_ctrl_scaleY";
	rename -uid "583C22A2-4428-171C-23F0-0FA5AA8F8341";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr ".ktv[0]"  0 1;
createNode animCurveTU -n "bot_ctrl_scaleZ";
	rename -uid "70900F49-4290-6119-4A3E-1A8795B1CF05";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr ".ktv[0]"  0 1;
createNode script -n "uiConfigurationScriptNode";
	rename -uid "0716908B-44F7-50DB-6136-E9BE2296CE3C";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $nodeEditorPanelVisible = stringArrayContains(\"nodeEditorPanel1\", `getPanel -vis`);\n\tint    $nodeEditorWorkspaceControlOpen = (`workspaceControl -exists nodeEditorPanel1Window` && `workspaceControl -q -visible nodeEditorPanel1Window`);\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\n\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"top\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n"
		+ "            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n"
		+ "            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"side\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n"
		+ "            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n"
		+ "            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n"
		+ "            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n"
		+ "            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n"
		+ "            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n"
		+ "            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"persp\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n"
		+ "            -wireframeOnShaded 1\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 1\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n"
		+ "            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n"
		+ "            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1264\n            -height 733\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"ToggledOutliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 1\n            -showReferenceMembers 1\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -autoExpandAnimatedShapes 1\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n"
		+ "            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n"
		+ "            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -autoExpandAnimatedShapes 1\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n"
		+ "            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n"
		+ "            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n"
		+ "                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -autoExpandAnimatedShapes 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n"
		+ "                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayValues 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showPlayRangeShades \"on\" \n                -lockPlayRangeShades \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n"
		+ "                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -valueLinesToggle 0\n                -highlightAffectedCurves 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n"
		+ "                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -autoExpandAnimatedShapes 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n"
		+ "                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayValues 0\n                -snapTime \"integer\" \n"
		+ "                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"timeEditorPanel\" (localizedPanelLabel(\"Time Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n"
		+ "            clipEditor -e \n                -displayValues 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayValues 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n"
		+ "                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif ($nodeEditorPanelVisible || $nodeEditorWorkspaceControlOpen) {\n\t\tif (\"\" == $panelName) {\n\t\t\tif ($useSceneConfig) {\n\t\t\t\t$panelName = `scriptedPanel -unParent  -type \"nodeEditorPanel\" -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n"
		+ "                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 0\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                -hasWatchpoint 0\n                $editorName;\n\t\t\t}\n\t\t} else {\n\t\t\t$label = `panel -q -label $panelName`;\n\t\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n"
		+ "                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 0\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                -hasWatchpoint 0\n                $editorName;\n\t\t\tif (!$useSceneConfig) {\n\t\t\t\tpanel -e -l $label $panelName;\n\t\t\t}\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"shapePanel\" (localizedPanelLabel(\"Shape Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tshapePanel -edit -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"posePanel\" (localizedPanelLabel(\"Pose Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tposePanel -edit -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"componentEditorPanel\" (localizedPanelLabel(\"Component Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"profilerPanel\" (localizedPanelLabel(\"Profiler Tool\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"contentBrowserPanel\" (localizedPanelLabel(\"Content Browser\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"single\\\" -ps 1 100 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 1\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 1\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1264\\n    -height 733\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 1\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 1\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1264\\n    -height 733\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 1 -size 12 -divisions 1 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "E26FD38E-4FAA-D964-157F-A19DA7842D84";
	setAttr ".b" -type "string" "playbackOptions -min 0 -max 300 -ast 0 -aet 300 ";
	setAttr ".st" 6;
createNode animCurveTL -n "up_ctrl_translateX";
	rename -uid "BCC16C35-46EA-E2C1-BBA2-54816DC552DC";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 81 ".ktv[0:80]"  0 0 1 -1.2502915772927281e-05 2 -0.00019332251869386141
		 3 -0.00094523076402452944 4 -0.0028834371068455766 5 -0.0067901976416173682 6 -0.013571856371289215
		 7 -0.024218267923316716 8 -0.039764575973855187 9 -0.061255353741239915 10 -0.089711147280388204
		 11 -0.12609749495267941 12 -0.17129652418786456 13 -0.2260812471023872 14 -0.29109268803134292
		 15 -0.36681997760240215 16 -0.45358353931279716 17 -0.55152147595041967 18 -0.66057923545936248
		 19 -0.78050260030285301 20 -0.91083400274013471 21 -1.050912122749132 22 -1.1998746778584852
		 23 -1.3566642672975568 24 -1.5200370890555366 25 -1.6885743100183408 26 -1.8606958385222985
		 27 -2.0346762273849546 28 -2.208662425394758 29 -2.3806930976520615 30 -2.5487192509451528
		 31 -2.7106259299913287 32 -2.8642547939272838 33 -3.0074274395305238 34 -3.1379694075292832
		 35 -3.2537348898574656 36 -3.3526322473028429 37 -3.4326505467672277 38 -3.4918874329886229
		 39 -3.5285787582881802 40 -3.5411305023714483 41 -3.5411305023714483 42 -3.5411305023714483
		 43 -3.5411305023714483 44 -3.5411305023714483 45 -3.5411305023714519 46 -3.5411305023714554
		 47 -3.5411305023714483 48 -3.5411305023714519 49 -3.5411305023714483 50 -3.5411305023714554
		 51 -3.5411305023714412 52 -3.5411305023714483 53 -3.5411305023714412 54 -3.5411305023714519
		 55 -3.5411305023714483 56 -3.5411305023714483 57 -3.5411305023714483 58 -3.5411305023714483
		 59 -3.5411305023714483 60 -3.5411305023714483 61 -3.5411305023714483 62 -3.5411305023714483
		 63 -3.5411305023714448 64 -3.5411305023714483 65 -3.5411305023714519 66 -3.5411305023714448
		 67 -3.5411305023714483 68 -3.5411305023714483 69 -3.5411305023714483 70 -3.5411305023714519
		 71 -3.5411305023714448 72 -3.5411305023714483 73 -3.5411305023714448 74 -3.5411305023714483
		 75 -3.5411305023714519 76 -3.5411305023714483 77 -3.5411305023714483 78 -3.5411305023714483
		 79 -3.5411305023714483 80 -3.5411305023714483;
createNode animCurveTL -n "up_ctrl_translateY";
	rename -uid "A259BC0D-442A-23B6-9997-3BBA9832923B";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 81 ".ktv[0:80]"  0 -6.1179483008789396e-15 1 -0.012476415250080286
		 2 -0.049059528870101662 3 -0.10847825403941704 4 -0.18945557095294843 5 -0.29070316148169295
		 6 -0.41091546691588643 7 -0.54876390763949678 8 -0.70289186982518292 9 -0.87191093830204591
		 10 -1.0543987359931941 11 -1.2488986183027748 12 -1.4539213653790932 13 -1.6679489164126882
		 14 -1.8894400984473809 15 -2.1168382182268908 16 -2.3485803101796905 17 -2.5831077676614611
		 18 -2.8188780289337845 19 -3.0543769448818416 20 -3.288131422821249 21 -3.5187219203378719
		 22 -3.7447943550790677 23 -3.9650710005808083 24 -4.1783599540468828 25 -4.3835627886416217
		 26 -4.5796800391707349 27 -4.7658142146217415 28 -4.9411700823665328 29 -5.1050520252684732
		 30 -5.2568583328849821 31 -5.3960723499459613 32 -5.5222504680962574 33 -5.6350070096442488
		 34 -5.7339961143427525 35 -5.8188908021711327 36 -5.8893594474413584 37 -5.94503996375059
		 38 -5.9855120675049349 39 -6.0102680628321536 40 -6.0186826762911467 41 -6.0186826762911494
		 42 -6.0186826762911458 43 -6.0186826762911476 44 -6.0186826762911521 45 -6.0186826762911521
		 46 -6.0186826762911494 47 -6.0186826762911503 48 -6.0186826762911503 49 -6.0186826762911485
		 50 -6.0186826762911512 51 -6.0186826762911494 52 -6.0186826762911529 53 -6.0186826762911476
		 54 -6.0186826762911476 55 -6.0186826762911494 56 -6.0186826762911494 57 -6.0186826762911494
		 58 -6.0186826762911494 59 -6.0186826762911494 60 -6.0186826762911512 61 -6.0186826762911503
		 62 -6.0186826762911476 63 -6.0186826762911485 64 -6.0186826762911494 65 -6.0186826762911503
		 66 -6.0186826762911529 67 -6.0186826762911521 68 -6.0186826762911556 69 -6.0186826762911494
		 70 -6.0186826762911476 71 -6.0186826762911485 72 -6.0186826762911494 73 -6.0186826762911529
		 74 -6.0186826762911494 75 -6.0186826762911476 76 -6.0186826762911458 77 -6.0186826762911476
		 78 -6.0186826762911476 79 -6.0186826762911494 80 -6.0186826762911494;
createNode animCurveTL -n "up_ctrl_translateZ";
	rename -uid "73663DED-4E1B-BE73-9221-E09CD412871E";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 81 ".ktv[0:80]"  0 0 1 0.023093707448684681 2 0.090809000944214055
		 3 0.20079607524846263 4 0.35070178897877197 5 0.53816664727652286 6 0.76082145889478048
		 7 1.0162840816296941 8 1.3021565940855355 9 1.6160231604508379 10 1.9554487881252824
		 11 2.3179791155714455 12 2.7011413096319679 13 3.1024460977786479 14 3.5193909114365911
		 15 3.9494640717999023 16 4.3901499096100567 17 4.8389346754103322 18 5.293313067027432
		 19 5.7507951766542762 20 6.2089136410699934 21 6.665230765335691 22 7.117345382784916
		 23 7.5628992122491301 24 7.9995824771085298 25 8.4251385597475466 26 8.837367479064147
		 27 9.2341279975152109 28 9.6133381874165753 29 9.9729743134723936 30 10.311067919400923
		 31 10.625701040693089 32 10.914999502682324 33 11.177124302990105 34 11.410261119924868
		 35 11.612608033562104 36 11.782361594188233 37 11.917701423886038 38 12.016773591795367
		 39 12.077673062703441 40 12.098425582995205 41 12.098425582995207 42 12.098425582995207
		 43 12.098425582995203 44 12.098425582995207 45 12.098425582995207 46 12.098425582995223
		 47 12.098425582995207 48 12.098425582995212 49 12.098425582995207 50 12.098425582995219
		 51 12.098425582995199 52 12.098425582995205 53 12.098425582995199 54 12.09842558299521
		 55 12.098425582995212 56 12.098425582995207 57 12.098425582995215 58 12.098425582995205
		 59 12.098425582995207 60 12.098425582995205 61 12.098425582995205 62 12.098425582995207
		 63 12.098425582995201 64 12.098425582995207 65 12.098425582995212 66 12.098425582995198
		 67 12.098425582995207 68 12.09842558299521 69 12.098425582995207 70 12.09842558299521
		 71 12.098425582995201 72 12.098425582995207 73 12.098425582995203 74 12.098425582995207
		 75 12.09842558299521 76 12.098425582995207 77 12.098425582995207 78 12.098425582995205
		 79 12.098425582995207 80 12.098425582995212;
createNode animCurveTA -n "up_ctrl_rotateX";
	rename -uid "4B2DFAF2-448A-CFD5-6905-89B812725FD0";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 81 ".ktv[0:80]"  0 0 1 -0.0008876044471404288 2 -0.0035058831890398255
		 3 -0.0077880343264153506 4 -0.013667255959984173 5 -0.021076746190463413 6 -0.029949703118570335
		 7 -0.040219324845021963 8 -0.051818809470535507 9 -0.064681355095828147 10 -0.078740159821617139
		 11 -0.093928421748619415 12 -0.11017933897755242 13 -0.12742610960913309 14 -0.14560193174407857
		 15 -0.16464000348310651 16 -0.18447352292693259 17 -0.20503568817627571 18 -0.22625969733185278
		 19 -0.24807874849438055 20 -0.27042603976457608 21 -0.29323476924315584 22 -0.31643813503083756
		 23 -0.33996933522834011 24 -0.36376156793637981 25 -0.38774803125567064 26 -0.41186192328693383
		 27 -0.43603644213088416 28 -0.46020478588824071 29 -0.48430015265971937 30 -0.50825574054603584
		 31 -0.53200474764791195 32 -0.5554803720660596 33 -0.57861581190119837 34 -0.60134426525404483
		 35 -0.62359893022532065 36 -0.64531300491573251 37 -0.66641968742600888 38 -0.68685217585686043
		 39 -0.70654366830900606 40 -0.72542736288316179 41 -0.7567586617514408 42 -0.84087199711923422
		 43 -0.97498408743380316 44 -1.1563116511424005 45 -1.3820714066923077 46 -1.6494800725307621
		 47 -1.9557543671050381 48 -2.2981110088623962 49 -2.6737667162500918 50 -3.0799382077154021
		 51 -3.5138422017055575 52 -3.9726954166678454 53 -4.4537145710495265 54 -4.9541163832978592
		 55 -5.4711175718600877 56 -6.001934855183495 57 -6.5437849517153426 58 -7.0938845799028591
		 59 -7.649450458193332 60 -8.207699305034021 61 -8.7658478388722063 62 -9.321112778155122
		 63 -9.8707108413300304 64 -10.411858746844201 65 -10.941773213144893 66 -11.457670958679362
		 67 -11.956768701894886 68 -12.436283161238713 69 -12.893431055158096 70 -13.32542910210033
		 71 -13.729494020512613 72 -14.102842528842279 73 -14.442691345536536 74 -14.746257189042687
		 75 -15.010756777807966 76 -15.233406830279653 77 -15.411424064904958 78 -15.542025200131208
		 79 -15.622426954405618 80 -15.649846046175476;
createNode animCurveTA -n "up_ctrl_rotateY";
	rename -uid "4DBDEAAB-4331-ACFE-3A95-21BCA86EE16F";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 81 ".ktv[0:80]"  0 0 1 -0.048023163535247639 2 -0.18883684644368531
		 3 -0.41755733717935606 4 -0.7293009241963031 5 -1.1191838959485658 6 -1.5823225408901951
		 7 -2.1138331474752237 8 -2.7088320041576956 9 -3.3624353993916598 10 -4.0697596216311513
		 11 -4.825920959330225 12 -5.6260357009429107 13 -6.4652201349232561 14 -7.3385905497253043
		 15 -8.2412632338030871 16 -9.1683544756106663 17 -10.114980563602073 18 -11.076257786231348
		 19 -12.047302431952534 20 -13.02323078921969 21 -13.999159146486841 22 -14.970203792208039
		 23 -15.931481014837319 24 -16.878107102828725 25 -17.805198344636302 26 -18.707871028714088
		 27 -19.58124144351611 28 -20.420425877496495 29 -21.220540619109151 30 -21.976701956808245
		 31 -22.684026179047716 32 -23.337629574281713 33 -23.932628430964179 34 -24.464139037549209
		 35 -24.927277682490818 36 -25.317160654243111 37 -25.62890424126002 38 -25.857624731995724
		 39 -25.99843841490414 40 -26.046461578439381 41 -26.037341860143972 42 -26.010600991243848
		 43 -25.967166400718199 44 -25.907965517546259 45 -25.833925770707211 46 -25.745974589180271
		 47 -25.645039401944501 48 -25.532047637979282 49 -25.407926726263657 50 -25.273604095776967
		 51 -25.130007175498193 52 -24.978063394406789 53 -24.81870018148177 54 -24.65284496570245
		 55 -24.48142517604791 56 -24.305368241497387 57 -24.125601591030133 58 -23.943052653625212
		 59 -23.758648858261971 60 -23.573317633919487 61 -23.387986409577024 62 -23.203582614213779
		 63 -23.021033676808877 64 -22.841267026341612 65 -22.665210091791124 66 -22.493790302136521
		 67 -22.327935086357204 68 -22.168571873432224 69 -22.01662809234076 70 -21.873031172062095
		 71 -21.738708541575321 72 -21.614587629859741 73 -21.50159586589448 74 -21.400660678658774
		 75 -21.312709497131802 76 -21.238669750292726 77 -21.179468867120772 78 -21.13603427659514
		 79 -21.109293407695027 80 -21.100173689399622;
createNode animCurveTA -n "up_ctrl_rotateZ";
	rename -uid "2ECF9522-4CEA-A201-88D4-199759350592";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 81 ".ktv[0:80]"  0 0 1 -0.025944603827723737 2 -0.10201945911918461
		 3 -0.22558613158681795 4 -0.39400618694305867 5 -0.60464119090033985 6 -0.85485270917110079
		 7 -1.1420023074677714 8 -1.4634515515027882 9 -1.8165620069885897 10 -2.1986952396376038
		 11 -2.6072128151622684 12 -3.0394762992750235 13 -3.4928472576882981 14 -3.9646872561145341
		 15 -4.4523578602661482 16 -4.953220635855593 17 -5.4646371485952976 18 -5.9839689641976985
		 19 -6.508577648375228 20 -7.0358247668403342 21 -7.5630718853054359 22 -8.0876805694829681
		 23 -8.6070123850853655 24 -9.1184288978250745 25 -9.6192916734145282 26 -10.106962277566138
		 27 -10.578802275992357 28 -11.032173234405645 29 -11.464436718518394 30 -11.872954294043067
		 31 -12.255087526692067 32 -12.608197982177877 33 -12.929647226212889 34 -13.216796824509579
		 35 -13.467008342780327 36 -13.677643346737614 37 -13.84606340209384 38 -13.969630074561492
		 39 -14.04570492985294 40 -14.071649533680661 41 -14.004836670977113 42 -13.808927768473438
		 43 -13.490717354580211 44 -13.056999957707955 45 -12.514570106267193 46 -11.870222328668442
		 47 -11.130751153322247 48 -10.30295110863916 49 -9.3936167230296661 50 -8.4095425249043441
		 51 -7.3575230426736971 52 -6.2443528047482877 53 -5.0768263395385764 54 -3.8617381754551858
		 55 -2.6058828409086057 56 -1.3160548643093484 57 0.00095122593202252859 58 1.3383409014049883
		 59 2.6893196336990326 60 4.0470928944035869 61 5.4048661551081461 62 6.7558448874021986
		 63 8.093234562875157 64 9.4102406531165244 65 10.700068629715796 66 11.955923964262354
		 67 13.171012128345753 68 14.33853859355543 69 15.451708831480872 70 16.503728313711537
		 71 17.487802511836843 72 18.397136897446323 73 19.224936942129411 74 19.964408117475617
		 75 20.608755895074367 76 21.151185746515143 77 21.584903143387407 78 21.903113557280641
		 79 22.099022459784287 80 22.165835322487869;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "0D1AB160-4EDB-B802-6F62-0E8B72362614";
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -1700.6527742040043 -388.09522267371972 ;
	setAttr ".tgi[0].vh" -type "double2" 3198.2717623130202 2004.7618250998273 ;
	setAttr -s 29 ".tgi[0].ni";
	setAttr ".tgi[0].ni[0].x" 1428.5714111328125;
	setAttr ".tgi[0].ni[0].y" 2178.571533203125;
	setAttr ".tgi[0].ni[0].nvs" 18306;
	setAttr ".tgi[0].ni[1].x" 1121.4285888671875;
	setAttr ".tgi[0].ni[1].y" 1732.857177734375;
	setAttr ".tgi[0].ni[1].nvs" 18306;
	setAttr ".tgi[0].ni[2].x" 200;
	setAttr ".tgi[0].ni[2].y" 1817.142822265625;
	setAttr ".tgi[0].ni[2].nvs" 18306;
	setAttr ".tgi[0].ni[3].x" 814.28570556640625;
	setAttr ".tgi[0].ni[3].y" -598.5714111328125;
	setAttr ".tgi[0].ni[3].nvs" 18304;
	setAttr ".tgi[0].ni[4].x" 814.28570556640625;
	setAttr ".tgi[0].ni[4].y" -192.85714721679688;
	setAttr ".tgi[0].ni[4].nvs" 18304;
	setAttr ".tgi[0].ni[5].x" 814.28570556640625;
	setAttr ".tgi[0].ni[5].y" -91.428573608398438;
	setAttr ".tgi[0].ni[5].nvs" 18304;
	setAttr ".tgi[0].ni[6].x" 814.28570556640625;
	setAttr ".tgi[0].ni[6].y" 2117.142822265625;
	setAttr ".tgi[0].ni[6].nvs" 18306;
	setAttr ".tgi[0].ni[7].x" 1428.5714111328125;
	setAttr ".tgi[0].ni[7].y" 1142.857177734375;
	setAttr ".tgi[0].ni[7].nvs" 18304;
	setAttr ".tgi[0].ni[8].x" 814.28570556640625;
	setAttr ".tgi[0].ni[8].y" -294.28570556640625;
	setAttr ".tgi[0].ni[8].nvs" 18304;
	setAttr ".tgi[0].ni[9].x" 814.28570556640625;
	setAttr ".tgi[0].ni[9].y" 10;
	setAttr ".tgi[0].ni[9].nvs" 18304;
	setAttr ".tgi[0].ni[10].x" 200;
	setAttr ".tgi[0].ni[10].y" 2377.142822265625;
	setAttr ".tgi[0].ni[10].nvs" 18306;
	setAttr ".tgi[0].ni[11].x" 814.28570556640625;
	setAttr ".tgi[0].ni[11].y" -395.71429443359375;
	setAttr ".tgi[0].ni[11].nvs" 18304;
	setAttr ".tgi[0].ni[12].x" 1428.5714111328125;
	setAttr ".tgi[0].ni[12].y" -324.28570556640625;
	setAttr ".tgi[0].ni[12].nvs" 18304;
	setAttr ".tgi[0].ni[13].x" 814.28570556640625;
	setAttr ".tgi[0].ni[13].y" -497.14285278320313;
	setAttr ".tgi[0].ni[13].nvs" 18304;
	setAttr ".tgi[0].ni[14].x" 507.14285278320313;
	setAttr ".tgi[0].ni[14].y" 2327.142822265625;
	setAttr ".tgi[0].ni[14].nvs" 18306;
	setAttr ".tgi[0].ni[15].x" 1121.4285888671875;
	setAttr ".tgi[0].ni[15].y" 2230;
	setAttr ".tgi[0].ni[15].nvs" 18306;
	setAttr ".tgi[0].ni[16].x" 2170;
	setAttr ".tgi[0].ni[16].y" 838.5714111328125;
	setAttr ".tgi[0].ni[16].nvs" 18304;
	setAttr ".tgi[0].ni[17].x" -111.42857360839844;
	setAttr ".tgi[0].ni[17].y" 1737.142822265625;
	setAttr ".tgi[0].ni[17].nvs" 18354;
	setAttr ".tgi[0].ni[18].x" 1121.4285888671875;
	setAttr ".tgi[0].ni[18].y" -170;
	setAttr ".tgi[0].ni[18].nvs" 18306;
	setAttr ".tgi[0].ni[19].x" -111.42857360839844;
	setAttr ".tgi[0].ni[19].y" 1130;
	setAttr ".tgi[0].ni[19].nvs" 18306;
	setAttr ".tgi[0].ni[20].x" 814.28570556640625;
	setAttr ".tgi[0].ni[20].y" -700;
	setAttr ".tgi[0].ni[20].nvs" 18304;
	setAttr ".tgi[0].ni[21].x" 507.14285278320313;
	setAttr ".tgi[0].ni[21].y" 1780;
	setAttr ".tgi[0].ni[21].nvs" 18306;
	setAttr ".tgi[0].ni[22].x" 814.28570556640625;
	setAttr ".tgi[0].ni[22].y" 111.42857360839844;
	setAttr ".tgi[0].ni[22].nvs" 18304;
	setAttr ".tgi[0].ni[23].x" 814.28570556640625;
	setAttr ".tgi[0].ni[23].y" 1894.2857666015625;
	setAttr ".tgi[0].ni[23].nvs" 18304;
	setAttr ".tgi[0].ni[24].x" 814.28570556640625;
	setAttr ".tgi[0].ni[24].y" 1792.857177734375;
	setAttr ".tgi[0].ni[24].nvs" 18304;
	setAttr ".tgi[0].ni[25].x" 814.28570556640625;
	setAttr ".tgi[0].ni[25].y" 1691.4285888671875;
	setAttr ".tgi[0].ni[25].nvs" 18304;
	setAttr ".tgi[0].ni[26].x" 814.28570556640625;
	setAttr ".tgi[0].ni[26].y" 1590;
	setAttr ".tgi[0].ni[26].nvs" 18304;
	setAttr ".tgi[0].ni[27].x" 814.28570556640625;
	setAttr ".tgi[0].ni[27].y" 1488.5714111328125;
	setAttr ".tgi[0].ni[27].nvs" 18304;
	setAttr ".tgi[0].ni[28].x" 814.28570556640625;
	setAttr ".tgi[0].ni[28].y" 1387.142822265625;
	setAttr ".tgi[0].ni[28].nvs" 18304;
select -ne :time1;
	setAttr ".o" 0;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 5 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
	setAttr -s 3 ".u";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	addAttr -ci true -h true -sn "dss" -ln "defaultSurfaceShader" -dt "string";
	setAttr ".ren" -type "string" "arnold";
	setAttr ".dss" -type "string" "lambert1";
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "groupId2.id" "pCylinderShape1.iog.og[1].gid";
connectAttr "tweakSet1.mwc" "pCylinderShape1.iog.og[1].gco";
connectAttr "skinCluster1GroupId.id" "pCylinderShape1.iog.og[4].gid";
connectAttr "skinCluster1Set.mwc" "pCylinderShape1.iog.og[4].gco";
connectAttr "skinCluster1.og[0]" "pCylinderShape1.i";
connectAttr "tweak1.vl[0].vt[0]" "pCylinderShape1.twl";
connectAttr "polyCylinder1.out" "pCylinderShape1Orig.i";
connectAttr "bind_jnt_parentConstraint1.ctx" "bind_jnt.tx";
connectAttr "bind_jnt_parentConstraint1.cty" "bind_jnt.ty";
connectAttr "bind_jnt_parentConstraint1.ctz" "bind_jnt.tz";
connectAttr "bind_jnt_parentConstraint1.crx" "bind_jnt.rx";
connectAttr "bind_jnt_parentConstraint1.cry" "bind_jnt.ry";
connectAttr "bind_jnt_parentConstraint1.crz" "bind_jnt.rz";
connectAttr "bind_jnt.ro" "bind_jnt_parentConstraint1.cro";
connectAttr "bind_jnt.pim" "bind_jnt_parentConstraint1.cpim";
connectAttr "bind_jnt.rp" "bind_jnt_parentConstraint1.crp";
connectAttr "bind_jnt.rpt" "bind_jnt_parentConstraint1.crt";
connectAttr "bind_jnt.jo" "bind_jnt_parentConstraint1.cjo";
connectAttr "main_ctrl.t" "bind_jnt_parentConstraint1.tg[0].tt";
connectAttr "main_ctrl.rp" "bind_jnt_parentConstraint1.tg[0].trp";
connectAttr "main_ctrl.rpt" "bind_jnt_parentConstraint1.tg[0].trt";
connectAttr "main_ctrl.r" "bind_jnt_parentConstraint1.tg[0].tr";
connectAttr "main_ctrl.ro" "bind_jnt_parentConstraint1.tg[0].tro";
connectAttr "main_ctrl.s" "bind_jnt_parentConstraint1.tg[0].ts";
connectAttr "main_ctrl.pm" "bind_jnt_parentConstraint1.tg[0].tpm";
connectAttr "bind_jnt_parentConstraint1.w0" "bind_jnt_parentConstraint1.tg[0].tw"
		;
connectAttr "joint2_parentConstraint1.ctx" "bot_jnt.tx";
connectAttr "joint2_parentConstraint1.cty" "bot_jnt.ty";
connectAttr "joint2_parentConstraint1.ctz" "bot_jnt.tz";
connectAttr "joint2_parentConstraint1.crx" "bot_jnt.rx";
connectAttr "joint2_parentConstraint1.cry" "bot_jnt.ry";
connectAttr "joint2_parentConstraint1.crz" "bot_jnt.rz";
connectAttr "bot_jnt.ro" "joint2_parentConstraint1.cro";
connectAttr "bot_jnt.pim" "joint2_parentConstraint1.cpim";
connectAttr "bot_jnt.rp" "joint2_parentConstraint1.crp";
connectAttr "bot_jnt.rpt" "joint2_parentConstraint1.crt";
connectAttr "bot_jnt.jo" "joint2_parentConstraint1.cjo";
connectAttr "bot_ctrl.t" "joint2_parentConstraint1.tg[0].tt";
connectAttr "bot_ctrl.rp" "joint2_parentConstraint1.tg[0].trp";
connectAttr "bot_ctrl.rpt" "joint2_parentConstraint1.tg[0].trt";
connectAttr "bot_ctrl.r" "joint2_parentConstraint1.tg[0].tr";
connectAttr "bot_ctrl.ro" "joint2_parentConstraint1.tg[0].tro";
connectAttr "bot_ctrl.s" "joint2_parentConstraint1.tg[0].ts";
connectAttr "bot_ctrl.pm" "joint2_parentConstraint1.tg[0].tpm";
connectAttr "joint2_parentConstraint1.w0" "joint2_parentConstraint1.tg[0].tw";
connectAttr "bot_jnt.s" "bind_jnt_bot.is";
connectAttr "bot_jnt.s" "up_jnt_bot.is";
connectAttr "joint3_parentConstraint1.ctx" "up_jnt.tx";
connectAttr "joint3_parentConstraint1.cty" "up_jnt.ty";
connectAttr "joint3_parentConstraint1.ctz" "up_jnt.tz";
connectAttr "joint3_parentConstraint1.crx" "up_jnt.rx";
connectAttr "joint3_parentConstraint1.cry" "up_jnt.ry";
connectAttr "joint3_parentConstraint1.crz" "up_jnt.rz";
connectAttr "up_jnt.ro" "joint3_parentConstraint1.cro";
connectAttr "up_jnt.pim" "joint3_parentConstraint1.cpim";
connectAttr "up_jnt.rp" "joint3_parentConstraint1.crp";
connectAttr "up_jnt.rpt" "joint3_parentConstraint1.crt";
connectAttr "up_jnt.jo" "joint3_parentConstraint1.cjo";
connectAttr "up_ctrl.t" "joint3_parentConstraint1.tg[0].tt";
connectAttr "up_ctrl.rp" "joint3_parentConstraint1.tg[0].trp";
connectAttr "up_ctrl.rpt" "joint3_parentConstraint1.tg[0].trt";
connectAttr "up_ctrl.r" "joint3_parentConstraint1.tg[0].tr";
connectAttr "up_ctrl.ro" "joint3_parentConstraint1.tg[0].tro";
connectAttr "up_ctrl.s" "joint3_parentConstraint1.tg[0].ts";
connectAttr "up_ctrl.pm" "joint3_parentConstraint1.tg[0].tpm";
connectAttr "joint3_parentConstraint1.w0" "joint3_parentConstraint1.tg[0].tw";
connectAttr "up_jnt.s" "bind_jnt_up.is";
connectAttr "up_jnt.s" "bot_jnt_up.is";
connectAttr "bot_ctrl_translateX.o" "bot_ctrl.tx";
connectAttr "bot_ctrl_translateY.o" "bot_ctrl.ty";
connectAttr "bot_ctrl_translateZ.o" "bot_ctrl.tz";
connectAttr "bot_ctrl_rotateX.o" "bot_ctrl.rx";
connectAttr "bot_ctrl_rotateY.o" "bot_ctrl.ry";
connectAttr "bot_ctrl_rotateZ.o" "bot_ctrl.rz";
connectAttr "bot_ctrl_scaleX.o" "bot_ctrl.sx";
connectAttr "bot_ctrl_scaleY.o" "bot_ctrl.sy";
connectAttr "bot_ctrl_scaleZ.o" "bot_ctrl.sz";
connectAttr "reverse1.ox" "bot_ctrl.v";
connectAttr "up_ctrl_translateX.o" "up_ctrl.tx";
connectAttr "up_ctrl_translateY.o" "up_ctrl.ty";
connectAttr "up_ctrl_translateZ.o" "up_ctrl.tz";
connectAttr "up_ctrl_rotateX.o" "up_ctrl.rx";
connectAttr "up_ctrl_rotateY.o" "up_ctrl.ry";
connectAttr "up_ctrl_rotateZ.o" "up_ctrl.rz";
connectAttr "main_ctrl.change" "up_ctrl.v";
connectAttr "decomposeMatrix1.ot" "main_offset_grp.t";
connectAttr "decomposeMatrix1.or" "main_offset_grp.r";
connectAttr "decomposeMatrix1.os" "main_offset_grp.s";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "groupParts2.og" "tweak1.ip[0].ig";
connectAttr "groupId2.id" "tweak1.ip[0].gi";
connectAttr "groupId2.msg" "tweakSet1.gn" -na;
connectAttr "pCylinderShape1.iog.og[1]" "tweakSet1.dsm" -na;
connectAttr "tweak1.msg" "tweakSet1.ub[0]";
connectAttr "pCylinderShape1Orig.w" "groupParts2.ig";
connectAttr "groupId2.id" "groupParts2.gi";
connectAttr "skinCluster1GroupParts.og" "skinCluster1.ip[0].ig";
connectAttr "skinCluster1GroupId.id" "skinCluster1.ip[0].gi";
connectAttr "bindPose1.msg" "skinCluster1.bp";
connectAttr "bind_jnt.wm" "skinCluster1.ma[0]";
connectAttr "bind_jnt.liw" "skinCluster1.lw[0]";
connectAttr "bind_jnt.obcc" "skinCluster1.ifcl[0]";
connectAttr "skinCluster1GroupId.msg" "skinCluster1Set.gn" -na;
connectAttr "pCylinderShape1.iog.og[4]" "skinCluster1Set.dsm" -na;
connectAttr "skinCluster1.msg" "skinCluster1Set.ub[0]";
connectAttr "tweak1.og[0]" "skinCluster1GroupParts.ig";
connectAttr "skinCluster1GroupId.id" "skinCluster1GroupParts.gi";
connectAttr "bind_jnt.msg" "bindPose1.m[0]";
connectAttr "bindPose1.w" "bindPose1.p[0]";
connectAttr "bind_jnt.bps" "bindPose1.wm[0]";
connectAttr "multMatrix1.o" "blendMatrix1.imat";
connectAttr "multMatrix2.o" "blendMatrix1.tgt[0].tmat";
connectAttr "main_ctrl.change" "blendMatrix1.tgt[0].wgt";
connectAttr "blendMatrix1.omat" "decomposeMatrix1.imat";
connectAttr "bind_jnt_bot.m" "multMatrix1.i[1]";
connectAttr "bot_jnt.m" "multMatrix1.i[2]";
connectAttr "bind_jnt_up.m" "multMatrix2.i[0]";
connectAttr "up_jnt.m" "multMatrix2.i[1]";
connectAttr "main_ctrl.change" "reverse1.ix";
connectAttr "main_offset_grp.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[0].dn";
connectAttr "up_ctrl.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[1].dn";
connectAttr "bind_jnt_up.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[2].dn";
connectAttr "bot_ctrl_rotateY.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[3].dn"
		;
connectAttr "bot_ctrl_rotateZ.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[4].dn"
		;
connectAttr "bot_ctrl_scaleX.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[5].dn";
connectAttr "blendMatrix1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[6].dn";
connectAttr "joint3_parentConstraint1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[7].dn"
		;
connectAttr "bot_ctrl_translateZ.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[8].dn"
		;
connectAttr "bot_ctrl_translateX.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[9].dn"
		;
connectAttr "bind_jnt_bot.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[10].dn";
connectAttr "bot_ctrl_scaleY.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[11].dn"
		;
connectAttr "joint2_parentConstraint1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[12].dn"
		;
connectAttr "bot_ctrl_translateY.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[13].dn"
		;
connectAttr "multMatrix1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[14].dn";
connectAttr "decomposeMatrix1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[15].dn"
		;
connectAttr "dontTouch_grp.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[16].dn";
connectAttr "up_jnt.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[17].dn";
connectAttr "bot_ctrl.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[18].dn";
connectAttr "bot_jnt.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[19].dn";
connectAttr "bot_ctrl_scaleZ.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[20].dn"
		;
connectAttr "multMatrix2.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[21].dn";
connectAttr "bot_ctrl_rotateX.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[22].dn"
		;
connectAttr "up_ctrl_translateX.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[23].dn"
		;
connectAttr "up_ctrl_translateY.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[24].dn"
		;
connectAttr "up_ctrl_translateZ.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[25].dn"
		;
connectAttr "up_ctrl_rotateX.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[26].dn"
		;
connectAttr "up_ctrl_rotateY.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[27].dn"
		;
connectAttr "up_ctrl_rotateZ.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[28].dn"
		;
connectAttr "multMatrix1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "multMatrix2.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "reverse1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "pCylinderShape1.iog" ":initialShadingGroup.dsm" -na;
// End of capcom_switchCtrlPosScript_test03.ma
