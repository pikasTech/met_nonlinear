#include "frikan.h"

// IIR Filter: test_layer0_in0_out0
const port_float IIR_test_layer0_in0_out0_a[] = { 1.000000000000f, -1.820444583893f, 0.831216692924f };
const port_float IIR_test_layer0_in0_out0_b[] = { 1.018325090408f, -1.790701985359f, 0.783646047115f };

IIR IIR_test_layer0_in0_out0 = {
    .order = 2,
    .a = IIR_test_layer0_in0_out0_a,
    .b = IIR_test_layer0_in0_out0_b
};
        

// IIR Filter: test_layer0_in0_out1
const port_float IIR_test_layer0_in0_out1_a[] = { 1.000000000000f, -1.820444583893f, 0.831216692924f };
const port_float IIR_test_layer0_in0_out1_b[] = { 0.911797881126f, -1.661547899246f, 0.760684609413f };

IIR IIR_test_layer0_in0_out1 = {
    .order = 2,
    .a = IIR_test_layer0_in0_out1_a,
    .b = IIR_test_layer0_in0_out1_b
};
        

// IIR Filter: test_layer0_in0_out2
const port_float IIR_test_layer0_in0_out2_a[] = { 1.000000000000f, -1.820444583893f, 0.831216692924f };
const port_float IIR_test_layer0_in0_out2_b[] = { 0.587365806103f, -1.044862389565f, 0.468373358250f };

IIR IIR_test_layer0_in0_out2 = {
    .order = 2,
    .a = IIR_test_layer0_in0_out2_a,
    .b = IIR_test_layer0_in0_out2_b
};
        

// IIR Filter: test_layer0_in0_out3
const port_float IIR_test_layer0_in0_out3_a[] = { 1.000000000000f, -1.820444583893f, 0.831216692924f };
const port_float IIR_test_layer0_in0_out3_b[] = { 0.455322414637f, -0.780295670033f, 0.336097598076f };

IIR IIR_test_layer0_in0_out3 = {
    .order = 2,
    .a = IIR_test_layer0_in0_out3_a,
    .b = IIR_test_layer0_in0_out3_b
};
        

// IIR Filter: test_layer0_in0_out4
const port_float IIR_test_layer0_in0_out4_a[] = { 1.000000000000f, -1.820444583893f, 0.831216692924f };
const port_float IIR_test_layer0_in0_out4_b[] = { 0.375598490238f, -0.617120683193f, 0.254340112209f };

IIR IIR_test_layer0_in0_out4 = {
    .order = 2,
    .a = IIR_test_layer0_in0_out4_a,
    .b = IIR_test_layer0_in0_out4_b
};
        

// IIR Filter: test_layer0_in0_out5
const port_float IIR_test_layer0_in0_out5_a[] = { 1.000000000000f, -1.820444583893f, 0.831216692924f };
const port_float IIR_test_layer0_in0_out5_b[] = { 0.298605114222f, -0.472968548536f, 0.187419921160f };

IIR IIR_test_layer0_in0_out5 = {
    .order = 2,
    .a = IIR_test_layer0_in0_out5_a,
    .b = IIR_test_layer0_in0_out5_b
};
        

// IIR Filter: test_layer0_in0_out6
const port_float IIR_test_layer0_in0_out6_a[] = { 1.000000000000f, -1.820444583893f, 0.831216692924f };
const port_float IIR_test_layer0_in0_out6_b[] = { 0.242324307561f, -0.363667994738f, 0.134797453880f };

IIR IIR_test_layer0_in0_out6 = {
    .order = 2,
    .a = IIR_test_layer0_in0_out6_a,
    .b = IIR_test_layer0_in0_out6_b
};
        

// IIR Filter: test_layer0_in0_out7
const port_float IIR_test_layer0_in0_out7_a[] = { 1.000000000000f, -1.820444583893f, 0.831216692924f };
const port_float IIR_test_layer0_in0_out7_b[] = { 0.222028359771f, -0.327925950289f, 0.120659641922f };

IIR IIR_test_layer0_in0_out7 = {
    .order = 2,
    .a = IIR_test_layer0_in0_out7_a,
    .b = IIR_test_layer0_in0_out7_b
};
        
const IIR *IIRs_test_layer0[] = {
    &IIR_test_layer0_in0_out0, &IIR_test_layer0_in0_out1, &IIR_test_layer0_in0_out2, &IIR_test_layer0_in0_out3, &IIR_test_layer0_in0_out4, &IIR_test_layer0_in0_out5, &IIR_test_layer0_in0_out6, &IIR_test_layer0_in0_out7,
};


