/*****************************************************************************
 * FILE:    Main
 * DATE:    2/7/2018
 * AUTHOR:  Tylor Bayer
 * COPYRIGHT: (c) 2018 Brigham Young University
 * LICENSE: BSD 2-Clause
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/
(function packageEPANETModelViewer() {

    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/

        //  ********** Model/Graph **********
        //  VARIABLES
    let s = {}, model = {}, locate, highlight = '#1affff',
        graphColors = {Junction: '#666', Vertex: "#666", Reservoir: '#5F9EA0', Tank: '#8B4513', Label: '#d6d6c2', Pipe: '#ccc',
            Pump: '#D2B48C', Valve: '#7070db' }, hoverColors = {Pipe: '#808080', Pump: '#DAA520', Valve: '#3333cc' },
        file_text = "", modelResults = {}, ranModel = false, needed = "<tr><td></td><td>(* required fields)</td></tr>",
        firstRun = true;
    //  QUERY SELECTORS
    let $initialModel, $fileDisplayArea, $btnRunModel, $chkAutoUpdate;
    //  FUNCTIONS
    let addModelToUI, setStateAfterLastModel, openModel, readModel, canvasClick, drawModel, setGraphEventListeners,
        resetModelState, updateInp, populateNodeList, populateEdgeList;


    //  ********** Node **********
    //  VARIABLES
    let curNode = {}, isAddNode = false, nodeModalLeft = 0;
    //  QUERY SELECTORS
    let $modalNode, $modalNodeLabel, $btnNodeLeft, $btnNodeRight, $chkNodeEdit, $btnNodeOk, $btnNodeCancel, $btnNodeDelete, $nodeX, $nodeY, $nodeTabs,
        $nodePlot, $nodeStats, $viewNodeResults, $multipleNodeSelect;
    //  CONSTANTS
    let nodeHtml = {
        Junction: "<tr><td><b>Id:</b></td><td><input type='text' id='epaId' class='inp-properties needed' readonly> *</td></tr><tr><td>Elev:</td><td><input type='number' id='elev' class='inp-properties needed' readonly> *</td></tr><tr><td>Demand:</td><td><input type='number' id='demand' class='inp-properties needed' readonly> *</td></tr><tr><td>Pattern:</td><td><div class='form-group' style='display: inline-block'><select id='pattern' class='form-control' disabled><option value=''></option></select></div></td></tr><tr><td>Quality:</td><td><input type='number' id='node-quality' class='inp-properties' readonly></td></tr>" + needed,
        Reservoir: "<tr><td><b>Id:</b></td><td><input type='text' id='epaId' class='inp-properties needed' readonly> *</td></tr><tr><td>Head:</td><td><input type='text' id='head' class='inp-properties needed' readonly> *</td></tr><tr><td>Pattern:</td><td><div class='form-group' style='display: inline-block'><select id='pattern' class='form-control' disabled><option value=''></option></select></div></td></tr><tr><td>Quality:</td><td><input type='number' id='node-quality' class='inp-properties' readonly></td></tr>" + needed,
        Tank: "<tr><td><b>Id:</b></td><td><input type='text' id='epaId' class='inp-properties needed' readonly> *</td></tr><tr><td>Elev:</td><td><input type='number' id='elevation' class='inp-properties needed' readonly> *</td></tr><tr><td>InitLevel:</td><td><input type='number' id='initlevel' class='inp-properties needed' readonly> *</td></tr><tr><td>MinLevel:</td><td><input type='number' id='minlevel' class='inp-properties needed' readonly> *</td></tr><tr><td>MaxLevel:</td><td><input type='number' id='maxlevel' class='inp-properties needed' readonly> *</td></tr><tr><td>Diameter:</td><td><input type='number' id='diameter' class='inp-properties needed' readonly> *</td></tr><tr><td>MinVol:</td><td><input type='number' id='minvol' class='inp-properties needed' readonly> *</td></tr><tr><td>VolCurve:</td><td><div class='form-group' style='display: inline-block'><select id='volcurve' class='form-control' disabled><option value=''></option></select></div></td></tr><tr><td>Quality:</td><td><input type='number' id='node-quality' class='inp-properties' readonly></td></tr>" + needed,
        Vertex: "<tr><td><b>Id:</b></td><td><input type='text' id='epaId' readonly></td></tr>",
        Label: "<tr><td><b>Label:</b></td><td><input type='text' id='epaId' readonly></td></tr>"
    };
    //  FUNCTIONS
    let nodeClick, populateNodeModal, previousNode, nextNode;


    //  ********** Edge **********
    //  VARIABLES
    let curEdge = {}, edgeSource = null, isAddEdge = false,  edgeModalLeft = 0, edgeVerts = [];
    //  QUERY SELECTORS
    let $modalEdge, $modalEdgeLabel, $btnEdgeLeft, $btnEdgeRight, $chkEdgeEdit, $btnEdgeOk, $btnEdgeCancel, $btnEdgeDelete, $edgeTabs, $edgePlot,
        $edgeStats, $viewEdgeResults;
    //  CONSTANTS
    let edgeHtml = {
        Pipe: "<tr><td><b>Id:</b></td><td><input type='text' id='epaId' class='inp-properties needed' readonly> *</td></tr><tr><td>Length:</td><td><input type='number' id='length' class='inp-properties needed' readonly> *</td></tr><tr><td>Diameter:</td><td><input type='number' id='diameter' class='inp-properties needed' readonly> *</td></tr><tr><td>Roughness:</td><td><input type='number' id='roughness' class='inp-properties needed' readonly> *</td></tr><tr><td>Minor Loss:</td><td><input type='number' id='minorloss' class='inp-properties needed' value='0' readonly> *</td></tr><tr><td>Status:</td><td><div class='form-group' style='display: inline-block'><select id='status' class='form-control needed' disabled><option value='Open'>Open</option><option value='Closed'>Closed</option><option value='CV'>CV</option></select></div> *</td></tr>" + needed,
        Pump: "<tr><td><b>Id:</b></td><td><input type='text' id='epaId' class='inp-properties needed' readonly> *</td></tr><tr><td>Parameters:</td><td><div class='form-group' style='display: inline-block'><select id='phead' class='form-control needed' disabled><option value='HEAD'>HEAD</option><option value='POWER'>POWER</option></select></div> *<br><input type='text' id='phid' class='inp-properties needed' readonly> *</td></tr><tr><td>Optional<br>Parameters:</td><td><div class='form-group' style='display: inline-block'><select id='opt' class='form-control' disabled><option value=''></option><option value='SPEED'>SPEED</option><option value='PATTERN'>PATTERN</option></select></div><br><input type='text' id='optid' class='inp-properties' readonly></td></tr>" + needed,
        Valve: "<tr><td><b>Id:</b></td><td><input type='text' id='epaId' class='inp-properties needed' readonly> *</td></tr><tr><td>Diameter:</td><td><input type='number' id='diameter' class='inp-properties needed' readonly> *</td></tr><tr><td>Type:</td><td><div class='form-group' style='display: inline-block'><select id='type' class='form-control needed' disabled><option value='PRV'>PRV</option><option value='PSV'>PSV</option><option value='PBV'>PBV</option><option value='FCV'>FCV</option><option value='TCV'>TCV</option><option value='GPV'>GPV</option></select></div> *</td></tr><tr><td>Setting:</td><td><input type='number' id='setting' class='inp-properties needed' readonly> *</td></tr><tr><td>Minor Loss:</td><td><input type='number' id='minorloss' class='inp-properties needed' value='0' readonly> *</td></tr>" + needed
    };
    //  FUNCTIONS
    let edgeClick, populateEdgeModal, previousEdge, nextEdge;


    //  ********** Model Options **********
    //  QUERY SELECTORS
    let $modelOptions, $chkOptionsEdit, $btnOptionsOk, $btnOptionsCancel;
    //  FUNCTIONS
    let populateModelOptions;
    //  ---------- Time
    //  QUERY SELECTORS
    let $modalTime, $chkTimeEdit, $btnTimeOk;
    //  FUNCTIONS
    let populateTimeModal;
    //  ---------- Energy
    //  QUERY SELECTORS
    let $modalEnergy, $chkEnergyEdit, $btnEnergyOk;
    //  FUNCTIONS
    let populateEnergyModal;
    //  ---------- Reactions
    //  QUERY SELECTORS
    let $modalReactions, $chkReactionsEdit, $btnReactionsOk;
    //  FUNCTIONS
    let populateReactionsModal;
    //  ---------- Report
    //  QUERY SELECTORS
    let $modalReport, $chkReportEdit, $btnReportOk;
    //  FUNCTIONS
    let populateReportModal;
    //  ---------- Curve
    //  VARIABLES
    let dataTableLoadModels;
    //  QUERY SELECTORS
    let $modalCurve, $chkCurveEdit, $btnCurveOk, $btnCurveDelete, $curveSelect, $inpCurveType,
        $curveDisplay, $curveTable, $btnAddCurve, $inpCurveId;
    //  CONSTANTS
    let curveGraphLabels = {
        PUMP: ['Flow', 'Head'],
        EFFICIENCY: ['Flow', 'Efficiency'],
        VOLUME: ['Water Level', 'Volume'],
        HEADLOSS: ['Flow', 'Headloss']
    };
    //  FUNCTIONS
    let populateCurvesModal, resetCurveState, drawCurve, setAddRemovePointListener;
    //  ---------- Pattern
    //  QUERY SELECTORS
    let $modalPattern, $chkPatternEdit, $btnPatternOk, $btnPatternDelete, $patternSelect, $inpPatternMults,
        $patternDisplay, $btnAddPattern, $inpPatternId;
    //  FUNCTIONS
    let populatePatternModal, resetPatternState, drawPattern;
    //  ---------- Controls
    //  QUERY SELECTORS
    let $modalControls, $chkControlsEdit, $btnControlsOk, $controlsDisplay, $btnAddControl, $controlType, $addControlView;
    //  CONSTANTS
    let controlsHtml = {
            'IF NODE': '<h6 style="display: inline-block;">LINK </h6><div class="animate form-group" style="display: inline-block"><select id="controls-links" class="form-control"></select></div><div id="controls-status" style="display: inline-block;"></div><h6 style="display: inline-block;"> IF NODE </h6><div class="form-group" style="display: inline-block"><select id="controls-nodes" class="form-control"></select></div><div class="form-group" style="display: inline-block"><select id="controls-condition" class="form-control"><option value="above">Above</option><option value="below">Below</option><option value="equals">Equals</option></select></div><input id="controls-value" type="number" style="display: inline-block;">',
            'AT TIME': '<h6 style="display: inline-block;">LINK </h6><div class="animate form-group" style="display: inline-block"><select id="controls-links" class="form-control"></select></div><div id="controls-status" style="display: inline-block;"></div><h6 style="display: inline-block;"> AT TIME </h6><input id="controls-value" type="text" style="display: inline-block;">',
            'AT CLOCKTIME': '<h6 style="display: inline-block;">LINK </h6><div class="animate form-group" style="display: inline-block"><select id="controls-links" class="form-control"></select></div><div id="controls-status" style="display: inline-block;"></div><h6 style="display: inline-block;"> AT CLOCKTIME </h6><input id="controls-value" type="text" style="display: inline-block;"><div class="form-group" style="display: inline-block"><select id="controls-clocktime" class="form-control"><option value="AM">AM</option><option value="PM">PM</option></select></div>',
        },
        statusHtml = {
            Pipe: '<div class="animate form-group" style="display: inline-block"><select class="form-control"><option value="OPEN">Open</option><option value="CLOSED">Closed</option><option value="CV">CV</option></select></div>',
            Pump: '<input type="number" style="display: inline-block;">',
            Valve: '<input type="number" style="display: inline-block;">'
        };
    //  FUNCTIONS
    let populateControlsModal, setAddRemoveControlListener;
    //  ---------- Rules
    //  QUERY SELECTORS
    let $modalRules, $chkRulesEdit, $btnRulesOk, $rulesDisplay, $btnAddRule, $inpRuleId, $inpRuleBody;
    //  CONSTANTS
    // let ruleAttrs = {
    //     NODE: ["DEMAND", "HEAD", "PRESSURE"],
    //     TANK: ["LEVEL", "FILLTIME", "DRAINTIME"],
    //     LINK: ["FLOW", "STATUS", "SETTING"],
    //     SYSTEM: ["DEMAND", "TIME", "CLOCKTIME"]
    // };
    //  FUNCTIONS
    let populateRulesModal, setAddRemoveRuleListener;


    //  ********** Upload **********
    //  QUERY SELECTORS
    let $inpUlTitle, $inpUlDescription, $inpUlKeywords, $btnUl, $btnUlCancel;
    //  FUNCTIONS
    let uploadModel, resetUploadState;


    //  ********** Animation **********
    //  VARIABLES
    let nodeAnimColor, edgeAnimColor, animate = [], animationMaxStep = 0, playing = false, animationDelay = 1000;
    //  QUERY SELECTORS
    let $btnAnimateTools, $animateToolbar, $btnPlayAnimation, $btnStopAnimation, $animationSpeed, $animationSlider,
        $chkNodes, $nodeLegend, $nodeAnimColor, $nodeAnimType, $chkEdges, $edgeLegend, $edgeAnimColor, $edgeAnimType;
    //  CONSTANTS
    let animationLegends = {
        RdYlBu: '<div class="gradient"><span class="grad-step" style="background-color:#313695"></span><span class="grad-step" style="background-color:#333c98"></span><span class="grad-step" style="background-color:#35439b"></span><span class="grad-step" style="background-color:#37499e"></span><span class="grad-step" style="background-color:#394fa1"></span><span class="grad-step" style="background-color:#3b56a5"></span><span class="grad-step" style="background-color:#3d5ca8"></span><span class="grad-step" style="background-color:#3f62ab"></span><span class="grad-step" style="background-color:#4168ae"></span><span class="grad-step" style="background-color:#436fb1"></span><span class="grad-step" style="background-color:#4575b4"></span><span class="grad-step" style="background-color:#4a7bb7"></span><span class="grad-step" style="background-color:#4e80ba"></span><span class="grad-step" style="background-color:#5386bd"></span><span class="grad-step" style="background-color:#588bc0"></span><span class="grad-step" style="background-color:#5d91c3"></span><span class="grad-step" style="background-color:#6197c5"></span><span class="grad-step" style="background-color:#669cc8"></span><span class="grad-step" style="background-color:#6ba2cb"></span><span class="grad-step" style="background-color:#6fa7ce"></span><span class="grad-step" style="background-color:#74add1"></span><span class="grad-step" style="background-color:#7ab1d3"></span><span class="grad-step" style="background-color:#7fb6d6"></span><span class="grad-step" style="background-color:#85bad8"></span><span class="grad-step" style="background-color:#8abfdb"></span><span class="grad-step" style="background-color:#90c3dd"></span><span class="grad-step" style="background-color:#95c7df"></span><span class="grad-step" style="background-color:#9bcce2"></span><span class="grad-step" style="background-color:#a0d0e4"></span><span class="grad-step" style="background-color:#a6d5e7"></span><span class="grad-step" style="background-color:#abd9e9"></span><span class="grad-step" style="background-color:#b0dceb"></span><span class="grad-step" style="background-color:#b6deec"></span><span class="grad-step" style="background-color:#bbe1ee"></span><span class="grad-step" style="background-color:#c0e3ef"></span><span class="grad-step" style="background-color:#c5e6f1"></span><span class="grad-step" style="background-color:#cbe9f2"></span><span class="grad-step" style="background-color:#d0ebf4"></span><span class="grad-step" style="background-color:#d5eef5"></span><span class="grad-step" style="background-color:#dbf0f7"></span><span class="grad-step" style="background-color:#e0f3f8"></span><span class="grad-step" style="background-color:#e3f4f2"></span><span class="grad-step" style="background-color:#e6f5ed"></span><span class="grad-step" style="background-color:#e9f7e7"></span><span class="grad-step" style="background-color:#ecf8e1"></span><span class="grad-step" style="background-color:#eff9dc"></span><span class="grad-step" style="background-color:#f3fad6"></span><span class="grad-step" style="background-color:#f6fbd0"></span><span class="grad-step" style="background-color:#f9fdca"></span><span class="grad-step" style="background-color:#fcfec5"></span><span class="grad-step" style="background-color:#ffffbf"></span><span class="grad-step" style="background-color:#fffcba"></span><span class="grad-step" style="background-color:#fff9b6"></span><span class="grad-step" style="background-color:#fff6b1"></span><span class="grad-step" style="background-color:#fff3ac"></span><span class="grad-step" style="background-color:#ffefa7"></span><span class="grad-step" style="background-color:#feeca3"></span><span class="grad-step" style="background-color:#fee99e"></span><span class="grad-step" style="background-color:#fee699"></span><span class="grad-step" style="background-color:#fee395"></span><span class="grad-step" style="background-color:#fee090"></span><span class="grad-step" style="background-color:#fedb8b"></span><span class="grad-step" style="background-color:#fed687"></span><span class="grad-step" style="background-color:#fed182"></span><span class="grad-step" style="background-color:#fecc7d"></span><span class="grad-step" style="background-color:#fec778"></span><span class="grad-step" style="background-color:#fdc274"></span><span class="grad-step" style="background-color:#fdbd6f"></span><span class="grad-step" style="background-color:#fdb86a"></span><span class="grad-step" style="background-color:#fdb366"></span><span class="grad-step" style="background-color:#fdae61"></span><span class="grad-step" style="background-color:#fca85e"></span><span class="grad-step" style="background-color:#fba15b"></span><span class="grad-step" style="background-color:#fa9b58"></span><span class="grad-step" style="background-color:#f99455"></span><span class="grad-step" style="background-color:#f98e52"></span><span class="grad-step" style="background-color:#f8874f"></span><span class="grad-step" style="background-color:#f7814c"></span><span class="grad-step" style="background-color:#f67a49"></span><span class="grad-step" style="background-color:#f57346"></span><span class="grad-step" style="background-color:#f46d43"></span><span class="grad-step" style="background-color:#f16740"></span><span class="grad-step" style="background-color:#ee613d"></span><span class="grad-step" style="background-color:#eb5b3b"></span><span class="grad-step" style="background-color:#e85538"></span><span class="grad-step" style="background-color:#e64f35"></span><span class="grad-step" style="background-color:#e34832"></span><span class="grad-step" style="background-color:#e0422f"></span><span class="grad-step" style="background-color:#dd3c2d"></span><span class="grad-step" style="background-color:#da362a"></span><span class="grad-step" style="background-color:#d73027"></span><span class="grad-step" style="background-color:#d22b27"></span><span class="grad-step" style="background-color:#cd2627"></span><span class="grad-step" style="background-color:#c82227"></span><span class="grad-step" style="background-color:#c31d27"></span><span class="grad-step" style="background-color:#be1827"></span><span class="grad-step" style="background-color:#b91326"></span><span class="grad-step" style="background-color:#b40e26"></span><span class="grad-step" style="background-color:#af0a26"></span><span class="grad-step" style="background-color:#aa0526"></span><span class="grad-step" style="background-color:#a50026"></span><span class="domain-min"></span><span class="domain-med"></span><span class="domain-max"></span></div>',
        YlGnBu: '<div class="gradient"><span class="grad-step" style="background-color:#ffffd9"></span><span class="grad-step" style="background-color:#fefed6"></span><span class="grad-step" style="background-color:#fcfed3"></span><span class="grad-step" style="background-color:#fbfdcf"></span><span class="grad-step" style="background-color:#f9fdcc"></span><span class="grad-step" style="background-color:#f8fcc9"></span><span class="grad-step" style="background-color:#f6fcc6"></span><span class="grad-step" style="background-color:#f5fbc3"></span><span class="grad-step" style="background-color:#f3fbbf"></span><span class="grad-step" style="background-color:#f2fabc"></span><span class="grad-step" style="background-color:#f1f9b9"></span><span class="grad-step" style="background-color:#eff9b6"></span><span class="grad-step" style="background-color:#eef8b3"></span><span class="grad-step" style="background-color:#ebf7b1"></span><span class="grad-step" style="background-color:#e8f6b1"></span><span class="grad-step" style="background-color:#e5f5b2"></span><span class="grad-step" style="background-color:#e2f4b2"></span><span class="grad-step" style="background-color:#dff3b2"></span><span class="grad-step" style="background-color:#dcf1b2"></span><span class="grad-step" style="background-color:#d9f0b3"></span><span class="grad-step" style="background-color:#d6efb3"></span><span class="grad-step" style="background-color:#d3eeb3"></span><span class="grad-step" style="background-color:#d0edb3"></span><span class="grad-step" style="background-color:#cdebb4"></span><span class="grad-step" style="background-color:#caeab4"></span><span class="grad-step" style="background-color:#c7e9b4"></span><span class="grad-step" style="background-color:#c1e7b5"></span><span class="grad-step" style="background-color:#bbe5b5"></span><span class="grad-step" style="background-color:#b6e2b6"></span><span class="grad-step" style="background-color:#b0e0b6"></span><span class="grad-step" style="background-color:#aadeb7"></span><span class="grad-step" style="background-color:#a4dcb7"></span><span class="grad-step" style="background-color:#9fd9b8"></span><span class="grad-step" style="background-color:#99d7b8"></span><span class="grad-step" style="background-color:#93d5b9"></span><span class="grad-step" style="background-color:#8dd3ba"></span><span class="grad-step" style="background-color:#88d0ba"></span><span class="grad-step" style="background-color:#82cebb"></span><span class="grad-step" style="background-color:#7dccbb"></span><span class="grad-step" style="background-color:#78cabc"></span><span class="grad-step" style="background-color:#73c8bd"></span><span class="grad-step" style="background-color:#6ec7be"></span><span class="grad-step" style="background-color:#69c5be"></span><span class="grad-step" style="background-color:#64c3bf"></span><span class="grad-step" style="background-color:#5fc1c0"></span><span class="grad-step" style="background-color:#5abfc0"></span><span class="grad-step" style="background-color:#55bdc1"></span><span class="grad-step" style="background-color:#50bcc2"></span><span class="grad-step" style="background-color:#4bbac3"></span><span class="grad-step" style="background-color:#46b8c3"></span><span class="grad-step" style="background-color:#41b6c4"></span><span class="grad-step" style="background-color:#3eb3c4"></span><span class="grad-step" style="background-color:#3bb0c3"></span><span class="grad-step" style="background-color:#38adc3"></span><span class="grad-step" style="background-color:#35aac3"></span><span class="grad-step" style="background-color:#33a7c2"></span><span class="grad-step" style="background-color:#30a4c2"></span><span class="grad-step" style="background-color:#2da1c2"></span><span class="grad-step" style="background-color:#2a9ec1"></span><span class="grad-step" style="background-color:#279bc1"></span><span class="grad-step" style="background-color:#2498c1"></span><span class="grad-step" style="background-color:#2195c0"></span><span class="grad-step" style="background-color:#1e92c0"></span><span class="grad-step" style="background-color:#1d8fbf"></span><span class="grad-step" style="background-color:#1e8bbd"></span><span class="grad-step" style="background-color:#1e87bb"></span><span class="grad-step" style="background-color:#1e83b9"></span><span class="grad-step" style="background-color:#1f7fb7"></span><span class="grad-step" style="background-color:#1f7bb5"></span><span class="grad-step" style="background-color:#2076b4"></span><span class="grad-step" style="background-color:#2072b2"></span><span class="grad-step" style="background-color:#206eb0"></span><span class="grad-step" style="background-color:#216aae"></span><span class="grad-step" style="background-color:#2166ac"></span><span class="grad-step" style="background-color:#2262aa"></span><span class="grad-step" style="background-color:#225ea8"></span><span class="grad-step" style="background-color:#225ba6"></span><span class="grad-step" style="background-color:#2257a5"></span><span class="grad-step" style="background-color:#2354a3"></span><span class="grad-step" style="background-color:#2351a2"></span><span class="grad-step" style="background-color:#234da0"></span><span class="grad-step" style="background-color:#234a9e"></span><span class="grad-step" style="background-color:#24469d"></span><span class="grad-step" style="background-color:#24439b"></span><span class="grad-step" style="background-color:#24409a"></span><span class="grad-step" style="background-color:#243c98"></span><span class="grad-step" style="background-color:#253996"></span><span class="grad-step" style="background-color:#253695"></span><span class="grad-step" style="background-color:#243392"></span><span class="grad-step" style="background-color:#22318d"></span><span class="grad-step" style="background-color:#1f2f88"></span><span class="grad-step" style="background-color:#1d2e83"></span><span class="grad-step" style="background-color:#1b2c7e"></span><span class="grad-step" style="background-color:#182a7a"></span><span class="grad-step" style="background-color:#162875"></span><span class="grad-step" style="background-color:#142670"></span><span class="grad-step" style="background-color:#11246b"></span><span class="grad-step" style="background-color:#0f2366"></span><span class="grad-step" style="background-color:#0d2162"></span><span class="grad-step" style="background-color:#0a1f5d"></span><span class="grad-step" style="background-color:#081d58"></span><span class="domain-min"></span><span class="domain-med"></span><span class="domain-max"></span></div>',
        OrRd: '<div class="gradient"><span class="grad-step" style="background-color:#fff7ec"></span><span class="grad-step" style="background-color:#fff6e9"></span><span class="grad-step" style="background-color:#fff5e6"></span><span class="grad-step" style="background-color:#fff3e3"></span><span class="grad-step" style="background-color:#fff2e0"></span><span class="grad-step" style="background-color:#fff1de"></span><span class="grad-step" style="background-color:#fff0db"></span><span class="grad-step" style="background-color:#feefd8"></span><span class="grad-step" style="background-color:#feedd5"></span><span class="grad-step" style="background-color:#feecd2"></span><span class="grad-step" style="background-color:#feebcf"></span><span class="grad-step" style="background-color:#feeacc"></span><span class="grad-step" style="background-color:#fee9c9"></span><span class="grad-step" style="background-color:#fee7c6"></span><span class="grad-step" style="background-color:#fee6c3"></span><span class="grad-step" style="background-color:#fee4c0"></span><span class="grad-step" style="background-color:#fee2bc"></span><span class="grad-step" style="background-color:#fee1b9"></span><span class="grad-step" style="background-color:#fedfb6"></span><span class="grad-step" style="background-color:#fddeb2"></span><span class="grad-step" style="background-color:#fddcaf"></span><span class="grad-step" style="background-color:#fddaab"></span><span class="grad-step" style="background-color:#fdd9a8"></span><span class="grad-step" style="background-color:#fdd7a5"></span><span class="grad-step" style="background-color:#fdd6a1"></span><span class="grad-step" style="background-color:#fdd49e"></span><span class="grad-step" style="background-color:#fdd29c"></span><span class="grad-step" style="background-color:#fdd09a"></span><span class="grad-step" style="background-color:#fdce98"></span><span class="grad-step" style="background-color:#fdcc96"></span><span class="grad-step" style="background-color:#fdca94"></span><span class="grad-step" style="background-color:#fdc892"></span><span class="grad-step" style="background-color:#fdc68f"></span><span class="grad-step" style="background-color:#fdc48d"></span><span class="grad-step" style="background-color:#fdc28b"></span><span class="grad-step" style="background-color:#fdc089"></span><span class="grad-step" style="background-color:#fdbe87"></span><span class="grad-step" style="background-color:#fdbc85"></span><span class="grad-step" style="background-color:#fdb982"></span><span class="grad-step" style="background-color:#fdb57f"></span><span class="grad-step" style="background-color:#fdb27b"></span><span class="grad-step" style="background-color:#fdae78"></span><span class="grad-step" style="background-color:#fdaa75"></span><span class="grad-step" style="background-color:#fda771"></span><span class="grad-step" style="background-color:#fca36e"></span><span class="grad-step" style="background-color:#fc9f6a"></span><span class="grad-step" style="background-color:#fc9c67"></span><span class="grad-step" style="background-color:#fc9863"></span><span class="grad-step" style="background-color:#fc9460"></span><span class="grad-step" style="background-color:#fc915c"></span><span class="grad-step" style="background-color:#fc8d59"></span><span class="grad-step" style="background-color:#fb8a58"></span><span class="grad-step" style="background-color:#fa8756"></span><span class="grad-step" style="background-color:#f98355"></span><span class="grad-step" style="background-color:#f88054"></span><span class="grad-step" style="background-color:#f77d52"></span><span class="grad-step" style="background-color:#f67a51"></span><span class="grad-step" style="background-color:#f5774f"></span><span class="grad-step" style="background-color:#f4734e"></span><span class="grad-step" style="background-color:#f3704d"></span><span class="grad-step" style="background-color:#f26d4b"></span><span class="grad-step" style="background-color:#f16a4a"></span><span class="grad-step" style="background-color:#f06749"></span><span class="grad-step" style="background-color:#ee6346"></span><span class="grad-step" style="background-color:#ec5f43"></span><span class="grad-step" style="background-color:#ea5a40"></span><span class="grad-step" style="background-color:#e8563d"></span><span class="grad-step" style="background-color:#e65239"></span><span class="grad-step" style="background-color:#e44e36"></span><span class="grad-step" style="background-color:#e34933"></span><span class="grad-step" style="background-color:#e1452f"></span><span class="grad-step" style="background-color:#df412c"></span><span class="grad-step" style="background-color:#dd3d29"></span><span class="grad-step" style="background-color:#db3826"></span><span class="grad-step" style="background-color:#d93422"></span><span class="grad-step" style="background-color:#d7301f"></span><span class="grad-step" style="background-color:#d42c1d"></span><span class="grad-step" style="background-color:#d1281a"></span><span class="grad-step" style="background-color:#ce2418"></span><span class="grad-step" style="background-color:#cb2115"></span><span class="grad-step" style="background-color:#c91d13"></span><span class="grad-step" style="background-color:#c61910"></span><span class="grad-step" style="background-color:#c3150e"></span><span class="grad-step" style="background-color:#c0110b"></span><span class="grad-step" style="background-color:#bd0d09"></span><span class="grad-step" style="background-color:#ba0a06"></span><span class="grad-step" style="background-color:#b70604"></span><span class="grad-step" style="background-color:#b40201"></span><span class="grad-step" style="background-color:#b10000"></span><span class="grad-step" style="background-color:#ad0000"></span><span class="grad-step" style="background-color:#a90000"></span><span class="grad-step" style="background-color:#a40000"></span><span class="grad-step" style="background-color:#a00000"></span><span class="grad-step" style="background-color:#9c0000"></span><span class="grad-step" style="background-color:#980000"></span><span class="grad-step" style="background-color:#940000"></span><span class="grad-step" style="background-color:#900000"></span><span class="grad-step" style="background-color:#8b0000"></span><span class="grad-step" style="background-color:#870000"></span><span class="grad-step" style="background-color:#830000"></span><span class="grad-step" style="background-color:#7f0000"></span><span class="domain-min"></span><span class="domain-med"></span><span class="domain-max"></span></div>',
        Spectral: '<div class="gradient"><span class="grad-step" style="background-color:#5e4fa2"></span><span class="grad-step" style="background-color:#5a55a5"></span><span class="grad-step" style="background-color:#555aa7"></span><span class="grad-step" style="background-color:#5160aa"></span><span class="grad-step" style="background-color:#4c66ad"></span><span class="grad-step" style="background-color:#486cb0"></span><span class="grad-step" style="background-color:#4471b2"></span><span class="grad-step" style="background-color:#3f77b5"></span><span class="grad-step" style="background-color:#3b7db8"></span><span class="grad-step" style="background-color:#3682ba"></span><span class="grad-step" style="background-color:#3288bd"></span><span class="grad-step" style="background-color:#378ebb"></span><span class="grad-step" style="background-color:#3c94b8"></span><span class="grad-step" style="background-color:#4299b6"></span><span class="grad-step" style="background-color:#479fb3"></span><span class="grad-step" style="background-color:#4ca5b1"></span><span class="grad-step" style="background-color:#51abaf"></span><span class="grad-step" style="background-color:#56b1ac"></span><span class="grad-step" style="background-color:#5cb6aa"></span><span class="grad-step" style="background-color:#61bca7"></span><span class="grad-step" style="background-color:#66c2a5"></span><span class="grad-step" style="background-color:#6dc5a5"></span><span class="grad-step" style="background-color:#74c7a5"></span><span class="grad-step" style="background-color:#7bcaa5"></span><span class="grad-step" style="background-color:#82cda5"></span><span class="grad-step" style="background-color:#89d0a5"></span><span class="grad-step" style="background-color:#8fd2a4"></span><span class="grad-step" style="background-color:#96d5a4"></span><span class="grad-step" style="background-color:#9dd8a4"></span><span class="grad-step" style="background-color:#a4daa4"></span><span class="grad-step" style="background-color:#abdda4"></span><span class="grad-step" style="background-color:#b1dfa3"></span><span class="grad-step" style="background-color:#b7e2a2"></span><span class="grad-step" style="background-color:#bde4a0"></span><span class="grad-step" style="background-color:#c3e79f"></span><span class="grad-step" style="background-color:#c8e99e"></span><span class="grad-step" style="background-color:#ceeb9d"></span><span class="grad-step" style="background-color:#d4ee9c"></span><span class="grad-step" style="background-color:#daf09a"></span><span class="grad-step" style="background-color:#e0f399"></span><span class="grad-step" style="background-color:#e6f598"></span><span class="grad-step" style="background-color:#e8f69c"></span><span class="grad-step" style="background-color:#ebf7a0"></span><span class="grad-step" style="background-color:#edf8a4"></span><span class="grad-step" style="background-color:#f0f9a8"></span><span class="grad-step" style="background-color:#f3faab"></span><span class="grad-step" style="background-color:#f5fbaf"></span><span class="grad-step" style="background-color:#f8fcb3"></span><span class="grad-step" style="background-color:#fafdb7"></span><span class="grad-step" style="background-color:#fdfebb"></span><span class="grad-step" style="background-color:#ffffbf"></span><span class="grad-step" style="background-color:#fffcba"></span><span class="grad-step" style="background-color:#fff9b5"></span><span class="grad-step" style="background-color:#fff6af"></span><span class="grad-step" style="background-color:#fff3aa"></span><span class="grad-step" style="background-color:#ffefa5"></span><span class="grad-step" style="background-color:#feeca0"></span><span class="grad-step" style="background-color:#fee99b"></span><span class="grad-step" style="background-color:#fee695"></span><span class="grad-step" style="background-color:#fee390"></span><span class="grad-step" style="background-color:#fee08b"></span><span class="grad-step" style="background-color:#fedb87"></span><span class="grad-step" style="background-color:#fed683"></span><span class="grad-step" style="background-color:#fed17e"></span><span class="grad-step" style="background-color:#fecc7a"></span><span class="grad-step" style="background-color:#fec776"></span><span class="grad-step" style="background-color:#fdc272"></span><span class="grad-step" style="background-color:#fdbd6e"></span><span class="grad-step" style="background-color:#fdb869"></span><span class="grad-step" style="background-color:#fdb365"></span><span class="grad-step" style="background-color:#fdae61"></span><span class="grad-step" style="background-color:#fca85e"></span><span class="grad-step" style="background-color:#fba15b"></span><span class="grad-step" style="background-color:#fa9b58"></span><span class="grad-step" style="background-color:#f99455"></span><span class="grad-step" style="background-color:#f98e52"></span><span class="grad-step" style="background-color:#f8874f"></span><span class="grad-step" style="background-color:#f7814c"></span><span class="grad-step" style="background-color:#f67a49"></span><span class="grad-step" style="background-color:#f57346"></span><span class="grad-step" style="background-color:#f46d43"></span><span class="grad-step" style="background-color:#f16844"></span><span class="grad-step" style="background-color:#ee6445"></span><span class="grad-step" style="background-color:#eb5f47"></span><span class="grad-step" style="background-color:#e85a48"></span><span class="grad-step" style="background-color:#e55649"></span><span class="grad-step" style="background-color:#e1514a"></span><span class="grad-step" style="background-color:#de4c4b"></span><span class="grad-step" style="background-color:#db474d"></span><span class="grad-step" style="background-color:#d8434e"></span><span class="grad-step" style="background-color:#d53e4f"></span><span class="grad-step" style="background-color:#d0384e"></span><span class="grad-step" style="background-color:#ca324c"></span><span class="grad-step" style="background-color:#c42c4b"></span><span class="grad-step" style="background-color:#bf264a"></span><span class="grad-step" style="background-color:#ba2049"></span><span class="grad-step" style="background-color:#b41947"></span><span class="grad-step" style="background-color:#af1346"></span><span class="grad-step" style="background-color:#a90d45"></span><span class="grad-step" style="background-color:#a40743"></span><span class="grad-step" style="background-color:#9e0142"></span><span class="domain-min"></span><span class="domain-med"></span><span class="domain-max"></span></div>'
    };
    //  FUNCTIONS
    let resetPlay, stopAnimation, resetAnimation, resetNodeAnim, resetEdgeAnim;


    //  ********** Query **********
    //  VARIABLES
    let queryElements = [];
    //  QUERY SELECTORS
    let $btnQueryTools, $btnQuery, $btnClearQuery, $queryToolbar, $queryType, $queryResult, $queryCondintion, $queryValue,
        $queryCount, $queryTimestep;
    //  CONSTANTS
    let queryResults = {
        nodes: '<option value="EN_HEAD">Head</option><option value="EN_PRESSURE">Pressure</option><option value="EN_DEMAND">Demand</option><option value="EN_QUALITY">Quality</option>',
        edges: '<option value="EN_FLOW">Flow</option><option value="EN_VELOCITY">Velocity</option><option value="EN_ENERGY">Energy</option><option value="EN_HEADLOSS">Head Loss</option>'
    };


    //  ********** Editing **********
    //  VARIABLES
    let addType = "";
    //  QUERY SELECTORS
    let $btnEditTools, $editToolbar, $btnEditDefualt;


    //  ********** Results Overview **********
    //  VARIABLES
    let resultsNodes = [], resultsEdges = [];
    //  QUERY SELECTORS
    let $ddNodes, $chkNodesFullResults, $nodesPlot, $nodesStats, $nodesFullResults, $ddEdges, $chkEdgesFullResults,
        $edgesPlot, $edgesStats, $edgesFullResults;
    // FUNCTIONS
    let populateNodesResults, populateEdgesResults, resetResultsOverview;


    //  ********** Other **********
    //  VARIABLES
    let showLog = false;
    //  QUERY SELECTORS
    let $modalLog, $loadFromLocal, $viewTabs, $loadingModel, $loadingAnimation;
    //  FUNCTIONS
    let initializeJqueryVariables, addInitialEventListeners, addMetadataToUI, hideMainLoadAnim, addLogEntry,
        showLoadingCompleteStatus, checkCsrfSafe, getCookie, addDefaultBehaviorToAjax;


    /******************************************************
     *               FUNCTION DECLARATIONS
     ******************************************************/

    /*-----------------------------------------------
     ************ Model/Graph FUNCTIONS ************
     ----------------------------------------------*/
    addModelToUI = function (result) {
        $fileDisplayArea.innerText = result;

        setStateAfterLastModel();
    };

    setStateAfterLastModel = function () {
        hideMainLoadAnim();
        if (showLog) {
            $modalLog.modal('show');
            showLog = false;
        } else {
            showLoadingCompleteStatus(true, 'Resource(s) added successfully!');
        }
    };

    openModel = function (modelId) {
        let data = {'model_id': modelId};

        $('#view-tabs').addClass('hidden');
        $('#loading-model').removeClass('hidden');

        $.ajax({
            type: 'GET',
            url: '/apps/epanet-model-viewer/get-epanet-model',
            dataType: 'json',
            data: data,
            error: function () {
                let message = 'An unexpected error ocurred while processing the following model ' +
                    '<a href="https://www.hydroshare.org/resource/' + modelId + '" target="_blank">' +
                    modelId + '</a>. An app admin has been notified.';

                addLogEntry('danger', message, true);
            },
            success: function (response) {
                let message;

                if (response.hasOwnProperty('success')) {
                    if (response.hasOwnProperty('message')) {
                        message = response.message;
                    }

                    if (!response.success) {
                        if (!message) {
                            message = 'An unexpected error ocurred while processing the following model ' +
                                '<a href="https://www.hydroshare.org/resource/' + modelId + '" target="_blank">' +
                                modelId + '</a>. An app admin has been notified.';
                        }

                        addLogEntry('danger', message, true);
                    } else {
                        if (message) {
                            addLogEntry('warning', message, true);
                        }
                        if (response.hasOwnProperty('results')) {
                            file_text = response.results;
                            addModelToUI(response.results);
                            addMetadataToUI(response.metadata);
                            populateTimeModal();
                        }
                    }
                }
            }
        });
    };

    readModel = function () {
        let epanetReader = new EPANET_Reader(file_text);

        model = epanetReader.getModel();
        console.log(model);

        // if (model.nodes.length < 2)
        //     model.nodes = s.graph.nodes();
    };

    canvasClick = function(e) {
        if(!e.data.captor.isDragging && (isAddNode || edgeSource !== null)) {
            $('#node-dialog').css({top: e.data.captor.clientY - 10, left: e.data.captor.clientX * 2 - 1600});

            curNode = {};

            let newX,
                newY;

            let _renderer = e.data.renderer,
                _camera = e.data.renderer.camera,
                _prefix = _renderer.options.prefix;

            let offset = calculateOffset(_renderer.container),
                x = event.clientX - offset.left,
                y = event.clientY - offset.top,
                cos = Math.cos(_camera.angle),
                sin = Math.sin(_camera.angle),
                nodes = s.graph.nodes(),
                ref = [];

            // Getting and derotating the reference coordinates.
            for (let i = 0; i < 2; i++) {
                let n = nodes[i];
                let aux = {
                    x: n.x * cos + n.y * sin,
                    y: n.y * cos - n.x * sin,
                    renX: n[_prefix + 'x'],
                    renY: n[_prefix + 'y'],
                };
                ref.push(aux);
            }

            // Applying linear interpolation.
            // if the nodes are on top of each other, we use the camera ratio to interpolate
            if (ref[0].x === ref[1].x && ref[0].y === ref[1].y) {
                let xRatio = (ref[0].renX === 0) ? 1 : ref[0].renX;
                let yRatio = (ref[0].renY === 0) ? 1 : ref[0].renY;
                x = (ref[0].x / xRatio) * (x - ref[0].renX) + ref[0].x;
                y = (ref[0].y / yRatio) * (y - ref[0].renY) + ref[0].y;
            } else {
                let xRatio = (ref[1].renX - ref[0].renX) / (ref[1].x - ref[0].x);
                let yRatio = (ref[1].renY - ref[0].renY) / (ref[1].y - ref[0].y);

                // if the coordinates are the same, we use the other ratio to interpolate
                if (ref[1].x === ref[0].x) {
                    xRatio = yRatio;
                }

                if (ref[1].y === ref[0].y) {
                    yRatio = xRatio;
                }

                x = (x - ref[0].renX) / xRatio + ref[0].x;
                y = (y - ref[0].renY) / yRatio + ref[0].y;
            }

            // Rotating the coordinates.
            newX = x * cos - y * sin;
            newY = y * cos + x * sin;

            $nodeX.html(newX);
            $nodeY.html(newY);

            curNode.properties = {};
            if (edgeSource !== null) {
                curNode.epaType = "Vertex";
                populateNodeModal(true);
                $btnNodeOk.click();
            }
            else {
                curNode.epaType = addType;
                populateNodeModal();
                if (!$chkNodeEdit.is(':checked'))
                    $chkNodeEdit.trigger('click');
                $btnNodeDelete.attr('disabled', true);
            }
        }
    };

    drawModel = function() {
        let maxNSize = 6, maxESize = 4, nPowRat = 0.2, ePowRat = 0.1;
        if (parseInt(model.nodes.length) > 1000) {
            maxNSize = 2;
            maxESize = 2;
            nPowRat = 0.2;
            ePowRat = 0.2;
        };

        if (!$chkAutoUpdate.is(':checked')) {
            model.nodes = s.graph.nodes();
            model.edges = s.graph.edges();
        }

        s = new sigma({
            graph: model,
            renderer: {
                container: $("#model-container")[0],
                type: 'canvas'
            },
            settings: {
                minNodeSize: 0,
                maxNodeSize: maxNSize,
                minEdgeSize: 0.5,
                maxEdgeSize: maxESize,
                enableEdgeHovering: true,
                edgeHoverSizeRatio: 1.5,
                nodesPowRatio: nPowRat,
                edgesPowRatio: ePowRat,
                immutable: false,
                drawEdgeLabels: false, // change to true to display edge labels
                // add showLabel: true to each node to display label always
            }
        });

        let conf = {
            animation: {
                node: {
                    duration: 800
                },
                edge: {
                    duration: 800
                },
                center: {
                    duration: 300
                }
            },
            //focusOut: true,
            zoomDef: 1
        };
        locate = sigma.plugins.locate(s, conf);

        s.cameras[0].goTo({ratio: 1.2});

        setGraphEventListeners();

        s.refresh();
    };

    setGraphEventListeners = function () {
        s.bind('clickStage', function(e) {
            canvasClick(e);
        });

        s.bind('clickNodes', function(e) {
            nodeClick(e);
        });

        s.bind('clickEdges', function(e) {
            edgeClick(e);
        });
    };

    resetModelState = function() {
        s.refresh();
        $nodePlot.empty();
        $nodeStats.empty();
        $edgePlot.empty();
        $edgeStats.empty();

        for (let i in s.graph.nodes())
            s.graph.nodes()[i].color = s.graph.nodes()[i].epaColor;

        for (let i in s.graph.edges())
            s.graph.edges()[i].color = s.graph.edges()[i].epaColor;
    };

    updateInp = function () {
        if ($chkAutoUpdate.is(':checked')) {

            $("#loading-animation-update").removeAttr('hidden');

            // setTimeout(function() {
                model.nodes = s.graph.nodes();
                model.edges = s.graph.edges();

                getEPANETObject(model);
            // }, 8000);
        }
    };

    populateNodeList = function ($selectEl) {
        $selectEl.empty();

        s.graph.nodes().forEach(function(n) {
            if (n.epaType !== "Vertex" && n.epaType !== "Label") {
                let optionElt = document.createElement("option");
                optionElt.text = n.epaType + ' ' + n.id;
                optionElt.value = n.id;
                $selectEl.append(optionElt);
            }
        });
    };

    populateEdgeList = function ($selectEl) {
        $selectEl.empty();

        s.graph.edges().forEach(function(n) {
            let optionElt = document.createElement("option");
            optionElt.text = n.epaType + ' ' + n.id;
            optionElt.value = n.id;
            $selectEl.append(optionElt);
        });
    };

    let getEPANETObject = async function(model) {
        let epanetWriter = new EPANET_Writer(model);

         $fileDisplayArea.innerText = epanetWriter.getFile();
         file_text = epanetWriter.getFile();
    };


    /*-----------------------------------------------
     ************ Node FUNCTIONS ************
     ----------------------------------------------*/
    nodeClick = function (e) {
        if(!e.data.captor.isDragging) {
            nodeModalLeft = e.data.captor.clientX * 2 - 1600;
            $('#node-dialog').css({top: e.data.captor.clientY - 10, left: nodeModalLeft});

            let curNodes = e.data.node;
            if (curNodes.length > 1) {
                $multipleNodeSelect.empty();
                $multipleNodeSelect.append('<p>Select a Node to display</p>');

                let selectHtml = "<select id='select-node-edge'>";
                for (let i in curNodes) {
                    selectHtml += "<option value='" + i + "'>" + curNodes[i].epaType + " " + curNodes[i].properties.epaId + "</option>";
                }
                selectHtml += "</select";
                $multipleNodeSelect.append(selectHtml);
                $multipleNodeSelect.dialog({
                    title: "Node Select",
                    dialogClass: "no-close",
                    resizable: false,
                    height: "auto",
                    width: 400,
                    modal: true,
                    buttons: {
                        Ok: function () {
                            curNode = curNodes[$('#select-node-edge').val()];
                            populateNodeModal();
                            $(this).dialog("close");
                        },
                        Cancel: function () {
                            $(this).dialog("close");
                        }
                    }
                });

                $multipleNodeSelect.dialog("open");
            }
            else {
                curNode = curNodes[0];

                if (isAddEdge) {
                    if (curNode.epaType === "Label" || curNode.epaType === "Vertex")
                        alert("Can't create edges off of Vertices or Labels");
                    else {
                        if (edgeSource !== null && edgeSource.properties.epaId !== curNode.properties.epaId) {
                            $('#edge-dialog').css({top: e.data.captor.clientY - 10, left: e.data.captor.clientX * 2 - 1600});

                            curEdge = {};
                            curNode.color = highlight;

                            curEdge.epaType = addType;
                            curEdge.properties = {epaId: ''};
                            populateEdgeModal();
                            $chkEdgeEdit.trigger('click');
                        }
                        else {
                            edgeSource = curNode;
                            edgeSource.color = highlight;
                        }
                    }
                }
                else {
                    populateNodeModal();
                }
            }
            s.refresh();
        }
    };

    populateNodeModal = function (nOpen) {
        curNode.color = highlight;
        s.refresh();

        let properties = curNode.properties;

        let html = "<table class='table table-nonfluid'><tbody>" + nodeHtml[curNode.epaType] + "</tbody></table>";

        $modalNodeLabel.html(curNode.epaType);
        $modalNode.find('.modal-body-content').html(html);

        for (let key in model.patterns) {
            $('#pattern').append('<option value="' + key + '">' + key + '</option>');
        }

        for (let key in model.curves) {
            if(model.curves[key].type === "VOLUME")
                $('#volcurve').append('<option value="' + key + '">' + key + '</option>');
        }

        if (ranModel && !isAddNode && curNode.epaType !== "Vertex" && curNode.epaType !== "Label" && typeof nOpen === 'undefined') {
            $('#node-results-tab').removeClass('hidden');
            $nodeTabs.tabs({active: 1});
            $('#node-results-tab').click();
        }
        else {
            $('#node-results-tab').addClass('hidden');
            $nodeTabs.tabs({active: 0});
            $('#node-view-tab').click();
        }

        if (typeof nOpen === 'undefined')
            $modalNode.modal('show');

        if (curNode.epaType !== "Label") {
            for (let key in properties)
                $('#' + key).val(properties[key]);

            if (model.quality.hasOwnProperty(curNode.properties.epaId)) {
                $('#node-quality').val(model.quality[curNode.properties.epaId]);
            }
        }
        else
            $('#epaId').val(curNode.label);
    };

    previousNode = function() {
        curNode.color = curNode.epaColor;
        s.renderers[0].dispatchEvent('outNode', {node: curNode});

        let nodes = s.graph.nodes();

        for (let i = 0; i < nodes.length; ++i) {
            if (nodes[i].properties.epaId === curNode.properties.epaId) {
                if (i === 0)
                    curNode = nodes[nodes.length - 1];
                else
                    curNode = nodes[i - 1];

                s.renderers[0].dispatchEvent('overNode', {node: curNode});
                populateNodeModal();
                if (ranModel && curNode.epaType !== "Vertex" && curNode.epaType !== "Label")
                    $('#node-results-view').find('select').change();
                else if (ranModel)
                    $edgeTabs.tabs({active: 0});
                break;
            }
        }
    };

    nextNode = function() {
        curNode.color = curNode.epaColor;
        s.renderers[0].dispatchEvent('outNode', {node: curNode});

        let nodes = s.graph.nodes();

        for (let i = 0; i < nodes.length; ++i) {
            if (nodes[i].properties.epaId === curNode.properties.epaId) {
                if (i + 1 === nodes.length)
                    curNode = nodes[0];
                else
                    curNode = nodes[i + 1];

                s.renderers[0].dispatchEvent('overNode', {node: curNode});
                populateNodeModal();
                if (ranModel && curNode.epaType !== "Vertex" && curNode.epaType !== "Label")
                    $('#node-results-view').find('select').change();
                else if (ranModel)
                    $edgeTabs.tabs({active: 0});
                break;
            }
        }
    };


    /*-----------------------------------------------
     ************ Edge FUNCTIONS ************
     ----------------------------------------------*/
    edgeClick = function(e) {
        if(!e.data.captor.isDragging) {
            edgeModalLeft = e.data.captor.clientX * 2 - 1600;
            $('#edge-dialog').css({top: e.data.captor.clientY - 10, left: edgeModalLeft});

            let curEdges = e.data.edge;
            if (curEdges.length > 1) {
                $multipleNodeSelect.empty();
                $multipleNodeSelect.append('<p>Select an Edge to display</p>');

                let selectHtml = "<select id='select-node-edge'>";
                for (let i in curEdges) {
                    selectHtml += "<option value='" + i + "'>" + curEdges[i].epaType + " " + curEdges[i].properties.epaId + "</option>";
                }
                selectHtml += "</select";
                $multipleNodeSelect.append(selectHtml);

                $multipleNodeSelect.dialog({
                    title: "Edge Select",
                    dialogClass: "no-close",
                    resizable: false,
                    height: "auto",
                    width: 400,
                    modal: true,
                    buttons: {
                        Ok: function () {
                            curEdge = curEdges[$('#select-node-edge').val()];
                            populateEdgeModal();
                            $(this).dialog("close");
                        },
                        Cancel: function () {
                            $(this).dialog("close");
                        }
                    }
                });

                $multipleNodeSelect.dialog("open");
            }
            else {
                curEdge = curEdges[0];
                populateEdgeModal();
            }
            s.refresh();
        }
    };

    populateEdgeModal = function (nOpen) {
        curEdge.color = highlight;
        s.refresh();

        let properties = curEdge.properties;

        let html = "<table class='table table-nonfluid'><tbody>" + edgeHtml[curEdge.epaType] + "</tbody></table>";

        $modalEdgeLabel.html(curEdge.epaType);
        $modalEdge.find('.modal-body-content').html(html);

        if (ranModel && isAddEdge === false) {
            $edgeTabs.tabs({active: 1});
            $('#edge-results-tab').click();
        }
        else {
            $edgeTabs.tabs({active: 0});
            $('#edge-view-tab').click();
        }

        if (typeof nOpen === 'undefined')
            $modalEdge.modal('show');

        for (let key in properties)
            $('#' + key).val(properties[key]);
    };

    previousEdge = function() {
        curEdge.color = curEdge.epaColor;
        s.renderers[0].dispatchEvent('outEdge', {edge: curEdge});

        let edges = s.graph.edges();

        for (let i = 0; i < edges.length; ++i) {
            if (edges[i].properties.epaId === curEdge.properties.epaId) {
                if (i === 0)
                    curEdge = edges[edges.length - 1];
                else
                    curEdge = edges[i - 1];

                s.renderers[0].dispatchEvent('overEdge', {edge: curEdge});
                populateEdgeModal();
                if (ranModel)
                    $('#edge-results-view').find('select').change();
                break;
            }
        }
    };

    nextEdge = function() {
        curEdge.color = curEdge.epaColor;
        s.renderers[0].dispatchEvent('outEdge', {edge: curEdge});

        let edges = s.graph.edges();

        for (let i = 0; i < edges.length; ++i) {
            if (edges[i].properties.epaId === curEdge.properties.epaId) {
                if (i + 1 === edges.length)
                    curEdge = edges[0];
                else
                    curEdge = edges[i + 1];

                s.renderers[0].dispatchEvent('overEdge', {edge: curEdge});
                populateEdgeModal();
                if (ranModel)
                    $('#edge-results-view').find('select').change();
                break;
            }
        }
    };


    /*-----------------------------------------------
     ************ Model Options FUNCTIONS ************
     ----------------------------------------------*/
    populateModelOptions = function () {
        for (let key in model.patterns) {
            $('#opt-pattern').append('<option value="' + key + '">' + key + '</option>');
        }
        for (let key in model.options) {
            if(key === "opt-unbalanced" || key === "opt-quality" || key === "opt-hydraulics") {
                $('#' + key + 1).val(model.options[key][0]);
                $('#' + key + 2).val(model.options[key][1]);
            }
            else
                $('#' + key).val(model.options[key]);
        }

        $('#node-count').html(s.graph.nodes().length);
        $('#edge-count').html(s.graph.edges().length);
    };
    //  ---------- Time
    populateTimeModal = function () {
        let timeOptions = model.times;

        for (let key in timeOptions) {
            if (key === "pattern" || key === "report") {
                $('#' + key + '1').val(timeOptions[key][0]);
                $('#' + key + '2').val(timeOptions[key][1]);
            }
            else if (key === "start") {
                $('#' + key).val(timeOptions[key].join(' '));
            }
            else {
                $('#' + key).val(timeOptions[key]);
            }
        }
    };
    //  ---------- Energy
    populateEnergyModal = function () {
        let energyOptions = model.energy;

        for (let key in energyOptions) {
            $('#' + key).val(energyOptions[key]);
        }
    };
    //  ---------- Reactions
    populateReactionsModal = function () {
        let reactionsOptions = model.reactions;

        for (let key in reactionsOptions) {
            $('#' + key).val(reactionsOptions[key]);
        }
    };
    //  ---------- Report
    populateReportModal = function () {
        let reportOptions = model.report;

        for (let key in reportOptions) {
            $('#' + key).val(reportOptions[key]);
        }
    };
    //  ---------- Curve
    populateCurvesModal = function () {
        $curveSelect.find('select').empty();

        for (let key in model.curves) {
            $curveSelect.find('select').append('<option>' + key + '</option>');
        }
    };

    resetCurveState = function () {
        updateInp();
        $chkCurveEdit.trigger('click');
        $inpCurveId.val('');

        $curveSelect.find('select').change();
    };

    drawCurve = function (values) {
        if (values !== undefined) {
            let x = [];
            let y = [];

            if (values.length === 2 && $inpCurveType.val() === "PUMP") {
                x = [0, values[0], 2 * values[0]];
                y = [1.33 * values[1], values[1], 0];
            }
            else {
                for (let i = 0; i < values.length; ++i) {
                    x.push(values[i]);
                    ++i;
                    y.push(values[i]);
                }
            }

            let trace1 = {
                x: x,
                y: y,
                mode: 'lines+markers',
                type: 'scatter',
                name: 'Curve ' + $curveSelect.find('select').val(),
                line: {shape: 'spline'}
            };

            let layout = {
                xaxis: {
                    title: curveGraphLabels[$inpCurveType.val()][0]
                },
                yaxis: {
                    title: curveGraphLabels[$inpCurveType.val()][1]
                }
            };

            let data = [trace1];

            Plotly.newPlot('curve-display', data, layout);
        }
        else {
            $curveSelect.find('select').empty();
            $curveDisplay.empty();
            $curveTable.find('tbody').empty();
            $btnAddCurve.click();
        }
    };

    setAddRemovePointListener = function () {
        $('.curve-table-edit').click(function (e) {
            $(this).parents('tr').remove();
        });

        $('#btn-add-curve-point').unbind('click').click(function () {
            if ($curveTable.find('input').filter(function() {return !$(this).val().trim().length;}).length !== 0)
                alert("All new points must have values.");
            else {
                let pointHtml = '<tr><td><input type="number" name="x" class="x"></td><td><input type="number" name="y" class="y"></td>' +
                    '<td><div class="btn btn-danger btn-group btn-xs curve-table-edit" role="group" data-toggle="tooltip" ' +
                    'title="Remove Point"><span class="glyphicon glyphicon-remove"></span></div></td></tr>';

                $curveTable.find('tbody').append(pointHtml);
                setAddRemovePointListener();
            }
        });
    };
    //  ---------- Pattern
    populatePatternModal = function () {
        $patternSelect.find('select').empty();

        for (let key in model.patterns) {
            $patternSelect.find('select').append('<option>' + key + '</option>');
        }
    };

    resetPatternState = function () {
        updateInp();
        $chkPatternEdit.trigger('click');
        $inpPatternId.val('');
        $inpPatternMults.tagsinput('removeAll');

        $patternSelect.find('select').change();
    };

    drawPattern = function (multipliers) {
        if (multipliers !== undefined) {
            let trace1 = {
                x: [],
                y: [],
                fill: 'tozeroy',
                type: 'scatter',
                name: 'Pattern ' + $patternSelect.find('select').val()
            };

            let interval = 24 / multipliers.length;
            let total = 0;

            for (let i = 0; i < multipliers.length; ++i) {
                total += parseFloat(multipliers[i]);

                if (i !== 0) {
                    trace1.x.push(i * interval);
                    trace1.y.push(multipliers[i - 1]);
                }

                trace1.x.push(i * interval);
                trace1.y.push(multipliers[i]);

                if (i === multipliers.length - 1) {
                    trace1.x.push(24);
                    trace1.y.push(multipliers[i]);
                }
            }

            let avg = total / multipliers.length;

            let trace2 = {
                x: [0, 24],
                y: [avg, avg],
                type: 'line',
                name: 'Average'
            };

            let layout = {
                legend: {
                    x: 0,
                    y: 1.1,
                    orientation: "h",
                    bgcolor: '#66000000'
                },
                xaxis: {
                    title: 'Time (Time Period = ' + interval.toFixed(2) + ' hrs)',
                    range: [0, 24]
                },
                yaxis: {
                    title: 'Multiplier',
                    range: [(Math.min(trace1.y) - 0.1), (Math.max(trace1.y) + 0.1)]
                }
            };

            let data = [trace1, trace2];

            Plotly.newPlot('pattern-display', data, layout);
        }
        else {
            $patternSelect.find('select').empty();
            $patternDisplay.empty();
            $btnAddPattern.click();
        }
    };
    //  ---------- Controls
    populateControlsModal = function () {
        $controlsDisplay.empty();

        let hidden = '';
        if (!$chkControlsEdit.is(':checked'))
            hidden = ' hidden';

        for (let key in model.controls)
            $controlsDisplay.append('<tr><td><h6>' + model.controls[key] + '</h6></td><td><div class="btn btn-danger ' +
                'btn-group btn-xs control-remove' + hidden + '" style="margin-top: 10px;" role="group" data-toggle="tooltip" ' +
                'title="Remove Control"><span class="glyphicon glyphicon-remove"></span></div></td></tr>');

        $('[data-toggle="tooltip"]').tooltip();

        setAddRemoveControlListener();
    };

    setAddRemoveControlListener = function () {
        $('.control-remove').click(function (e) {
            $(this).parents('tr').remove();
        });
    };
    //  ---------- Rules
    populateRulesModal = function () {
        $rulesDisplay.empty();

        let hidden = '';
        if (!$chkRulesEdit.is(':checked'))
            hidden = ' hidden';

        for (let key in model.rules) {
            let rule = model.rules[key];
            let ruleHtml = '<tr><td><div class="rules"><h6>Rule ' + key + '</h6>';
            for (let i in rule) {
                ruleHtml += '<p>' + rule[i] + '</p>';
            }

            ruleHtml += '</div></td><td style="vertical-align: middle;"><div class="btn btn-danger btn-group btn-xs rule-remove' +
                hidden + '" style="margin-top: 10px;" role="group" data-toggle="tooltip" title="Remove Rule">' +
                '<span class="glyphicon glyphicon-remove"></span></div></td></tr>';

            $rulesDisplay.append(ruleHtml);
        }

        $('[data-toggle="tooltip"]').tooltip();

        setAddRemoveRuleListener();
    };

    setAddRemoveRuleListener = function () {
        $('.rule-remove').click(function (e) {
            $(this).parents('tr').remove();
        });
    };


    /*-----------------------------------------------
     ************ Upload FUNCTIONS ************
     ----------------------------------------------*/
    uploadModel = function (data) {
        $.ajax({
            type: 'POST',
            url: '/apps/epanet-model-viewer/upload-epanet-model/',
            dataType: 'json',
            processData: false,
            contentType: false,
            data: data,
            error: function () {
                let message = 'An unexpected error occurred while uploading the model ';

                addLogEntry('danger', message, true);
            },
            success: function (response) {
                let message;

                if (response.hasOwnProperty('success')) {
                    $loadingAnimation.attr('hidden', true);

                    if (response.hasOwnProperty('message')) {
                        message = response.message;
                    }

                    if (!response.success) {
                        if (!message) {
                            message = 'An unexpected error occurred while uploading the model';
                        }

                        addLogEntry('danger', message, true);
                    } else {
                        if (message) {
                            addLogEntry('warning', message, true);
                        }
                        alert("Model has successfully been uploaded to HydroShare.");
                    }
                }
            }
        });
    };

    resetUploadState = function() {
        $inpUlTitle.val('');
        $inpUlDescription.val('');
        $inpUlKeywords.tagsinput('removeAll');
    };


    /*-----------------------------------------------
     ************ Animation FUNCTIONS ************
     ----------------------------------------------*/
    resetPlay = function() {
        if (playing === false) {
            playing = true;
            $btnPlayAnimation.find('span').removeClass('glyphicon-play');
            $btnPlayAnimation.find('span').addClass('glyphicon-pause');
            $btnPlayAnimation.removeClass('btn-success');
            $btnPlayAnimation.addClass('btn-warning');
        }
        else {
            playing = false;
            $btnPlayAnimation.find('span').addClass('glyphicon-play');
            $btnPlayAnimation.find('span').removeClass('glyphicon-pause');
            $btnPlayAnimation.removeClass('btn-warning');
            $btnPlayAnimation.addClass('btn-success');
        }
    };

    stopAnimation = function() {
        animate.forEach(function(call) {
            clearTimeout(call);
        });
    };

    resetAnimation = function(resetSlider) {
        playing = true;
        resetPlay();

        stopAnimation();

        if (resetSlider === true) {
            $animationSlider.slider("value", 0);
            $('#timestep').val('');
            $queryTimestep.val(1);
        }

        for (let node in s.graph.nodes()) {
            s.graph.nodes()[node].color = s.graph.nodes()[node].epaColor;
        }
        for (let edge in s.graph.edges()) {
            s.graph.edges()[edge].color = s.graph.edges()[edge].epaColor;
        }

        s.refresh();
    };

    resetNodeAnim = function() {
        let nodeData = [];
        for (let node in s.graph.nodes()) {
            try {
                nodeData = nodeData.concat(s.graph.nodes()[node].modelResults[$nodeAnimType.val()]);
            }
            catch (e) {
                // nothing
            }
        }

        $nodeLegend.html(animationLegends[$nodeAnimColor.val()]);
        $nodeLegend.find('.domain-min').html(Math.floor(Math.min(...nodeData)));
        $nodeLegend.find('.domain-med').html(Math.round((Math.max(...nodeData) + Math.min(...nodeData))/2));
        $nodeLegend.find('.domain-max').html(Math.ceil(Math.max(...nodeData)));

        nodeAnimColor = chroma.scale($nodeAnimColor.val())
            .domain([Math.max(...nodeData), Math.min(...nodeData)]);

    };

    resetEdgeAnim = function() {
        let edgeData = [];
        for (let edge in s.graph.edges()) {
            try {
                edgeData = edgeData.concat(s.graph.edges()[edge].modelResults[$edgeAnimType.val()]);
            }
            catch (e) {
                // nothing
            }
        }

        $edgeLegend.html(animationLegends[$edgeAnimColor.val()]);
        $edgeLegend.find('.domain-min').html(Math.floor(Math.min(...edgeData)));
        $edgeLegend.find('.domain-med').html(Math.round((Math.max(...edgeData) + Math.min(...edgeData))/2));
        $edgeLegend.find('.domain-max').html(Math.ceil(Math.max(...edgeData)));

        edgeAnimColor = chroma.scale($edgeAnimColor.val())
            .domain([Math.max(...edgeData), Math.min(...edgeData)]);
    };


    /*-----------------------------------------------
     ************ Results Overview FUNCTIONS ************
     ----------------------------------------------*/
    populateNodesResults = function() {
        if (resultsNodes.length === 0) {
            $nodesPlot.empty();
            $nodesStats.empty();
            $nodesFullResults.empty();
        }
        else {
            let resultType = $ddNodes.find('option:selected');
            let plotData = [];
            let statsValues = [[],[],[],[]];

            for (let i in resultsNodes) {
                let node = s.graph.nodes().find(node => node.properties.epaId === resultsNodes[i]);

                try {
                    let modelResults = node.modelResults;

                    // let headerVals = [];
                    // for (let key in modelResults) {
                    //     if (headerVals.length !== modelResults.length) {
                    //         headerVals.push("<b>" + key + "</b>");
                    //     }
                    // }
                    // Work on getting more graphs and tables after basic functionality is all built and working

                    let dataset = modelResults[resultType.val()];
                    let x = [], y = [];
                    for (let i in dataset) {
                        y.push(dataset[i]);
                        x.push(i);
                    }

                    let trace = {
                        x: x,
                        y: y,
                        name: node.epaType + " " + node.properties.epaId,
                        type: 'scatter'
                    };

                    plotData.push(trace);

                    let total = 0;
                    for (let i = 0; i < y.length; i++) {
                        total += parseInt(y[i]);
                    }

                    statsValues[0].push(node.epaType + " " + node.properties.epaId);
                    statsValues[1].push(Math.min.apply(null, y).toFixed(2));
                    statsValues[2].push(Math.max.apply(null, y).toFixed(2));
                    statsValues[3].push((total / y.length).toFixed(2));
                }
                catch (e) {
                    console.log(e);
                }

            }

            let layout = {
                title: resultType.text() + " for Selected Nodes",
                xaxis: {
                    title: 'Timestep'
                },
                yaxis: {
                    title: resultType.text()
                }
            };

            Plotly.newPlot('nodes-plot', plotData, layout);

            let statsData = [{
                type: 'table',
                header: {
                    values: [["<b>Node</b>"],["<b>Min</b>"], ["<b>Max</b>"],["<b>Avg</b>"]],
                    align: "center",
                    line: {width: 1, color: 'black'},
                    fill: {color: '#2076b4'},
                    font: {family: "Arial", size: 12, color: "white"}
                },
                cells: {
                    values: statsValues,
                    align: "center",
                    line: {color: "black", width: 1},
                    font: {family: "Arial", size: 11, color: ["black"]}
                }
            }];

            Plotly.newPlot('nodes-stats', statsData);
        }
    };

    populateEdgesResults = function() {
        if (resultsEdges.length === 0) {
            $edgesPlot.empty();
            $edgesStats.empty();
            $edgesFullResults.empty();
        }
        else {
            let resultType = $ddEdges.find('option:selected');
            let plotData = [];
            let statsData = [];

            for (let i in resultsEdges) {
                let edge = s.graph.edges().find(edge => edge.properties.epaId === resultsEdges[i]);

                try {
                    let dataset = edge.modelResults[resultType.val()];
                    let x = [], y = [];
                    for (let i in dataset) {
                        y.push(dataset[i]);
                        x.push(i);
                    }

                    let trace = {
                        x: x,
                        y: y,
                        name: edge.epaType + " " + edge.properties.epaId,
                        type: 'scatter'
                    };

                    plotData.push(trace);

                    trace = {
                        x: y,
                        name: edge.epaType + " " + edge.properties.epaId,
                        type: 'box',
                        boxmean: true
                    };

                    statsData.push(trace);
                }
                catch (e) {
                    console.log(e);
                    // $('#edges-results').append('<p>Results data for this edge have not been computed</p>');
                }
            }

            let layout = {
                title: resultType.text() + " for Selected Links",
                xaxis: {
                    title: 'Timestep'
                },
                yaxis: {
                    title: resultType.text()
                }
            };

            Plotly.newPlot('edges-plot', plotData, layout);

            layout = {
                xaxis: {
                    title: resultType.text()
                }
            };

            Plotly.newPlot('edges-stats', statsData, layout);
        }
    };

    resetResultsOverview = function () {
        $nodesPlot.empty();
        $nodesStats.empty();
        $nodesFullResults.empty();
        $ddNodes.find('ul').empty();
        resultsNodes = [];
        $edgesPlot.empty();
        $edgesStats.empty();
        $edgesFullResults.empty();
        $ddEdges.find('ul').empty();
        resultsEdges = [];
    };


    /*-----------------------------------------------
     ************ Other FUNCTIONS ************
     ----------------------------------------------*/
    initializeJqueryVariables = function () {
        //  ********** Model/Graph **********
        $initialModel = $('#initial-model');
        $fileDisplayArea = $("#file-display-area")[0];
        $btnRunModel = $('#btn-run-model');
        $chkAutoUpdate = $('#chk-auto-update');


        //  ********** Node **********
        $modalNode = $('#modal-node');
        $modalNodeLabel = $('#modal-node-label');
        $btnNodeLeft = $('#btn-node-left');
        $btnNodeRight = $('#btn-node-right');
        $chkNodeEdit = $('#chk-node');
        $btnNodeOk = $('#btn-node-ok');
        $btnNodeCancel = $('#btn-node-cancel');
        $btnNodeDelete = $('#btn-node-delete');
        $nodeX = $('#node-x');
        $nodeY = $('#node-y');
        $nodeTabs = $('#node-tabs');
        $nodePlot = $('#node-plot');
        $nodeStats = $('#node-stats');
        $viewNodeResults = $('#node-results-view');
        $multipleNodeSelect = $('#multiple-node-select');


        //  ********** Edge **********
        $modalEdge = $('#modal-edge');
        $modalEdgeLabel = $('#modal-edge-label');
        $btnEdgeLeft = $('#btn-edge-left');
        $btnEdgeRight = $('#btn-edge-right');
        $chkEdgeEdit = $('#chk-edge');
        $btnEdgeOk = $('#btn-edge-ok');
        $btnEdgeCancel = $('#btn-edge-cancel');
        $btnEdgeDelete = $('#btn-edge-delete');
        $edgeTabs = $('#edge-tabs');
        $edgePlot = $('#edge-plot');
        $edgeStats = $('#edge-stats');
        $viewEdgeResults = $('#edge-results-view');


        //  ********** Model Options **********
        $modelOptions = $('#model-options-view');
        $chkOptionsEdit = $('#chk-options');
        $btnOptionsOk = $('#btn-options-ok');
        $btnOptionsCancel = $('#btn-options-cancel');
        //  ---------- Time
        $modalTime = $('#modal-time');
        $chkTimeEdit = $('#chk-time-edit');
        $btnTimeOk = $('#btn-time-ok');
        //  ---------- Energy
        $modalEnergy = $('#modal-energy');
        $chkEnergyEdit = $('#chk-energy-edit');
        $btnEnergyOk = $('#btn-energy-ok');
        //  ---------- Reactions
        $modalReactions = $('#modal-reactions');
        $chkReactionsEdit = $('#chk-reactions-edit');
        $btnReactionsOk = $('#btn-reactions-ok');
        //  ---------- Report
        $modalReport = $('#modal-report');
        $chkReportEdit = $('#chk-report-edit');
        $btnReportOk = $('#btn-report-ok');
        //  ---------- Curve
        $modalCurve = $('#modal-curve');
        $chkCurveEdit = $('#chk-curve-edit');
        $btnCurveOk = $('#btn-curve-ok');
        $btnCurveDelete = $('#btn-curve-delete');
        $curveSelect = $("#curve-select");
        $inpCurveType = $("#slc-curve-type");
        $curveDisplay = $("#curve-display");
        $curveTable = $("#curve-points");
        $btnAddCurve = $("#btn-add-curve");
        $inpCurveId = $("#inp-curve-id");
        //  ---------- Pattern
        $modalPattern = $('#modal-pattern');
        $chkPatternEdit = $('#chk-pattern-edit');
        $btnPatternOk = $('#btn-pattern-ok');
        $btnPatternDelete = $('#btn-pattern-delete');
        $patternSelect = $('#pattern-select');
        $inpPatternMults = $('#tagsinp-pattern-mults');
        $patternDisplay = $('#pattern-display');
        $btnAddPattern = $('#btn-add-pattern');
        $inpPatternId = $('#inp-pattern-id');
        //  ---------- Controls
        $modalControls = $('#modal-controls');
        $chkControlsEdit = $('#chk-controls-edit');
        $btnControlsOk = $('#btn-controls-ok');
        $controlsDisplay = $('#controls-container');
        $btnAddControl = $('#btn-add-control');
        $controlType = $('#controls-type');
        $addControlView = $('#add-control');
        //  ---------- Rules
        $modalRules = $('#modal-rules');
        $chkRulesEdit = $('#chk-rules-edit');
        $btnRulesOk = $('#btn-rules-ok');
        $rulesDisplay = $('#rules-container');
        $btnAddRule = $('#btn-add-rule');
        $inpRuleId = $('#inp-rule-id')
        $inpRuleBody = $('#inp-rule-body');


        //  ********** Upload **********
        $inpUlTitle = $('#inp-upload-title');
        $inpUlDescription = $('#inp-upload-description');
        $inpUlKeywords = $('#tagsinp-upload-keywords');
        $btnUl = $('#btn-upload');
        $btnUlCancel = $('#btn-upload-cancel');


        //  ********** Animation **********
        $btnAnimateTools = $('#btn-animate-tools');
        $animateToolbar = $('#animate-toolbar');
        $btnPlayAnimation = $('#btn-play');
        $btnStopAnimation = $('#btn-stop');
        $animationSpeed = $("#speed");
        $animationSlider = $("#slider");
        $chkNodes = $('#chk-nodes');
        $nodeLegend = $("#node-leg");
        $nodeAnimColor = $('#node-anim-color');
        $nodeAnimType = $('#node-anim-type');
        $chkEdges = $('#chk-edges');
        $edgeLegend = $("#edge-leg");
        $edgeAnimColor = $('#edge-anim-color');
        $edgeAnimType = $('#edge-anim-type');


        //  ********** Query **********
        $btnQueryTools = $('#btn-query-tools');
        $btnQuery = $('#btn-query');
        $btnClearQuery = $('#btn-query-clear');
        $queryToolbar = $('#query-toolbar');
        $queryType = $('#inp-query-type');
        $queryResult = $('#inp-query-result');
        $queryCondintion = $('#inp-query-condition');
        $queryValue = $('#inp-query-value');
        $queryCount = $('#query-count');
        $queryTimestep = $('#query-timestep');


        //  ********** Editing **********
        $btnEditTools = $('#btn-edit-tools');
        $editToolbar = $('#edit-toolbar');
        $btnEditDefualt = $('#btn-default-edit');


        //  ********** Results Overview **********
        $ddNodes = $('#nodes-results');
        $chkNodesFullResults = $('#chk-nodes-full-results');
        $nodesPlot = $('#nodes-plot');
        $nodesStats = $('#nodes-stats');
        $nodesFullResults = $('#nodes-results-table');
        $ddEdges = $('#edges-results');
        $chkEdgesFullResults = $('#chk-edges-full-results');
        $edgesPlot = $('#edges-plot');
        $edgesStats = $('#edges-stats');
        $edgesFullResults = $('#edges-results-table');


        //  ********** Other **********
        $modalLog = $('#modalLog');
        $loadFromLocal = $("#load-from-local")[0];
        $viewTabs = $('#view-tabs');
        $loadingModel = $('#loading-model');
        $loadingAnimation = $('#loading-animation');
    };

    addInitialEventListeners = function () {
        //  ********** Keypress FUNCTIONS **********
        document.onkeydown = function(evt) {
            evt = evt || window.event;

            switch(evt.which) {
                case 27: // esc
                    $btnEditDefualt.click();
                case 37: // left
                    if ($modalNode.is(':visible') && !$chkNodeEdit.is(':checked')) {
                        previousNode();
                    }
                    else if ($modalEdge.is(':visible') && !$chkEdgeEdit.is(':checked')) {
                        previousEdge();
                    }
                    break;
                case 39: // right
                    if ($modalNode.is(':visible') && !$chkNodeEdit.is(':checked')) {
                        nextNode();
                    }
                    else if ($modalEdge.is(':visible') && !$chkEdgeEdit.is(':checked')) {
                        nextEdge();
                    }
                    break;

                default: return; // exit this handler for other keys
            }
        };


        //  ********** Model/Graph **********
        $('#btn-model-rep').click(function () {
            let curURL = window.location.href;
            window.open(curURL.substring(0, curURL.indexOf('/apps/') + 6) + "epanet-model-repository/", "modelRepository");
        });

        $('#file-display-area').bind("DOMSubtreeModified",function(){
            if ($fileDisplayArea.innerText !== "") {
                $("#loading-animation-update").attr('hidden', true);
                $('#view-tabs').removeClass('hidden');
                $('#loading-model').addClass('hidden');

                $("#model-container").remove();
                $("#model-display").append("<div id='model-container'></div>");

                // file_text = $fileDisplayArea.innerText;

                readModel();

                let activeIndex = $viewTabs.tabs("option", "active");
                $viewTabs.tabs({active: 0});
                drawModel();
                populateModelOptions();
                $viewTabs.tabs({active: activeIndex});

                $('.ran-model').addClass('hidden');

                $btnRunModel.css('background-color', '#');
                $btnRunModel.css('color', '');
                $btnRunModel.unbind('mouseenter mouseleave');
                $btnRunModel.hover(function() {
                    $(this).css('background-color', '');
                }).mouseout(function() {
                    $(this).css('background-color', '');
                });
                $btnRunModel.trigger('mouseout');

                ranModel = false;

                let searchNodeListElt = $('#search-nodelist');
                searchNodeListElt.empty();
                s.graph.nodes().forEach(function(n) {
                    let optionElt = document.createElement("option");

                    if (n.epaType === "Label") {
                        optionElt.text = n.epaType + ': ' + n.label;
                        optionElt.value = n.id;
                    }
                    else if (n.epaType === "Vertex") {
                        optionElt.text = n.id;
                    }
                    else {
                        optionElt.text = n.epaType + ' ' + n.id;
                        optionElt.value = n.id;
                    }
                    searchNodeListElt.append(optionElt);
                });

                searchNodeListElt.change(function(e) {
                    locateNode(e);
                    $('#search-type').html('node');
                });

                let searchedgelistElt = $('#search-edgelist');
                searchedgelistElt.empty();
                s.graph.edges().forEach(function(n) {
                    let optionElt = document.createElement("option");
                    optionElt.text = n.epaType + ' ' + n.id;
                    optionElt.value = n.id;
                    searchedgelistElt.append(optionElt);
                });

                searchedgelistElt.change(function(e) {
                    locateEdge(e);
                    $('#search-type').html('edge');
                });

                if (s.graph.nodes().length > 2000) {
                    alert("This application is not yet able to process models with over 2000 nodes/links. You will not " +
                        "be able to run models of this size at this time. Editing is still possible but auto-update is defaulted " +
                        "to off. If you would like to update the changes you have made to the .inp file uncheck the " +
                        "auto-update slider and they will be made.");

                    $btnRunModel.attr('disabled', true);

                    if (firstRun == true)
                        $chkAutoUpdate.attr('checked', false);
                }
                else {
                    $btnRunModel.removeAttr('disabled');
                    $chkAutoUpdate.attr('checked', true);
                }

                firstRun = false;
            }
        });

        $btnRunModel.click(function() {
            let data = {'model': file_text, 'quality': model.options['opt-quality'][0]};

            resetResultsOverview();

            $('#loading-animation-run').removeAttr('hidden');
            if (parseInt($('#node-count').text()) > 1000)
                alert("Due to large model size this may take some time.");

            $.ajax({
                type: 'POST',
                url: '/apps/epanet-model-viewer/run-epanet-model/',
                dataType: 'json',
                data: data,
                error: function () {
                    $('#loading-animation-run').attr('hidden', true);
                    let message = 'An unexpected error occurred while uploading the model ';

                    addLogEntry('danger', message, true);
                },
                success: function (response) {
                    $('#loading-animation-run').attr('hidden', true);
                    let message;

                    if (response.hasOwnProperty('success')) {
                        if (response.hasOwnProperty('message')) {
                            message = response.message;
                        }

                        if (!response.success) {
                            if (!message) {
                                message = 'An unexpected error occurred while uploading the model';
                            }

                            addLogEntry('danger', message, true);
                        } else {
                            if (message) {
                                addLogEntry('warning', message, true);
                            }
                            if (response.hasOwnProperty('results')) {
                                modelResults = response.results;

                                $btnRunModel.css('background-color', '#915F6D');
                                $btnRunModel.css('color', 'white');
                                $btnRunModel.unbind('mouseenter mouseleave');
                                $btnRunModel.hover(function() {
                                    $(this).css('background-color', '#744c57');
                                }).mouseout(function() {
                                    $(this).css('background-color', '#915F6D');
                                });
                                $('.ran-model').removeClass('hidden');
                                modelResults = response.results;

                                for (let i in modelResults['nodes']) {
                                    s.graph.nodes().find(node => node.properties.epaId === i).modelResults = modelResults['nodes'][i];
                                    animationMaxStep = modelResults['nodes'][i]['EN_DEMAND'].length;
                                }

                                if (animationMaxStep === 1)
                                    $('#total-timesteps').val(animationMaxStep);
                                else
                                    $('#total-timesteps').val(animationMaxStep - 1);

                                for (let i in modelResults['edges']) {
                                    s.graph.edges().find(edge => edge.properties.epaId === i).modelResults = modelResults['edges'][i];
                                }

                                $animationSlider.slider({
                                    value: 0,
                                    min: 0,
                                    max: animationMaxStep - 1,
                                    step: 1, //Assigning the slider step based on the depths that were retrieved in the controller
                                    animate: "fast",
                                    slide: function (event, ui) {
                                        playing = true;
                                        $btnPlayAnimation.click();
                                        $('#timestep').val($animationSlider.slider("value") + 1);
                                        $queryTimestep.val($animationSlider.slider("value") + 1);
                                    },
                                    stop: function (event, ui) {
                                        playing = true;
                                        $btnPlayAnimation.click();
                                        $('#timestep').val($animationSlider.slider("value") + 1);
                                        $queryTimestep.val($animationSlider.slider("value") + 1);
                                    }
                                });
                                $animationSlider.trigger('slidestop');

                                let nodesDropdown = $ddNodes.find('.dropdown-menu');

                                nodesDropdown.append('<li><a href="#" id="chk-all-nodes" class="dropdown-item"' +
                                    '" tabIndex="-1"><input type="checkbox"/>&nbsp;Select All</a></li>');

                                for (let i in s.graph.nodes()) {
                                    let node = s.graph.nodes()[i];
                                    if (node.epaType !== "Vertex" && node.epaType !== "Label")
                                        nodesDropdown.append('<li><a href="#" class="dropdown-item" data-value="' + node.properties.epaId +
                                            '" tabIndex="-1"><input type="checkbox"/>&nbsp;' + node.epaType + ' ' +
                                            node.properties.epaId + '</a></li>');
                                }

                                $ddNodes.find('.dropdown-menu a').on('click', function (event) {
                                    let $target = $(event.currentTarget);
                                    let val = $target.attr('data-value');
                                    let $inp = $target.find('input');
                                    let idx;

                                    if ($(this).attr('id') === 'chk-all-nodes') {
                                        if (!$inp.is(':checked')) {
                                            $inp.prop('checked', true);
                                        }
                                        else {
                                            $inp.prop('checked', false);
                                        }

                                        $ddNodes.find('.dropdown-menu a').each(function () {
                                            if ($(this).attr('id') !== 'chk-all-nodes' && $(this).find('input').is(':checked') !== $inp.is(':checked'))
                                                $(this).click();
                                        });
                                    }
                                    else {
                                        if ((idx = resultsNodes.indexOf(val)) > -1) {
                                            resultsNodes.splice(idx, 1);
                                            $inp.prop('checked', false);
                                        }
                                        else {
                                            resultsNodes.push(val);
                                            $inp.prop('checked', true);
                                        }
                                    }

                                    $(event.target).blur();

                                    populateNodesResults();
                                    return false;
                                });

                                $ddNodes.find('select').change(function () {
                                    populateNodesResults();
                                });

                                $chkNodesFullResults.click(function () {
                                    populateNodesResults();
                                });

                                let edgesDropdown = $ddEdges.find('.dropdown-menu');

                                edgesDropdown.append('<li><a href="#" id="chk-all-edges" class="dropdown-item"' +
                                    '" tabIndex="-1"><input type="checkbox"/>&nbsp;Select All</a></li>');

                                for (let i in s.graph.edges()) {
                                    let edge = s.graph.edges()[i];
                                    edgesDropdown.append('<li><a href="#" class="dropdown-item" data-value="' + edge.properties.epaId +
                                        '" tabIndex="-1"><input type="checkbox"/>&nbsp;' + edge.epaType + ' ' +
                                        edge.properties.epaId + '</a></li>');
                                }

                                $ddEdges.find('.dropdown-menu a').on('click', function (event) {
                                    let $target = $(event.currentTarget);
                                    let val = $target.attr('data-value');
                                    let $inp = $target.find('input');
                                    let idx;

                                    if ($(this).attr('id') === 'chk-all-edges') {
                                        if (!$inp.is(':checked')) {
                                            $inp.prop('checked', true);
                                        }
                                        else {
                                            $inp.prop('checked', false);
                                        }

                                        $ddEdges.find('.dropdown-menu a').each(function () {
                                            if ($(this).attr('id') !== 'chk-all-nodes' && $(this).find('input').is(':checked') !== $inp.is(':checked'))
                                                $(this).click();
                                        });
                                    }
                                    else {
                                        if ((idx = resultsEdges.indexOf(val)) > -1) {
                                            resultsEdges.splice(idx, 1);
                                            $inp.prop('checked', false);
                                        }
                                        else {
                                            resultsEdges.push(val);
                                            $inp.prop('checked', true);
                                        }
                                    }

                                    $(event.target).blur();

                                    populateEdgesResults();
                                    return false;
                                });

                                $ddEdges.find('select').change(function () {
                                    populateEdgesResults();
                                });

                                $chkEdgesFullResults.click(function () {
                                    populateEdgesResults();
                                });

                                resetNodeAnim();
                                resetEdgeAnim();

                                ranModel = true;
                            }
                        }
                    }
                }
            });
        });

        $chkAutoUpdate.click(function () {
            if ($chkAutoUpdate.is(':checked')) {
                updateInp();
            }
        });

        $('#modal-search').on('hidden.bs.modal', function () {
            if ($('#search-type').html() === "node")
                populateNodeModal();
            else if ($('#search-type').html() === "edge")
                populateEdgeModal();

            $('#search-type').html('');
        });


        //  ********** Node **********
        $modalNode.on('shown.bs.modal', function () {
            if (ranModel && !isAddNode && (curNode.epaType !== "Vertex" && curNode.epaType !== "Label"))
                $('#node-results-view').find('select').change();
            else {
                $modalNode.find('input').keyup(function(event) {
                    if (event.keyCode === 13) {
                        $btnNodeOk.click();
                    }
                });

                $modalNode.find('input')[0].focus();
            }
        });

        $modalNode.on('hidden.bs.modal', function () {
            if (edgeVerts.length === 0) {
                if ($chkNodeEdit.is(':checked'))
                    $chkNodeEdit.trigger('click');

                $modalNode.find('.modal-body-content').empty();
                resetModelState();
                s.refresh();
            }
        });

        $btnNodeLeft.click(previousNode);

        $btnNodeRight.click(nextNode);

        $chkNodeEdit.click(function() {
            if ($chkNodeEdit.is(':checked')) {
                $btnNodeOk.removeAttr('disabled');
                $btnNodeDelete.removeAttr('disabled');

                $modalNode.find('input').attr('readonly', false);
                $modalNode.find('select').attr('disabled', false);

                $modalNode.find('input')[0].focus();
                $modalNode.find('input')[0].select();
            }
            else {
                $btnNodeOk.attr('disabled', true);
                $btnNodeDelete.attr('disabled', true);

                $modalNode.find('input').attr('readonly', true);
                $modalNode.find('select').attr('disabled', true);

                populateNodeModal(true);
            }
        });

        $btnNodeOk.click(function() {
            if ($('.needed').filter(function() {return !$(this).val().trim().length;}).length !== 0 && curNode.epaType !== "Vertex")
                alert("Required fields must have values.");
            else {
                if (curNode.epaType !== "Label") {
                    let edges = s.graph.edges;

                    for (let i in edges) {
                        if (edges[i].type === "vert") {
                            for (let j in edges[i].vert) {
                                if (edges[i].vert[j] === curNode.properties.epaId) {
                                    edges[i].vert[j] = $('#epaId').val();
                                }
                            }
                        }
                    }

                    if (curNode.epaType !== "Vertex") {
                        curNode.properties.epaId = $('#epaId').val();
                        curNode.label = curNode.epaType + ' ' + $('#epaId').val();

                        let properties = curNode.properties;
                        $('#node-properties-view').find('input, select').each(function () {
                            if ($(this).attr('id') !== 'node-quality')
                                properties[$(this).attr('id')] = $(this).val();
                        });

                        if ($('#node-quality').val() !== "")
                            model.quality[curNode.properties.epaId] = $('#node-quality').val();
                        else if (model.quality.hasOwnProperty(curNode.properties.epaId))
                            delete model.quality[curNode.properties.epaId];
                    }
                    else {
                        curNode.id = "vert " + edgeVerts.length;
                        curNode.properties.epaId = "vert " + edgeVerts.length;
                        curNode.label = "vert " + edgeVerts.length;
                    }
                }
                else {
                    curNode.label = $('#epaId').val();
                }

                if ($nodeX.html() !== "") {
                    if (curNode.epaType === "Vertex") {
                        curNode.id = Math.random().toString(36).replace(/[^a-z]+/g, '').substr(2, 10);
                        curNode.size = 0.6;
                        edgeVerts.push(curNode.properties.epaId);
                    }
                    else if (curNode.epaType !== "Label") {
                        curNode.id = curNode.properties.epaId;
                        curNode.label = curNode.epaType + " " + curNode.id;
                        curNode.size = 2;
                    }
                    else {
                        curNode.id = Math.random().toString(36).replace(/[^a-z]+/g, '').substr(2, 10);
                        curNode.size = 1;
                        curNode.showLabel = true;
                    }

                    curNode.color = graphColors[curNode.epaType];
                    curNode.epaColor = curNode.color;
                    curNode.x = $nodeX.html();
                    curNode.y = $nodeY.html();

                    try {
                        s.graph.addNode(curNode);
                        $modalNode.modal('hide');
                    }
                    catch (e) {
                        alert(e);
                        return;
                    }

                    s.refresh();

                    $nodeX.empty();
                    $nodeY.empty();
                }
                resetModelState();
                $chkNodeEdit.trigger('click');

                if (!isAddEdge)
                    updateInp();
            }
        });

        $btnNodeCancel.click(function() {
            resetModelState();
        });

        $btnNodeDelete.click(function() {
            $modalNode.modal('hide');

            if (curNode.epaType === "Vertex") {
                try {
                    let edge = s.graph.edges().find(edge => edge.properties.epaId === curNode.id.split(" ")[0]);
                    let verts = edge.vert;
                    if (verts.length === 1) {
                        delete edge.vert;
                        delete edge.type;
                    }
                    else
                        verts.splice(verts.indexOf(curNode.properties.epaId), 1);
                }
                catch (e) {
                    // vert edge is gone already
                }
            }
            s.graph.dropNode(curNode.id);

            resetModelState();
        });

        $nodeTabs.tabs({ active: 0 });

        $('#node-view-tab').click(function () {
            $modalNode.find('.modal-dialog').css('left', nodeModalLeft);
            $modalNode.find('.modal-dialog').css('width', '350px');
            $modalNode.find('.modal-dialog').css('height', '550px');
        });

        $('#node-results-tab').click(function () {
            $modalNode.find('.modal-dialog').css('left', '0');
            $modalNode.find('.modal-dialog').css('width', '1000px');
            $modalNode.find('.modal-dialog').css('height', '1180px');
        });

        $viewNodeResults.find('select').change(function () {
            try {
                let dataset = curNode.modelResults[$(this).val()];
                let x = [], y = [];
                for (let i in dataset) {
                    y.push(dataset[i]);
                    x.push(i);
                }

                let trace = {
                    x: x,
                    y: y,
                    type: 'scatter'
                };

                let data = [trace];

                let layout = {
                    title: $(this).find('option:selected').text() + " for " + curNode.epaType + " " + curNode.id,
                    xaxis: {
                        title: 'Timestep'
                    },
                    yaxis: {
                        title: $(this).find('option:selected').text()
                    },
                };

                Plotly.newPlot('node-plot', data, layout);

                let total = 0;
                for (let i = 0; i < y.length; i++) {
                    total += parseInt(y[i]);
                }

                let values = [
                    [Math.min.apply(null, y).toFixed(2)],
                    [Math.max.apply(null, y).toFixed(2)],
                    [(total / y.length).toFixed(2)]
                ];

                data = [{
                    type: 'table',
                    header: {
                        values: [["<b>Min</b>"], ["<b>Max</b>"],
                            ["<b>Avg</b>"]],
                        align: "center",
                        line: {width: 1, color: 'black'},
                        fill: {color: '#2076b4'},
                        font: {family: "Arial", size: 12, color: "white"}
                    },
                    cells: {
                        values: values,
                        align: "center",
                        line: {color: "black", width: 1},
                        font: {family: "Arial", size: 11, color: ["black"]}
                    }
                }];

                Plotly.newPlot('node-stats', data);
            }
            catch (e) {
                $('#node-results').html('<p>Results data for this node have not been computed</p>');
            }
        });

        $multipleNodeSelect.dialog({ autoOpen: false });


        //  ********** Edge **********
        $modalEdge.on('shown.bs.modal', function () {
            if (ranModel && isAddEdge === false)
                $('#edge-results-view').find('select').change();
            else {
                $modalEdge.find('input').keyup(function(event) {
                    if (event.keyCode === 13) {
                        $btnEdgeOk.click();
                    }
                });

                $modalEdge.find('input')[0].focus();
            }
        });

        $modalEdge.on('hidden.bs.modal', function () {
            if ($chkEdgeEdit.is(':checked'))
                $chkEdgeEdit.trigger('click');

            $modalEdge.find('.modal-body-content').empty();
            resetModelState();
            s.refresh();
        });

        $btnEdgeLeft.click(previousEdge);

        $btnEdgeRight.click(nextEdge);

        $chkEdgeEdit.click(function() {
            if ($chkEdgeEdit.is(':checked')) {
                $btnEdgeOk.removeAttr('disabled');
                $btnEdgeDelete.removeAttr('disabled');

                $modalEdge.find('input').attr('readonly', false);
                $modalEdge.find('select').attr('disabled', false);

                $modalEdge.find('input')[0].focus();
                $modalEdge.find('input')[0].select();
            }
            else {
                $btnEdgeOk.attr('disabled', true);
                $btnEdgeDelete.attr('disabled', true);

                $modalEdge.find('input').attr('readonly', true);
                $modalEdge.find('select').attr('disabled', true);

                populateEdgeModal(true);
            }
        });

        $btnEdgeOk.click(function() {
            if ($('.needed').filter(function() {return !$(this).val().trim().length;}).length !== 0)
                alert("Required fields must have values.");
            else {
                curEdge.properties.epaId = $('#epaId').val();
                curEdge.label = curEdge.epaType + ' ' + $('#epaId').val();

                let properties = curEdge.properties;
                $('#edge-properties-view').find('input, select').each(function () {
                    properties[$(this).attr('id')] = $(this).val();
                });

                if (isAddEdge && edgeSource !== null) {
                    curEdge.id = curEdge.properties.epaId;
                    curEdge.label = curEdge.epaType + " " + curEdge.properties.epaId;
                    curEdge.color = graphColors[curEdge.epaType];
                    curEdge.epaColor = graphColors[curEdge.epaType];
                    curEdge.size = 1;
                    curEdge.source = edgeSource.id;
                    curEdge.target = curNode.id;

                    if (edgeVerts.length > 0) {
                        curEdge.type = "vert";

                        for (let vert in edgeVerts) {
                            let node = s.graph.nodes().find(node => node.properties.epaId === edgeVerts[vert]);
                            s.graph.dropNode(node.id);
                            node.properties.epaId = curEdge.id + " " + edgeVerts[vert].substr(edgeVerts[vert].indexOf('vert'));
                            node.id = node.properties.epaId;
                            node.label = node.properties.epaId;
                            edgeVerts[vert] = node.id;

                            try {
                                s.graph.addNode(node);
                            }
                            catch (e) {
                                alert(e);
                                return;
                            }
                        }

                        curEdge.vert = edgeVerts;
                    }

                    try {
                        curEdge.color = graphColors[curEdge.epaType];
                        s.graph.addEdge(curEdge);
                        curEdge.color = graphColors[curEdge.epaType];
                        $modalEdge.modal('hide');
                        curEdge.color = graphColors[curEdge.epaType];
                        edgeVerts = [];
                    }
                    catch (e) {
                        alert(e);
                        return;
                    }

                    edgeSource.color = graphColors[edgeSource.epaType];
                    edgeSource = null;
                    curNode.color = graphColors[curNode.epaType];
                    s.refresh();
                }

                resetModelState();
                $chkEdgeEdit.trigger('click');
                updateInp();
            }
        });

        $btnEdgeCancel.click(function() {
            resetModelState();
        });

        $btnEdgeDelete.click(function() {
            $modalEdge.modal('hide');

            s.graph.dropEdge(curEdge.id);

            if (curEdge.type === "vert") {
                for (let vert in curEdge.vert) {
                    s.graph.dropNode(curEdge.vert[vert]);
                }
            }

            resetModelState();
        });

        $edgeTabs.tabs({ active: 0 });

        $('#edge-view-tab').click(function () {
            $modalEdge.find('.modal-dialog').css('left', edgeModalLeft);
            $modalEdge.find('.modal-dialog').css('width', '350px');
            $modalEdge.find('.modal-dialog').css('height', '550px');
        });

        $('#edge-results-tab').click(function () {
            $modalEdge.find('.modal-dialog').css('left', '0');
            $modalEdge.find('.modal-dialog').css('width', '1000px');
            $modalEdge.find('.modal-dialog').css('height', '1180px');
        });

        $viewEdgeResults.find('select').change(function () {
            try {
                let dataset = curEdge.modelResults[$(this).val()];
                let x = [], y = [];
                for (let i in dataset) {
                    y.push(dataset[i]);
                    x.push(i);
                }

                let trace = {
                    x: x,
                    y: y,
                    type: 'scatter'
                };

                let data = [trace];

                let layout = {
                    title: $(this).find('option:selected').text() + " for " + curEdge.epaType + " " + curEdge.properties.epaId,
                    xaxis: {
                        title: 'Timestep'
                    },
                    yaxis: {
                        title: $(this).find('option:selected').text()
                    }
                };

                Plotly.newPlot('edge-plot', data, layout);

                trace = {
                    x: y,
                    name: curEdge.epaType + " " + curEdge.properties.epaId,
                    type: 'box',
                    boxmean: true
                };

                layout = {
                    xaxis: {
                        title: $(this).find('option:selected').text()
                    }
                };

                data = [trace];

                Plotly.newPlot('edge-stats', data, layout);

            }
            catch (e) {
                $('#edge-results').html('<p>Results data for this edge have not been computed</p>');
            }
        });


        //  ********** Model Options **********
        $chkOptionsEdit.click(function () {
            if ($chkOptionsEdit.is(':checked')) {
                $btnOptionsOk.removeAttr('disabled');

                $modelOptions.find('input').attr('readonly', false);
                $modelOptions.find('select').attr('disabled', false);

                $modelOptions.find('input').keyup(function(event) {
                    if (event.keyCode === 13) {
                        $btnOptionsOk.click();
                    }
                });
            }
            else {
                $btnOptionsOk.attr('disabled', true);

                $modelOptions.find('input').attr('readonly', true);
                $modelOptions.find('select').attr('disabled', true);

                $modelOptions.find('input').unbind('keyup');

                populateModelOptions();
            }
        });

        $btnOptionsOk.click(function() {
            for(let key in model.options) {
                if(key.substr(4) === "unbalanced" || key.substr(4) === "quality" || key.substr(4) === "hydraulics") {
                    model.options[key][0] = $('#' + key + 1).val();
                    model.options[key][1] = $('#' + key + 2).val();
                }
                else
                    model.options[key] = $('#' + key).val();
            }

            $chkOptionsEdit.trigger('click');
            updateInp();
        });

        $btnOptionsCancel.click(function () {
            if ($chkOptionsEdit.is(':checked'))
                $chkOptionsEdit.trigger('click')
        });
        //  ---------- Time
        $modalTime.on('shown.bs.modal', function () {
            $modalTime.find('input').keyup(function(event) {
                if (event.keyCode === 13 && $chkTimeEdit.is(':checked')) {
                    $btnTimeOk.click();
                }
            });

            populateTimeModal();
        });

        $modalTime.on('hidden.bs.modal', function () {
            $modalTime.find('input').unbind('keyup');
            if ($chkTimeEdit.is(':checked'))
                $chkTimeEdit.trigger('click')
        });

        $chkTimeEdit.click(function() {
            if ($chkTimeEdit.is(':checked')) {
                $btnTimeOk.removeAttr('disabled');

                $modalTime.find('input').attr('readonly', false);
                $modalTime.find('select').attr('disabled', false);

                $modalTime.find('input')[0].focus();
                $modalTime.find('input')[0].select();
            }
            else {
                $btnTimeOk.attr('disabled', true);

                $modalTime.find('input').attr('readonly', true);
                $modalTime.find('select').attr('disabled', true);

                populateTimeModal();
            }
        });

        $btnTimeOk.click(function () {
            let timeOptions = model.times;
            for (let key in timeOptions) {
                if (key === "pattern" || key === "report") {
                    timeOptions[key][0] = $('#' + key + '1').val();
                    timeOptions[key][1] = $('#' + key + '2').val();
                }
                else if (key === "start")
                    timeOptions[key] = $('#' + key).val().split(' ');
                else
                    timeOptions[key] = $('#' + key).val();
            }

            $chkTimeEdit.trigger('click');
            updateInp();
        });
        //  ---------- Energy
        $modalEnergy.on('shown.bs.modal', function () {
            $modalEnergy.find('input').keyup(function(event) {
                if (event.keyCode === 13 && $chkEnergyEdit.is(':checked')) {
                    $btnEnergyOk.click();
                }
            });

            populateEnergyModal();
        });

        $modalEnergy.on('hidden.bs.modal', function () {
            $modalEnergy.find('input').unbind('keyup');
            if ($chkEnergyEdit.is(':checked'))
                $chkEnergyEdit.trigger('click')
        });

        $chkEnergyEdit.click(function() {
            if ($chkEnergyEdit.is(':checked')) {
                $btnEnergyOk.removeAttr('disabled');

                $modalEnergy.find('input').attr('readonly', false);

                $modalEnergy.find('input')[0].focus();
                $modalEnergy.find('input')[0].select();
            }
            else {
                $btnEnergyOk.attr('disabled', true);

                $modalEnergy.find('input').attr('readonly', true);

                populateEnergyModal();
            }
        });

        $btnEnergyOk.click(function () {
            let energyOptions = model.energy;

            for (let key in energyOptions) {
                energyOptions[key] = $('#' + key).val();
            }

            $chkEnergyEdit.trigger('click');
            updateInp();
        });
        //  ---------- Reactions
        $modalReactions.on('shown.bs.modal', function () {
            $modalReactions.find('input').keyup(function(event) {
                if (event.keyCode === 13 && $chkReactionsEdit.is(':checked')) {
                    $btnReactionsOk.click();
                }
            });

            populateReactionsModal();
        });

        $modalReactions.on('hidden.bs.modal', function () {
            $modalReactions.find('input').unbind('keyup');
            if ($chkReactionsEdit.is(':checked'))
                $chkReactionsEdit.trigger('click')
        });

        $chkReactionsEdit.click(function() {
            if ($chkReactionsEdit.is(':checked')) {
                $btnReactionsOk.removeAttr('disabled');

                $modalReactions.find('input').attr('readonly', false);

                $modalReactions.find('input')[0].focus();
                $modalReactions.find('input')[0].select();
            }
            else {
                $btnReactionsOk.attr('disabled', true);

                $modalReactions.find('input').attr('readonly', true);

                populateReactionsModal();
            }
        });

        $btnReactionsOk.click(function () {
            let reactionsOptions = model.reactions;

            for (let key in reactionsOptions) {
                reactionsOptions[key] = $('#' + key).val();
            }

            $chkReactionsEdit.trigger('click');
            updateInp();
        });
        //  ---------- Report
        $modalReport.on('shown.bs.modal', function () {
            $modalReport.find('input').keyup(function(event) {
                if (event.keyCode === 13 && $chkReportEdit.is(':checked')) {
                    $btnReportOk.click();
                }
            });

            populateReportModal();
        });

        $modalReport.on('hidden.bs.modal', function () {
            $modalReport.find('input').unbind('keyup');
            if ($chkReportEdit.is(':checked'))
                $chkReportEdit.trigger('click')
        });

        $chkReportEdit.click(function() {
            if ($chkReportEdit.is(':checked')) {
                $btnReportOk.removeAttr('disabled');

                $modalReport.find('input').attr('readonly', false);
                $modalReport.find('select').attr('disabled', false);

                $modalReport.find('input')[0].focus();
                $modalReport.find('input')[0].select();
            }
            else {
                $btnReportOk.attr('disabled', true);

                $modalReport.find('input').attr('readonly', true);
                $modalReport.find('select').attr('disabled', false);

                populateReportModal();
            }
        });

        $btnReportOk.click(function () {
            let reportOptions = model.report;

            for (let key in reportOptions) {
                reportOptions[key] = $('#' + key).val();
            }

            $chkReportEdit.trigger('click');
            updateInp();
        });
        //  ---------- Curve
        $modalCurve.on('shown.bs.modal', function () {
            if (Object.keys(model.curves).length > 0) {
                populateCurvesModal();
                $curveSelect.find('select').change();
            }
        });

        $modalCurve.on('hidden.bs.modal', function () {
            if ($btnAddCurve.hasClass('btn-danger'))
                $btnAddCurve.click();
            else if ($chkCurveEdit.is(':checked'))
                $chkCurveEdit.trigger('click')
        });

        $btnCurveOk.click(function () {
            if ($btnAddCurve.hasClass('btn-success')) {
                let values = []
                $curveTable.find('input').each(function( index ) {
                    values.push($(this).val());
                });
                model.curves[$curveSelect.find('select').val()]["values"] = values;

                model.curves[$curveSelect.find('select').val()]["type"] = $inpCurveType.val();

                resetCurveState();
            }
            else {
                let curveId = $inpCurveId.val();

                if (!(curveId in model.curves))
                    model.curves[curveId] = {};

                let values = []
                $curveTable.find('input').each(function( index ) {
                    values.push($(this).val());
                });
                model.curves[curveId]["values"] = values;

                model.curves[curveId]["type"] = $inpCurveType.val();
                $curveSelect.find('select').empty();
                populateCurvesModal();
                $btnAddCurve.click();
                $curveSelect.find('select').val(curveId);
                $curveSelect.find('select').change();
            }
        });

        $btnCurveDelete.click(function () {
            delete model.curves[$curveSelect.find('select').val()];

            $curveSelect.find('select').empty();
            populateCurvesModal();

            if(model.curves.length != 0)
                $curveSelect.find('select').val($curveSelect.find('select option:first').val());

            resetCurveState();
        });

        $chkCurveEdit.click(function () {
            if ($chkCurveEdit.is(':checked')) {
                $btnCurveOk.removeAttr('disabled');
                $btnCurveDelete.removeAttr('disabled');

                $inpCurveType.attr('disabled', false);
                $curveTable.find('input').removeAttr('disabled');
                $('.curve-table-edit').removeClass('hidden');

                $modalCurve.find('input')[0].focus();
                $modalCurve.find('input')[0].select();
            }
            else {
                $btnCurveOk.attr('disabled', true);
                $btnCurveDelete.attr('disabled', true);

                $inpCurveType.attr('disabled', true);
                $curveTable.find('input').attr('disabled', true);
                $('.curve-table-edit').addClass('hidden');

                if ($btnAddCurve.hasClass('btn-danger'))
                    $btnAddCurve.click();
            }
        });

        $curveSelect.find('select').change(function () {
            if (model.curves[$(this).val()]) {
                $inpCurveType.val(model.curves[$(this).val()]["type"]);

                try {
                    dataTableLoadModels.destroy();
                }
                catch (e) {
                    // nothing
                }

                $curveTable.empty();
                $curveTable.html('<thead><th>' + curveGraphLabels[model.curves[$(this).val()]["type"]][0] + '</th><th>' +
                    curveGraphLabels[model.curves[$(this).val()]["type"]][1] + '</th><th></th></thead><tbody></tbody>');

                let hidden = '';
                if (!$chkCurveEdit.is(':checked'))
                    hidden = ' hidden';
                let values = model.curves[$(this).val()]["values"];
                for (let i = 0; i < values.length; ++i) {

                    let pointHtml = '<tr><td><input type="number" name="x" class="x" value="' + parseFloat(values[i]) +
                        '" disabled></td>';
                    ++i;
                    pointHtml += '<td><input type="number" name="y" class="y" value="' + parseFloat(values[i]) +
                        '" disabled></td>';

                    pointHtml += '<td><div class="btn btn-danger btn-group btn-xs curve-table-edit' + hidden +
                        '" role="group" data-toggle="tooltip" title="Remove Point"><span class="glyphicon glyphicon-remove">' +
                        '</span></div></td></tr>';

                    $curveTable.find('tbody').append(pointHtml);
                }

                dataTableLoadModels = $curveTable.DataTable({
                    // "scrollY": '500px',
                    paging: false,
                    searching: false,
                    ordering:  false
                });

                $('#curve-points_info').html('<div id="btn-add-curve-point" class="btn btn-success btn-group btn-xs curve-table-edit hidden" ' +
                    'role="group" style="margin-left: 13px;" data-toggle="tooltip" title="Add Point">' +
                    '<span class="glyphicon glyphicon-plus"></span></div>');

                setAddRemovePointListener();

                $('[data-toggle="tooltip"]').tooltip();

                drawCurve(values);
            }
            else
                $btnAddCurve.click();
        });

        $btnAddCurve.click(function () {
            if ($btnAddCurve.hasClass('btn-success')) {
                if (!$chkCurveEdit.is(':checked'))
                    $chkCurveEdit.trigger('click');

                $btnAddCurve.removeClass('btn-success').addClass('btn-danger');
                $btnAddCurve.find('span').removeClass('glyphicon-plus').addClass('glyphicon-remove');
                $btnAddCurve.prop('title', 'Cancel');
                $curveSelect.addClass('hidden');
                $inpCurveId.removeAttr('hidden');

                $curveDisplay.empty();
                $curveTable.find('tbody').empty();
            }
            else {
                $btnAddCurve.removeClass('btn-danger').addClass('btn-success');
                $btnAddCurve.find('span').removeClass('glyphicon-remove').addClass('glyphicon-plus');
                $btnAddCurve.prop('title', 'New Curve');
                $curveSelect.removeClass('hidden');
                $inpCurveId.attr('hidden', true);

                resetCurveState();
            }
        });

        //  ---------- Pattern
        $modalPattern.on('shown.bs.modal', function () {
            populatePatternModal();
            $patternSelect.find('select').change();
        });

        $modalPattern.on('hidden.bs.modal', function () {
            if ($btnAddPattern.hasClass('btn-danger'))
                $btnAddPattern.click();
            else if ($chkPatternEdit.is(':checked'))
                $chkPatternEdit.trigger('click')
        });

        $btnPatternOk.click(function () {
            if ($btnAddPattern.hasClass('btn-success')) {
                model.patterns[$patternSelect.find('select').val()] = $inpPatternMults.tagsinput('items');
                resetPatternState();
            }
            else {
                let patternId = $inpPatternId.val();
                model.patterns[patternId] = $inpPatternMults.tagsinput('items');
                $patternSelect.find('select').empty();
                populatePatternModal();
                $btnAddPattern.click();
                $patternSelect.find('select').val(patternId);
                $patternSelect.find('select').change();
            }
        });

        $btnPatternDelete.click(function () {
            delete model.patterns[$patternSelect.find('select').val()];

            $patternSelect.find('select').empty();
            populatePatternModal();

            if(model.patterns.length != 0)
                $patternSelect.find('select').val($patternSelect.find('select option:first').val());

            resetPatternState();
        });

        $chkPatternEdit.click(function () {
            if ($chkPatternEdit.is(':checked')) {
                $btnPatternOk.removeAttr('disabled');
                $btnPatternDelete.removeAttr('disabled');

                $inpPatternMults.attr('disabled', false);

                $modalPattern.find('input')[0].focus();
                $modalPattern.find('input')[0].select();
            }
            else {
                $btnPatternOk.attr('disabled', true);
                $btnPatternDelete.attr('disabled', true);

                $inpPatternMults.attr('disabled', true);

                if ($btnAddPattern.hasClass('btn-danger'))
                    $btnAddPattern.click();
            }
        });

        $patternSelect.find('select').change(function () {
            let multipliers = model.patterns[$(this).val()];

            $inpPatternMults.tagsinput('removeAll');
            for (let i in multipliers) {
                $inpPatternMults.tagsinput('add', multipliers[i]);
            }

            drawPattern(multipliers);
        });

        $inpPatternMults.on('itemAdded', function(event) {
            let item = event.item;

            if (isNaN(item)) {
                $inpPatternMults.tagsinput('remove', item);
                alert('Pattern multiplier must be a number.');
            }
        });

        $btnAddPattern.click(function () {
            if ($btnAddPattern.hasClass('btn-success')) {
                if (!$chkPatternEdit.is(':checked'))
                    $chkPatternEdit.trigger('click');

                $btnAddPattern.removeClass('btn-success').addClass('btn-danger');
                $btnAddPattern.find('span').removeClass('glyphicon-plus').addClass('glyphicon-remove');
                $btnAddPattern.prop('title', 'Cancel');
                $patternSelect.addClass('hidden');
                $inpPatternId.removeAttr('hidden');

                $inpPatternMults.tagsinput('removeAll');
                $patternDisplay.empty();
            }
            else {
                $btnAddPattern.removeClass('btn-danger').addClass('btn-success');
                $btnAddPattern.find('span').removeClass('glyphicon-remove').addClass('glyphicon-plus');
                $btnAddPattern.prop('title', 'New Pattern');
                $patternSelect.removeClass('hidden');
                $inpPatternId.attr('hidden', true);

                resetPatternState();
            }
        });
        //  ---------- Controls
        $modalControls.on('shown.bs.modal', function () {
            populateControlsModal();
        });

        $modalControls.on('hidden.bs.modal', function () {
            if ($btnAddControl.hasClass('btn-danger'))
                $btnAddControl.click();
            else if ($chkControlsEdit.is(':checked'))
                $chkControlsEdit.trigger('click')
        });

        $btnControlsOk.click(function () {
            if ($btnAddControl.hasClass('btn-danger')) {
                let newControl = [];
                $('#add-control').find('input, select, h6').each(function () {
                    if ($(this).val() === '')
                        newControl.push($(this).text());
                    else
                        newControl.push($(this).val());
                });
                $controlsDisplay.append('<h6>' + newControl.join(' ') + '</h6>');
                $btnAddControl.click();
            }

            model.controls = [];
            $controlsDisplay.find('h6').each(function (index) {
                model.controls.push($(this).text());
            });

            if ($chkControlsEdit.is(':checked'))
                $chkControlsEdit.trigger('click');

            populateControlsModal();
            updateInp();
        });

        $chkControlsEdit.click(function () {
            if ($chkControlsEdit.is(':checked')) {
                $btnControlsOk.removeAttr('disabled');

                $('.control-remove').removeClass('hidden');
            }
            else {
                $btnControlsOk.attr('disabled', true);

                $('.control-remove').addClass('hidden');

                if ($btnAddControl.hasClass('btn-danger'))
                    $btnAddControl.click();
            }
        });

        $btnAddControl.click(function () {
            if ($btnAddControl.hasClass('btn-success')) {
                if (!$chkControlsEdit.is(':checked'))
                    $chkControlsEdit.trigger('click');

                $btnAddControl.removeClass('btn-success').addClass('btn-danger');
                $btnAddControl.find('span').removeClass('glyphicon-plus').addClass('glyphicon-remove');
                $btnAddControl.prop('title', 'Cancel');

                $controlType.attr('disabled', true);
                $addControlView.html(controlsHtml[$controlType.val()]);

                $('#controls-links').change(function() {
                    let edge = s.graph.edges().find(edge => edge.properties.epaId === $(this).val());

                    $('#controls-status').html(statusHtml[edge.epaType]);
                });
                populateEdgeList($('#controls-links'));
                $('#controls-links').change();

                if ($controlType.val() === "IF NODE") {
                    populateNodeList($('#controls-nodes'));
                }
            }
            else {
                $chkControlsEdit.trigger('click');

                $btnAddControl.removeClass('btn-danger').addClass('btn-success');
                $btnAddControl.find('span').removeClass('glyphicon-remove').addClass('glyphicon-plus');
                $btnAddControl.prop('title', 'New Control');

                $controlType.attr('disabled', false);
                $addControlView.empty();
            }
        });
        //  ---------- Rules
        $modalRules.on('shown.bs.modal', function () {
            populateRulesModal();
        });

        $modalRules.on('hidden.bs.modal', function () {
            if ($chkRulesEdit.is(':checked'))
                $chkRulesEdit.trigger('click')
        });

        $btnRulesOk.click(function () {
            if ($btnAddRule.hasClass('btn-danger') && $inpRuleId.val() !== "" && $inpRuleBody.val() !== "") {
                console.log($inpRuleBody.val().split(/\r?\n/));
                model.rules[$inpRuleId.val()] = $inpRuleBody.val().split(/\r?\n/);
                populateRulesModal();
            }

            model.rules = {};
            $('.rules').each(function (index) {
                let ruleId = $(this).find('h6').text().substr(5);
                model.rules[ruleId] = [];
                let rule = model.rules[ruleId];

                $(this).find('p').each(function (index) {
                    rule.push($(this).text());
                });
            });

            if ($chkRulesEdit.is(':checked'))
                $chkRulesEdit.trigger('click');

            populateRulesModal();
            updateInp();
        });

        $chkRulesEdit.click(function () {
            if ($chkRulesEdit.is(':checked')) {
                $btnRulesOk.removeAttr('disabled');

                $('.rule-remove').removeClass('hidden');
            }
            else {
                $btnRulesOk.attr('disabled', true);

                $('.rule-remove').addClass('hidden');

                if ($btnAddRule.hasClass('btn-danger')) {
                    $btnAddRule.click();
                }
            }
        });

        $btnAddRule.click(function () {
            if ($btnAddRule.hasClass('btn-success')) {
                if (!$chkRulesEdit.is(':checked'))
                    $chkRulesEdit.trigger('click');

                $btnAddRule.removeClass('btn-success').addClass('btn-danger');
                $btnAddRule.find('span').removeClass('glyphicon-plus').addClass('glyphicon-remove');
                $btnAddRule.prop('title', 'Cancel');

                $inpRuleId.removeAttr('hidden');
                $inpRuleBody.removeAttr('hidden');
                $('.rule-add').removeClass('hidden');
            }
            else {
                $chkRulesEdit.trigger('click');

                $btnAddRule.removeClass('btn-danger').addClass('btn-success');
                $btnAddRule.find('span').removeClass('glyphicon-remove').addClass('glyphicon-plus');
                $btnAddRule.prop('title', 'New Rule');

                $inpRuleId.attr('hidden', true);
                $inpRuleBody.attr('hidden', true);
                $inpRuleId.val('');
                $inpRuleBody.val('');
                $('.rule-add').addClass('hidden');
            }
        });


        //  ********** Upload **********
        $btnUl.click(function() {
            if ($inpUlTitle.val() !== '' && $inpUlDescription.val() !== '' && $inpUlKeywords.val() !== '') {
                $loadingAnimation.removeAttr('hidden');
                model.title = [$inpUlTitle.val(), $inpUlDescription.val()];
                model.nodes = s.graph.nodes();
                model.edges = s.graph.edges();

                let epanetWriter = new EPANET_Writer(model);

                let data = new FormData();
                data.append('model_title', $inpUlTitle.val());
                data.append('model_description', $inpUlDescription.val());
                data.append('model_keywords', $inpUlKeywords.tagsinput('items'));
                data.append('model_file', epanetWriter.getFile());

                uploadModel(data);

                $('#modal-upload').modal('hide');
                resetUploadState();
            }
            else {
                alert("Fields not entered correctly. Cannot upload model to Hydroshare. Fill the correct fields in and try again.");
            }
        });

        $btnUlCancel.click(function() {
            resetUploadState();
        });


        //  ********** Animation **********
        $btnAnimateTools.click(function () {
            if ($animateToolbar.is(':hidden')) {
                $animateToolbar.removeClass('hidden');
                $btnAnimateTools.css("background-color", "#915F6D");
                $btnAnimateTools.css("color", "white");
            }
            else {
                $animateToolbar.addClass('hidden');
                $btnAnimateTools.css("background-color", "white");
                $btnAnimateTools.css("color", "#555");
            }
        });

        $btnPlayAnimation.click(function () {
            if ($chkNodes.is(':checked') || $chkEdges.is(':checked')) {
                if (playing === false) {
                    resetPlay();

                    let delayStep = -1;
                    for (let j = $animationSlider.slider("value"); j <= animationMaxStep; ++j) {
                        delayStep++;
                        animate.push(setTimeout(function () {
                            $animationSlider.slider("value", j);
                            $('#timestep').val(j + 1);
                            $queryTimestep.val($animationSlider.slider("value") + 1);
                            if (j === animationMaxStep)
                                resetAnimation(true);
                            else {
                                if ($chkNodes.is(':checked')) {
                                    for (let node in s.graph.nodes()) {
                                        try {
                                            s.graph.nodes()[node].color = nodeAnimColor(s.graph.nodes()[node].modelResults[$nodeAnimType.val()][j]).hex();
                                        }
                                        catch (e) {
                                            // nothing
                                        }
                                    }
                                }

                                if ($chkEdges.is(':checked')) {
                                    for (let edge in s.graph.edges()) {
                                        try {
                                            s.graph.edges()[edge].color = edgeAnimColor(s.graph.edges()[edge].modelResults[$edgeAnimType.val()][j]).hex();
                                        }
                                        catch (e) {
                                            // nothing
                                        }
                                    }
                                }
                                s.refresh();
                            }
                        }, animationDelay * delayStep));
                    }
                }
                else {
                    resetPlay();

                    stopAnimation();
                }
            }
            else {
                $btnStopAnimation.click();
            }
        });

        $btnStopAnimation.click(function() {
            resetAnimation(true);
        });

        $chkNodes.click(function () {
            let reStart = playing;

            playing = true;
            $btnPlayAnimation.click();
            if (!$(this).is(':checked')) {
                for (let node in s.graph.nodes()) {
                    s.graph.nodes()[node].color = s.graph.nodes()[node].epaColor;
                }
                s.refresh();
            }
            resetNodeAnim();

            if (reStart)
                $btnPlayAnimation.click();
        });

        $nodeAnimColor.change(function () {
            let reStart = playing;

            playing = true;
            $btnPlayAnimation.click();
            resetNodeAnim();

            if (reStart)
                $btnPlayAnimation.click();
        });

        $nodeAnimType.change(function () {
            let reStart = playing;

            playing = true;
            $btnPlayAnimation.click();
            resetNodeAnim();

            if (reStart)
                $btnPlayAnimation.click();
        });

        $chkEdges.click(function () {
            let reStart = playing;

            playing = true;
            $btnPlayAnimation.click();
            if (!$(this).is(':checked')) {
                for (let edge in s.graph.edges()) {
                    s.graph.edges()[edge].color = s.graph.edges()[edge].epaColor;
                }
                s.refresh();
            }
            resetEdgeAnim();

            if (reStart)
                $btnPlayAnimation.click();
        });

        $edgeAnimColor.change(function () {
            let reStart = playing;

            playing = true;
            $btnPlayAnimation.click();
            resetEdgeAnim();

            if (reStart)
                $btnPlayAnimation.click();
        });

        $edgeAnimType.change(function () {
            let reStart = playing;

            playing = true;
            $btnPlayAnimation.click();
            resetEdgeAnim();

            if (reStart)
                $btnPlayAnimation.click();
        });

        $("#btn-increase").on("click", function() {
            if ($animationSpeed.val() < 99) {
                $animationSpeed.val(parseInt($animationSpeed.val()) + 1);
                animationDelay = 1000 / $animationSpeed.val();
            }
            if (playing === true) {
                stopAnimation();
                playing = false;
                $btnPlayAnimation.click();
            }
        });

        $("#btn-decrease").on("click", function() {
            if ($animationSpeed.val() > 1) {
                $animationSpeed.val(parseInt($animationSpeed.val()) - 1);
                animationDelay = 1000 / $animationSpeed.val();
            }
            if (playing === true) {
                stopAnimation();
                playing = false;
                $btnPlayAnimation.click();
            }
        });


        //  ********** Query **********d
        $btnQueryTools.click(function () {
            if ($queryToolbar.is(':hidden')) {
                $queryToolbar.css({left:($('#model-container').children('canvas').offset().left - 146), position:'absolute'});
                $queryToolbar.removeClass('hidden');
                $btnQueryTools.css("background-color", "#915F6D");
                $btnQueryTools.css("color", "white");
                $queryType.change();
            }
            else {
                $queryToolbar.addClass('hidden');
                $btnQueryTools.css("background-color", "white");
                $btnQueryTools.css("color", "#555");
                $btnClearQuery.click();
            }
        });

        $btnQuery.click(function () {
            $btnClearQuery.click();

            let count = 0;
            let elements = s.graph[$queryType.val()]();
            for (let elem in elements) {
                elem = elements[elem];
                try {
                    let value = parseFloat(elem.modelResults[$queryResult.val()][$animationSlider.slider("value")]);
                    if ($queryCondintion.val() === 'above') {
                        if (value > $queryValue.val()) {
                            queryElements.push(elem);
                            elem.color = highlight;
                            ++count;
                        }
                    }
                    else if ($queryCondintion.val() === 'below') {
                        if (value < $queryValue.val()) {
                            queryElements.push(elem);
                            elem.color = highlight;
                            ++count;
                        }
                    }
                    else {
                        if (value === $queryValue.val()) {
                            queryElements.push(elem);
                            elem.color = highlight;
                            ++count;
                        }
                    }
                }
                catch (e) {
                    // nothing
                }
            }

            $queryCount.val(count);
            s.refresh();
        });

        $btnClearQuery.click(function () {
            queryElements = [];
            resetAnimation(false);
            $queryCount.val('');
            s.refresh();
        });

        $queryType.change(function () {
            $queryResult.empty();
            $queryResult.append(queryResults[$(this).val()]);
            $queryTimestep.val($animationSlider.slider("value") + 1);
            $btnClearQuery.click();
        });

        $queryResult.change(function () {
            $btnClearQuery.click();
        });

        $queryCondintion.change(function () {
            $btnClearQuery.click();
        });


        //  ********** Editing **********
        $btnEditTools.click(function () {
            if ($editToolbar.is(':hidden')) {
                $editToolbar.removeClass('hidden');
                $btnEditTools.css("background-color", "#915F6D");
                $btnEditTools.css("color", "white");
                $queryType.trigger('click');
            }
            else {
                $editToolbar.addClass('hidden');
                $editToolbar.find('a').removeClass('active');
                $btnEditDefualt.addClass('active');
                $btnEditTools.css("background-color", "white");
                $btnEditTools.css("color", "#555");
                $('#model-container').css("cursor", "default");
                isAddEdge = false;
                isAddNode = false;
            }
        });

        $editToolbar.find('a').click(function () {
            addType = this.name;
            if (this.name === 'Full-Extent') {
                $("#model-container").remove();
                $("#model-display").append("<div id='model-container'></div>");
                drawModel();
            }
            else if (this.name !== 'Search') {
                if ($(this).hasClass('active') && addType !== "Default")
                    $btnEditDefualt.click();
                else {
                    $editToolbar.find('a').removeClass('active');
                    $(this).addClass('active');

                    sigma.plugins.killDragNodes(s);

                    isAddEdge = false;
                    isAddNode = false;
                    if (edgeSource) {
                        edgeSource.color = edgeSource.epaColor;
                        curNode.color = curNode.epaColor;
                        s.refresh();
                    }
                    edgeSource = null;

                    if (addType === "Default") {
                        $('#model-container').css("cursor", "default");
                        s.refresh();
                    }
                    else if (addType === "Drag") {
                        let dragListener = sigma.plugins.dragNodes(s, s.renderers[0]);

                        dragListener.bind('startdrag', function(e) {
                            s.settings.autoRescale = false;
                            $('#model-container').css("cursor", "-webkit-grabbing");
                        });
                        dragListener.bind('drag', function(e) {
                            s.unbind('clickNodes');
                        });
                        dragListener.bind('dragend', function(e) {
                            $('#model-container').css("cursor", "-webkit-grab");

                            setTimeout(function(){
                                s.bind('clickNodes', function(e) {
                                    nodeClick(e);
                                });
                            },250);
                        });

                        $('#model-container').css("cursor", "-webkit-grab");
                    }
                    else if (addType === "Junction" || addType === "Reservoir" || addType === "Tank" || addType === "Label") {
                        isAddNode = true;
                        $('#model-container').css("cursor", "crosshair");
                    }
                    else {
                        isAddEdge = true;
                        $('#model-container').css("cursor", "pointer");
                    }
                }
            }
        });


        //  ********** Other **********
        $loadFromLocal.addEventListener('change', function() {
            let file = $loadFromLocal.files[0];

            let reader = new FileReader();

            reader.onload = function() {
                $fileDisplayArea.innerText = reader.result;
                file_text = reader.result;
            };

            reader.readAsText(file);
        });

        $viewTabs.tabs({ active: 0 });
    };

    addMetadataToUI = function (metadata) {
        let metadataDisplayArea = $('#metadata-display-area')[0];
        let metadataHTML = '<p><h1>' + metadata['title'] + '</h1><h6>' + metadata['description'] + '</h6>' +
            '<a href="' + metadata['identifiers'][0]['url'] + '" style="color:#3366ff">View the Model in HydroShare</a><br><br>' +
            'Created: ' + metadata['dates'][1]['start_date'].substring(0, 10) +
            ', &emsp;Last Modified: ' + metadata['dates'][1]['start_date'].substring(0, 10) +
            '<br>Author: ' + metadata['creators'][0]['name'] + '<br>Rights: ' + metadata['rights'];

        let subjects = "";
        let i;
        for (i in metadata['subjects']) {
            subjects += metadata['subjects'][i]['value'] + ', ';
        }
        metadataHTML += '<br>Subjects: ' + subjects.substring(0, subjects.length - 2);


        try {
            metadataHTML += '<br> Program: ' + '<a href="' + metadata['executed_by']['modelProgramIdentifier'] +
                '" style="color:#3366ff">' + metadata['executed_by']['modelProgramName'] + '</a>';
        }
        catch (error) {
            //    No program included in metadata
        }


        metadataHTML += '</p><br>';

        metadataHTML += '<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title"><a data-toggle="collapse" href="#metadata-json">&nbsp; Raw Metadata JSON<span class="glyphicon glyphicon-minus pull-left"></span></a></h4></div><div id="metadata-json" class="filter-list panel-collapse collapse"><pre>' + JSON.stringify(metadata, null, 2) + '</pre></div></div>';

        metadataDisplayArea.innerHTML = metadataHTML;
    };

    hideMainLoadAnim = function () {
        $('#div-loading').addClass('hidden');
    };

    showLoadingCompleteStatus = function (success, message) {
        let successClass = success ? 'success' : 'error';
        let $modelLoadingStatus = $('#model-load-status');
        let $statusText = $('#status-text');
        let showTime = success ? 2000 : 4000;
        $statusText.text(message)
            .removeClass('success error')
            .addClass(successClass);
        $modelLoadingStatus.removeClass('hidden');
        setTimeout(function () {
            $modelLoadingStatus.addClass('hidden');
        }, showTime);
    };

    addLogEntry = function (type, message, show) {
        let icon;
        let timeStamp;

        switch (type) {
            case 'success':
                icon = 'ok';
                break;
            case 'danger':
                icon = 'remove';
                showLog = true;
                break;
            default:
                icon = type;
                showLog = true;
        }

        timeStamp = new Date().toISOString();

        $('#logEntries').prepend('<div class="alert-' + type + '">' +
            '<span class="glyphicon glyphicon-' + icon + '-sign" aria-hidden="true"></span>  '
            + timeStamp + ' *** \t'
            + message +
            '</div><br>');

        if (show) {
            $modalLog.modal('show');
            showLog = false;
        }
    };

    checkCsrfSafe = function (method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    };

    getCookie = function (name) {
        let cookie;
        let cookies;
        let cookieValue = null;
        let i;

        if (document.cookie && document.cookie !== '') {
            cookies = document.cookie.split(';');
            for (i = 0; i < cookies.length; i += 1) {
                cookie = $.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    addDefaultBehaviorToAjax = function () {
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!checkCsrfSafe(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                }
            }
        });
    };


    /*-----------------------------------------------
     ************** ONLOAD FUNCTION ****************
     ----------------------------------------------*/
    $(function () {
        $('#tagsinp-pattern-mults').tagsinput({allowDuplicates: true});

        initializeJqueryVariables();
        addInitialEventListeners();

        if ($initialModel.length) {
            openModel($initialModel.html());
        }
        else {
            $chkAutoUpdate.attr('checked', false);
            alert("For optimization in creating a new model, auto-update is turned off. Once the initial model has been created" +
                " check the auto-update toggle to update the .inp file. Once this is done the model can then be run.");

            $btnEditTools.click();
            s = new sigma({
                graph: {
                    nodes: [
                        {
                            id: 'rando1',
                            size: 0,
                            x: 0,
                            y: 0,
                            hidden: true,
                            properties: {epaId: ''}
                        },
                        {
                            id: 'rando2',
                            size: 0,
                            x: 1000,
                            y: 1000,
                            hidden: true,
                            properties: {epaId: ''}
                        }
                    ]
                },
                renderer: {
                    container: $("#model-container")[0],
                    type: 'canvas'
                },
                settings: {
                    minNodeSize: 0,
                    maxNodeSize: 6.5,
                    minEdgeSize: 0.5,
                    maxEdgeSize: 4,
                    enableEdgeHovering: true,
                    edgeHoverSizeRatio: 1.5,
                    nodesPowRatio: 0.3,
                    edgesPowRatio: 0.2,
                    immutable: false,
                }
            });
            readModel();
            setGraphEventListeners();
        }

        $("#app-content-wrapper").removeClass('show-nav');
        $('[data-toggle="tooltip"]').tooltip();

        addDefaultBehaviorToAjax();

        // Custom edge render for edges with vertices
        sigma.utils.pkg('sigma.canvas.edges');
        sigma.canvas.edges.vert = function(edge, source, target, context, settings) {
            let color = edge.color,
                prefix = settings('prefix') || '';

            context.strokeStyle = color;
            context.lineWidth = edge[prefix + 'size'];

            context.beginPath();
            context.moveTo(
                source[prefix + 'x'],
                source[prefix + 'y']
            );

            let verticies = edge.vert;

            for (let i = 0; i < verticies.length; ++i) {
                try {
                    let nodesOnScreen = s.renderers["0"].nodesOnScreen;
                    let nextVert = nodesOnScreen.find(node => node.properties.epaId === verticies[i]);

                    context.lineTo(
                        nextVert[prefix + 'x'],
                        nextVert[prefix + 'y']
                    );
                }
                catch (e) {
                    // nothing
                }
            }

            context.lineTo(
                target[prefix + 'x'],
                target[prefix + 'y']
            );

            context.stroke();
        };

        sigma.utils.pkg('sigma.canvas.edgehovers');
        sigma.canvas.edgehovers.vert = function(edge, source, target, context, settings) {
            let color = edge.color,
                prefix = settings('prefix') || '',
                size = settings('edgeHoverSizeRatio') * (edge[prefix + 'size'] || 1),
                edgeColor = settings('edgeColor'),
                defaultNodeColor = settings('defaultNodeColor'),
                defaultEdgeColor = settings('defaultEdgeColor'),
                sX = source[prefix + 'x'],
                sY = source[prefix + 'y'],
                tX = target[prefix + 'x'],
                tY = target[prefix + 'y'];

            if (!color)
                switch (edgeColor) {
                    case 'source':
                        color = source.color || defaultNodeColor;
                        break;
                    case 'target':
                        color = target.color || defaultNodeColor;
                        break;
                    default:
                        color = defaultEdgeColor;
                        break;
                }

            if (settings('edgeHoverColor') === 'edge') {
                color = edge.hover_color || color;
            } else {
                color = edge.hover_color || settings('defaultEdgeHoverColor') || color;
            }

            context.strokeStyle = color;
            context.lineWidth = size;
            context.beginPath();
            context.moveTo(sX, sY);
            let verticies = edge.vert;
            for (let i = 0; i < verticies.length; ++i) {
                try {
                    let nodesOnScreen = s.renderers["0"].nodesOnScreen;
                    let nextVert = nodesOnScreen.find(node => node.properties.epaId === verticies[i]);

                    context.lineTo(
                        nextVert[prefix + 'x'],
                        nextVert[prefix + 'y']
                    );
                }
                catch (e) {
                    // nothing
                }
            }
            context.lineTo(tX, tY);
            context.stroke();
        };
    });


    function locateNode (e) {
        if (curNode && curNode.color === highlight)
            curNode.color = curNode.epaColor;
        let nid = e.target[e.target.selectedIndex].value;
        curNode = s.graph.nodes().find(node => node.properties.epaId === nid);
        curNode.color = highlight;

        if (nid == '') {
            locate.center(1);
        }
        else {
            locate.nodes(nid);
        }
    };

    function locateEdge (e) {
        if (curEdge && curEdge.color === highlight)
            curEdge.color = curEdge.epaColor;
        let nid = e.target[e.target.selectedIndex].value;
        curEdge = s.graph.edges().find(edge => edge.properties.epaId === nid);
        curEdge.color = highlight;

        if (nid == '') {
            locate.center(1);
        }
        else {
            locate.edges(nid);
        }
    };


    /*-----------------------------------------------
     ************** Helper FUNCTION ****************
     ----------------------------------------------*/
    function calculateOffset(element) {
        let style = window.getComputedStyle(element);
        let getCssProperty = function(prop) {
            return parseInt(style.getPropertyValue(prop).replace('px', '')) || 0;
        };
        return {
            left: element.getBoundingClientRect().left + getCssProperty('padding-left'),
            top: element.getBoundingClientRect().top + getCssProperty('padding-top')
        };
    }


    /*-----------------------------------------------
     ***************INVOKE IMMEDIATELY***************
     ----------------------------------------------*/

    sigma.utils.pkg('sigma.canvas.nodes');

    showLog = false;
}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.