const LayerIIR LayerIIR_test_layer0 = {
    .in_size = 1,
    .out_size = 8,
    .order = 2,
    .iirs = IIRs_test_layer0
};
        

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in0_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in0_out0_spline_kernel[] = { 0.285295188427f, 0.000512709201f, 0.013794871978f, 0.000041202620f, 0.080398499966f, 0.104102306068f, 0.146431043744f, 0.114856280386f, 0.067011639476f, 0.056499674916f };
const port_float KAN_LUT_test_layer0_in0_out0_lut[] = { 0.142903948814f, 0.007177993321f, 0.008971831197f, 0.021804219374f, 0.079885151790f, 0.107950402778f, 0.136872351016f, 0.118086235552f, 0.079273826820f, 0.059084263469f, 0.023346973106f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in0_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in0_out0_grid,
    .spline_kernel = KAN_LUT_test_layer0_in0_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in0_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in0_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in0_out1_spline_kernel[] = { 0.293657064438f, 0.024601744488f, 0.133116498590f, 0.000647736888f, 0.015495155938f, 0.062922857702f, 0.117763020098f, 0.142650783062f, 0.109081283212f, 0.082030996680f };
const port_float KAN_LUT_test_layer0_in0_out1_lut[] = { 0.159129404463f, 0.070554350811f, 0.086984148531f, 0.009500851245f, 0.024116638093f, 0.066181342422f, 0.112176029304f, 0.135392054207f, 0.116953165078f, 0.089729133963f, 0.033897106066f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in0_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in0_out1_grid,
    .spline_kernel = KAN_LUT_test_layer0_in0_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in0_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in0_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in0_out2_spline_kernel[] = { 0.000008540420f, 0.093588136137f, 0.185168772936f, 0.256632983685f, 0.200922384858f, 0.176692038774f, 0.171065300703f, 0.058063276112f, 0.039654877037f, 0.009885269217f };
const port_float KAN_LUT_test_layer0_in0_out2_lut[] = { 0.046798338278f, 0.131044681939f, 0.207574882537f, 0.239241842273f, 0.199699585780f, 0.178358138285f, 0.160228573248f, 0.079726767103f, 0.043416079807f, 0.019686083914f, 0.004084821991f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in0_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in0_out2_grid,
    .spline_kernel = KAN_LUT_test_layer0_in0_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in0_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in0_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in0_out3_spline_kernel[] = { 0.000433497888f, 0.171546608210f, 0.232616171241f, 0.271786034107f, 0.161218732595f, 0.069406993687f, 0.004442616366f, 0.002706188709f, 0.020767532289f, 0.019884437323f };
const port_float KAN_LUT_test_layer0_in0_out3_lut[] = { 0.085990053049f, 0.196074885866f, 0.244717330910f, 0.241088364427f, 0.149938987214f, 0.069227555213f, 0.013927355590f, 0.004251917851f, 0.015958136240f, 0.019851350310f, 0.008216709637f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in0_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in0_out3_grid,
    .spline_kernel = KAN_LUT_test_layer0_in0_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in0_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in0_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in0_out4_spline_kernel[] = { 0.000003665448f, 0.098945371807f, 0.145685479045f, 0.068946108222f, 0.021869795397f, 0.001928650425f, 0.010223447345f, 0.051829818636f, 0.083725526929f, 0.075405113399f };
const port_float KAN_LUT_test_layer0_in0_out4_lut[] = { 0.049474518627f, 0.117850615680f, 0.119227423402f, 0.059350117795f, 0.020944609040f, 0.005222622794f, 0.013287689466f, 0.045514195245f, 0.074980861423f, 0.076943679690f, 0.031159137768f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in0_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in0_out4_grid,
    .spline_kernel = KAN_LUT_test_layer0_in0_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in0_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in0_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in0_out5_spline_kernel[] = { 0.205807328224f, 0.117941498756f, 0.009918499738f, 0.000035512054f, 0.000233723782f, 0.025105379522f, 0.028593635187f, 0.020440630615f, 0.027746455744f, 0.018412249163f };
const port_float KAN_LUT_test_layer0_in0_out5_lut[] = { 0.161874413490f, 0.073666977796f, 0.008396061695f, 0.000455480813f, 0.005256615284f, 0.023054907664f, 0.027232468582f, 0.022574475351f, 0.025467196787f, 0.021232173693f, 0.007608367423f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in0_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in0_out5_grid,
    .spline_kernel = KAN_LUT_test_layer0_in0_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in0_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in1_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in1_out0_spline_kernel[] = { 0.041986040771f, 0.000020934516f, 0.131614923477f, 0.001916027628f, 0.000010606269f, 0.000015990647f, 0.000047574689f, 0.027956804261f, 0.048448763788f, 0.365897238255f };
const port_float KAN_LUT_test_layer0_in1_out0_lut[] = { 0.021003487644f, 0.054572025435f, 0.086028202322f, 0.006235627197f, 0.000137674766f, 0.000020132862f, 0.002926061110f, 0.023660602209f, 0.054835337591f, 0.253595935011f, 0.151197205890f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in1_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in1_out0_grid,
    .spline_kernel = KAN_LUT_test_layer0_in1_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in1_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in1_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in1_out1_spline_kernel[] = { 0.287234574556f, 0.035389866680f, 0.284318238497f, 0.242631703615f, 0.194337576628f, 0.035032704473f, 0.126427039504f, 0.241846039891f, 0.252145022154f, 0.005757375155f };
const port_float KAN_LUT_test_layer0_in1_out1_lut[] = { 0.161312220618f, 0.139293510852f, 0.266250788858f, 0.231410028767f, 0.165274631571f, 0.065085670857f, 0.124754638465f, 0.219157001450f, 0.240258147411f, 0.088130804520f, 0.002379080642f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in1_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in1_out1_grid,
    .spline_kernel = KAN_LUT_test_layer0_in1_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in1_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in1_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in1_out2_spline_kernel[] = { 0.117366053164f, 0.041725590825f, 0.000921454339f, 0.104267157614f, 0.036958634853f, 0.087449178100f, 0.158448964357f, 0.203767910600f, 0.251005679369f, 0.000021151238f };
const port_float KAN_LUT_test_layer0_in1_out2_lut[] = { 0.079545821995f, 0.025176941295f, 0.036186820088f, 0.082623121308f, 0.051632076933f, 0.092795164563f, 0.152568722005f, 0.197714918593f, 0.229178910962f, 0.084028019724f, 0.000008740181f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in1_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in1_out2_grid,
    .spline_kernel = KAN_LUT_test_layer0_in1_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in1_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in1_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in1_out3_spline_kernel[] = { 0.110873229802f, 0.064471043646f, 0.000035855162f, 0.001105657197f, 0.199526920915f, 0.200000554323f, 0.168905675411f, 0.024673266336f, 0.119651481509f, 0.013131547719f };
const port_float KAN_LUT_test_layer0_in1_out3_lut[] = { 0.087672136724f, 0.038036677273f, 0.001458973835f, 0.053540916121f, 0.186504060657f, 0.195325940786f, 0.158631317618f, 0.060156900582f, 0.090571790703f, 0.048567863612f, 0.005426259388f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in1_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in1_out3_grid,
    .spline_kernel = KAN_LUT_test_layer0_in1_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in1_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in1_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in1_out4_spline_kernel[] = { 0.178580299020f, 0.057601667941f, 0.000156904585f, 0.120526686311f, 0.102273732424f, 0.197369590402f, 0.073034077883f, 0.066850818694f, 0.098177433014f, 0.511686205864f };
const port_float KAN_LUT_test_layer0_in1_out4_lut[] = { 0.118090983480f, 0.034364074121f, 0.041395463979f, 0.111222896706f, 0.122735485742f, 0.169049446186f, 0.090891503383f, 0.070173982038f, 0.105271134002f, 0.364822753697f, 0.211440580936f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in1_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in1_out4_grid,
    .spline_kernel = KAN_LUT_test_layer0_in1_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in1_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in1_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in1_out5_spline_kernel[] = { 0.000011272247f, 0.032314572483f, 0.141098573804f, 0.165521144867f, 0.147311791778f, 0.152184158564f, 0.158235177398f, 0.217510327697f, 0.124832242727f, 0.676389753819f };
const port_float KAN_LUT_test_layer0_in1_out5_lut[] = { 0.016162922365f, 0.077133154433f, 0.147474988064f, 0.159797170746f, 0.149502269554f, 0.152580966449f, 0.163458491776f, 0.199380857762f, 0.169854618917f, 0.480597533101f, 0.279499898272f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in1_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in1_out5_grid,
    .spline_kernel = KAN_LUT_test_layer0_in1_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in1_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in2_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in2_out0_spline_kernel[] = { 0.000457609742f, 0.068427078426f, 0.043151393533f, 0.000016273460f, 0.038151722401f, 0.043187163770f, 0.000057254172f, 0.266748219728f, 0.417211085558f, 0.031900566071f };
const port_float KAN_LUT_test_layer0_in2_out0_lut[] = { 0.034442344084f, 0.057701714963f, 0.029131385325f, 0.011705880125f, 0.036649943244f, 0.036250953937f, 0.034023993364f, 0.222696767419f, 0.363089523209f, 0.160340854559f, 0.013182052096f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in2_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in2_out0_grid,
    .spline_kernel = KAN_LUT_test_layer0_in2_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in2_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in2_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in2_out1_spline_kernel[] = { 0.177977859974f, 0.015617411584f, 0.229702860117f, 0.156713560224f, 0.274789959192f, 0.070800371468f, 0.055232509971f, 0.055305071175f, 0.045042082667f, 0.837570726871f };
const port_float KAN_LUT_test_layer0_in2_out1_lut[] = { 0.096797635779f, 0.104753383905f, 0.201733954805f, 0.190654854575f, 0.225679578275f, 0.089557795762f, 0.057555886186f, 0.054611834336f, 0.077230467222f, 0.558458730640f, 0.346103606145f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in2_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in2_out1_grid,
    .spline_kernel = KAN_LUT_test_layer0_in2_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in2_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in2_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in2_out2_spline_kernel[] = { 0.120539039373f, 0.000005301830f, 0.020550755784f, 0.000057010955f, 0.322616666555f, 0.148170381784f, 0.191125348210f, 0.138236060739f, 0.240669965744f, 0.016077008098f };
const port_float KAN_LUT_test_layer0_in2_out2_lut[] = { 0.060272170602f, 0.008993232132f, 0.013351684929f, 0.086124207905f, 0.265968639930f, 0.172581687200f, 0.179271583838f, 0.155717538285f, 0.205227376739f, 0.090984948334f, 0.006643391776f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in2_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in2_out2_grid,
    .spline_kernel = KAN_LUT_test_layer0_in2_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in2_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in2_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in2_out3_spline_kernel[] = { 0.283228248358f, 0.046595841646f, 0.002237551380f, 0.048309657723f, 0.176567137241f, 0.248431876302f, 0.238589197397f, 0.115156777203f, 0.000156211856f, 0.035258211195f };
const port_float KAN_LUT_test_layer0_in2_out3_lut[] = { 0.164912045002f, 0.029243789498f, 0.018391575243f, 0.080515565707f, 0.182638428736f, 0.239543632843f, 0.227302114487f, 0.132545948872f, 0.031875030766f, 0.022926414537f, 0.014569508758f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in2_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in2_out3_grid,
    .spline_kernel = KAN_LUT_test_layer0_in2_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in2_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in2_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in2_out4_spline_kernel[] = { 0.268884390593f, 0.000339692488f, 0.000012919518f, 0.006687251851f, 0.070079959929f, 0.066624894738f, 0.318944782019f, 0.077093847096f, 0.000064338208f, 0.922946453094f };
const port_float KAN_LUT_test_layer0_in2_out4_lut[] = { 0.134612041540f, 0.001314351170f, 0.002252291463f, 0.023204046586f, 0.065189127187f, 0.104517012804f, 0.256424991460f, 0.120970804406f, 0.054757840699f, 0.598792580705f, 0.381382831857f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in2_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in2_out4_grid,
    .spline_kernel = KAN_LUT_test_layer0_in2_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in2_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in2_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in2_out5_spline_kernel[] = { 0.000333015138f, 0.018087340519f, 0.102843463421f, 0.166153371334f, 0.197335422039f, 0.025305584073f, 0.055417042226f, 0.016933031380f, 0.100206889212f, 0.118953160942f };
const port_float KAN_LUT_test_layer0_in2_out5_lut[] = { 0.009210177828f, 0.053037166820f, 0.122633042137f, 0.172045363375f, 0.160441310999f, 0.047556652018f, 0.046962030802f, 0.030230958061f, 0.078881226172f, 0.110712414438f, 0.049154198736f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in2_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in2_out5_grid,
    .spline_kernel = KAN_LUT_test_layer0_in2_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in2_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in3_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in3_out0_spline_kernel[] = { 0.112609624863f, 0.057225387543f, 0.000026745065f, 0.028623851016f, 0.129470393062f, 0.013872695155f, 0.168521344662f, 0.158328309655f, 0.045300614089f, 0.402966737747f };
const port_float KAN_LUT_test_layer0_in3_out0_lut[] = { 0.084917506203f, 0.033818445351f, 0.010543935776f, 0.054230482162f, 0.099396707648f, 0.048820190320f, 0.144462760953f, 0.152919283152f, 0.088493868755f, 0.276591436229f, 0.166515180887f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in3_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in3_out0_grid,
    .spline_kernel = KAN_LUT_test_layer0_in3_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in3_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in3_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in3_out1_spline_kernel[] = { 0.119108833373f, 0.094405844808f, 0.053592700511f, 0.000018131674f, 0.136021926999f, 0.132574722171f, 0.126459896564f, 0.054720778018f, 0.144455149770f, 0.000056972247f };
const port_float KAN_LUT_test_layer0_in3_out1_lut[] = { 0.106757339090f, 0.077642987613f, 0.036335314153f, 0.037978520188f, 0.126331952777f, 0.132021194893f, 0.119958474078f, 0.075179318336f, 0.115353565514f, 0.048387651959f, 0.000023542251f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in3_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in3_out1_grid,
    .spline_kernel = KAN_LUT_test_layer0_in3_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in3_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in3_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in3_out2_spline_kernel[] = { 0.145499482751f, 0.000047766305f, 0.113208755851f, 0.148052588105f, 0.005758957472f, 0.144038647413f, 0.079566784203f, 0.163787603378f, 0.001926228520f, 0.632958471775f };
const port_float KAN_LUT_test_layer0_in3_out2_lut[] = { 0.072773624528f, 0.047409545937f, 0.123000931282f, 0.109125369713f, 0.043165581014f, 0.120162699793f, 0.097858137736f, 0.136033049092f, 0.068200683811f, 0.411283076772f, 0.261553087510f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in3_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in3_out2_grid,
    .spline_kernel = KAN_LUT_test_layer0_in3_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in3_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in3_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in3_out3_spline_kernel[] = { 0.004357653670f, 0.055885024369f, 0.162967726588f, 0.038943883032f, 0.000033234275f, 0.000050854374f, 0.130826637149f, 0.212952211499f, 0.344821244478f, 0.562617242336f };
const port_float KAN_LUT_test_layer0_in3_out3_lut[] = { 0.030121339019f, 0.099921151853f, 0.119685651642f, 0.033265920518f, 0.002609406858f, 0.019503282793f, 0.119856435409f, 0.205042093253f, 0.318046640636f, 0.480419123345f, 0.232486463775f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in3_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in3_out3_grid,
    .spline_kernel = KAN_LUT_test_layer0_in3_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in3_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in3_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in3_out4_spline_kernel[] = { 0.078274227679f, 0.057633385062f, 0.072442762554f, 0.000029852323f, 0.023210572079f, 0.075778797269f, 0.084471486509f, 0.155305191875f, 0.161331266165f, 0.000033573815f };
const port_float KAN_LUT_test_layer0_in3_out4_lut[] = { 0.067953806370f, 0.063838255276f, 0.047960600410f, 0.008853332721f, 0.032321941989f, 0.071641322818f, 0.090495890730f, 0.141361248179f, 0.153738919116f, 0.054021089456f, 0.000013873477f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in3_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in3_out4_grid,
    .spline_kernel = KAN_LUT_test_layer0_in3_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in3_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in3_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in3_out5_spline_kernel[] = { 0.121868446469f, 0.121591277421f, 0.000778812391f, 0.000003746721f, 0.013659511693f, 0.080345109105f, 0.059739463031f, 0.024231266230f, 0.065190784633f, 0.510296761990f };
const port_float KAN_LUT_test_layer0_in3_out5_lut[] = { 0.121729861945f, 0.071669916537f, 0.002516289833f, 0.003644013453f, 0.026259106873f, 0.070390798386f, 0.059136563604f, 0.034129009775f, 0.070912043387f, 0.352880352015f, 0.210866430574f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in3_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in3_out5_grid,
    .spline_kernel = KAN_LUT_test_layer0_in3_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in3_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in4_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in4_out0_spline_kernel[] = { 0.008765056729f, 0.103803902864f, 0.054772406816f, 0.031028814614f, 0.160121858120f, 0.106197044253f, 0.230562657118f, 0.037201810628f, 0.040999103338f, 0.084777891636f };
const port_float KAN_LUT_test_layer0_in4_out0_lut[] = { 0.056284479797f, 0.083150231580f, 0.047635609361f, 0.066052149797f, 0.140668120204f, 0.130268459170f, 0.192086693377f, 0.076604447659f, 0.041622997392f, 0.068723373377f, 0.035032186626f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in4_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in4_out0_grid,
    .spline_kernel = KAN_LUT_test_layer0_in4_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in4_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in4_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in4_out1_spline_kernel[] = { 0.097846962512f, 0.040914785117f, 0.178204819560f, 0.000009883598f, 0.000075275617f, 0.000052669147f, 0.118590630591f, 0.224569976330f, 0.111650429666f, 0.086975425482f };
const port_float KAN_LUT_test_layer0_in4_out1_lut[] = { 0.069380873814f, 0.097881461240f, 0.116291803235f, 0.006654261750f, 0.000066374835f, 0.017688750857f, 0.111905163779f, 0.195645593322f, 0.140595784826f, 0.093796804147f, 0.035940258464f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in4_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in4_out1_grid,
    .spline_kernel = KAN_LUT_test_layer0_in4_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in4_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in4_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in4_out2_spline_kernel[] = { 0.131740182638f, 0.060958962888f, 0.188795968890f, 0.170951321721f, 0.025573415682f, 0.011623282917f, 0.025243459269f, 0.109937638044f, 0.106734514236f, 0.047562476248f };
const port_float KAN_LUT_test_layer0_in4_out2_lut[] = { 0.096349572763f, 0.114076656359f, 0.180710165400f, 0.133167916093f, 0.032360564405f, 0.015090554271f, 0.031966715966f, 0.092577039941f, 0.105381008376f, 0.066581836463f, 0.019653915805f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in4_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in4_out2_grid,
    .spline_kernel = KAN_LUT_test_layer0_in4_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in4_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in4_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in4_out3_spline_kernel[] = { 0.000763851276f, 0.116825319827f, 0.245886430144f, 0.020612362772f, 0.156887844205f, 0.002651496790f, 0.000041565439f, 0.000025429714f, 0.282286554575f, 0.335611879826f };
const port_float KAN_LUT_test_layer0_in4_out3_lut[] = { 0.058794585551f, 0.169676764303f, 0.168351538002f, 0.065030120698f, 0.116648221369f, 0.018196749504f, 0.000428152776f, 0.018690589418f, 0.209622157617f, 0.312216016749f, 0.138682594969f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in4_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in4_out3_grid,
    .spline_kernel = KAN_LUT_test_layer0_in4_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in4_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in4_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in4_out4_spline_kernel[] = { 0.091310188174f, 0.073993571103f, 0.097320638597f, 0.004654650576f, 0.030988527462f, 0.157958537340f, 0.089409142733f, 0.027021922171f, 0.070341631770f, 0.088269084692f };
const port_float KAN_LUT_test_layer0_in4_out4_lut[] = { 0.082651879638f, 0.083704411460f, 0.065918765458f, 0.015065237406f, 0.054956248346f, 0.134644370180f, 0.093161612534f, 0.042518158374f, 0.059551903101f, 0.080809580455f, 0.036474828385f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in4_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in4_out4_grid,
    .spline_kernel = KAN_LUT_test_layer0_in4_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in4_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in4_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in4_out5_spline_kernel[] = { 0.210153058171f, 0.052231810987f, 0.000218138564f, 0.000017136692f, 0.020556122065f, 0.013089409098f, 0.023682475090f, 0.047844249755f, 0.116093449295f, 0.109679490328f };
const port_float KAN_LUT_test_layer0_in4_out5_lut[] = { 0.131192434579f, 0.031391125057f, 0.001010591201f, 0.005456409753f, 0.017686317514f, 0.015436591742f, 0.024602698193f, 0.047464333367f, 0.097805538546f, 0.110013427167f, 0.045322103441f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in4_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in4_out5_grid,
    .spline_kernel = KAN_LUT_test_layer0_in4_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in4_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in5_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in5_out0_spline_kernel[] = { 0.001585468068f, 0.000028739576f, 0.123898945749f, 0.133394479752f, 0.168120071292f, 0.137431710958f, 0.126218542457f, 0.135709837079f, 0.138591006398f, 0.203219816089f };
const port_float KAN_LUT_test_layer0_in5_out0_lut[] = { 0.000807103822f, 0.051221207947f, 0.125029761573f, 0.142224967572f, 0.159610405503f, 0.138933921464f, 0.128867122753f, 0.133978536553f, 0.140232595038f, 0.178228853902f, 0.083975130615f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in5_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in5_out0_grid,
    .spline_kernel = KAN_LUT_test_layer0_in5_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in5_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in5_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in5_out1_spline_kernel[] = { 0.089068755507f, 0.001801643404f, 0.134133383632f, 0.000014709296f, 0.026958134025f, 0.000052014253f, 0.091151081026f, 0.242048174143f, 0.110270917416f, 0.154483333230f };
const port_float KAN_LUT_test_layer0_in5_out1_lut[] = { 0.045435199456f, 0.056844788590f, 0.087055120896f, 0.012128127691f, 0.019728817230f, 0.016383499369f, 0.093187696415f, 0.202782084596f, 0.146765364411f, 0.137131519123f, 0.063836088112f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in5_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in5_out1_grid,
    .spline_kernel = KAN_LUT_test_layer0_in5_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in5_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in5_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in5_out2_spline_kernel[] = { 0.116249300539f, 0.000007362044f, 0.193433880806f, 0.033062689006f, 0.072633296251f, 0.021309759468f, 0.009981879964f, 0.107155054808f, 0.080470897257f, 0.282211929560f };
const port_float KAN_LUT_test_layer0_in5_out2_lut[] = { 0.058128331292f, 0.080416014171f, 0.136558787373f, 0.049491860865f, 0.059625101961f, 0.024926638631f, 0.021705570184f, 0.085715252791f, 0.095030630208f, 0.210022378590f, 0.116616499818f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in5_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in5_out2_grid,
    .spline_kernel = KAN_LUT_test_layer0_in5_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in5_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in5_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in5_out3_spline_kernel[] = { 0.001179149840f, 0.116782866418f, 0.089849591255f, 0.078413337469f, 0.104960948229f, 0.048386309296f, 0.000047960279f, 0.025857409462f, 0.122541233897f, 0.196048885584f };
const port_float KAN_LUT_test_layer0_in5_out3_lut[] = { 0.058981008129f, 0.105175712563f, 0.086466932346f, 0.085859508431f, 0.091750538808f, 0.047039968010f, 0.009905054470f, 0.027023848227f, 0.099705713655f, 0.168204607365f, 0.081011936192f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in5_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in5_out3_grid,
    .spline_kernel = KAN_LUT_test_layer0_in5_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in5_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in5_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in5_out4_spline_kernel[] = { 0.020924327895f, 0.036609917879f, 0.007177315187f, 0.006648285780f, 0.135973066092f, 0.074418768287f, 0.166577786207f, 0.097216419876f, 0.024973824620f, 0.100325077772f };
const port_float KAN_LUT_test_layer0_in5_out4_lut[] = { 0.028767122887f, 0.024382868874f, 0.007486732661f, 0.040869555221f, 0.114959193871f, 0.094487289321f, 0.145702749829f, 0.106484293537f, 0.046881623689f, 0.073445938035f, 0.041456643707f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in5_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in5_out4_grid,
    .spline_kernel = KAN_LUT_test_layer0_in5_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in5_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in5_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in5_out5_spline_kernel[] = { 0.024794733152f, 0.109992206097f, 0.000022248818f, 0.002988985740f, 0.138261958957f, 0.000025229359f, 0.021401789039f, 0.156567499042f, 0.118191316724f, 0.108872212470f };
const port_float KAN_LUT_test_layer0_in5_out5_lut[] = { 0.067393469624f, 0.064198019316f, 0.002832932784f, 0.038653323151f, 0.101328209693f, 0.017485867328f, 0.032185204748f, 0.126661967194f, 0.127993811476f, 0.110191876084f, 0.044988517549f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in5_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in5_out5_grid,
    .spline_kernel = KAN_LUT_test_layer0_in5_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in5_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in6_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in6_out0_spline_kernel[] = { 0.072568126023f, 0.141146153212f, 0.100530810654f, 0.083144098520f, 0.238377273083f, 0.278208911419f, 0.297595471144f, 0.241663202643f, 0.221523776650f, 0.019062690437f };
const port_float KAN_LUT_test_layer0_in6_out0_lut[] = { 0.106857139617f, 0.124079573530f, 0.095382619280f, 0.124844113319f, 0.236179006494f, 0.276978023781f, 0.288933393199f, 0.251656799092f, 0.219320361310f, 0.086513505402f, 0.007877144809f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in6_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in6_out0_grid,
    .spline_kernel = KAN_LUT_test_layer0_in6_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in6_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in6_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in6_out1_spline_kernel[] = { 0.196103587747f, 0.116084128618f, 0.062805898488f, 0.000018524779f, 0.018356811255f, 0.000034176697f, 0.085650749505f, 0.163408815861f, 0.238952293992f, 0.044084459543f };
const port_float KAN_LUT_test_layer0_in6_out1_lut[] = { 0.156093858182f, 0.094398989966f, 0.042670921835f, 0.007203387167f, 0.013434407631f, 0.014663360520f, 0.080947257925f, 0.152659024120f, 0.211726702627f, 0.108580148602f, 0.018216718820f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in6_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in6_out1_grid,
    .spline_kernel = KAN_LUT_test_layer0_in6_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in6_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in6_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in6_out2_spline_kernel[] = { 0.123108386993f, 0.003349754959f, 0.253615379333f, 0.077661938965f, 0.000042681866f, 0.065818466246f, 0.006343823392f, 0.052790641785f, 0.118628643453f, 0.177238777280f };
const port_float KAN_LUT_test_layer0_in6_out2_lut[] = { 0.063229070976f, 0.107260172602f, 0.190585250543f, 0.063678255118f, 0.018492770908f, 0.050175979667f, 0.019989515965f, 0.047739046435f, 0.103396656253f, 0.154691769226f, 0.073239164165f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in6_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in6_out2_grid,
    .spline_kernel = KAN_LUT_test_layer0_in6_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in6_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in6_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in6_out3_spline_kernel[] = { 0.023590095341f, 0.080587454140f, 0.181747987866f, 0.194092303514f, 0.048475250602f, 0.022694457322f, 0.000035272198f, 0.076110810041f, 0.049810353667f, 0.121197320521f };
const port_float KAN_LUT_test_layer0_in6_out3_lut[] = { 0.052088774741f, 0.122153801305f, 0.184207688001f, 0.155122922410f, 0.052882746370f, 0.021986974543f, 0.011265103233f, 0.058968212288f, 0.059420733459f, 0.095300074251f, 0.050081537405f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in6_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in6_out3_grid,
    .spline_kernel = KAN_LUT_test_layer0_in6_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in6_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in6_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in6_out4_spline_kernel[] = { 0.096133805811f, 0.249704241753f, 0.084936574101f, 0.093973413110f, 0.098804391921f, 0.101449042559f, 0.170162826777f, 0.239969432354f, 0.071602128446f, 0.106070049107f };
const port_float KAN_LUT_test_layer0_in6_out4_lut[] = { 0.172919023782f, 0.180983840095f, 0.090684733731f, 0.094914946551f, 0.099020475476f, 0.111397720104f, 0.167152367717f, 0.214703314437f, 0.117410883554f, 0.092780041793f, 0.043830598805f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in6_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in6_out4_grid,
    .spline_kernel = KAN_LUT_test_layer0_in6_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in6_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in6_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in6_out5_spline_kernel[] = { 0.062942720950f, 0.014789444394f, 0.000022933495f, 0.007952113636f, 0.000047920410f, 0.000026866290f, 0.082944266498f, 0.029826845974f, 0.010758129880f, 0.043347883970f };
const port_float KAN_LUT_test_layer0_in6_out5_lut[] = { 0.038866082672f, 0.008886560868f, 0.002920989838f, 0.005566861620f, 0.000566248673f, 0.012363861168f, 0.065122109801f, 0.039321284603f, 0.017013111768f, 0.031723249188f, 0.017912348748f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in6_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in6_out5_grid,
    .spline_kernel = KAN_LUT_test_layer0_in6_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in6_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in7_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in7_out0_spline_kernel[] = { 0.006960591767f, 0.089633539319f, 0.070918269455f, 0.184956878424f, 0.161386013031f, 0.062167197466f, 0.061087142676f, 0.152801617980f, 0.144613519311f, 0.213508889079f };
const port_float KAN_LUT_test_layer0_in7_out0_lut[] = { 0.048297065543f, 0.081558332981f, 0.109397560389f, 0.174482155838f, 0.142854657178f, 0.072256405799f, 0.070722447862f, 0.133689969763f, 0.149341191388f, 0.186919796073f, 0.088226813669f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in7_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in7_out0_grid,
    .spline_kernel = KAN_LUT_test_layer0_in7_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in7_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in7_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in7_out1_spline_kernel[] = { 0.098084136844f, 0.076014399529f, 0.000019122685f, 0.074257329106f, 0.151983618736f, 0.116833060980f, 0.154614314437f, 0.090521708131f, 0.115352012217f, 0.123229779303f };
const port_float KAN_LUT_test_layer0_in7_out1_lut[] = { 0.087049268186f, 0.044702589830f, 0.026123568253f, 0.092052117034f, 0.139727428802f, 0.126084668700f, 0.142372825668f, 0.105140809678f, 0.109078295036f, 0.118556150166f, 0.050921396406f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in7_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in7_out1_grid,
    .spline_kernel = KAN_LUT_test_layer0_in7_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in7_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in7_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in7_out2_spline_kernel[] = { 0.175513193011f, 0.000002331165f, 0.070806063712f, 0.031303539872f, 0.152759969234f, 0.017352828756f, 0.063933961093f, 0.173171982169f, 0.058360196650f, 0.000019346942f };
const port_float KAN_LUT_test_layer0_in7_out2_lut[] = { 0.087757762088f, 0.029985323382f, 0.056413834946f, 0.064893350590f, 0.117312643808f, 0.038270594360f, 0.068289455981f, 0.143462678033f, 0.086553943038f, 0.019546336358f, 0.000007994604f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in7_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in7_out2_grid,
    .spline_kernel = KAN_LUT_test_layer0_in7_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in7_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in7_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in7_out3_spline_kernel[] = { 0.127186432481f, 0.001040431205f, 0.000004364582f, 0.035051014274f, 0.122029125690f, 0.212570339441f, 0.228575631976f, 0.166560262442f, 0.102348804474f, 0.031358480453f };
const port_float KAN_LUT_test_layer0_in7_out3_lut[] = { 0.064113431843f, 0.001133568970f, 0.011751979837f, 0.056750102222f, 0.134611231852f, 0.205597860877f, 0.219788132928f, 0.174871707812f, 0.116690211060f, 0.054601382618f, 0.012958049774f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in7_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in7_out3_grid,
    .spline_kernel = KAN_LUT_test_layer0_in7_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in7_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in7_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in7_out4_spline_kernel[] = { 0.148704096675f, 0.130812078714f, 0.113830111921f, 0.125969931483f, 0.206189393997f, 0.257979273796f, 0.248207420111f, 0.207101345062f, 0.226355791092f, 0.079403527081f };
const port_float KAN_LUT_test_layer0_in7_out4_lut[] = { 0.139758087695f, 0.123868671023f, 0.118174133622f, 0.146733515057f, 0.211372008501f, 0.251175415417f, 0.245414588939f, 0.216697497186f, 0.215798539348f, 0.127277573678f, 0.032811374827f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in7_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in7_out4_grid,
    .spline_kernel = KAN_LUT_test_layer0_in7_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in7_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer0_in7_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer0_in7_out5_spline_kernel[] = { 0.000012972647f, 0.255829274654f, 0.304833441973f, 0.147732838988f, 0.071965157986f, 0.109680324793f, 0.000013711890f, 0.059861510992f, 0.036318510771f, 0.029849512503f };
const port_float KAN_LUT_test_layer0_in7_out5_lut[] = { 0.127921123651f, 0.275021838414f, 0.251440196059f, 0.133537689578f, 0.084611133480f, 0.089470088286f, 0.022510377353f, 0.046187006200f, 0.042304176183f, 0.031521375353f, 0.012334509299f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer0_in7_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer0_in7_out5_grid,
    .spline_kernel = KAN_LUT_test_layer0_in7_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer0_in7_out5_lut
};
    
const KAN_LUT *KAN_LUTs_test_layer0[] = {
    &KAN_LUT_test_layer0_in0_out0, &KAN_LUT_test_layer0_in0_out1, &KAN_LUT_test_layer0_in0_out2, &KAN_LUT_test_layer0_in0_out3, &KAN_LUT_test_layer0_in0_out4, &KAN_LUT_test_layer0_in0_out5,
    &KAN_LUT_test_layer0_in1_out0, &KAN_LUT_test_layer0_in1_out1, &KAN_LUT_test_layer0_in1_out2, &KAN_LUT_test_layer0_in1_out3, &KAN_LUT_test_layer0_in1_out4, &KAN_LUT_test_layer0_in1_out5,
    &KAN_LUT_test_layer0_in2_out0, &KAN_LUT_test_layer0_in2_out1, &KAN_LUT_test_layer0_in2_out2, &KAN_LUT_test_layer0_in2_out3, &KAN_LUT_test_layer0_in2_out4, &KAN_LUT_test_layer0_in2_out5,
    &KAN_LUT_test_layer0_in3_out0, &KAN_LUT_test_layer0_in3_out1, &KAN_LUT_test_layer0_in3_out2, &KAN_LUT_test_layer0_in3_out3, &KAN_LUT_test_layer0_in3_out4, &KAN_LUT_test_layer0_in3_out5,
    &KAN_LUT_test_layer0_in4_out0, &KAN_LUT_test_layer0_in4_out1, &KAN_LUT_test_layer0_in4_out2, &KAN_LUT_test_layer0_in4_out3, &KAN_LUT_test_layer0_in4_out4, &KAN_LUT_test_layer0_in4_out5,
    &KAN_LUT_test_layer0_in5_out0, &KAN_LUT_test_layer0_in5_out1, &KAN_LUT_test_layer0_in5_out2, &KAN_LUT_test_layer0_in5_out3, &KAN_LUT_test_layer0_in5_out4, &KAN_LUT_test_layer0_in5_out5,
    &KAN_LUT_test_layer0_in6_out0, &KAN_LUT_test_layer0_in6_out1, &KAN_LUT_test_layer0_in6_out2, &KAN_LUT_test_layer0_in6_out3, &KAN_LUT_test_layer0_in6_out4, &KAN_LUT_test_layer0_in6_out5,
    &KAN_LUT_test_layer0_in7_out0, &KAN_LUT_test_layer0_in7_out1, &KAN_LUT_test_layer0_in7_out2, &KAN_LUT_test_layer0_in7_out3, &KAN_LUT_test_layer0_in7_out4, &KAN_LUT_test_layer0_in7_out5,
};


const LayerKAN_LUT LayerKAN_LUT_test_layer0 = {
    .in_size = 8,
    .out_size = 6,
    .spline_kernel_size = 10,
    .kan_luts = KAN_LUTs_test_layer0
};


// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in0_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in0_out0_spline_kernel[] = { 0.000018481151f, 0.000010372517f, 0.000000264535f, 0.002855198923f, 0.184022575617f, 0.168095856905f, 0.179236277938f, 0.143295064569f, 0.132161393762f, 0.038104172796f };
const port_float KAN_LUT_test_layer1_in0_out0_lut[] = { 0.000014426834f, 0.000006229172f, 0.000956008822f, 0.050661057183f, 0.168819735766f, 0.171398431802f, 0.173866089957f, 0.149836307222f, 0.131607839807f, 0.068956314147f, 0.015745525949f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in0_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in0_out0_grid,
    .spline_kernel = KAN_LUT_test_layer1_in0_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in0_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in0_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in0_out1_spline_kernel[] = { 0.000056647143f, 0.005328532308f, 0.034404363483f, 0.247032374144f, 0.104576759040f, 0.136383533478f, 0.141753956676f, 0.000347040012f, 0.006061797962f, 0.092983692884f };
const port_float KAN_LUT_test_layer1_in0_out1_lut[] = { 0.002692589725f, 0.017321553929f, 0.105092650834f, 0.201450508596f, 0.120435526764f, 0.133896615603f, 0.126346898197f, 0.029356854242f, 0.007783089472f, 0.062353080239f, 0.038423013589f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in0_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in0_out1_grid,
    .spline_kernel = KAN_LUT_test_layer1_in0_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in0_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in0_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in0_out2_spline_kernel[] = { 0.088141202927f, 0.002470834181f, 0.045164681971f, 0.000003107868f, 0.009542477317f, 0.000874641933f, 0.134561389685f, 0.242737069726f, 0.247202217579f, 0.335709750652f };
const port_float KAN_LUT_test_layer1_in0_out2_lut[] = { 0.045306018554f, 0.020466929833f, 0.029342934477f, 0.004205478990f, 0.007156717627f, 0.021657364263f, 0.125849278453f, 0.221128945939f, 0.249312954501f, 0.300536406927f, 0.138723037460f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in0_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in0_out2_grid,
    .spline_kernel = KAN_LUT_test_layer1_in0_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in0_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in0_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in0_out3_spline_kernel[] = { 0.245221063495f, 0.082097269595f, 0.164360627532f, 0.203875228763f, 0.004259497393f, 0.041375245899f, 0.001006215578f, 0.085196964443f, 0.044633865356f, 0.000011928832f };
const port_float KAN_LUT_test_layer1_in0_out3_lut[] = { 0.163659166545f, 0.116764457973f, 0.176226864176f, 0.149614740255f, 0.024972403917f, 0.031535664063f, 0.015708917285f, 0.065468219485f, 0.053701803013f, 0.014947173225f, 0.000004929269f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in0_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in0_out3_grid,
    .spline_kernel = KAN_LUT_test_layer1_in0_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in0_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in0_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in0_out4_spline_kernel[] = { 0.123650424182f, 0.029981996864f, 0.000000404545f, 0.000577839906f, 0.113543473184f, 0.141423910856f, 0.186027795076f, 0.028184475377f, 0.000016036003f, 0.010163485073f };
const port_float KAN_LUT_test_layer1_in0_out4_lut[] = { 0.076816210523f, 0.017979968746f, 0.000689241874f, 0.030431573838f, 0.111719883570f, 0.145178988915f, 0.163086378447f, 0.058282110234f, 0.007842925101f, 0.006599033358f, 0.004199787220f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in0_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in0_out4_grid,
    .spline_kernel = KAN_LUT_test_layer1_in0_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in0_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in0_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in0_out5_spline_kernel[] = { 0.197357401252f, 0.072514146566f, 0.170578286052f, 0.000039918057f, 0.053675360978f, 0.071404345334f, 0.000860327214f, 0.139823153615f, 0.197674527764f, 0.035204477608f };
const port_float KAN_LUT_test_layer1_in0_out5_lut[] = { 0.134935773909f, 0.113552399472f, 0.111876367186f, 0.020566834003f, 0.053718969022f, 0.059078687230f, 0.025710142555f, 0.115510936643f, 0.176332716207f, 0.089003056750f, 0.014547304797f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in0_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in0_out5_grid,
    .spline_kernel = KAN_LUT_test_layer1_in0_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in0_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in1_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in1_out0_spline_kernel[] = { 0.108138263226f, 0.014035101049f, 0.086555808783f, 0.063397668302f, 0.222089231014f, 0.070088915527f, 0.039421420544f, 0.012650136836f, 0.089240625501f, 0.002673296491f };
const port_float KAN_LUT_test_layer1_in1_out0_lut[] = { 0.061086682137f, 0.044391191691f, 0.077605840973f, 0.106226938045f, 0.180820303484f, 0.081229320766f, 0.041217898754f, 0.023134602622f, 0.065765843535f, 0.031604124854f, 0.001104667971f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in1_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in1_out0_grid,
    .spline_kernel = KAN_LUT_test_layer1_in1_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in1_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in1_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in1_out1_spline_kernel[] = { 0.345747739077f, 0.304798394442f, 0.135916039348f, 0.160590261221f, 0.095167160034f, 0.004683951382f, 0.031523037702f, 0.041409116238f, 0.073722757399f, 0.058769553900f };
const port_float KAN_LUT_test_layer1_in1_out1_lut[] = { 0.325273066759f, 0.235181509463f, 0.146966210389f, 0.142370647697f, 0.081171674063f, 0.018023981645f, 0.028551735453f, 0.041543828678f, 0.064620890185f, 0.062803154180f, 0.024284939628f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in1_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in1_out1_grid,
    .spline_kernel = KAN_LUT_test_layer1_in1_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in1_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in1_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in1_out2_spline_kernel[] = { 0.000030646614f, 0.011348130181f, 0.063356667757f, 0.112179018557f, 0.065435156226f, 0.079189062119f, 0.088170960546f, 0.068251267076f, 0.000028757262f, 0.212534114718f };
const port_float KAN_LUT_test_layer1_in1_out2_lut[] = { 0.005689388398f, 0.032792494950f, 0.078838387858f, 0.098001298117f, 0.071310541292f, 0.079104354251f, 0.084776990793f, 0.067774014278f, 0.025974165713f, 0.137893327889f, 0.087824014346f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in1_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in1_out2_grid,
    .spline_kernel = KAN_LUT_test_layer1_in1_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in1_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in1_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in1_out3_spline_kernel[] = { 0.000013503225f, 0.000053038679f, 0.032564952970f, 0.006198889576f, 0.170141324401f, 0.102899208665f, 0.000071048067f, 0.024142952636f, 0.278807938099f, 0.098020993173f };
const port_float KAN_LUT_test_layer1_in1_out3_lut[] = { 0.000033270952f, 0.013487550636f, 0.023202561267f, 0.050536122631f, 0.145687016020f, 0.094548957061f, 0.017854566231f, 0.036106243725f, 0.204735039033f, 0.156912144274f, 0.040504542634f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in1_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in1_out3_grid,
    .spline_kernel = KAN_LUT_test_layer1_in1_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in1_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in1_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in1_out4_spline_kernel[] = { 0.053219757974f, 0.000050285147f, 0.035069793463f, 0.030429640785f, 0.000026538522f, 0.121750414371f, 0.032999616116f, 0.000441729353f, 0.187422543764f, 0.081214226782f };
const port_float KAN_LUT_test_layer1_in1_out4_lut[] = { 0.026635021561f, 0.014740864917f, 0.032937849660f, 0.022561718592f, 0.026683230889f, 0.095973035721f, 0.042838796150f, 0.019396396634f, 0.134023176098f, 0.115420907643f, 0.033559597844f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in1_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in1_out4_grid,
    .spline_kernel = KAN_LUT_test_layer1_in1_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in1_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in1_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in1_out5_spline_kernel[] = { 0.033406145871f, 0.172824576497f, 0.064145117998f, 0.053120687604f, 0.173237547278f, 0.167965993285f, 0.105454839766f, 0.000013480286f, 0.074505433440f, 0.481893926859f };
const port_float KAN_LUT_test_layer1_in1_out5_lut[] = { 0.103115361184f, 0.127339600131f, 0.062251477387f, 0.085297129309f, 0.164228555954f, 0.159211395447f, 0.103861317203f, 0.026288264852f, 0.069955893931f, 0.337571432337f, 0.199129721843f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in1_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in1_out5_grid,
    .spline_kernel = KAN_LUT_test_layer1_in1_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in1_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in2_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in2_out0_spline_kernel[] = { 0.018139719963f, 0.011085625738f, 0.011946454644f, 0.097347900271f, 0.123902760446f, 0.000009450959f, 0.086747735739f, 0.192089214921f, 0.220098838210f, 0.223858073354f };
const port_float KAN_LUT_test_layer1_in2_out0_lut[] = { 0.014612672850f, 0.011470489312f, 0.040517007455f, 0.101194586389f, 0.097061231819f, 0.025711562485f, 0.084726904034f, 0.172611617783f, 0.212831140796f, 0.218899683519f, 0.092503336097f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in2_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in2_out0_grid,
    .spline_kernel = KAN_LUT_test_layer1_in2_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in2_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in2_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in2_out1_spline_kernel[] = { 0.063231095672f, 0.103666789830f, 0.000018898165f, 0.071769855917f, 0.053119689226f, 0.008069566451f, 0.046096369624f, 0.000003165191f, 0.009366367944f, 0.138838842511f };
const port_float KAN_LUT_test_layer1_in2_out1_lut[] = { 0.083448942751f, 0.060669992885f, 0.025747902894f, 0.064169156380f, 0.045231039024f, 0.018380384565f, 0.035677795140f, 0.009955141477f, 0.011705241063f, 0.093208157346f, 0.057371422525f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in2_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in2_out1_grid,
    .spline_kernel = KAN_LUT_test_layer1_in2_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in2_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in2_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in2_out2_spline_kernel[] = { 0.227752745152f, 0.174003124237f, 0.053860794753f, 0.022844446823f, 0.025184107944f, 0.011940033175f, 0.082234732807f, 0.030479570851f, 0.037599679083f, 0.140304505825f };
const port_float KAN_LUT_test_layer1_in2_out2_lut[] = { 0.200877934694f, 0.124579639413f, 0.045465113495f, 0.024616700720f, 0.022347768103f, 0.023765285472f, 0.066431062411f, 0.041429672783f, 0.039536276247f, 0.103609014133f, 0.057977068523f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in2_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in2_out2_grid,
    .spline_kernel = KAN_LUT_test_layer1_in2_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in2_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in2_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in2_out3_spline_kernel[] = { 0.018304267898f, 0.127545699477f, 0.020318999887f, 0.143169239163f, 0.000754029956f, 0.063242740929f, 0.018829772249f, 0.059161704034f, 0.000029887144f, 0.023140028119f };
const port_float KAN_LUT_test_layer1_in2_out3_lut[] = { 0.072924983688f, 0.082785735053f, 0.063210636993f, 0.100936902210f, 0.022822584439f, 0.050180407678f, 0.029603182030f, 0.047085779539f, 0.016527521647f, 0.015022335840f, 0.009561995091f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in2_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in2_out3_grid,
    .spline_kernel = KAN_LUT_test_layer1_in2_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in2_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in2_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in2_out4_spline_kernel[] = { 0.240066066384f, 0.047673694789f, 0.001616974245f, 0.023371731862f, 0.020845711231f, 0.000164520243f, 0.108858354390f, 0.050724465400f, 0.028598915786f, 0.226134493947f };
const port_float KAN_LUT_test_layer1_in2_out4_lut[] = { 0.143869880587f, 0.029437001885f, 0.009659793456f, 0.021894632115f, 0.016825206982f, 0.018470337615f, 0.086683456646f, 0.061032530551f, 0.041796665285f, 0.156279453423f, 0.093444005763f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in2_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in2_out4_grid,
    .spline_kernel = KAN_LUT_test_layer1_in2_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in2_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in2_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in2_out5_spline_kernel[] = { 0.174053564668f, 0.119905620813f, 0.056258916855f, 0.000021997565f, 0.023964788765f, 0.067061051726f, 0.000033501703f, 0.090107358992f, 0.254687607288f, 0.317058444023f };
const port_float KAN_LUT_test_layer1_in2_out5_lut[] = { 0.146979592741f, 0.093829081756f, 0.038487827406f, 0.008445431079f, 0.031107897136f, 0.052637917946f, 0.019309692749f, 0.082750602651f, 0.213481828940f, 0.290941619430f, 0.131015885960f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in2_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in2_out5_grid,
    .spline_kernel = KAN_LUT_test_layer1_in2_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in2_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in3_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in3_out0_spline_kernel[] = { 0.000036827871f, 0.008156903088f, 0.117605283856f, 0.042405761778f, 0.025028720498f, 0.120122365654f, 0.055220320821f, 0.008120833896f, 0.061488982290f, 0.000070841357f };
const port_float KAN_LUT_test_layer1_in3_out0_lut[] = { 0.004096865479f, 0.053349952682f, 0.090626131743f, 0.040606857054f, 0.045432114189f, 0.100643792336f, 0.060009520990f, 0.021185979490f, 0.045090946069f, 0.020626982060f, 0.000029273288f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in3_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in3_out0_grid,
    .spline_kernel = KAN_LUT_test_layer1_in3_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in3_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in3_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in3_out1_spline_kernel[] = { 0.198910430074f, 0.000166454134f, 0.022922074422f, 0.010010987520f, 0.194032117724f, 0.112042017281f, 0.000019093946f, 0.056943334639f, 0.264211982489f, 0.101214461029f };
const port_float KAN_LUT_test_layer1_in3_out1_lut[] = { 0.099538442104f, 0.010390859112f, 0.018224468967f, 0.059157897087f, 0.165264130100f, 0.103847501872f, 0.022564264431f, 0.059121064274f, 0.203335242177f, 0.154098516376f, 0.041824157450f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in3_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in3_out1_grid,
    .spline_kernel = KAN_LUT_test_layer1_in3_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in3_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in3_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in3_out2_spline_kernel[] = { 0.443477153778f, 0.066506341100f, 0.047149788588f, 0.119007453322f, 0.000027820837f, 0.000501929026f, 0.228557810187f, 0.213299423456f, 0.167791113257f, 0.424989312887f };
const port_float KAN_LUT_test_layer1_in3_out2_lut[] = { 0.254991747439f, 0.060065496313f, 0.071521264016f, 0.084869372902f, 0.007990239932f, 0.034378619179f, 0.193055862294f, 0.213380117616f, 0.189391591147f, 0.331877695443f, 0.175615418548f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in3_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in3_out2_grid,
    .spline_kernel = KAN_LUT_test_layer1_in3_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in3_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in3_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in3_out3_spline_kernel[] = { 0.252203673124f, 0.101157307625f, 0.285276323557f, 0.000006133368f, 0.197465136647f, 0.000014145006f, 0.081591270864f, 0.062762841582f, 0.119261987507f, 0.052962303162f };
const port_float KAN_LUT_test_layer1_in3_out3_lut[] = { 0.176680490375f, 0.177863704148f, 0.186750036495f, 0.062835918168f, 0.144430249693f, 0.032547414932f, 0.067510744984f, 0.070310690217f, 0.101854373878f, 0.074278109853f, 0.021885249240f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in3_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in3_out3_grid,
    .spline_kernel = KAN_LUT_test_layer1_in3_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in3_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in3_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in3_out4_spline_kernel[] = { 0.058664236218f, 0.015630034730f, 0.142314761877f, 0.000002108637f, 0.297796666622f, 0.000783265976f, 0.046552013606f, 0.006122641731f, 0.058449588716f, 0.000024639348f };
const port_float KAN_LUT_test_layer1_in3_out4_lut[] = { 0.037147135474f, 0.068156922813f, 0.092587225426f, 0.084050313555f, 0.217968693236f, 0.038275042549f, 0.035566851575f, 0.017768387077f, 0.042438228586f, 0.019579690346f, 0.000010181549f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in3_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in3_out4_grid,
    .spline_kernel = KAN_LUT_test_layer1_in3_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in3_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in3_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in3_out5_spline_kernel[] = { 0.011401686817f, 0.081069402397f, 0.070705011487f, 0.093171440065f, 0.000017148790f, 0.149059027433f, 0.000018909532f, 0.172365114093f, 0.207805544138f, 0.269743710756f };
const port_float KAN_LUT_test_layer1_in3_out5_lut[] = { 0.046235544607f, 0.076498713113f, 0.078396078753f, 0.067700066103f, 0.036354011244f, 0.111490881935f, 0.039994526716f, 0.139811737470f, 0.200736353959f, 0.244553767206f, 0.111464343288f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in3_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in3_out5_grid,
    .spline_kernel = KAN_LUT_test_layer1_in3_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in3_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in4_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in4_out0_spline_kernel[] = { 0.007955279201f, 0.061223696917f, 0.029625521973f, 0.104583099484f, 0.075555920601f, 0.006062048953f, 0.000026585667f, 0.000507119927f, 0.006726023741f, 0.045559622347f };
const port_float KAN_LUT_test_layer1_in4_out0_lut[] = { 0.034589488059f, 0.047946482404f, 0.055236912379f, 0.094118811690f, 0.063403999739f, 0.012343330411f, 0.000974065150f, 0.000820988862f, 0.006525579705f, 0.031808548064f, 0.018826290226f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in4_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in4_out0_grid,
    .spline_kernel = KAN_LUT_test_layer1_in4_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in4_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in4_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in4_out1_spline_kernel[] = { 0.006875536405f, 0.000279718428f, 0.119789190590f, 0.079566292465f, 0.031076997519f, 0.018871655688f, 0.013144200668f, 0.001373957726f, 0.001200802508f, 0.001543201855f };
const port_float KAN_LUT_test_layer1_in4_out1_lut[] = { 0.003577627416f, 0.049691053280f, 0.104350791265f, 0.068238570178f, 0.031811571772f, 0.019280520006f, 0.012780284582f, 0.003745740456f, 0.001259329483f, 0.001403089646f, 0.000637686717f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in4_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in4_out1_grid,
    .spline_kernel = KAN_LUT_test_layer1_in4_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in4_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in4_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in4_out2_spline_kernel[] = { 0.259416997433f, 0.049879483879f, 0.000498472713f, 0.048081390560f, 0.000012620802f, 0.177197083831f, 0.049243960530f, 0.196480706334f, 0.021487146616f, 0.010746194981f };
const port_float KAN_LUT_test_layer1_in4_out2_lut[] = { 0.154648240656f, 0.030339964858f, 0.017241201598f, 0.033599375993f, 0.039066914209f, 0.139858554845f, 0.083488717075f, 0.155098485260f, 0.067366978257f, 0.014163683834f, 0.004440576438f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in4_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in4_out2_grid,
    .spline_kernel = KAN_LUT_test_layer1_in4_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in4_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in4_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in4_out3_spline_kernel[] = { 0.369099706411f, 0.070493116975f, 0.029040500522f, 0.131205856800f, 0.045858014375f, 0.059656731784f, 0.033800307661f, 0.095270372927f, 0.127046987414f, 0.243475541472f };
const port_float KAN_LUT_test_layer1_in4_out3_lut[] = { 0.219796411693f, 0.054597848149f, 0.063921510126f, 0.104834988529f, 0.054294802110f, 0.054384834249f, 0.043996931215f, 0.084924887943f, 0.122973242205f, 0.200481264429f, 0.100609727881f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in4_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in4_out3_grid,
    .spline_kernel = KAN_LUT_test_layer1_in4_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in4_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in4_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in4_out4_spline_kernel[] = { 0.068668402731f, 0.105664506555f, 0.158963218331f, 0.204399466515f, 0.234570398927f, 0.084843732417f, 0.057380266488f, 0.000241753311f, 0.009628729895f, 0.010207585059f };
const port_float KAN_LUT_test_layer1_in4_out4_lut[] = { 0.087166454643f, 0.127535891157f, 0.173290248314f, 0.210688778253f, 0.202259070094f, 0.096225888984f, 0.055563001793f, 0.012431748232f, 0.007167751362f, 0.009845115602f, 0.004218010355f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in4_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in4_out4_grid,
    .spline_kernel = KAN_LUT_test_layer1_in4_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in4_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in4_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in4_out5_spline_kernel[] = { 0.000023288681f, 0.173757642508f, 0.000035102439f, 0.021232090890f, 0.186214461923f, 0.136766478419f, 0.101545296609f, 0.000007506043f, 0.015160313807f, 0.273236244917f };
const port_float KAN_LUT_test_layer1_in4_out5_lut[] = { 0.086890465594f, 0.101253558373f, 0.010001409153f, 0.064075474568f, 0.165294341558f, 0.136635226529f, 0.096295370085f, 0.021568649274f, 0.020750824894f, 0.182339156489f, 0.112907539222f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in4_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in4_out5_grid,
    .spline_kernel = KAN_LUT_test_layer1_in4_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in4_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in5_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in5_out0_spline_kernel[] = { 0.042455684394f, 0.093006938696f, 0.075616009533f, 0.448770344257f, 0.045312527567f, 0.000025170175f, 0.145308658481f, 0.848580360413f, 0.148616358638f, 0.026701852679f };
const port_float KAN_LUT_test_layer1_in5_out0_lut[] = { 0.067731311545f, 0.085611714851f, 0.200802227836f, 0.328193115825f, 0.062817670356f, 0.026316035934f, 0.196348274056f, 0.659903759491f, 0.329196794836f, 0.067066594712f, 0.011033823421f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in5_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in5_out0_grid,
    .spline_kernel = KAN_LUT_test_layer1_in5_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in5_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in5_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in5_out1_spline_kernel[] = { 0.307005405426f, 0.229760751128f, 0.325304895639f, 0.163709893823f, 0.001431428245f, 0.000022924360f, 0.148229196668f, 0.428851038218f, 0.046324457973f, 0.003709830809f };
const port_float KAN_LUT_test_layer1_in5_out1_lut[] = { 0.268383078277f, 0.269560995365f, 0.269638070329f, 0.126803006300f, 0.011875390059f, 0.022215645022f, 0.155171842270f, 0.346739899706f, 0.145903670747f, 0.017912084847f, 0.001532987938f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in5_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in5_out1_grid,
    .spline_kernel = KAN_LUT_test_layer1_in5_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in5_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in5_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in5_out2_spline_kernel[] = { 0.294246792793f, 0.162657797337f, 0.002791610314f, 0.003203096800f, 0.112521320581f, 0.230661556125f, 0.000008599308f, 0.042040564120f, 0.006762233097f, 0.171889305115f };
const port_float KAN_LUT_test_layer1_in5_out2_lut[] = { 0.228452295065f, 0.097141145655f, 0.005571755576f, 0.032098398220f, 0.129214626206f, 0.184144976232f, 0.038662754538f, 0.031197508037f, 0.022233129104f, 0.113778354479f, 0.071028638477f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in5_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in5_out2_grid,
    .spline_kernel = KAN_LUT_test_layer1_in5_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in5_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in5_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in5_out3_spline_kernel[] = { 0.000029121456f, 0.000025852274f, 0.077454566956f, 0.069407358766f, 0.011863417923f, 0.161775290966f, 0.005678341258f, 0.000912985299f, 0.131465673447f, 0.186258420348f };
const port_float KAN_LUT_test_layer1_in5_out3_lut[] = { 0.000027486865f, 0.032021202428f, 0.073481266451f, 0.054488402814f, 0.046022032934f, 0.123067493381f, 0.028407086260f, 0.010509454110f, 0.098977089482f, 0.164840047702f, 0.076966289400f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in5_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in5_out3_grid,
    .spline_kernel = KAN_LUT_test_layer1_in5_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in5_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in5_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in5_out4_spline_kernel[] = { 0.046448875219f, 0.181012302637f, 0.294077426195f, 0.006239198148f, 0.000860276923f, 0.000032814052f, 0.105686120689f, 0.067174218595f, 0.021666018292f, 0.013731176965f };
const port_float KAN_LUT_test_layer1_in5_out4_lut[] = { 0.113730588928f, 0.227177380854f, 0.195866033774f, 0.015521401016f, 0.001048363943f, 0.015835316576f, 0.085990597585f, 0.071963276437f, 0.033406147414f, 0.016160092005f, 0.005674040068f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in5_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in5_out4_grid,
    .spline_kernel = KAN_LUT_test_layer1_in5_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in5_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer1_in5_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer1_in5_out5_spline_kernel[] = { 0.007065725513f, 0.150454580784f, 0.133387923241f, 0.000010396145f, 0.129494830966f, 0.000020276293f, 0.014542307705f, 0.000019612979f, 0.035968068987f, 0.061224710196f };
const port_float KAN_LUT_test_layer1_in5_out5_lut[] = { 0.078760153148f, 0.142809727025f, 0.089027125453f, 0.039214534874f, 0.094717954370f, 0.015556049011f, 0.010881727130f, 0.005336916027f, 0.027400335873f, 0.051759062350f, 0.025299467023f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer1_in5_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer1_in5_out5_grid,
    .spline_kernel = KAN_LUT_test_layer1_in5_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer1_in5_out5_lut
};
    
const KAN_LUT *KAN_LUTs_test_layer1[] = {
    &KAN_LUT_test_layer1_in0_out0, &KAN_LUT_test_layer1_in0_out1, &KAN_LUT_test_layer1_in0_out2, &KAN_LUT_test_layer1_in0_out3, &KAN_LUT_test_layer1_in0_out4, &KAN_LUT_test_layer1_in0_out5,
    &KAN_LUT_test_layer1_in1_out0, &KAN_LUT_test_layer1_in1_out1, &KAN_LUT_test_layer1_in1_out2, &KAN_LUT_test_layer1_in1_out3, &KAN_LUT_test_layer1_in1_out4, &KAN_LUT_test_layer1_in1_out5,
    &KAN_LUT_test_layer1_in2_out0, &KAN_LUT_test_layer1_in2_out1, &KAN_LUT_test_layer1_in2_out2, &KAN_LUT_test_layer1_in2_out3, &KAN_LUT_test_layer1_in2_out4, &KAN_LUT_test_layer1_in2_out5,
    &KAN_LUT_test_layer1_in3_out0, &KAN_LUT_test_layer1_in3_out1, &KAN_LUT_test_layer1_in3_out2, &KAN_LUT_test_layer1_in3_out3, &KAN_LUT_test_layer1_in3_out4, &KAN_LUT_test_layer1_in3_out5,
    &KAN_LUT_test_layer1_in4_out0, &KAN_LUT_test_layer1_in4_out1, &KAN_LUT_test_layer1_in4_out2, &KAN_LUT_test_layer1_in4_out3, &KAN_LUT_test_layer1_in4_out4, &KAN_LUT_test_layer1_in4_out5,
    &KAN_LUT_test_layer1_in5_out0, &KAN_LUT_test_layer1_in5_out1, &KAN_LUT_test_layer1_in5_out2, &KAN_LUT_test_layer1_in5_out3, &KAN_LUT_test_layer1_in5_out4, &KAN_LUT_test_layer1_in5_out5,
};


const LayerKAN_LUT LayerKAN_LUT_test_layer1 = {
    .in_size = 6,
    .out_size = 6,
    .spline_kernel_size = 10,
    .kan_luts = KAN_LUTs_test_layer1
};


// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in0_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in0_out0_spline_kernel[] = { 0.000032353077f, 0.000019110070f, 0.126736789942f, 0.034767795354f, 0.242458075285f, 0.003976884298f, 0.037463508546f, 0.089998014271f, 0.034067180008f, 0.546324014664f };
const port_float KAN_LUT_test_layer2_in0_out0_lut[] = { 0.000025731573f, 0.052381842426f, 0.093859272251f, 0.093114484887f, 0.180438972652f, 0.033594852263f, 0.037909145613f, 0.075662955888f, 0.067909679614f, 0.365835999516f, 0.225753725068f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in0_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in0_out0_grid,
    .spline_kernel = KAN_LUT_test_layer2_in0_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in0_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in0_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in0_out1_spline_kernel[] = { 0.016200415790f, 0.028455337510f, 0.027169505134f, 0.021449865773f, 0.102363213897f, 0.101469032466f, 0.186641752720f, 0.234902143478f, 0.334349393845f, 0.775975644588f };
const port_float KAN_LUT_test_layer2_in0_out1_lut[] = { 0.022327876650f, 0.027873361645f, 0.025276333817f, 0.043061151038f, 0.096832517781f, 0.114231728602f, 0.178957008256f, 0.231705436283f, 0.324473411337f, 0.615332550007f, 0.320651092805f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in0_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in0_out1_grid,
    .spline_kernel = KAN_LUT_test_layer2_in0_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in0_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in0_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in0_out2_spline_kernel[] = { 0.023728648201f, 0.006783537567f, 0.175249680877f, 0.134398952127f, 0.000004006679f, 0.086732141674f, 0.047383736819f, 0.162837430835f, 0.028166219592f, 0.313302874565f };
const port_float KAN_LUT_test_layer2_in0_out2_lut[] = { 0.015256092884f, 0.076467667491f, 0.158791938720f, 0.100375729193f, 0.026450278340f, 0.071919141882f, 0.065164253039f, 0.130556561468f, 0.074386002296f, 0.212686012784f, 0.129463997754f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in0_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in0_out2_grid,
    .spline_kernel = KAN_LUT_test_layer2_in0_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in0_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in0_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in0_out3_spline_kernel[] = { 0.088923439384f, 0.167949467897f, 0.113965041935f, 0.074972942472f, 0.077097959816f, 0.037062801421f, 0.024211734533f, 0.109743118286f, 0.142315819860f, 0.234172940254f };
const port_float KAN_LUT_test_layer2_in0_out3_lut[] = { 0.128436453640f, 0.145315300027f, 0.101806271883f, 0.076985049931f, 0.068851170399f, 0.039286935933f, 0.034959350243f, 0.094578347300f, 0.137117725574f, 0.199556748052f, 0.096765677791f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in0_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in0_out3_grid,
    .spline_kernel = KAN_LUT_test_layer2_in0_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in0_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in0_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in0_out4_spline_kernel[] = { 0.346257597208f, 0.366498917341f, 0.270346194506f, 0.015785461292f, 0.000002856209f, 0.025140000507f, 0.127945914865f, 0.020243642852f, 0.252739489079f, 1.275805592537f };
const port_float KAN_LUT_test_layer2_in0_out4_lut[] = { 0.356378257275f, 0.326682745425f, 0.186731283353f, 0.021078683910f, 0.006136086589f, 0.037836629885f, 0.101526205289f, 0.057422753878f, 0.229300897230f, 0.912286680346f, 0.527192393610f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in0_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in0_out4_grid,
    .spline_kernel = KAN_LUT_test_layer2_in0_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in0_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in0_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in0_out5_spline_kernel[] = { 0.002411497291f, 0.311850309372f, 0.206329256296f, 0.005914543755f, 0.000017689021f, 0.193727895617f, 0.031060185283f, 0.087215781212f, 0.093279518187f, 0.000005497405f };
const port_float KAN_LUT_test_layer2_in0_out5_lut[] = { 0.157130903332f, 0.266967895654f, 0.140992448430f, 0.011808484705f, 0.039629878273f, 0.149518008275f, 0.061059885574f, 0.076246341506f, 0.088207016727f, 0.031225223412f, 0.000002271655f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in0_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in0_out5_grid,
    .spline_kernel = KAN_LUT_test_layer2_in0_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in0_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in1_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in1_out0_spline_kernel[] = { 0.351361840963f, 0.126051276922f, 0.117638975382f, 0.131333872676f, 0.012131003663f, 0.008317815140f, 0.017577452585f, 0.084774956107f, 0.033416721970f, 0.000003925466f };
const port_float KAN_LUT_test_layer2_in1_out0_lut[] = { 0.238706558943f, 0.123506154650f, 0.122361850948f, 0.099299832624f, 0.019240093194f, 0.010089206301f, 0.023141876717f, 0.067773264294f, 0.045756440219f, 0.011187482553f, 0.000001622094f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in1_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in1_out0_grid,
    .spline_kernel = KAN_LUT_test_layer2_in1_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in1_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in1_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in1_out1_spline_kernel[] = { 0.235250890255f, 0.232080817223f, 0.153777435422f, 0.030965896323f, 0.010254534893f, 0.000030655916f, 0.126622900367f, 0.135811284184f, 0.347181856632f, 0.232029691339f };
const port_float KAN_LUT_test_layer2_in1_out1_lut[] = { 0.233665853739f, 0.199737147359f, 0.113965364596f, 0.030055882771f, 0.009553756847f, 0.019918745894f, 0.108740209438f, 0.147925740185f, 0.286999682565f, 0.266737156725f, 0.095880037743f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in1_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in1_out1_grid,
    .spline_kernel = KAN_LUT_test_layer2_in1_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in1_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in1_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in1_out2_spline_kernel[] = { 0.186955451965f, 0.014730500989f, 0.237357348204f, 0.069357812405f, 0.000014899355f, 0.058831997216f, 0.042824123055f, 0.082653366029f, 0.087380193174f, 0.205637440085f };
const port_float KAN_LUT_test_layer2_in1_out2_lut[] = { 0.100842976477f, 0.107436739305f, 0.177446316019f, 0.057267107392f, 0.016508801851f, 0.050374514090f, 0.049320050923f, 0.074901284742f, 0.090528119971f, 0.162656503060f, 0.084974148796f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in1_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in1_out2_grid,
    .spline_kernel = KAN_LUT_test_layer2_in1_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in1_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in1_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in1_out3_spline_kernel[] = { 0.043292410672f, 0.057580281049f, 0.107688628137f, 0.000037973386f, 0.083247654140f, 0.065724484622f, 0.303076595068f, 0.235612466931f, 0.500313222408f, 0.081023588777f };
const port_float KAN_LUT_test_layer2_in1_out3_lut[] = { 0.050436345860f, 0.078227168811f, 0.070828560273f, 0.026047376118f, 0.074198107866f, 0.102843307821f, 0.260798581930f, 0.266773435387f, 0.414716300701f, 0.220025101045f, 0.033480821809f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in1_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in1_out3_grid,
    .spline_kernel = KAN_LUT_test_layer2_in1_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in1_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in1_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in1_out4_spline_kernel[] = { 0.134954586625f, 0.141246184707f, 0.040978714824f, 0.003065352095f, 0.019621269777f, 0.119370482862f, 0.155710071325f, 0.186713382602f, 0.237372085452f, 0.106489203870f };
const port_float KAN_LUT_test_layer2_in1_out4_lut[] = { 0.138100385666f, 0.099787347573f, 0.029946018537f, 0.008853777699f, 0.038723818365f, 0.114471701282f, 0.153507003545f, 0.183785188358f, 0.219107197367f, 0.148536958385f, 0.044003803252f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in1_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in1_out4_grid,
    .spline_kernel = KAN_LUT_test_layer2_in1_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in1_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in1_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in1_out5_spline_kernel[] = { 0.290975332260f, 0.000081298043f, 0.002853235463f, 0.051991142333f, 0.147371277213f, 0.001295811962f, 0.000041043349f, 0.029618490487f, 0.220505729318f, 0.190098911524f };
const port_float KAN_LUT_test_layer2_in1_out5_lut[] = { 0.145528315152f, 0.002428768193f, 0.019254403673f, 0.075388197996f, 0.111487888968f, 0.016199592794f, 0.003283224542f, 0.036250312436f, 0.168892321693f, 0.197134269355f, 0.078553269225f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in1_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in1_out5_grid,
    .spline_kernel = KAN_LUT_test_layer2_in1_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in1_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in2_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in2_out0_spline_kernel[] = { 0.106622785330f, 0.199608698487f, 0.177373573184f, 0.050786383450f, 0.047653593123f, 0.016706999391f, 0.142918527126f, 0.200722679496f, 0.278200924397f, 0.232000187039f };
const port_float KAN_LUT_test_layer2_in2_out0_lut[] = { 0.153115741909f, 0.190036390870f, 0.135371003485f, 0.054665664965f, 0.041594673918f, 0.038679230142f, 0.130114761882f, 0.194141061530f, 0.255992600802f, 0.243629356369f, 0.095867845884f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in2_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in2_out0_grid,
    .spline_kernel = KAN_LUT_test_layer2_in2_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in2_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in2_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in2_out1_spline_kernel[] = { 0.055758669972f, 0.065708622336f, 0.073009535670f, 0.000024076593f, 0.108497068286f, 0.186267614365f, 0.120597817004f, 0.194766357541f, 0.230347782373f, 0.240035012364f };
const port_float KAN_LUT_test_layer2_in2_out1_lut[] = { 0.060733646154f, 0.068684413167f, 0.048459842122f, 0.031425484031f, 0.117072228992f, 0.168464406278f, 0.138028917080f, 0.182101251388f, 0.221298087665f, 0.232825071543f, 0.099188021638f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in2_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in2_out1_grid,
    .spline_kernel = KAN_LUT_test_layer2_in2_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in2_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in2_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in2_out2_spline_kernel[] = { 0.115385234356f, 0.036414962262f, 0.000003171429f, 0.190134555101f, 0.069229595363f, 0.080275505781f, 0.078583918512f, 0.109404563904f, 0.259260535240f, 0.028429413214f };
const port_float KAN_LUT_test_layer2_in2_out2_lut[] = { 0.075900098309f, 0.021695091141f, 0.064244036060f, 0.151088687844f, 0.079459880348f, 0.078882758252f, 0.082019510563f, 0.113071852818f, 0.211044575473f, 0.105221162104f, 0.011747691411f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in2_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in2_out2_grid,
    .spline_kernel = KAN_LUT_test_layer2_in2_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in2_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in2_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in2_out3_spline_kernel[] = { 0.082069300115f, 0.018583081663f, 0.097537808120f, 0.254563570023f, 0.002928579459f, 0.000008594727f, 0.055696357042f, 0.166006863117f, 0.113575778902f, 0.035456389189f };
const port_float KAN_LUT_test_layer2_in2_out3_lut[] = { 0.050326190889f, 0.051471341432f, 0.148790980882f, 0.182175672282f, 0.018974367050f, 0.008594375973f, 0.058807940548f, 0.140204746815f, 0.124536584201f, 0.061017732205f, 0.014651400491f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in2_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in2_out3_grid,
    .spline_kernel = KAN_LUT_test_layer2_in2_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in2_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in2_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in2_out4_spline_kernel[] = { 0.000044776545f, 0.130172386765f, 0.165786430240f, 0.000031592095f, 0.045369908214f, 0.359814137220f, 0.264120042324f, 0.128145858645f, 0.117459878325f, 0.000006657749f };
const port_float KAN_LUT_test_layer2_in2_out4_lut[] = { 0.065108581655f, 0.144351216258f, 0.109717843200f, 0.018186326702f, 0.106040793186f, 0.313094744074f, 0.264308607714f, 0.154971310361f, 0.115917827727f, 0.039319402524f, 0.000002751136f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in2_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in2_out4_grid,
    .spline_kernel = KAN_LUT_test_layer2_in2_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in2_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in2_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in2_out5_spline_kernel[] = { 0.024935668334f, 0.000586442649f, 0.001207924564f, 0.057008337229f, 0.019394472241f, 0.047983456403f, 0.013835826889f, 0.000015689686f, 0.000019060672f, 0.039622202516f };
const port_float KAN_LUT_test_layer2_in2_out5_lut[] = { 0.012761055492f, 0.000943869993f, 0.019874649764f, 0.044985646844f, 0.027670017959f, 0.039950236293f, 0.017487939419f, 0.002814204804f, 0.001491013289f, 0.025711693014f, 0.016372810957f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in2_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in2_out5_grid,
    .spline_kernel = KAN_LUT_test_layer2_in2_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in2_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in3_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in3_out0_spline_kernel[] = { 0.242232054472f, 0.155196949840f, 0.000011036911f, 0.061029389501f, 0.072659596801f, 0.148603245616f, 0.092686131597f, 0.532553672791f, 0.211392536759f, 0.050087150186f };
const port_float KAN_LUT_test_layer2_in3_out0_lut[] = { 0.198714502156f, 0.091430188731f, 0.022999591504f, 0.061835869228f, 0.087267677277f, 0.132439578983f, 0.146445241657f, 0.422255789753f, 0.290328752573f, 0.103249909325f, 0.020697169498f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in3_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in3_out0_grid,
    .spline_kernel = KAN_LUT_test_layer2_in3_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in3_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in3_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in3_out1_spline_kernel[] = { 0.035709831864f, 0.000020414867f, 0.009487645701f, 0.142830938101f, 0.022167429328f, 0.001687431708f, 0.001340821967f, 0.041016183794f, 0.038159381598f, 0.061061020941f };
const port_float KAN_LUT_test_layer2_in3_out1_lut[] = { 0.017865123365f, 0.004079970654f, 0.053962595127f, 0.105960879452f, 0.025998405597f, 0.003751572162f, 0.005491078151f, 0.032793863279f, 0.039766613394f, 0.052386323129f, 0.025231826835f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in3_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in3_out1_grid,
    .spline_kernel = KAN_LUT_test_layer2_in3_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in3_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in3_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in3_out2_spline_kernel[] = { 0.043460831046f, 0.051913090050f, 0.000010162584f, 0.045015081763f, 0.063572026789f, 0.033649157733f, 0.039623305202f, 0.069886900485f, 0.127606227994f, 0.001664472162f };
const port_float KAN_LUT_test_layer2_in3_out2_lut[] = { 0.047686960548f, 0.030430672671f, 0.015931692185f, 0.048248966925f, 0.056286358590f, 0.037629079366f, 0.041860993521f, 0.067575301606f, 0.107657828146f, 0.043791018996f, 0.000687798414f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in3_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in3_out2_grid,
    .spline_kernel = KAN_LUT_test_layer2_in3_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in3_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in3_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in3_out3_spline_kernel[] = { 0.001989631215f, 0.077040411532f, 0.000021705018f, 0.075810134411f, 0.104832343757f, 0.062399432063f, 0.045481815934f, 0.131282418966f, 0.316287517548f, 0.066275618970f };
const port_float KAN_LUT_test_layer2_in3_out3_lut[] = { 0.039515021374f, 0.044904372558f, 0.026661943063f, 0.080666851492f, 0.094321732094f, 0.064266327153f, 0.056862184762f, 0.126141311647f, 0.258062586158f, 0.148861822726f, 0.027386619409f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in3_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in3_out3_grid,
    .spline_kernel = KAN_LUT_test_layer2_in3_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in3_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in3_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in3_out4_spline_kernel[] = { 0.000006471176f, 0.169403493404f, 0.003147242358f, 0.092465750873f, 0.161706924438f, 0.068243816495f, 0.001244783634f, 0.193947508931f, 0.288571655750f, 0.010077428073f };
const port_float KAN_LUT_test_layer2_in3_out4_lut[] = { 0.084704982290f, 0.100002575525f, 0.035791143986f, 0.107455703483f, 0.138204647305f, 0.067932297964f, 0.031118888243f, 0.161185330458f, 0.253189864653f, 0.103125869104f, 0.004164226476f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in3_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in3_out4_grid,
    .spline_kernel = KAN_LUT_test_layer2_in3_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in3_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in3_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in3_out5_spline_kernel[] = { 0.053996328264f, 0.013776565902f, 0.043174896389f, 0.000012834721f, 0.128313660622f, 0.006016844884f, 0.003361449810f, 0.050361033529f, 0.548458993435f, 0.191486865282f };
const port_float KAN_LUT_test_layer2_in3_out5_lut[] = { 0.033886447083f, 0.026090833716f, 0.028242167806f, 0.035548832294f, 0.095068382995f, 0.018255796003f, 0.008611796155f, 0.073776685414f, 0.403454784396f, 0.307804199659f, 0.079126803836f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in3_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in3_out5_grid,
    .spline_kernel = KAN_LUT_test_layer2_in3_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in3_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in4_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in4_out0_spline_kernel[] = { 0.078269466758f, 0.229353293777f, 0.109664998949f, 0.090434461832f, 0.000025002964f, 0.048630662262f, 0.064307935536f, 0.007714056876f, 0.021745039150f, 0.020858258009f };
const port_float KAN_LUT_test_layer2_in4_out0_lut[] = { 0.153811380267f, 0.179271007372f, 0.105206650489f, 0.067239707561f, 0.015844129607f, 0.045941572822f, 0.056129304113f, 0.020100816259f, 0.018001386688f, 0.020810308589f, 0.008619114880f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in4_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in4_out0_grid,
    .spline_kernel = KAN_LUT_test_layer2_in4_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in4_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in4_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in4_out1_spline_kernel[] = { 0.000002836370f, 0.000007076801f, 0.000007158293f, 0.081761099398f, 0.005602278281f, 0.022929318249f, 0.111327588558f, 0.134120136499f, 0.113569289446f, 0.147097840905f };
const port_float KAN_LUT_test_layer2_in4_out1_lut[] = { 0.000004956585f, 0.000007092953f, 0.027371079382f, 0.058579487739f, 0.014145939836f, 0.034289490695f, 0.100532034705f, 0.128146382772f, 0.120251153804f, 0.133444105236f, 0.060784231779f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in4_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in4_out1_grid,
    .spline_kernel = KAN_LUT_test_layer2_in4_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in4_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in4_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in4_out2_spline_kernel[] = { 0.159227147698f, 0.019777765498f, 0.000011332988f, 0.015434393659f, 0.193433597684f, 0.191412389278f, 0.212917298079f, 0.213929399848f, 0.309283941984f, 0.100788928568f };
const port_float KAN_LUT_test_layer2_in4_out2_lut[] = { 0.089502456598f, 0.012186055296f, 0.005500314990f, 0.061934978418f, 0.181255802327f, 0.194820269142f, 0.209822776704f, 0.220028902689f, 0.276312265053f, 0.168908516884f, 0.041648317590f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in4_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in4_out2_grid,
    .spline_kernel = KAN_LUT_test_layer2_in4_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in4_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in4_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in4_out3_spline_kernel[] = { 0.506561636925f, 0.122192159295f, 0.128390133381f, 0.174229994416f, 0.000002320923f, 0.057804025710f, 0.037285998464f, 0.101993165910f, 0.001121500158f, 0.089381694794f };
const port_float KAN_LUT_test_layer2_in4_out3_lut[] = { 0.314376898110f, 0.126341609238f, 0.143630781511f, 0.126448466099f, 0.023225156917f, 0.048780506699f, 0.047022891716f, 0.082222100386f, 0.031080708256f, 0.058362676014f, 0.036934584625f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in4_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in4_out3_grid,
    .spline_kernel = KAN_LUT_test_layer2_in4_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in4_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in4_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in4_out4_spline_kernel[] = { 0.000099835903f, 0.058680441231f, 0.124913841486f, 0.032008368522f, 0.063575163484f, 0.000573958270f, 0.061831843108f, 0.009517484345f, 0.070234544575f, 0.066971659660f };
const port_float KAN_LUT_test_layer2_in4_out4_lut[] = { 0.029390138567f, 0.085807546273f, 0.092722614581f, 0.043811774035f, 0.048731660282f, 0.016195090438f, 0.047314724004f, 0.024124412209f, 0.054055793257f, 0.066956812716f, 0.027674239529f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in4_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in4_out4_grid,
    .spline_kernel = KAN_LUT_test_layer2_in4_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in4_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in4_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in4_out5_spline_kernel[] = { 0.243318796158f, 0.034473553300f, 0.000014370756f, 0.040895070881f, 0.075464338064f, 0.000050355859f, 0.109438382089f, 0.074589207768f, 0.000057810954f, 0.085777811706f };
const port_float KAN_LUT_test_layer2_in4_out5_lut[] = { 0.138896174729f, 0.021097218541f, 0.014267153567f, 0.048516999801f, 0.057908993424f, 0.024113655443f, 0.089565661832f, 0.076717749887f, 0.022956527495f, 0.055668591426f, 0.035445376738f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in4_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in4_out5_grid,
    .spline_kernel = KAN_LUT_test_layer2_in4_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in4_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in5_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in5_out0_spline_kernel[] = { 0.026426127180f, 0.002056572121f, 0.000010798706f, 0.082184575498f, 0.148507177830f, 0.144152641296f, 0.241570517421f, 0.246983647346f, 0.221887260675f, 0.259670168161f };
const port_float KAN_LUT_test_layer2_in5_out0_lut[] = { 0.014241349651f, 0.001311911846f, 0.027549059094f, 0.096668387722f, 0.143240508708f, 0.159094405568f, 0.227637809601f, 0.244228335144f, 0.229929471065f, 0.242731754199f, 0.107301722381f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in5_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in5_out0_grid,
    .spline_kernel = KAN_LUT_test_layer2_in5_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in5_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in5_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in5_out1_spline_kernel[] = { 0.046822104603f, 0.097906574607f, 0.050833027810f, 0.040961530060f, 0.082141064107f, 0.024840723723f, 0.097048483789f, 0.117801927030f, 0.088080927730f, 0.123504303396f };
const port_float KAN_LUT_test_layer2_in5_out1_lut[] = { 0.072364339605f, 0.078243602914f, 0.048307006609f, 0.052219107162f, 0.067816315250f, 0.041501830632f, 0.088450784279f, 0.111634758817f, 0.097258424987f, 0.109606325534f, 0.051034836114f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in5_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in5_out1_grid,
    .spline_kernel = KAN_LUT_test_layer2_in5_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in5_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in5_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in5_out2_spline_kernel[] = { 0.004836546257f, 0.106566131115f, 0.000010546282f, 0.000017088476f, 0.142585530877f, 0.129140257835f, 0.131727457047f, 0.237689524889f, 0.302749007940f, 0.242866054177f };
const port_float KAN_LUT_test_layer2_in5_out2_lut[] = { 0.055701338686f, 0.062114527528f, 0.001773985361f, 0.037720896054f, 0.130437128160f, 0.130914104933f, 0.142289079048f, 0.220535848875f, 0.283316142241f, 0.258895207227f, 0.100357873627f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in5_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in5_out2_grid,
    .spline_kernel = KAN_LUT_test_layer2_in5_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in5_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in5_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in5_out3_spline_kernel[] = { 0.129991501570f, 0.000000929729f, 0.083860717714f, 0.014811873436f, 0.135456025600f, 0.061120275408f, 0.000000959363f, 0.003814022988f, 0.027543172240f, 0.132954806089f };
const port_float KAN_LUT_test_layer2_in5_out3_lut[] = { 0.064996215649f, 0.035190885805f, 0.059363215489f, 0.049285697143f, 0.112428099179f, 0.059707458785f, 0.009487000554f, 0.004610825758f, 0.025187962127f, 0.095474799618f, 0.054940002516f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in5_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in5_out3_grid,
    .spline_kernel = KAN_LUT_test_layer2_in5_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in5_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in5_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in5_out4_spline_kernel[] = { 0.098086431623f, 0.198167696595f, 0.224219620228f, 0.024693094194f, 0.000009075248f, 0.077090993524f, 0.057434987277f, 0.253106921911f, 0.218168735504f, 0.098347373307f };
const port_float KAN_LUT_test_layer2_in5_out4_lut[] = { 0.148127064109f, 0.208519395348f, 0.157005337983f, 0.025585497177f, 0.017248572350f, 0.066203951450f, 0.080573064098f, 0.211177435219f, 0.222952420092f, 0.136827294153f, 0.040639410457f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in5_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in5_out4_grid,
    .spline_kernel = KAN_LUT_test_layer2_in5_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in5_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer2_in5_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer2_in5_out5_spline_kernel[] = { 0.109540134668f, 0.074584081769f, 0.000006705453f, 0.030977115035f, 0.041065901518f, 0.041940391064f, 0.081454560161f, 0.005383103155f, 0.046852368861f, 0.089072339237f };
const port_float KAN_LUT_test_layer2_in5_out5_lut[] = { 0.092062108219f, 0.043911430617f, 0.011605518186f, 0.032493431765f, 0.040575940377f, 0.047728192092f, 0.067717797712f, 0.023527771108f, 0.037455454515f, 0.073468591479f, 0.036806751751f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer2_in5_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer2_in5_out5_grid,
    .spline_kernel = KAN_LUT_test_layer2_in5_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer2_in5_out5_lut
};
    
const KAN_LUT *KAN_LUTs_test_layer2[] = {
    &KAN_LUT_test_layer2_in0_out0, &KAN_LUT_test_layer2_in0_out1, &KAN_LUT_test_layer2_in0_out2, &KAN_LUT_test_layer2_in0_out3, &KAN_LUT_test_layer2_in0_out4, &KAN_LUT_test_layer2_in0_out5,
    &KAN_LUT_test_layer2_in1_out0, &KAN_LUT_test_layer2_in1_out1, &KAN_LUT_test_layer2_in1_out2, &KAN_LUT_test_layer2_in1_out3, &KAN_LUT_test_layer2_in1_out4, &KAN_LUT_test_layer2_in1_out5,
    &KAN_LUT_test_layer2_in2_out0, &KAN_LUT_test_layer2_in2_out1, &KAN_LUT_test_layer2_in2_out2, &KAN_LUT_test_layer2_in2_out3, &KAN_LUT_test_layer2_in2_out4, &KAN_LUT_test_layer2_in2_out5,
    &KAN_LUT_test_layer2_in3_out0, &KAN_LUT_test_layer2_in3_out1, &KAN_LUT_test_layer2_in3_out2, &KAN_LUT_test_layer2_in3_out3, &KAN_LUT_test_layer2_in3_out4, &KAN_LUT_test_layer2_in3_out5,
    &KAN_LUT_test_layer2_in4_out0, &KAN_LUT_test_layer2_in4_out1, &KAN_LUT_test_layer2_in4_out2, &KAN_LUT_test_layer2_in4_out3, &KAN_LUT_test_layer2_in4_out4, &KAN_LUT_test_layer2_in4_out5,
    &KAN_LUT_test_layer2_in5_out0, &KAN_LUT_test_layer2_in5_out1, &KAN_LUT_test_layer2_in5_out2, &KAN_LUT_test_layer2_in5_out3, &KAN_LUT_test_layer2_in5_out4, &KAN_LUT_test_layer2_in5_out5,
};


const LayerKAN_LUT LayerKAN_LUT_test_layer2 = {
    .in_size = 6,
    .out_size = 6,
    .spline_kernel_size = 10,
    .kan_luts = KAN_LUTs_test_layer2
};


// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in0_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in0_out0_spline_kernel[] = { 0.061199806631f, 0.000050088784f, 0.044547244906f, 0.000042663283f, 0.182379513979f, 0.012967601418f, 0.151685312390f, 0.242683976889f, 0.367726266384f, 0.432136893272f };
const port_float KAN_LUT_test_layer3_in0_out0_lut[] = { 0.030624947707f, 0.018690028164f, 0.028915593105f, 0.049919108238f, 0.136021772960f, 0.051104524596f, 0.140450308330f, 0.232525886275f, 0.337052667683f, 0.403435205871f, 0.178568964162f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in0_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in0_out0_grid,
    .spline_kernel = KAN_LUT_test_layer3_in0_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in0_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in0_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in0_out1_spline_kernel[] = { 0.509814620018f, 0.561812758446f, 0.116156712174f, 0.000006335482f, 0.015827422962f, 0.032253682613f, 0.038748964667f, 0.248069137335f, 0.216088339686f, 0.149512708187f };
const port_float KAN_LUT_test_layer3_in0_out1_lut[] = { 0.535813689232f, 0.377442499084f, 0.084646148840f, 0.008510066841f, 0.018107378843f, 0.031522995269f, 0.059406709141f, 0.203571694264f, 0.222070118058f, 0.169325002892f, 0.061782110821f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in0_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in0_out1_grid,
    .spline_kernel = KAN_LUT_test_layer3_in0_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in0_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in0_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in0_out2_spline_kernel[] = { 0.354743421078f, 0.198975071311f, 0.084589913487f, 0.127632200718f, 0.047156170011f, 0.173853859305f, 0.000039369108f, 0.063297182322f, 0.183510795236f, 0.348214149475f };
const port_float KAN_LUT_test_layer3_in0_out2_lut[] = { 0.276859246194f, 0.152352148036f, 0.100887293227f, 0.104748537287f, 0.078130563675f, 0.134908554018f, 0.032430968188f, 0.058436789591f, 0.157844096730f, 0.287330561495f, 0.143890144411f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in0_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in0_out2_grid,
    .spline_kernel = KAN_LUT_test_layer3_in0_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in0_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in0_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in0_out3_spline_kernel[] = { 0.118264116347f, 0.066061474383f, 0.000062531435f, 0.009675982408f, 0.066023230553f, 0.073996089399f, 0.050326347351f, 0.050166942179f, 0.138522058725f, 0.192686036229f };
const port_float KAN_LUT_test_layer3_in0_out3_lut[] = { 0.092162795365f, 0.039004897305f, 0.004371148380f, 0.024220208947f, 0.063912131847f, 0.069651328304f, 0.053830998526f, 0.056040879031f, 0.117169779133f, 0.171371877871f, 0.079622329020f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in0_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in0_out3_grid,
    .spline_kernel = KAN_LUT_test_layer3_in0_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in0_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in0_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in0_out4_spline_kernel[] = { 0.012863571756f, 0.038643777370f, 0.095796182752f, 0.117071412504f, 0.092696100473f, 0.150813013315f, 0.125223934650f, 0.120201811194f, 0.006770613603f, 0.049515776336f };
const port_float KAN_LUT_test_layer3_in0_out4_lut[] = { 0.025753674563f, 0.062153944034f, 0.101972562869f, 0.109833821439f, 0.106075165439f, 0.141002560204f, 0.128511760045f, 0.113719104120f, 0.038358642985f, 0.034390068540f, 0.020461064602f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in0_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in0_out4_grid,
    .spline_kernel = KAN_LUT_test_layer3_in0_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in0_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in0_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in0_out5_spline_kernel[] = { 0.268994569778f, 0.288492172956f, 0.239390239120f, 0.047958806157f, 0.083258904517f, 0.009984332137f, 0.000602590095f, 0.000035373392f, 0.036600735039f, 0.028710374609f };
const port_float KAN_LUT_test_layer3_in0_out5_lut[] = { 0.278743371367f, 0.268121549044f, 0.176127684018f, 0.064413720172f, 0.066088426747f, 0.016158388319f, 0.001939624376f, 0.002567767627f, 0.026637113595f, 0.030876811371f, 0.011863791161f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in0_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in0_out5_grid,
    .spline_kernel = KAN_LUT_test_layer3_in0_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in0_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in1_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in1_out0_spline_kernel[] = { 0.067092537880f, 0.028239728883f, 0.012396356091f, 0.076117031276f, 0.176964968443f, 0.099368341267f, 0.000034994981f, 0.342043638229f, 0.098435960710f, 0.108346737921f };
const port_float KAN_LUT_test_layer3_in1_out0_lut[] = { 0.047666133381f, 0.021853429419f, 0.033986224608f, 0.100417782937f, 0.154585622467f, 0.092607660329f, 0.050143327822f, 0.256687661537f, 0.163229714248f, 0.103238639137f, 0.044771379306f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in1_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in1_out0_grid,
    .spline_kernel = KAN_LUT_test_layer3_in1_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in1_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in1_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in1_out1_spline_kernel[] = { 0.237159058452f, 0.199014708400f, 0.245143815875f, 0.162354394794f, 0.000015909942f, 0.000003234502f, 0.039114903659f, 0.400911390781f, 0.046794813126f, 0.085214026272f };
const port_float KAN_LUT_test_layer3_in1_out1_lut[] = { 0.218086883426f, 0.218233944340f, 0.216670842580f, 0.122500848344f, 0.010746466392f, 0.005822808781f, 0.070672308983f, 0.304242410982f, 0.141874292003f, 0.070946206562f, 0.035212407551f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in1_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in1_out1_grid,
    .spline_kernel = KAN_LUT_test_layer3_in1_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in1_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in1_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in1_out2_spline_kernel[] = { 0.432690858841f, 0.005063053686f, 0.000002532486f, 0.124958604574f, 0.193194150925f, 0.124700039625f, 0.107399143279f, 0.033172834665f, 0.033704522997f, 0.060040470213f };
const port_float KAN_LUT_test_layer3_in1_out2_lut[] = { 0.218876956264f, 0.004738986269f, 0.041910317296f, 0.138357242250f, 0.174814067473f, 0.129202190510f, 0.102304823250f, 0.048237281505f, 0.034543347260f, 0.050233141265f, 0.024810111658f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in1_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in1_out2_grid,
    .spline_kernel = KAN_LUT_test_layer3_in1_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in1_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in1_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in1_out3_spline_kernel[] = { 0.200974628329f, 0.042589087039f, 0.022978248075f, 0.096659183502f, 0.177459388971f, 0.018559537828f, 0.002128378022f, 0.715258777142f, 0.082227535546f, 0.033404480666f };
const port_float KAN_LUT_test_layer3_in1_out3_lut[] = { 0.121781857684f, 0.035139920282f, 0.047964194874f, 0.115287632805f, 0.139943289825f, 0.032530506942f, 0.078243178564f, 0.529011300190f, 0.247825023018f, 0.049193941503f, 0.013803504407f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in1_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in1_out3_grid,
    .spline_kernel = KAN_LUT_test_layer3_in1_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in1_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in1_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in1_out4_spline_kernel[] = { 0.300548553467f, 0.290019720793f, 0.177219897509f, 0.156838119030f, 0.020967440680f, 0.000001803173f, 0.021514866501f, 0.034567799419f, 0.089644633234f, 0.126641377807f };
const port_float KAN_LUT_test_layer3_in1_out4_lut[] = { 0.295284137130f, 0.243451731141f, 0.172262357163f, 0.121663377674f, 0.025705517604f, 0.005367965228f, 0.019663019572f, 0.035566293750f, 0.076454770990f, 0.112164923998f, 0.052331147854f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in1_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in1_out4_grid,
    .spline_kernel = KAN_LUT_test_layer3_in1_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in1_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in1_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in1_out5_spline_kernel[] = { 0.269787877798f, 0.074017696083f, 0.147693619132f, 0.215526565909f, 0.033293440938f, 0.000038412119f, 0.018419450149f, 0.242613524199f, 0.164863154292f, 0.015125559643f };
const port_float KAN_LUT_test_layer3_in1_out5_lut[] = { 0.171902786940f, 0.105271260077f, 0.169180251350f, 0.164809968723f, 0.038608455762f, 0.006208218275f, 0.038845625695f, 0.192078335988f, 0.179856482070f, 0.064994332073f, 0.006250231257f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in1_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in1_out5_grid,
    .spline_kernel = KAN_LUT_test_layer3_in1_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in1_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in2_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in2_out0_spline_kernel[] = { 0.078775234520f, 0.014642629772f, 0.000051419076f, 0.055117432028f, 0.180447056890f, 0.145746737719f, 0.000309949741f, 0.156345680356f, 0.000012734231f, 0.050133191049f };
const port_float KAN_LUT_test_layer3_in2_out0_lut[] = { 0.046708932146f, 0.008878214628f, 0.018723782266f, 0.086214547212f, 0.165134703017f, 0.127696256777f, 0.038064568057f, 0.114415606231f, 0.043220968377f, 0.032528687882f, 0.020716194648f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in2_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in2_out0_grid,
    .spline_kernel = KAN_LUT_test_layer3_in2_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in2_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in2_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in2_out1_spline_kernel[] = { 0.176771044731f, 0.255603432655f, 0.000172813263f, 0.033989042044f, 0.151997283101f, 0.020858692005f, 0.037318926305f, 0.002546386793f, 0.000001190702f, 0.093038029969f };
const port_float KAN_LUT_test_layer3_in2_out1_lut[] = { 0.216187238693f, 0.149727836262f, 0.015713462060f, 0.063940204724f, 0.117642230123f, 0.036854697014f, 0.031278091914f, 0.009418830176f, 0.004134348153f, 0.060359781620f, 0.038445466929f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in2_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in2_out1_grid,
    .spline_kernel = KAN_LUT_test_layer3_in2_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in2_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in2_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in2_out2_spline_kernel[] = { 0.085618071258f, 0.150890886784f, 0.186147451401f, 0.077784754336f, 0.096290014684f, 0.000020460924f, 0.032592501491f, 0.337093234062f, 0.000003045758f, 0.025786558166f };
const port_float KAN_LUT_test_layer3_in2_out2_lut[] = { 0.118254479021f, 0.165189992760f, 0.149294539332f, 0.086708725145f, 0.075573930801f, 0.014811090281f, 0.059203761218f, 0.253151172455f, 0.090109755110f, 0.016730315448f, 0.010655602548f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in2_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in2_out2_grid,
    .spline_kernel = KAN_LUT_test_layer3_in2_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in2_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in2_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in2_out3_spline_kernel[] = { 0.101585835218f, 0.001652813749f, 0.263603031635f, 0.187935665250f, 0.218679293990f, 0.013963976875f, 0.000017262508f, 0.010188795626f, 0.000004323843f, 0.031642206013f };
const port_float KAN_LUT_test_layer3_in2_out3_lut[] = { 0.051619324484f, 0.110309651807f, 0.233946595483f, 0.198880287303f, 0.175196035319f, 0.033037535597f, 0.003142758562f, 0.007455916819f, 0.003874353321f, 0.020529655270f, 0.013075291741f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in2_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in2_out3_grid,
    .spline_kernel = KAN_LUT_test_layer3_in2_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in2_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in2_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in2_out4_spline_kernel[] = { 0.030184777454f, 0.000004348105f, 0.073996149004f, 0.003263409948f, 0.100881829858f, 0.000013586498f, 0.015745244920f, 0.000363888015f, 0.065880864859f, 0.000000000000f };
const port_float KAN_LUT_test_layer3_in2_out4_lut[] = { 0.015094562779f, 0.030704184961f, 0.049098136330f, 0.031710407988f, 0.074003984225f, 0.012774106279f, 0.011816015061f, 0.007809995940f, 0.046103946257f, 0.022051033279f, 0.000000000000f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in2_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in2_out4_grid,
    .spline_kernel = KAN_LUT_test_layer3_in2_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in2_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in2_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in2_out5_spline_kernel[] = { 0.207395046949f, 0.153136968613f, 0.103322766721f, 0.100424073637f, 0.018252894282f, 0.004555149470f, 0.110324762762f, 0.037358224392f, 0.377986818552f, 0.002236091066f };
const port_float KAN_LUT_test_layer3_in2_out5_lut[] = { 0.180266007781f, 0.132776794601f, 0.103175918241f, 0.078800655286f, 0.020912189216f, 0.021704528390f, 0.087052574589f, 0.074653339626f, 0.273929022793f, 0.127966936364f, 0.000924004573f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in2_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in2_out5_grid,
    .spline_kernel = KAN_LUT_test_layer3_in2_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in2_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in3_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in3_out0_spline_kernel[] = { 0.258020818233f, 0.276292383671f, 0.050796300173f, 0.173254579306f, 0.258965790272f, 0.289296150208f, 0.116221927106f, 0.004472309723f, 0.119753643870f, 0.000005261361f };
const port_float KAN_LUT_test_layer3_in3_out0_lut[] = { 0.267156600952f, 0.183036681542f, 0.095511609858f, 0.191367773478f, 0.259440204575f, 0.260416269918f, 0.130424123788f, 0.034721204757f, 0.084812566069f, 0.040086244575f, 0.000002174116f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in3_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in3_out0_grid,
    .spline_kernel = KAN_LUT_test_layer3_in3_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in3_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in3_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in3_out1_spline_kernel[] = { 0.228600621223f, 0.165207058191f, 0.002912418917f, 0.000008775966f, 0.039028469473f, 0.161630466580f, 0.010190282017f, 0.000005902047f, 0.000002531532f, 0.464914351702f };
const port_float KAN_LUT_test_layer3_in3_out1_lut[] = { 0.196903839707f, 0.098405114537f, 0.004623094446f, 0.010436020475f, 0.061273026341f, 0.126436679093f, 0.031666468567f, 0.002067805726f, 0.017293531923f, 0.301618835832f, 0.192113368472f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in3_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in3_out1_grid,
    .spline_kernel = KAN_LUT_test_layer3_in3_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in3_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in3_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in3_out2_spline_kernel[] = { 0.001104841707f, 0.070088826120f, 0.000012221232f, 0.064745739102f, 0.097479842603f, 0.106306038797f, 0.287737697363f, 0.352374792099f, 0.277414649725f, 0.000009744167f };
const port_float KAN_LUT_test_layer3_in3_out2_lut[] = { 0.035596833914f, 0.040846493586f, 0.022837516137f, 0.070995247215f, 0.097102726725f, 0.132384075175f, 0.267425249677f, 0.334331073421f, 0.286922108245f, 0.092859985380f, 0.000004026515f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in3_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in3_out2_grid,
    .spline_kernel = KAN_LUT_test_layer3_in3_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in3_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in3_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in3_out3_spline_kernel[] = { 0.275033146143f, 0.029874162748f, 0.123736463487f, 0.060113824904f, 0.082332924008f, 0.078021585941f, 0.090639084578f, 0.049821395427f, 0.010182593018f, 0.000000927626f };
const port_float KAN_LUT_test_layer3_in3_out3_lut[] = { 0.152453654446f, 0.069673291084f, 0.100889839817f, 0.068356081474f, 0.079990935781f, 0.080343955373f, 0.084545397885f, 0.055465386873f, 0.020286925107f, 0.003408825090f, 0.000000383317f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in3_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in3_out3_grid,
    .spline_kernel = KAN_LUT_test_layer3_in3_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in3_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in3_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in3_out4_spline_kernel[] = { 0.391009569168f, 0.163377657533f, 0.165526762605f, 0.003642909462f, 0.129810065031f, 0.177788615227f, 0.136302039027f, 0.280432492495f, 0.330084830523f, 0.067646764219f };
const port_float KAN_LUT_test_layer3_in3_out4_lut[] = { 0.277193613350f, 0.165206345214f, 0.111306975312f, 0.043029903820f, 0.131183100033f, 0.166660596640f, 0.157363105473f, 0.254531852778f, 0.307193540314f, 0.154369476259f, 0.027953208355f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in3_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in3_out4_grid,
    .spline_kernel = KAN_LUT_test_layer3_in3_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in3_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in3_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in3_out5_spline_kernel[] = { 0.341086000204f, 0.150025606155f, 0.002235684777f, 0.000030053470f, 0.102899529040f, 0.074623554945f, 0.024747954682f, 0.007093517575f, 0.002500205534f, 0.000000738494f };
const port_float KAN_LUT_test_layer3_in3_out5_lut[] = { 0.245555803180f, 0.089744896470f, 0.003940244899f, 0.027317231645f, 0.090372940859f, 0.070125115866f, 0.030343659978f, 0.010364486276f, 0.003622010357f, 0.000837324759f, 0.000000305163f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in3_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in3_out5_grid,
    .spline_kernel = KAN_LUT_test_layer3_in3_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in3_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in4_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in4_out0_spline_kernel[] = { 0.087781049311f, 0.059143636376f, 0.029361292720f, 0.014440337196f, 0.161737754941f, 0.178836762905f, 0.089840292931f, 0.151856973767f, 0.088297396898f, 0.150113508105f };
const port_float KAN_LUT_test_layer3_in4_out0_lut[] = { 0.073462342843f, 0.046955219216f, 0.024859358741f, 0.053949937755f, 0.155461278521f, 0.163831192169f, 0.109486119129f, 0.135097591160f, 0.107405487479f, 0.126941776534f, 0.062030375250f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in4_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in4_out0_grid,
    .spline_kernel = KAN_LUT_test_layer3_in4_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in4_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in4_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in4_out1_spline_kernel[] = { 0.201317101717f, 0.203198090196f, 0.038785427809f, 0.012384759262f, 0.001181564177f, 0.046627640724f, 0.000008124196f, 0.215573668480f, 0.199074268341f, 0.321725159883f };
const port_float KAN_LUT_test_layer3_in4_out1_lut[] = { 0.202257595956f, 0.135251200827f, 0.032666405070f, 0.010403773855f, 0.011124162823f, 0.034997663416f, 0.029212426684f, 0.170835230165f, 0.207999142857f, 0.275354817510f, 0.132944280944f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in4_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in4_out1_grid,
    .spline_kernel = KAN_LUT_test_layer3_in4_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in4_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in4_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in4_out2_spline_kernel[] = { 0.000081092890f, 0.038748901337f, 0.049686931074f, 0.128591105342f, 0.000061200866f, 0.034894566983f, 0.100912556052f, 0.059562049806f, 0.127104312181f, 0.205830335617f };
const port_float KAN_LUT_test_layer3_in4_out2_lut[] = { 0.019414997114f, 0.043108964003f, 0.075916212052f, 0.091665272884f, 0.015612082731f, 0.041116936626f, 0.086819951661f, 0.072400277096f, 0.112169723003f, 0.176077735449f, 0.085053857693f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in4_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in4_out2_grid,
    .spline_kernel = KAN_LUT_test_layer3_in4_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in4_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in4_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in4_out3_spline_kernel[] = { 0.190899401903f, 0.133459478617f, 0.110892646015f, 0.000030107272f, 0.076692633331f, 0.096761964262f, 0.124509856105f, 0.180621489882f, 0.000015300478f, 0.109668210149f };
const port_float KAN_LUT_test_layer3_in4_out3_lut[] = { 0.162179440260f, 0.124371696233f, 0.074158768710f, 0.024427481307f, 0.075687661424f, 0.098816471836f, 0.126178726923f, 0.157319138289f, 0.051856921590f, 0.071153505505f, 0.045317442210f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in4_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in4_out3_grid,
    .spline_kernel = KAN_LUT_test_layer3_in4_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in4_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in4_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in4_out4_spline_kernel[] = { 0.138172134757f, 0.000011420386f, 0.034978676587f, 0.000066548120f, 0.228527143598f, 0.243288949132f, 0.252148181200f, 0.114295519888f, 0.293246328831f, 0.018241260201f };
const port_float KAN_LUT_test_layer3_in4_out4_lut[] = { 0.069091777571f, 0.015031611851f, 0.022715240924f, 0.061784264099f, 0.216411271463f, 0.243081871513f, 0.236589301501f, 0.154039294051f, 0.235693033831f, 0.109986902838f, 0.007537710827f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in4_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in4_out4_grid,
    .spline_kernel = KAN_LUT_test_layer3_in4_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in4_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in4_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in4_out5_spline_kernel[] = { 0.395910263062f, 0.108929917216f, 0.109479181468f, 0.023481110111f, 0.023356745020f, 0.016419101506f, 0.000008650662f, 0.128757834435f, 0.507647037506f, 0.453330785036f };
const port_float KAN_LUT_test_layer3_in4_out5_lut[] = { 0.252420090139f, 0.110342755113f, 0.080685624291f, 0.026646495550f, 0.021960238033f, 0.014694576124f, 0.015750410268f, 0.127739310651f, 0.405424908296f, 0.464017947474f, 0.187326770676f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in4_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in4_out5_grid,
    .spline_kernel = KAN_LUT_test_layer3_in4_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in4_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in5_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in5_out0_spline_kernel[] = { 0.243997126818f, 0.081560805440f, 0.002151960274f, 0.064544610679f, 0.042077727616f, 0.069947905838f, 0.082382462919f, 0.237889349461f, 0.000000000000f, 0.110508099198f };
const port_float KAN_LUT_test_layer3_in5_out0_lut[] = { 0.162778966129f, 0.049418457526f, 0.024347993594f, 0.056282567829f, 0.049206276632f, 0.068918524018f, 0.096597455103f, 0.190674196436f, 0.067022691150f, 0.071693270968f, 0.045664503801f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in5_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in5_out0_grid,
    .spline_kernel = KAN_LUT_test_layer3_in5_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in5_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in5_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in5_out1_spline_kernel[] = { 0.001119782915f, 0.120376206934f, 0.112636543810f, 0.000040356372f, 0.096241019666f, 0.118729032576f, 0.222863614559f, 0.022841118276f, 0.044274289161f, 0.019859416410f };
const port_float KAN_LUT_test_layer3_in5_out1_lut[] = { 0.060747994925f, 0.116685203891f, 0.075077318480f, 0.029669315619f, 0.094434003219f, 0.131896985587f, 0.186709038698f, 0.064758610227f, 0.037698021428f, 0.027703081812f, 0.008206370417f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in5_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in5_out1_grid,
    .spline_kernel = KAN_LUT_test_layer3_in5_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in5_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in5_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in5_out2_spline_kernel[] = { 0.000133608104f, 0.063612863421f, 0.177057668567f, 0.003992178012f, 0.000026506939f, 0.174461260438f, 0.703687489033f, 0.124356418848f, 0.000000000000f, 0.219846129417f };
const port_float KAN_LUT_test_layer3_in5_out2_lut[] = { 0.031873235763f, 0.110228571104f, 0.117255668750f, 0.009379725393f, 0.035608133628f, 0.235169009991f, 0.565111369264f, 0.233437078920f, 0.041063743682f, 0.142627447597f, 0.090845508024f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in5_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in5_out2_grid,
    .spline_kernel = KAN_LUT_test_layer3_in5_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in5_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in5_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in5_out3_spline_kernel[] = { 0.292845815420f, 0.047424014658f, 0.102893620729f, 0.024692760780f, 0.077538944781f, 0.133796796203f, 0.018001770601f, 0.331838190556f, 0.162519708276f, 0.142951816320f };
const port_float KAN_LUT_test_layer3_in5_out3_lut[] = { 0.170134915039f, 0.071359479153f, 0.075802099737f, 0.041576907539f, 0.085436034763f, 0.110759328404f, 0.067648594653f, 0.257098189340f, 0.206570418351f, 0.147138560052f, 0.059070998480f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in5_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in5_out3_grid,
    .spline_kernel = KAN_LUT_test_layer3_in5_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in5_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in5_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in5_out4_spline_kernel[] = { 0.158319428563f, 0.090292237699f, 0.000001313661f, 0.221899762750f, 0.183729141951f, 0.477610617876f, 0.271537989378f, 0.442263513803f, 0.000000000000f, 0.113879792392f };
const port_float KAN_LUT_test_layer3_in5_out4_lut[] = { 0.124305833131f, 0.053263042604f, 0.075765520572f, 0.203552631457f, 0.245757746302f, 0.416595528934f, 0.319830356058f, 0.378454559598f, 0.121197450475f, 0.073880691759f, 0.047057765451f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in5_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in5_out4_grid,
    .spline_kernel = KAN_LUT_test_layer3_in5_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in5_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer3_in5_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer3_in5_out5_spline_kernel[] = { 0.002689009067f, 0.057156361639f, 0.043603468686f, 0.116655558348f, 0.041428662837f, 0.188493534923f, 0.104915864766f, 0.182825848460f, 0.121278665960f, 0.032452538610f };
const port_float KAN_LUT_test_layer3_in5_out5_lut[] = { 0.029922685353f, 0.051330920946f, 0.068278802713f, 0.094044028928f, 0.076179939946f, 0.160867841006f, 0.125397458642f, 0.162981451266f, 0.134252155769f, 0.061647192167f, 0.013410139921f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer3_in5_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer3_in5_out5_grid,
    .spline_kernel = KAN_LUT_test_layer3_in5_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer3_in5_out5_lut
};
    
const KAN_LUT *KAN_LUTs_test_layer3[] = {
    &KAN_LUT_test_layer3_in0_out0, &KAN_LUT_test_layer3_in0_out1, &KAN_LUT_test_layer3_in0_out2, &KAN_LUT_test_layer3_in0_out3, &KAN_LUT_test_layer3_in0_out4, &KAN_LUT_test_layer3_in0_out5,
    &KAN_LUT_test_layer3_in1_out0, &KAN_LUT_test_layer3_in1_out1, &KAN_LUT_test_layer3_in1_out2, &KAN_LUT_test_layer3_in1_out3, &KAN_LUT_test_layer3_in1_out4, &KAN_LUT_test_layer3_in1_out5,
    &KAN_LUT_test_layer3_in2_out0, &KAN_LUT_test_layer3_in2_out1, &KAN_LUT_test_layer3_in2_out2, &KAN_LUT_test_layer3_in2_out3, &KAN_LUT_test_layer3_in2_out4, &KAN_LUT_test_layer3_in2_out5,
    &KAN_LUT_test_layer3_in3_out0, &KAN_LUT_test_layer3_in3_out1, &KAN_LUT_test_layer3_in3_out2, &KAN_LUT_test_layer3_in3_out3, &KAN_LUT_test_layer3_in3_out4, &KAN_LUT_test_layer3_in3_out5,
    &KAN_LUT_test_layer3_in4_out0, &KAN_LUT_test_layer3_in4_out1, &KAN_LUT_test_layer3_in4_out2, &KAN_LUT_test_layer3_in4_out3, &KAN_LUT_test_layer3_in4_out4, &KAN_LUT_test_layer3_in4_out5,
    &KAN_LUT_test_layer3_in5_out0, &KAN_LUT_test_layer3_in5_out1, &KAN_LUT_test_layer3_in5_out2, &KAN_LUT_test_layer3_in5_out3, &KAN_LUT_test_layer3_in5_out4, &KAN_LUT_test_layer3_in5_out5,
};


const LayerKAN_LUT LayerKAN_LUT_test_layer3 = {
    .in_size = 6,
    .out_size = 6,
    .spline_kernel_size = 10,
    .kan_luts = KAN_LUTs_test_layer3
};


// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in0_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in0_out0_spline_kernel[] = { 0.000115250827f, 0.070123553276f, 0.279969692230f, 0.363606184721f, 0.046072084457f, 0.124322995543f, 0.193304419518f, 0.000044044715f, 0.002299170010f, 0.000023495237f };
const port_float KAN_LUT_test_layer4_in0_out0_lut[] = { 0.035119402051f, 0.156547543330f, 0.304495193618f, 0.276519776253f, 0.082910267298f, 0.126500923171f, 0.163077805331f, 0.039324376822f, 0.001618140705f, 0.000784799682f, 0.000009708776f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in0_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in0_out0_grid,
    .spline_kernel = KAN_LUT_test_layer4_in0_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in0_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in0_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in0_out1_spline_kernel[] = { 0.086016833782f, 0.001963616116f, 0.022126557305f, 0.176471561193f, 0.308077484369f, 0.097327016294f, 0.064150936902f, 0.039889335632f, 0.054681468755f, 0.240855634212f };
const port_float KAN_LUT_test_layer4_in0_out1_lut[] = { 0.043990224949f, 0.010642737342f, 0.073454216604f, 0.205536329988f, 0.256703650871f, 0.114163474326f, 0.066579857672f, 0.045779800889f, 0.057693332264f, 0.174560055953f, 0.099527121575f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in0_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in0_out1_grid,
    .spline_kernel = KAN_LUT_test_layer4_in0_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in0_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in0_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in0_out2_spline_kernel[] = { 0.134484902024f, 0.112752951682f, 0.041964642704f, 0.222967237234f, 0.039608001709f, 0.117713943124f, 0.051021426916f, 0.037480473518f, 0.093527778983f, 0.182362183928f };
const port_float KAN_LUT_test_layer4_in0_out2_lut[] = { 0.123618926853f, 0.083591385783f, 0.103718210443f, 0.167744037133f, 0.067545765749f, 0.099723946765f, 0.059543768852f, 0.043927843783f, 0.082009109953f, 0.149614103200f, 0.075356274351f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in0_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in0_out2_grid,
    .spline_kernel = KAN_LUT_test_layer4_in0_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in0_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in0_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in0_out3_spline_kernel[] = { 0.124521926045f, 0.085025429726f, 0.006528020371f, 0.000088541456f, 0.031066695228f, 0.010181636550f, 0.000013235242f, 0.195599704981f, 0.199345290661f, 0.258661180735f };
const port_float KAN_LUT_test_layer4_in0_out3_lut[] = { 0.104773677886f, 0.052751692374f, 0.005670135434f, 0.008520595801f, 0.024789759957f, 0.010826529194f, 0.021731103798f, 0.156245127930f, 0.200560685401f, 0.234532123632f, 0.106884785428f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in0_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in0_out3_grid,
    .spline_kernel = KAN_LUT_test_layer4_in0_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in0_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in0_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in0_out4_spline_kernel[] = { 0.102113895118f, 0.000003743168f, 0.000000600558f, 0.005030162632f, 0.041462767869f, 0.000006479727f, 0.102670311928f, 0.052809555084f, 0.096721701324f, 0.214943364263f };
const port_float KAN_LUT_test_layer4_in0_out4_lut[] = { 0.051058819143f, 0.000424387346f, 0.001684100965f, 0.014478181957f, 0.030659958767f, 0.019561459738f, 0.082247101678f, 0.065808610560f, 0.089505245155f, 0.171820520647f, 0.088819572009f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in0_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in0_out4_grid,
    .spline_kernel = KAN_LUT_test_layer4_in0_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in0_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in0_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in0_out5_spline_kernel[] = { 0.000004694621f, 0.043155848980f, 0.128919586539f, 0.012361197732f, 0.160014688969f, 0.163325548172f, 0.168240219355f, 0.200436204672f, 0.011870701797f, 0.000010976182f };
const port_float KAN_LUT_test_layer4_in0_out5_lut[] = { 0.021580271801f, 0.078417099400f, 0.088488659086f, 0.055744871031f, 0.150922855255f, 0.163714625372f, 0.170835142786f, 0.181450042166f, 0.061298200365f, 0.003980372340f, 0.000004535612f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in0_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in0_out5_grid,
    .spline_kernel = KAN_LUT_test_layer4_in0_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in0_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in1_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in1_out0_spline_kernel[] = { 0.263376682997f, 0.088652826846f, 0.000859632972f, 0.107855677605f, 0.118102729321f, 0.192302316427f, 0.220840051770f, 0.321834415197f, 0.043554753065f, 0.503668844700f };
const port_float KAN_LUT_test_layer4_in1_out0_lut[] = { 0.176014754921f, 0.053096646964f, 0.038123485826f, 0.106586449952f, 0.132449121638f, 0.188882352769f, 0.227028070834f, 0.282986487916f, 0.134261055549f, 0.341338609984f, 0.208127621777f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in1_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in1_out0_grid,
    .spline_kernel = KAN_LUT_test_layer4_in1_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in1_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in1_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in1_out1_spline_kernel[] = { 0.279776185751f, 0.151330843568f, 0.092822670937f, 0.039053555578f, 0.218763530254f, 0.168858528137f, 0.168495044112f, 0.031803376973f, 0.026009712368f, 0.168112620711f };
const port_float KAN_LUT_test_layer4_in1_out1_lut[] = { 0.215553514659f, 0.127684678605f, 0.075792647575f, 0.088579838295f, 0.196777147202f, 0.173959931559f, 0.154428076122f, 0.059097563155f, 0.032826740095f, 0.117770529560f, 0.069468025087f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in1_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in1_out1_grid,
    .spline_kernel = KAN_LUT_test_layer4_in1_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in1_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in1_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in1_out2_spline_kernel[] = { 0.069711290300f, 0.112997584045f, 0.036795239896f, 0.000008935167f, 0.181182771921f, 0.175656080246f, 0.080943644047f, 0.333748042583f, 0.348373711109f, 0.381135076284f };
const port_float KAN_LUT_test_layer4_in1_out2_lut[] = { 0.091354437172f, 0.081330143100f, 0.025742011357f, 0.049290762832f, 0.168085295557f, 0.162137566150f, 0.121149254239f, 0.283527361460f, 0.345724163592f, 0.363869742052f, 0.157493833175f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in1_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in1_out2_grid,
    .spline_kernel = KAN_LUT_test_layer4_in1_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in1_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in1_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in1_out3_spline_kernel[] = { 0.170936748385f, 0.006399750244f, 0.000084098778f, 0.000030437814f, 0.116521775723f, 0.065801039338f, 0.070105396211f, 0.028189711273f, 0.206650704145f, 0.319481581450f };
const port_float KAN_LUT_test_layer4_in1_out3_lut[] = { 0.088668249315f, 0.004469881862f, 0.000170528810f, 0.030840060024f, 0.098549967915f, 0.071681102384f, 0.065134945918f, 0.048475845355f, 0.163650598161f, 0.276435187287f, 0.132017182417f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in1_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in1_out3_grid,
    .spline_kernel = KAN_LUT_test_layer4_in1_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in1_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in1_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in1_out4_spline_kernel[] = { 0.039128690958f, 0.090387083590f, 0.037814892828f, 0.094093181193f, 0.118259944022f, 0.152048379183f, 0.001516857650f, 0.000001893414f, 0.070586763322f, 0.333444654942f };
const port_float KAN_LUT_test_layer4_in1_out4_lut[] = { 0.064757887274f, 0.068451226281f, 0.057520802418f, 0.098391397002f, 0.123503601533f, 0.126164719455f, 0.023753471986f, 0.004975410629f, 0.061695397002f, 0.239951812624f, 0.137787047497f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in1_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in1_out4_grid,
    .spline_kernel = KAN_LUT_test_layer4_in1_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in1_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in1_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in1_out5_spline_kernel[] = { 0.000000731748f, 0.002084887587f, 0.102355919778f, 0.004961267579f, 0.066729761660f, 0.046050976962f, 0.000012640992f, 0.108873784542f, 0.059606011957f, 0.236800149083f };
const port_float KAN_LUT_test_layer4_in1_out5_lut[] = { 0.001042809667f, 0.043510586195f, 0.068099510866f, 0.024918852253f, 0.058458867629f, 0.041338536972f, 0.018107304974f, 0.083574278776f, 0.079225370137f, 0.173577315597f, 0.097851301274f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in1_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in1_out5_grid,
    .spline_kernel = KAN_LUT_test_layer4_in1_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in1_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in2_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in2_out0_spline_kernel[] = { 0.175845399499f, 0.291808813810f, 0.097081400454f, 0.087288036942f, 0.015647349879f, 0.034886911511f, 0.000060990387f, 0.000050383453f, 0.038638722152f, 0.018697828054f };
const port_float KAN_LUT_test_layer4_in2_out0_lut[] = { 0.233827106655f, 0.210863752860f, 0.097022091400f, 0.068705955536f, 0.024279537949f, 0.027718637952f, 0.005240610169f, 0.002603826258f, 0.027691938170f, 0.025063204541f, 0.007726375229f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in2_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in2_out0_grid,
    .spline_kernel = KAN_LUT_test_layer4_in2_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in2_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in2_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in2_out1_spline_kernel[] = { 0.290871202946f, 0.341783016920f, 0.043650820851f, 0.083233848214f, 0.132423952222f, 0.094396278262f, 0.121385730803f, 0.118684656918f, 0.001182125765f, 0.143317565322f };
const port_float KAN_LUT_test_layer4_in2_out1_lut[] = { 0.316327109933f, 0.218377515181f, 0.061827490276f, 0.094770705281f, 0.121471895659f, 0.102339716859f, 0.117091734363f, 0.111462806182f, 0.037543204070f, 0.093374421250f, 0.059222134431f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in2_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in2_out1_grid,
    .spline_kernel = KAN_LUT_test_layer4_in2_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in2_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in2_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in2_out2_spline_kernel[] = { 0.185877099633f, 0.233888521791f, 0.140553534031f, 0.162228390574f, 0.049668230116f, 0.131402701139f, 0.000004166702f, 0.019473839551f, 0.107815399766f, 0.008865841664f };
const port_float KAN_LUT_test_layer4_in2_out2_lut[] = { 0.209882810712f, 0.195121950724f, 0.149351068457f, 0.131654324549f, 0.073659765850f, 0.103412168018f, 0.021562385962f, 0.021372397377f, 0.080772400276f, 0.041838779018f, 0.003663570936f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in2_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in2_out2_grid,
    .spline_kernel = KAN_LUT_test_layer4_in2_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in2_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in2_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in2_out3_spline_kernel[] = { 0.093068502843f, 0.093063898385f, 0.000003039859f, 0.069513052702f, 0.081362932920f, 0.002841434907f, 0.000204318218f, 0.031346276402f, 0.192646592855f, 0.037655808032f };
const port_float KAN_LUT_test_layer4_in2_out3_lut[] = { 0.093066200614f, 0.054609017194f, 0.024806983968f, 0.070061822199f, 0.064680488763f, 0.010560861558f, 0.003813761009f, 0.035705157031f, 0.144224537829f, 0.088910478852f, 0.015560251253f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in2_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in2_out3_grid,
    .spline_kernel = KAN_LUT_test_layer4_in2_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in2_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in2_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in2_out4_spline_kernel[] = { 0.091498911381f, 0.008836528286f, 0.063964322209f, 0.001596637885f, 0.114687837660f, 0.044945694506f, 0.208474680781f, 0.256791323423f, 0.325032562017f, 0.270923852921f };
const port_float KAN_LUT_test_layer4_in2_out4_lut[] = { 0.050167719834f, 0.031958188515f, 0.042177984995f, 0.033824513689f, 0.093089390508f, 0.076477087418f, 0.189139443427f, 0.251520018994f, 0.304972984944f, 0.284556538975f, 0.111952005339f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in2_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in2_out4_grid,
    .spline_kernel = KAN_LUT_test_layer4_in2_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in2_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in2_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in2_out5_spline_kernel[] = { 0.000001019315f, 0.000006386212f, 0.073488108814f, 0.234129354358f, 0.068486817181f, 0.010206602514f, 0.055370595306f, 0.011273993179f, 0.029895847663f, 0.017997546121f };
const port_float KAN_LUT_test_layer4_in2_out5_lut[] = { 0.000003702763f, 0.030370712217f, 0.126041885668f, 0.184348802336f, 0.067637850554f, 0.022945896345f, 0.044096550704f, 0.021433841014f, 0.024528560883f, 0.021682555379f, 0.007437002530f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in2_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in2_out5_grid,
    .spline_kernel = KAN_LUT_test_layer4_in2_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in2_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in3_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in3_out0_spline_kernel[] = { 0.075640164316f, 0.228014200926f, 0.006778305862f, 0.092658653855f, 0.001214681310f, 0.037713829428f, 0.000023796965f, 0.005902980454f, 0.223612472415f, 0.025898218155f };
const port_float KAN_LUT_test_layer4_in3_out0_lut[] = { 0.151827182621f, 0.135964764798f, 0.039180172671f, 0.065281226686f, 0.014650887171f, 0.028336474587f, 0.006237932320f, 0.019106583266f, 0.158683398969f, 0.091647233537f, 0.010701743039f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in3_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in3_out0_grid,
    .spline_kernel = KAN_LUT_test_layer4_in3_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in3_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in3_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in3_out1_spline_kernel[] = { 0.000006340402f, 0.080758057535f, 0.111262992024f, 0.195112898946f, 0.187021344900f, 0.135018408298f, 0.070449255407f, 0.362737119198f, 0.000000085156f, 0.000000000000f };
const port_float KAN_LUT_test_layer4_in3_out1_lut[] = { 0.040382198968f, 0.093029717584f, 0.138824242945f, 0.189854598858f, 0.177026803459f, 0.130785283964f, 0.110249611187f, 0.279572251965f, 0.095930537273f, 0.000000028503f, 0.000000000000f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in3_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in3_out1_grid,
    .spline_kernel = KAN_LUT_test_layer4_in3_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in3_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in3_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in3_out2_spline_kernel[] = { 0.136550486088f, 0.173773810267f, 0.073587439954f, 0.275787383318f, 0.042058400810f, 0.003646087367f, 0.000556135958f, 0.000045814853f, 0.000000044571f, 0.000000000000f };
const port_float KAN_LUT_test_layer4_in3_out2_lut[] = { 0.155162148178f, 0.132220668303f, 0.142921906457f, 0.206454927240f, 0.049733856849f, 0.007154639373f, 0.000963079028f, 0.000146118199f, 0.000012147451f, 0.000000014918f, 0.000000000000f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in3_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in3_out2_grid,
    .spline_kernel = KAN_LUT_test_layer4_in3_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in3_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in3_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in3_out3_spline_kernel[] = { 0.376073449850f, 0.188268989325f, 0.000007769973f, 0.000011558755f, 0.016455765814f, 0.007211509626f, 0.038915891200f, 0.300344318151f, 0.001163425390f, 0.147029787302f };
const port_float KAN_LUT_test_layer4_in3_out3_lut[] = { 0.282171219587f, 0.111251148520f, 0.003120793811f, 0.004360299055f, 0.013496774631f, 0.012882849053f, 0.061206605816f, 0.227629908214f, 0.085710427018f, 0.095776504392f, 0.060756110455f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in3_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in3_out3_grid,
    .spline_kernel = KAN_LUT_test_layer4_in3_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in3_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in3_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in3_out4_spline_kernel[] = { 0.302615553141f, 0.122722677886f, 0.029857566580f, 0.191497430205f, 0.017883058637f, 0.017091013491f, 0.000588729919f, 0.017217097804f, 0.454085320234f, 0.118157275021f };
const port_float KAN_LUT_test_layer4_in3_out4_lut[] = { 0.212669115514f, 0.085092023939f, 0.085495126080f, 0.139571485772f, 0.029201321997f, 0.014717951177f, 0.004761421678f, 0.042734046286f, 0.326056730803f, 0.228642988088f, 0.048825320257f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in3_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in3_out4_grid,
    .spline_kernel = KAN_LUT_test_layer4_in3_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in3_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in3_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in3_out5_spline_kernel[] = { 0.024655738845f, 0.103226870298f, 0.057999152690f, 0.094161950052f, 0.131236821413f, 0.034397818148f, 0.042127367109f, 0.202766805887f, 0.061591073871f, 0.172974377871f };
const port_float KAN_LUT_test_layer4_in3_out5_lut[] = { 0.063941304572f, 0.084213056694f, 0.070850795073f, 0.102621977287f, 0.109177692893f, 0.045551697670f, 0.057572500195f, 0.160906705836f, 0.103069158933f, 0.132834108716f, 0.071477015649f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in3_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in3_out5_grid,
    .spline_kernel = KAN_LUT_test_layer4_in3_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in3_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in4_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in4_out0_spline_kernel[] = { 0.318994134665f, 0.413740247488f, 0.074996978045f, 0.000040762025f, 0.005287282635f, 0.113057300448f, 0.019073454663f, 0.155249074101f, 0.057353317738f, 0.014991256408f };
const port_float KAN_LUT_test_layer4_in4_out0_lut[] = { 0.366367191076f, 0.273372177004f, 0.055507389533f, 0.004215899476f, 0.026761607193f, 0.087942966177f, 0.047122251912f, 0.121203878009f, 0.081667655983f, 0.028922504103f, 0.006194734053f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in4_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in4_out0_grid,
    .spline_kernel = KAN_LUT_test_layer4_in4_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in4_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in4_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in4_out1_spline_kernel[] = { 0.257948786020f, 0.252765834332f, 0.176140859723f, 0.105761028826f, 0.145137622952f, 0.138340815902f, 0.080133885145f, 0.075988836586f, 0.104411408305f, 0.000005240830f };
const port_float KAN_LUT_test_layer4_in4_out1_lut[] = { 0.255357310176f, 0.221124038839f, 0.153850502681f, 0.118792105281f, 0.141157998773f, 0.130384083129f, 0.088364559911f, 0.078707301574f, 0.093011821126f, 0.034951020178f, 0.000002165632f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in4_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in4_out1_grid,
    .spline_kernel = KAN_LUT_test_layer4_in4_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in4_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in4_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in4_out2_spline_kernel[] = { 0.078256152570f, 0.294753164053f, 0.035922873765f, 0.156533926725f, 0.000019179268f, 0.065182000399f, 0.082249611616f, 0.104553259909f, 0.003908740822f, 0.143699780107f };
const port_float KAN_LUT_test_layer4_in4_out2_lut[] = { 0.186504658312f, 0.186903882895f, 0.080570875629f, 0.110656061792f, 0.023561386684f, 0.060989287488f, 0.082014724027f, 0.093383048869f, 0.035724313447f, 0.094535014394f, 0.059380074424f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in4_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in4_out2_grid,
    .spline_kernel = KAN_LUT_test_layer4_in4_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in4_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in4_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in4_out3_spline_kernel[] = { 0.206506758928f, 0.287895947695f, 0.130336299539f, 0.087003186345f, 0.052228756249f, 0.176304414868f, 0.000026992611f, 0.000128267959f, 0.106885276735f, 0.000011221498f };
const port_float KAN_LUT_test_layer4_in4_out3_lut[] = { 0.247201353312f, 0.222452336106f, 0.118436532695f, 0.079418204910f, 0.079650649447f, 0.137263593931f, 0.026260542549f, 0.007166076423f, 0.074677363269f, 0.035782930540f, 0.000004636983f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in4_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in4_out3_grid,
    .spline_kernel = KAN_LUT_test_layer4_in4_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in4_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in4_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in4_out4_spline_kernel[] = { 0.014779800549f, 0.008458199911f, 0.191030010581f, 0.000002951792f, 0.093646705151f, 0.154851660132f, 0.059360951185f, 0.071509838104f, 0.001345418394f, 0.303722888231f };
const port_float KAN_LUT_test_layer4_in4_out4_lut[] = { 0.011619000230f, 0.083927219199f, 0.124073485769f, 0.031872554040f, 0.099848121433f, 0.134323604774f, 0.074821230917f, 0.064410969615f, 0.031146741080f, 0.197493687364f, 0.125505325715f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in4_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in4_out4_grid,
    .spline_kernel = KAN_LUT_test_layer4_in4_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in4_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in4_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in4_out5_spline_kernel[] = { 0.011734792963f, 0.133996054530f, 0.000001041222f, 0.034770574421f, 0.039079602808f, 0.003857444506f, 0.112485833466f, 0.227873608470f, 0.107659101486f, 0.766945302486f };
const port_float KAN_LUT_test_layer4_in4_out5_lut[] = { 0.072865423746f, 0.078121002495f, 0.013853571149f, 0.034617070363f, 0.031662949043f, 0.023655692275f, 0.108246463105f, 0.196561901499f, 0.163970276098f, 0.533598345912f, 0.316919546482f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in4_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in4_out5_grid,
    .spline_kernel = KAN_LUT_test_layer4_in4_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in4_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in5_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in5_out0_spline_kernel[] = { 0.196658506989f, 0.041727628559f, 0.060058500618f, 0.000027690587f, 0.231334835291f, 0.190964519978f, 0.217397615314f, 0.448619127274f, 0.274812042713f, 0.035064298660f };
const port_float KAN_LUT_test_layer4_in5_out0_lut[] = { 0.119193067774f, 0.049942579321f, 0.039662553920f, 0.063432378815f, 0.207867646177f, 0.199067203097f, 0.237351939144f, 0.390310170914f, 0.311861314264f, 0.114730869212f, 0.014489379611f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in5_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in5_out0_grid,
    .spline_kernel = KAN_LUT_test_layer4_in5_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in5_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in5_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in5_out1_spline_kernel[] = { 0.103782288730f, 0.000416764582f, 0.008321714588f, 0.059759944677f, 0.244001999497f, 0.180128246546f, 0.163590520620f, 0.043571043760f, 0.181300565600f, 0.065608367324f };
const port_float KAN_LUT_test_layer4_in5_out1_lut[] = { 0.052099526656f, 0.004110403114f, 0.025407982510f, 0.106572124172f, 0.218887591350f, 0.184266617168f, 0.153651971909f, 0.076978592171f, 0.140573626831f, 0.103247353238f, 0.027110895588f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in5_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in5_out1_grid,
    .spline_kernel = KAN_LUT_test_layer4_in5_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in5_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in5_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in5_out2_spline_kernel[] = { 0.108012080193f, 0.036822836846f, 0.166725784540f, 0.000010073761f, 0.091117367148f, 0.129361391068f, 0.131919309497f, 0.294024735689f, 0.038315322250f, 0.179131254554f };
const port_float KAN_LUT_test_layer4_in5_out2_lut[] = { 0.072417458519f, 0.090795911279f, 0.108777088822f, 0.030304735636f, 0.092837369123f, 0.125791078941f, 0.148285221031f, 0.244295328671f, 0.111177908411f, 0.129037801931f, 0.074021179568f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in5_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in5_out2_grid,
    .spline_kernel = KAN_LUT_test_layer4_in5_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in5_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in5_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in5_out3_spline_kernel[] = { 0.270081788301f, 0.340297639370f, 0.144862338901f, 0.000012823747f, 0.049856510013f, 0.089568026364f, 0.049776107073f, 0.134624376893f, 0.036403559148f, 0.074393600225f };
const port_float KAN_LUT_test_layer4_in5_out3_lut[] = { 0.305189713836f, 0.259249102601f, 0.099609985489f, 0.018581590513f, 0.054601821257f, 0.079546137921f, 0.064460883271f, 0.110950416955f, 0.063792165369f, 0.060448279035f, 0.030741157118f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in5_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in5_out3_grid,
    .spline_kernel = KAN_LUT_test_layer4_in5_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in5_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in5_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in5_out4_spline_kernel[] = { 0.153286248446f, 0.243224054575f, 0.267288476229f, 0.253769516945f, 0.002347072586f, 0.056455891579f, 0.000002018330f, 0.071107417345f, 0.013400203548f, 0.228330507874f };
const port_float KAN_LUT_test_layer4_in5_out4_lut[] = { 0.198255151510f, 0.252796386638f, 0.262365776276f, 0.187780402047f, 0.029925962010f, 0.042468040704f, 0.015745714249f, 0.052894690186f, 0.036654891242f, 0.152616967867f, 0.094351449535f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in5_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in5_out4_grid,
    .spline_kernel = KAN_LUT_test_layer4_in5_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in5_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer4_in5_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer4_in5_out5_spline_kernel[] = { 0.138005033135f, 0.381022393703f, 0.212682113051f, 0.000021900325f, 0.074940361083f, 0.053743746132f, 0.066270448267f, 0.019872006029f, 0.000004409047f, 0.022418545559f };
const port_float KAN_LUT_test_layer4_in5_out5_lut[] = { 0.259513713419f, 0.310456090291f, 0.144284939050f, 0.027743897858f, 0.065695197840f, 0.057796955432f, 0.059613744413f, 0.027953171806f, 0.006092233160f, 0.014545738783f, 0.009263861801f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer4_in5_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer4_in5_out5_grid,
    .spline_kernel = KAN_LUT_test_layer4_in5_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer4_in5_out5_lut
};
    
const KAN_LUT *KAN_LUTs_test_layer4[] = {
    &KAN_LUT_test_layer4_in0_out0, &KAN_LUT_test_layer4_in0_out1, &KAN_LUT_test_layer4_in0_out2, &KAN_LUT_test_layer4_in0_out3, &KAN_LUT_test_layer4_in0_out4, &KAN_LUT_test_layer4_in0_out5,
    &KAN_LUT_test_layer4_in1_out0, &KAN_LUT_test_layer4_in1_out1, &KAN_LUT_test_layer4_in1_out2, &KAN_LUT_test_layer4_in1_out3, &KAN_LUT_test_layer4_in1_out4, &KAN_LUT_test_layer4_in1_out5,
    &KAN_LUT_test_layer4_in2_out0, &KAN_LUT_test_layer4_in2_out1, &KAN_LUT_test_layer4_in2_out2, &KAN_LUT_test_layer4_in2_out3, &KAN_LUT_test_layer4_in2_out4, &KAN_LUT_test_layer4_in2_out5,
    &KAN_LUT_test_layer4_in3_out0, &KAN_LUT_test_layer4_in3_out1, &KAN_LUT_test_layer4_in3_out2, &KAN_LUT_test_layer4_in3_out3, &KAN_LUT_test_layer4_in3_out4, &KAN_LUT_test_layer4_in3_out5,
    &KAN_LUT_test_layer4_in4_out0, &KAN_LUT_test_layer4_in4_out1, &KAN_LUT_test_layer4_in4_out2, &KAN_LUT_test_layer4_in4_out3, &KAN_LUT_test_layer4_in4_out4, &KAN_LUT_test_layer4_in4_out5,
    &KAN_LUT_test_layer4_in5_out0, &KAN_LUT_test_layer4_in5_out1, &KAN_LUT_test_layer4_in5_out2, &KAN_LUT_test_layer4_in5_out3, &KAN_LUT_test_layer4_in5_out4, &KAN_LUT_test_layer4_in5_out5,
};


const LayerKAN_LUT LayerKAN_LUT_test_layer4 = {
    .in_size = 6,
    .out_size = 6,
    .spline_kernel_size = 10,
    .kan_luts = KAN_LUTs_test_layer4
};


// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in0_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in0_out0_spline_kernel[] = { 0.137474089861f, 0.056229453534f, 0.334325134754f, 0.036882944405f, 0.058817107230f, 0.043045565486f, 0.096922077239f, 0.091488376260f, 0.015945652500f, 0.255273699760f };
const port_float KAN_LUT_test_layer5_in0_out0_lut[] = { 0.096851771697f, 0.171480745924f, 0.230171415154f, 0.053745614380f, 0.054173503302f, 0.052689544687f, 0.088346056794f, 0.087594028193f, 0.044824523351f, 0.170948631053f, 0.105484999901f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in0_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in0_out0_grid,
    .spline_kernel = KAN_LUT_test_layer5_in0_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in0_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in0_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in0_out1_spline_kernel[] = { 0.013272812590f, 0.085951752961f, 0.056506264955f, 0.014570109546f, 0.004464474507f, 0.101745329797f, 0.204222634435f, 0.281413704157f, 0.058543838561f, 0.214855030179f };
const port_float KAN_LUT_test_layer5_in0_out1_lut[] = { 0.049612282775f, 0.073483869734f, 0.042956485467f, 0.013457153993f, 0.024829978928f, 0.106940212379f, 0.196952360782f, 0.251048909670f, 0.123297855597f, 0.158984672155f, 0.088783070322f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in0_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in0_out1_grid,
    .spline_kernel = KAN_LUT_test_layer5_in0_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in0_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in0_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in0_out2_spline_kernel[] = { 0.044827114791f, 0.012602876872f, 0.010456999764f, 0.128786131740f, 0.029416235164f, 0.077420212328f, 0.000014979807f, 0.059664282948f, 0.000027568331f, 0.000015205913f };
const port_float KAN_LUT_test_layer5_in0_out2_lut[] = { 0.028714995831f, 0.011849308802f, 0.050098500584f, 0.098105819473f, 0.045705959239f, 0.060946295800f, 0.017691925878f, 0.043643608205f, 0.015798801693f, 0.000019092409f, 0.000006283435f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in0_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in0_out2_grid,
    .spline_kernel = KAN_LUT_test_layer5_in0_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in0_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in0_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in0_out3_spline_kernel[] = { 0.300410330296f, 0.241885378957f, 0.169676765800f, 0.128609418869f, 0.059598680586f, 0.125328302383f, 0.043236915022f, 0.102198332548f, 0.070965394378f, 0.118427760899f };
const port_float KAN_LUT_test_layer5_in0_out3_lut[] = { 0.271147854626f, 0.212288947699f, 0.157124614358f, 0.111885943134f, 0.077470264390f, 0.106326110276f, 0.061539912473f, 0.088194876063f, 0.080990474302f, 0.100584113247f, 0.048937091281f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in0_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in0_out3_grid,
    .spline_kernel = KAN_LUT_test_layer5_in0_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in0_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in0_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in0_out4_spline_kernel[] = { 0.305329799652f, 0.288350820541f, 0.000007215166f, 0.000047761994f, 0.069065041840f, 0.258192956448f, 0.251229435205f, 0.449447214603f, 0.108625851572f, 0.000029992940f };
const port_float KAN_LUT_test_layer5_in0_out4_lut[] = { 0.296840310097f, 0.169270731457f, 0.004786796631f, 0.018298757815f, 0.102796411006f, 0.237619053018f, 0.272742374254f, 0.386778565847f, 0.194721737961f, 0.036377697805f, 0.000012393777f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in0_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in0_out4_grid,
    .spline_kernel = KAN_LUT_test_layer5_in0_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in0_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in0_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in0_out5_spline_kernel[] = { 0.173657193780f, 0.000638232741f, 0.052790846676f, 0.061302181333f, 0.000008751705f, 0.039479669183f, 0.000002878409f, 0.000000145117f, 0.000002664058f, 0.000081149898f };
const port_float KAN_LUT_test_layer5_in0_out5_lut[] = { 0.087147713260f, 0.022903854041f, 0.054777655153f, 0.044775811465f, 0.012053255137f, 0.029529514618f, 0.005875176490f, 0.000000865094f, 0.000004916787f, 0.000053538523f, 0.000033533016f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in0_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in0_out5_grid,
    .spline_kernel = KAN_LUT_test_layer5_in0_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in0_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in1_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in1_out0_spline_kernel[] = { 0.136550232768f, 0.032304957509f, 0.000000023304f, 0.065251179039f, 0.028845952824f, 0.008853130043f, 0.137704461813f, 0.140790551901f, 0.178367823362f, 0.212421074510f };
const port_float KAN_LUT_test_layer5_in1_out0_lut[] = { 0.084427595139f, 0.019386576744f, 0.022374252029f, 0.053196654744f, 0.027204776391f, 0.030086471006f, 0.118855306063f, 0.142650130120f, 0.169696475787f, 0.197511993349f, 0.087777303516f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in1_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in1_out0_grid,
    .spline_kernel = KAN_LUT_test_layer5_in1_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in1_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in1_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in1_out1_spline_kernel[] = { 0.250843316317f, 0.193271398544f, 0.274110317230f, 0.133932575583f, 0.182084634900f, 0.047038175166f, 0.004249067046f, 0.031201863661f, 0.150377556682f, 0.096757397056f };
const port_float KAN_LUT_test_layer5_in1_out1_lut[] = { 0.222057357430f, 0.226913810885f, 0.225855140585f, 0.151880226290f, 0.151556909792f, 0.054623933848f, 0.013398768730f, 0.033623863885f, 0.116865879864f, 0.113105344748f, 0.039982395478f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in1_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in1_out1_grid,
    .spline_kernel = KAN_LUT_test_layer5_in1_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in1_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in1_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in1_out2_spline_kernel[] = { 0.015956657007f, 0.024552192539f, 0.038255568594f, 0.000002879493f, 0.014580248855f, 0.000002765207f, 0.066984683275f, 0.029316885397f, 0.074732773006f, 0.000003382232f };
const port_float KAN_LUT_test_layer5_in1_out2_lut[] = { 0.020254424773f, 0.030179225886f, 0.025225480489f, 0.005280672225f, 0.010664816588f, 0.011472955875f, 0.053129129567f, 0.039946539520f, 0.059942767535f, 0.025016056297f, 0.000001397616f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in1_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in1_out2_grid,
    .spline_kernel = KAN_LUT_test_layer5_in1_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in1_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in1_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in1_out3_spline_kernel[] = { 0.000004874048f, 0.051331087947f, 0.219804570079f, 0.075843185186f, 0.021684363484f, 0.048108428717f, 0.111271865666f, 0.169279366732f, 0.160570517182f, 0.139568328857f };
const port_float KAN_LUT_test_layer5_in1_out3_lut[] = { 0.025667980998f, 0.120736137531f, 0.168834462208f, 0.066874126819f, 0.030615439284f, 0.054774883673f, 0.107868162346f, 0.156958254562f, 0.162092610886f, 0.144291072407f, 0.057672863164f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in1_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in1_out3_grid,
    .spline_kernel = KAN_LUT_test_layer5_in1_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in1_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in1_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in1_out4_spline_kernel[] = { 0.433793157339f, 0.377764850855f, 0.295386433601f, 0.207577899098f, 0.018811604008f, 0.090064913034f, 0.040043670684f, 0.065434597433f, 0.003420484485f, 0.110488556325f };
const port_float KAN_LUT_test_layer5_in1_out4_lut[] = { 0.405779004097f, 0.343955704496f, 0.267357600437f, 0.160921840936f, 0.045719343114f, 0.075262857455f, 0.050107876855f, 0.056193352731f, 0.023802781490f, 0.072825465233f, 0.045656428234f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in1_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in1_out4_grid,
    .spline_kernel = KAN_LUT_test_layer5_in1_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in1_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in1_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in1_out5_spline_kernel[] = { 0.037912733853f, 0.002938558115f, 0.003865203355f, 0.168572843075f, 0.163981452584f, 0.048317905515f, 0.022217703983f, 0.000001982226f, 0.000000369750f, 0.000003077113f };
const port_float KAN_LUT_test_layer5_in1_out5_lut[] = { 0.020425645984f, 0.003465990758f, 0.058979303505f, 0.161233100311f, 0.140865537053f, 0.056383944447f, 0.023805366013f, 0.004500100269f, 0.000000896877f, 0.000002120068f, 0.000001271534f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in1_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in1_out5_grid,
    .spline_kernel = KAN_LUT_test_layer5_in1_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in1_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in2_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in2_out0_spline_kernel[] = { 0.699036657810f, 0.056013394147f, 0.094843141735f, 0.011924765073f, 0.149106606841f, 0.109495162964f, 0.117346629500f, 0.072468213737f, 0.009834578261f, 0.000009394066f };
const port_float KAN_LUT_test_layer5_in2_out0_lut[] = { 0.377525025979f, 0.074715865314f, 0.066447656198f, 0.051288001697f, 0.132016234038f, 0.114755241031f, 0.111542442767f, 0.077414098881f, 0.026033446082f, 0.003297833502f, 0.000003881846f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in2_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in2_out0_grid,
    .spline_kernel = KAN_LUT_test_layer5_in2_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in2_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in2_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in2_out1_spline_kernel[] = { 0.324483305216f, 0.529103040695f, 0.149132698774f, 0.315433323383f, 0.000048000293f, 0.022387215868f, 0.005302567501f, 0.085300847888f, 0.131986081600f, 0.000116481322f };
const port_float KAN_LUT_test_layer5_in2_out1_lut[] = { 0.426793172956f, 0.371244966614f, 0.211075806051f, 0.225840900659f, 0.025423152080f, 0.017537927725f, 0.016108370604f, 0.072189475989f, 0.114735332178f, 0.044252728005f, 0.000048132778f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in2_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in2_out1_grid,
    .spline_kernel = KAN_LUT_test_layer5_in2_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in2_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in2_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in2_out2_spline_kernel[] = { 0.231925442815f, 0.000003870065f, 0.000000899891f, 0.016229704022f, 0.027522290125f, 0.165327638388f, 0.015900574625f, 0.032853938639f, 0.049086641520f, 0.544536292553f };
const port_float KAN_LUT_test_layer5_in2_out2_lut[] = { 0.115964656440f, 0.000960996327f, 0.005432904087f, 0.018612622508f, 0.054678408668f, 0.128862729288f, 0.039880774607f, 0.030494469256f, 0.063219508772f, 0.369703371463f, 0.225014996923f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in2_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in2_out2_grid,
    .spline_kernel = KAN_LUT_test_layer5_in2_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in2_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in2_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in2_out3_spline_kernel[] = { 0.000004271744f, 0.036201745272f, 0.065396286547f, 0.110535323620f, 0.059924583882f, 0.135088518262f, 0.093877986073f, 0.132588416338f, 0.000014375894f, 0.553939580917f };
const port_float KAN_LUT_test_layer5_in2_out3_lut[] = { 0.018103008508f, 0.048116028966f, 0.080022252819f, 0.095471940658f, 0.078489892231f, 0.121193156616f, 0.104007489856f, 0.115985128197f, 0.055675803306f, 0.359378837403f, 0.228900653272f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in2_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in2_out3_grid,
    .spline_kernel = KAN_LUT_test_layer5_in2_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in2_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in2_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in2_out4_spline_kernel[] = { 0.242177352309f, 0.438562929630f, 0.025292387232f, 0.013479745016f, 0.053812246770f, 0.094579339027f, 0.284079492092f, 0.236465692520f, 0.305110335350f, 0.119172699749f };
const port_float KAN_LUT_test_layer5_in2_out4_lut[] = { 0.340370140970f, 0.266978467576f, 0.028169487026f, 0.024585504901f, 0.059400128970f, 0.118557967969f, 0.250970605730f, 0.250644991959f, 0.280041344187f, 0.179438227372f, 0.049244917252f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in2_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in2_out4_grid,
    .spline_kernel = KAN_LUT_test_layer5_in2_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in2_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in2_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in2_out5_spline_kernel[] = { 0.000011457943f, 0.000004612898f, 0.000010856052f, 0.074692226946f, 0.000005074897f, 0.029044110328f, 0.002440782730f, 0.000000682750f, 0.000013960728f, 0.280381232500f };
const port_float KAN_LUT_test_layer5_in2_out5_lut[] = { 0.000008035421f, 0.000007220999f, 0.025007410059f, 0.052162846495f, 0.010822873116f, 0.022086690166f, 0.006146226093f, 0.000495630464f, 0.010437331205f, 0.181904893890f, 0.115860013430f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in2_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in2_out5_grid,
    .spline_kernel = KAN_LUT_test_layer5_in2_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in2_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in3_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in3_out0_spline_kernel[] = { 0.198950305581f, 0.079595692456f, 0.063214138150f, 0.046116154641f, 0.238127708435f, 0.001415417995f, 0.027041118592f, 0.014231003821f, 0.003980560228f, 0.065921217203f };
const port_float KAN_LUT_test_layer5_in3_out0_lut[] = { 0.139272999018f, 0.073319656020f, 0.057762028865f, 0.097531945114f, 0.177503381608f, 0.029681254700f, 0.021905671936f, 0.016147072111f, 0.008994999496f, 0.044099406940f, 0.027240172398f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in3_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in3_out0_grid,
    .spline_kernel = KAN_LUT_test_layer5_in3_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in3_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in3_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in3_out1_spline_kernel[] = { 0.171692609787f, 0.051182314754f, 0.060775130987f, 0.064238667488f, 0.055341910571f, 0.006297017913f, 0.038976028562f, 0.055589564145f, 0.059595912695f, 0.000000000000f };
const port_float KAN_LUT_test_layer5_in3_out1_lut[] = { 0.111437462270f, 0.055644264830f, 0.061775854920f, 0.061756996946f, 0.045999548465f, 0.016224979483f, 0.035830962472f, 0.052490548993f, 0.056320005581f, 0.019947392266f, 0.000000000000f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in3_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in3_out1_grid,
    .spline_kernel = KAN_LUT_test_layer5_in3_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in3_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in3_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in3_out2_spline_kernel[] = { 0.392569899559f, 0.264967590570f, 0.011999003589f, 0.029232822359f, 0.132903367281f, 0.333495169878f, 0.295939922333f, 0.000001710253f, 0.172894597054f, 0.251416921616f };
const port_float KAN_LUT_test_layer5_in3_out2_lut[] = { 0.328768745065f, 0.160962398880f, 0.021948646846f, 0.056008898830f, 0.166664811944f, 0.307186145181f, 0.270954524025f, 0.071354018438f, 0.130091110135f, 0.220979004359f, 0.103891289924f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in3_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in3_out2_grid,
    .spline_kernel = KAN_LUT_test_layer5_in3_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in3_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in3_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in3_out3_spline_kernel[] = { 0.000001783456f, 0.025508044288f, 0.104008942842f, 0.042762827128f, 0.108270436525f, 0.209172084928f, 0.135291710496f, 0.291138857603f, 0.133045092225f, 0.121997617185f };
const port_float KAN_LUT_test_layer5_in3_out3_lut[] = { 0.012754913872f, 0.057841034348f, 0.082211674383f, 0.062364901685f, 0.124369853969f, 0.187757891995f, 0.162382091311f, 0.249130549941f, 0.174444157138f, 0.123678836233f, 0.050412238506f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in3_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in3_out3_grid,
    .spline_kernel = KAN_LUT_test_layer5_in3_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in3_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in3_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in3_out4_spline_kernel[] = { 0.060411479324f, 0.028560448438f, 0.062773302197f, 0.043154817075f, 0.141570419073f, 0.044593311846f, 0.000001046116f, 0.000000653618f, 0.236159935594f, 0.285898149014f };
const port_float KAN_LUT_test_layer5_in3_out4_lut[] = { 0.044485963881f, 0.042829607144f, 0.055641282735f, 0.069911696802f, 0.115427741858f, 0.047978047856f, 0.006634565760f, 0.015614569916f, 0.175554356562f, 0.264524645364f, 0.118139730997f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in3_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in3_out4_grid,
    .spline_kernel = KAN_LUT_test_layer5_in3_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in3_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in3_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in3_out5_spline_kernel[] = { 1.109958291054f, 0.000004968788f, 0.022900084034f, 0.000005309732f, 0.000001029765f, 0.103064313531f, 0.000025254823f, 0.082696013153f, 0.000526808202f, 0.000342679996f };
const port_float KAN_LUT_test_layer5_in3_out5_lut[] = { 0.554981629921f, 0.014052344188f, 0.014858525441f, 0.000855636389f, 0.020869498294f, 0.077089155648f, 0.023893746855f, 0.060524217957f, 0.022250659289f, 0.000398645553f, 0.000141603304f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in3_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in3_out5_grid,
    .spline_kernel = KAN_LUT_test_layer5_in3_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in3_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in4_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in4_out0_spline_kernel[] = { 0.262366771698f, 0.021384857595f, 0.060441035777f, 0.042424082756f, 0.161050900817f, 0.017150916159f, 0.165384545922f, 0.210768595338f, 0.092281855643f, 0.359280914068f };
const port_float KAN_LUT_test_layer5_in4_out0_lut[] = { 0.141875814646f, 0.038519567233f, 0.053765011366f, 0.074466516364f, 0.124071031655f, 0.054067900820f, 0.148021697013f, 0.193745428989f, 0.133546908809f, 0.263974933123f, 0.148463187631f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in4_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in4_out0_grid,
    .spline_kernel = KAN_LUT_test_layer5_in4_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in4_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in4_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in4_out1_spline_kernel[] = { 0.000001402514f, 0.056282810867f, 0.268857508898f, 0.139640375972f, 0.160318672657f, 0.100048221648f, 0.029307428747f, 0.013198786415f, 0.045832432806f, 0.012522147968f };
const port_float KAN_LUT_test_layer5_in4_out1_lut[] = { 0.028142106691f, 0.143891027374f, 0.222093514852f, 0.149914612270f, 0.146747991473f, 0.095751084172f, 0.038166736541f, 0.018618050120f, 0.035963234738f, 0.023464480530f, 0.005174441309f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in4_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in4_out1_grid,
    .spline_kernel = KAN_LUT_test_layer5_in4_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in4_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in4_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in4_out2_spline_kernel[] = { 0.182278975844f, 0.067667864263f, 0.045272152871f, 0.093449659646f, 0.005188934505f, 0.019731696695f, 0.240882590413f, 0.191824048758f, 0.108341619372f, 0.136993929744f };
const port_float KAN_LUT_test_layer5_in4_out2_lut[] = { 0.124973420054f, 0.058887037703f, 0.061767859046f, 0.068316254811f, 0.013968963222f, 0.051127825286f, 0.202916079193f, 0.196237890373f, 0.131485199017f, 0.125139331153f, 0.056609061878f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in4_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in4_out2_grid,
    .spline_kernel = KAN_LUT_test_layer5_in4_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in4_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in4_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in4_out3_spline_kernel[] = { 0.582988142967f, 0.011591183022f, 0.175326630473f, 0.064658924937f, 0.112549491227f, 0.056262783706f, 0.242801636457f, 0.222271084785f, 0.269912451506f, 0.343930900097f };
const port_float KAN_LUT_test_layer5_in4_out3_lut[] = { 0.297289662994f, 0.081611603291f, 0.135578589406f, 0.081439939782f, 0.097986277470f, 0.089827107620f, 0.212931130297f, 0.229577939742f, 0.260065834015f, 0.313471321848f, 0.142120206652f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in4_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in4_out3_grid,
    .spline_kernel = KAN_LUT_test_layer5_in4_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in4_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in4_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in4_out4_spline_kernel[] = { 0.005452063866f, 0.050554778427f, 0.108601003885f, 0.116461165249f, 0.128724783659f, 0.000029165527f, 0.219409540296f, 0.322836697102f, 0.353467226028f, 0.011242385954f };
const port_float KAN_LUT_test_layer5_in4_out4_lut[] = { 0.028003421146f, 0.074354447151f, 0.110272442599f, 0.119412116183f, 0.101855762242f, 0.045959264473f, 0.197459066860f, 0.303919993710f, 0.332639220194f, 0.125602892161f, 0.004645614030f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in4_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in4_out4_grid,
    .spline_kernel = KAN_LUT_test_layer5_in4_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in4_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in4_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in4_out5_spline_kernel[] = { 0.058303486556f, 0.011760340072f, 0.030816247687f, 0.020635068417f, 0.000017016340f, 0.071145370603f, 0.062815248966f, 0.285877108574f, 0.115991197526f, 0.315826922655f };
const port_float KAN_LUT_test_layer5_in4_out5_lut[] = { 0.035031913314f, 0.019827009113f, 0.027093523921f, 0.015560999328f, 0.015782215481f, 0.062558208473f, 0.087098021153f, 0.229479564369f, 0.168351610060f, 0.243719478746f, 0.130506992833f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in4_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in4_out5_grid,
    .spline_kernel = KAN_LUT_test_layer5_in4_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in4_out5_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in5_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in5_out0_spline_kernel[] = { 0.470796495676f, 0.343881458044f, 0.118859641254f, 0.116619259119f, 0.027444565669f, 0.041919648647f, 0.071125514805f, 0.000034587698f, 0.019635980949f, 0.158467337489f };
const port_float KAN_LUT_test_layer5_in5_out0_lut[] = { 0.407338976860f, 0.251421678534f, 0.121829130156f, 0.093119189112f, 0.036271318401f, 0.044768963140f, 0.059436736461f, 0.015724991501f, 0.019615291035f, 0.109379696044f, 0.065482370863f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in5_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in5_out0_grid,
    .spline_kernel = KAN_LUT_test_layer5_in5_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in5_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in5_out1_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in5_out1_spline_kernel[] = { 0.211007609963f, 0.027357356623f, 0.000009350329f, 0.059078536928f, 0.066257551312f, 0.007491103839f, 0.076144307852f, 0.074644722044f, 0.084568642080f, 0.246873155236f };
const port_float KAN_LUT_test_layer5_in5_out1_lut[] = { 0.119182483293f, 0.016815412920f, 0.020232474873f, 0.058780331313f, 0.053883914303f, 0.023774891159f, 0.065776518638f, 0.075604484132f, 0.087980252560f, 0.188467542895f, 0.102013700511f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in5_out1 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in5_out1_grid,
    .spline_kernel = KAN_LUT_test_layer5_in5_out1_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in5_out1_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in5_out2_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in5_out2_spline_kernel[] = { 0.107592523098f, 0.166603028774f, 0.043674506247f, 0.072098888457f, 0.026830611750f, 0.000793385901f, 0.024106990546f, 0.061105486006f, 0.292063266039f, 0.097219198942f };
const port_float KAN_LUT_test_layer5_in5_out2_lut[] = { 0.137097775936f, 0.115562273574f, 0.055220328764f, 0.059070007675f, 0.024551555390f, 0.006951321494f, 0.024461009634f, 0.068883990977f, 0.223737255601f, 0.160828672657f, 0.040173222703f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in5_out2 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in5_out2_grid,
    .spline_kernel = KAN_LUT_test_layer5_in5_out2_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in5_out2_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in5_out3_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in5_out3_spline_kernel[] = { 0.000032598655f, 0.002771746134f, 0.193166166544f, 0.188042357564f, 0.135519474745f, 0.119069397449f, 0.009628001601f, 0.031672809273f, 0.000002355087f, 0.000002084807f };
const port_float KAN_LUT_test_layer5_in5_out3_lut[] = { 0.001402172395f, 0.081435807678f, 0.188304157416f, 0.174342563268f, 0.135661261264f, 0.104488247374f, 0.028185895990f, 0.025115276864f, 0.008378002340f, 0.000002140813f, 0.000000861490f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in5_out3 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in5_out3_grid,
    .spline_kernel = KAN_LUT_test_layer5_in5_out3_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in5_out3_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in5_out4_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in5_out4_spline_kernel[] = { 0.407347679138f, 0.639377057552f, 0.088856019080f, 0.142142459750f, 0.089189872146f, 0.291673898697f, 0.157958343625f, 0.000001428144f, 0.000000104882f, 0.524864852428f };
const port_float KAN_LUT_test_layer5_in5_out4_lut[] = { 0.523362368345f, 0.410930226041f, 0.115791084568f, 0.126156742508f, 0.133689701496f, 0.250864557183f, 0.161532050632f, 0.031984352468f, 0.019520218174f, 0.340511530276f, 0.216886302656f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in5_out4 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in5_out4_grid,
    .spline_kernel = KAN_LUT_test_layer5_in5_out4_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in5_out4_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer5_in5_out5_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer5_in5_out5_spline_kernel[] = { 0.066700443625f, 0.000005837758f, 0.065016806126f, 0.000004240299f, 0.006236991845f, 0.016814615577f, 0.107733875513f, 0.136933073401f, 0.198934718966f, 0.231158360839f };
const port_float KAN_LUT_test_layer5_in5_out5_lut[] = { 0.033353140692f, 0.027145471819f, 0.042181840401f, 0.004070393982f, 0.007966659358f, 0.029247065017f, 0.097225142412f, 0.135120121470f, 0.183735989465f, 0.216551962347f, 0.095519983818f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer5_in5_out5 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer5_in5_out5_grid,
    .spline_kernel = KAN_LUT_test_layer5_in5_out5_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer5_in5_out5_lut
};
    
const KAN_LUT *KAN_LUTs_test_layer5[] = {
    &KAN_LUT_test_layer5_in0_out0, &KAN_LUT_test_layer5_in0_out1, &KAN_LUT_test_layer5_in0_out2, &KAN_LUT_test_layer5_in0_out3, &KAN_LUT_test_layer5_in0_out4, &KAN_LUT_test_layer5_in0_out5,
    &KAN_LUT_test_layer5_in1_out0, &KAN_LUT_test_layer5_in1_out1, &KAN_LUT_test_layer5_in1_out2, &KAN_LUT_test_layer5_in1_out3, &KAN_LUT_test_layer5_in1_out4, &KAN_LUT_test_layer5_in1_out5,
    &KAN_LUT_test_layer5_in2_out0, &KAN_LUT_test_layer5_in2_out1, &KAN_LUT_test_layer5_in2_out2, &KAN_LUT_test_layer5_in2_out3, &KAN_LUT_test_layer5_in2_out4, &KAN_LUT_test_layer5_in2_out5,
    &KAN_LUT_test_layer5_in3_out0, &KAN_LUT_test_layer5_in3_out1, &KAN_LUT_test_layer5_in3_out2, &KAN_LUT_test_layer5_in3_out3, &KAN_LUT_test_layer5_in3_out4, &KAN_LUT_test_layer5_in3_out5,
    &KAN_LUT_test_layer5_in4_out0, &KAN_LUT_test_layer5_in4_out1, &KAN_LUT_test_layer5_in4_out2, &KAN_LUT_test_layer5_in4_out3, &KAN_LUT_test_layer5_in4_out4, &KAN_LUT_test_layer5_in4_out5,
    &KAN_LUT_test_layer5_in5_out0, &KAN_LUT_test_layer5_in5_out1, &KAN_LUT_test_layer5_in5_out2, &KAN_LUT_test_layer5_in5_out3, &KAN_LUT_test_layer5_in5_out4, &KAN_LUT_test_layer5_in5_out5,
};


const LayerKAN_LUT LayerKAN_LUT_test_layer5 = {
    .in_size = 6,
    .out_size = 6,
    .spline_kernel_size = 10,
    .kan_luts = KAN_LUTs_test_layer5
};


// KAN_LUT arrays
const port_float KAN_LUT_test_layer6_in0_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer6_in0_out0_spline_kernel[] = { 0.000003619610f, 0.078683406115f, 0.000019063866f, 0.008028800599f, 0.000007657161f, 0.000002698269f, 0.000000882806f, 0.099073514342f, 0.601456761360f, 0.262338280678f };
const port_float KAN_LUT_test_layer6_in0_out0_lut[] = { 0.039343512862f, 0.045852356481f, 0.004000245867f, 0.005609623696f, 0.000536976621f, 0.000002940483f, 0.010235928860f, 0.112228774702f, 0.455983231876f, 0.371508709655f, 0.108404248214f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer6_in0_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer6_in0_out0_grid,
    .spline_kernel = KAN_LUT_test_layer6_in0_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer6_in0_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer6_in1_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer6_in1_out0_spline_kernel[] = { 0.000000923434f, 0.049092352390f, 0.273028433323f, 0.000003027147f, 0.000001714998f, 0.000007695690f, 0.010818407871f, 0.000002070908f, 0.000004824492f, 0.000006152028f };
const port_float KAN_LUT_test_layer6_in1_out0_lut[] = { 0.024546637912f, 0.141425065879f, 0.177942473720f, 0.010156517552f, 0.000003012718f, 0.001615282968f, 0.008092812571f, 0.002192337720f, 0.000004145643f, 0.000005606001f, 0.000002542160f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer6_in1_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer6_in1_out0_grid,
    .spline_kernel = KAN_LUT_test_layer6_in1_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer6_in1_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer6_in2_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer6_in2_out0_spline_kernel[] = { 0.000001433271f, 0.000023297778f, 0.000012320475f, 0.000001140330f, 0.000002826410f, 0.034741152078f, 0.210457548499f, 0.121486134827f, 0.248096078634f, 0.073641046882f };
const port_float KAN_LUT_test_layer6_in2_out0_lut[] = { 0.000012365525f, 0.000018671353f, 0.000008759804f, 0.000002002026f, 0.007036508147f, 0.057292111291f, 0.175126657536f, 0.147871913219f, 0.208124460083f, 0.130815812933f, 0.030430184662f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer6_in2_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer6_in2_out0_grid,
    .spline_kernel = KAN_LUT_test_layer6_in2_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer6_in2_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer6_in3_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer6_in3_out0_spline_kernel[] = { 0.003819047473f, 0.006705074571f, 0.000000242144f, 0.031605355442f, 0.068952403963f, 0.000000330247f, 0.000006796957f, 0.007719409652f, 0.227315261960f, 0.226800024509f };
const port_float KAN_LUT_test_layer6_in3_out0_lut[] = { 0.005262061022f, 0.003922556927f, 0.010689636800f, 0.040306864060f, 0.052521807316f, 0.007124440348f, 0.000802592477f, 0.020676498970f, 0.169221164089f, 0.223223719284f, 0.093719018392f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer6_in3_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer6_in3_out0_grid,
    .spline_kernel = KAN_LUT_test_layer6_in3_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer6_in3_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer6_in4_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer6_in4_out0_spline_kernel[] = { 0.004693554249f, 0.003387883771f, 0.002258507302f, 0.038306873292f, 0.020647350699f, 0.008246242069f, 0.000963161117f, 0.000000279526f, 0.000003871690f, 0.085326455534f };
const port_float KAN_LUT_test_layer6_in4_out0_lut[] = { 0.004040719010f, 0.002926594612f, 0.014342950075f, 0.032295944615f, 0.019303954164f, 0.008443914802f, 0.001947123409f, 0.000195480653f, 0.003176075641f, 0.055357715395f, 0.035258865923f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer6_in4_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer6_in4_out0_grid,
    .spline_kernel = KAN_LUT_test_layer6_in4_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer6_in4_out0_lut
};
    

// KAN_LUT arrays
const port_float KAN_LUT_test_layer6_in5_out0_grid[] = { -0.250000000000f, -0.125000000000f, 0.000000000000f, 0.125000000000f, 0.250000000000f, 0.375000000000f, 0.500000000000f, 0.625000000000f, 0.750000000000f, 0.875000000000f, 1.000000000000f, 1.125000000000f, 1.250000000000f };
const port_float KAN_LUT_test_layer6_in5_out0_spline_kernel[] = { 0.000009488268f, 0.000003274460f, 0.000001742163f, 0.094558961689f, 0.004464605357f, 0.001342048636f, 0.000002835728f, 0.088092066348f, 0.103226728737f, 0.100339129567f };
const port_float KAN_LUT_test_layer6_in5_out0_lut[] = { 0.000006381364f, 0.000002666956f, 0.031651084770f, 0.067215764247f, 0.009789003795f, 0.001465405055f, 0.009302184613f, 0.071256456008f, 0.099116783343f, 0.099647142024f, 0.041462450234f, 0.000000000000f };

// KAN_LUT instance
const KAN_LUT KAN_LUT_test_layer6_in5_out0 = {
    .grid_size = 8,
    .spline_order = 2,
    .grid_range = { 0.000000000000f, 1.000000000000f },
    .grid = KAN_LUT_test_layer6_in5_out0_grid,
    .spline_kernel = KAN_LUT_test_layer6_in5_out0_spline_kernel,
    .lut_points = 10,
    .lut = KAN_LUT_test_layer6_in5_out0_lut
};
    
const KAN_LUT *KAN_LUTs_test_layer6[] = {
    &KAN_LUT_test_layer6_in0_out0,
    &KAN_LUT_test_layer6_in1_out0,
    &KAN_LUT_test_layer6_in2_out0,
    &KAN_LUT_test_layer6_in3_out0,
    &KAN_LUT_test_layer6_in4_out0,
    &KAN_LUT_test_layer6_in5_out0,
};


const LayerKAN_LUT LayerKAN_LUT_test_layer6 = {
    .in_size = 6,
    .out_size = 1,
    .spline_kernel_size = 10,
    .kan_luts = KAN_LUTs_test_layer6
};

const LayerKAN_LUT *LayerKAN_LUTs_test[] = {
    &LayerKAN_LUT_test_layer0,
    &LayerKAN_LUT_test_layer1,
    &LayerKAN_LUT_test_layer2,
    &LayerKAN_LUT_test_layer3,
    &LayerKAN_LUT_test_layer4,
    &LayerKAN_LUT_test_layer5,
    &LayerKAN_LUT_test_layer6,
};

const LayerIIR *LayerIIRs_test[] = {
    &LayerIIR_test_layer0,
};


const ModelKAN_LUT ModelKAN_LUT_test = {
    .num_layers = 7,
    .layers = LayerKAN_LUTs_test,
    .num_rnn_layers = 1,
    .rnn_layers = LayerIIRs_test
};
        