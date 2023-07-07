inputSparam = r"D:\Scripts\aapyAEDT\SparamDelayCheck\hbm_dqh7_13_notsv_0ord_solvIns.s12p"
drvName = "N7"
rcvName = "HBM"
# portNamingConvention="$REFDES.$PINNAME.$NETNAME"
portNamingConventionSeparator = '.'
diffPairSuffix_pos = '_t'
diffPairSuffix_neg = '_c'
drv_datarate='3.2GHz'

desktop_version = "2023.1"
non_graphical = False
new_thread = True

# =======================================================================================================================
# ============================================== Code starts here: ======================================================
# =======================================================================================================================

import pyaedt
import os
from itertools import permutations as perm

aedt_file_name = os.path.join(os.path.dirname(inputSparam),'SkewCheck.aedt')
aedb_folder = os.path.join(os.path.dirname(inputSparam),'SkewCheck.aedb')

if os.path.exists(aedt_file_name):
    os.remove(aedt_file_name)
if os.path.exists(aedb_folder):
    os.remove(aedb_folder)
 
desktop = pyaedt.launch_desktop(desktop_version, non_graphical, new_thread)
circ = pyaedt.Circuit(projectname=aedt_file_name,designname='skewAnalysis')
circ.modeler.schematic_units='mil'
circ['datarate']=drv_datarate
circ['ui']='1/datarate'
circ['trf']='ui/5'
sch_circ = circ.modeler.schematic

setup1 = circ.create_setup(setupname="MyTransient", setuptype=circ.SETUPS.NexximTransient)
setup1.props["TransientData"] = ["0.01ns", "10ns"]

sparam_filename = os.path.basename(inputSparam)
sparam_modelname = sparam_filename.split('.s')[0]
mynport=sch_circ.create_model_from_touchstone(touchstone_full_path=inputSparam,
                                              model_name=sparam_modelname)
sparam = sch_circ.create_touchsthone_component(model_name=sparam_modelname)
sparam_npins = len(sparam.pins)
sparam_pinlist = {p.name:p for p in sparam.pins}

sparam_pins_dict = {}
for p in sparam_pinlist:
    rd,_,net = p.split(portNamingConventionSeparator)
    if net.endswith(diffPairSuffix_pos):
        sparam_pins_dict[p] = {'RefDes':rd,
                               'NetName':net,
                               'isDiffPair':True,
                               'diffNet':net.rstrip(diffPairSuffix_pos),
                               'posTerm':p,
                               'negTerm':None}
    elif net.endswith(diffPairSuffix_neg):
        sparam_pins_dict[p] = {'RefDes':rd,
                               'NetName':net,
                               'isDiffPair':True,
                               'diffNet':net.rstrip(diffPairSuffix_neg),
                               'posTerm':None,
                               'negTerm':p}        
    else:
        sparam_pins_dict[p] = {'RefDes':rd,
                               'NetName':net,
                               'isDiffPair':False,
                               'diffNet':None,
                               'posTerm':p,
                               'negTerm':None}

for p1,p2 in perm(sparam_pins_dict,2):
    if sparam_pins_dict[p1]['isDiffPair'] and sparam_pins_dict[p2]['isDiffPair']:
        if sparam_pins_dict[p1]['RefDes'] == sparam_pins_dict[p2]['RefDes']:
            if sparam_pins_dict[p1]['diffNet'] == sparam_pins_dict[p2]['diffNet']:
                if sparam_pins_dict[p1]['posTerm'] == None:
                    sparam_pins_dict[p1]['posTerm'] = p2
                elif sparam_pins_dict[p1]['negTerm'] == None:
                    sparam_pins_dict[p1]['negTerm'] = p2
                elif sparam_pins_dict[p2]['posTerm'] == None:
                    sparam_pins_dict[p2]['posTerm'] = p1
                elif sparam_pins_dict[p2]['negTerm'] == None:
                    sparam_pins_dict[p2]['negTerm'] = p1  

added_src=[]
page_ports_diff=[]
curves2plot = []
for pin in sparam.pins:
    if sparam_pins_dict[pin.name]['RefDes'] == drvName:
        if sparam_pins_dict[pin.name]['isDiffPair'] and sparam_pins_dict[pin.name]['diffNet'] not in added_src:
            srcloc = [pin.location[0]-2700,pin.location[1]*8]
            diffsrc = sch_circ.create_component(component_library="Independent Sources",
                                                component_name="EYESOURCE_DIFF",
                                                location=srcloc)
            diffsrc.parameters['vlow']='-0.5V'
            diffsrc.parameters['vhigh']='0.5V'
            diffsrc.parameters['trise']='trf'
            diffsrc.parameters['tfall']='trf'
            diffsrc.parameters['UIorBPSValue']='ui'
            if pin.name == sparam_pins_dict[pin.name]['posTerm']:
                pos_page_port_name = '{}_{}'.format(sparam_pins_dict[pin.name]['RefDes'],
                                         sparam_pins_dict[pin.name]['NetName'])
                neg_page_port_name = '{}_{}'.format(sparam_pins_dict[pin.name]['RefDes'],
                                         sparam_pins_dict[sparam_pins_dict[pin.name]['negTerm']]['NetName'])
                page_ports_diff.append((pos_page_port_name,neg_page_port_name,sparam_pins_dict[pin.name]['diffNet']))
                diffsrc.pins[1].connect_to_component(component_pin=pin,
                                                     page_name=pos_page_port_name)
                diffsrc.pins[0].connect_to_component(component_pin=sparam_pinlist[sparam_pins_dict[pin.name]['negTerm']],
                                                     page_name=neg_page_port_name)
            if pin.name == sparam_pins_dict[pin.name]['negTerm']:
                neg_page_port_name = '{}_{}'.format(sparam_pins_dict[pin.name]['RefDes'],
                                         sparam_pins_dict[pin.name]['NetName'])
                pos_page_port_name = '{}_{}'.format(sparam_pins_dict[pin.name]['RefDes'],
                                         sparam_pins_dict[sparam_pins_dict[pin.name]['posTerm']]['NetName'])
                page_ports_diff.append((pos_page_port_name,neg_page_port_name,sparam_pins_dict[pin.name]['diffNet']))
                diffsrc.pins[0].connect_to_component(component_pin=pin,
                                                     page_name=neg_page_port_name)
                diffsrc.pins[1].connect_to_component(component_pin=sparam_pinlist[sparam_pins_dict[pin.name]['posTerm']],
                                                     page_name=pos_page_port_name)
            added_src.append(sparam_pins_dict[pin.name]['diffNet'])
        elif not sparam_pins_dict[pin.name]['isDiffPair']:
            srcloc = [pin.location[0]-2000,pin.location[1]*8]
            eyesrc = sch_circ.create_component(component_library="Independent Sources",
                                                component_name="EYESOURCE",
                                                location=srcloc)
            eyesrc.parameters['vlow']='0V'
            eyesrc.parameters['vhigh']='0.5V'
            eyesrc.parameters['trise']='trf'
            eyesrc.parameters['tfall']='trf'
            eyesrc.parameters['UIorBPSValue']='ui'
            page_port_name='{}_{}'.format(sparam_pins_dict[pin.name]['RefDes'],
                                          sparam_pins_dict[pin.name]['NetName'])
            eyesrc.pins[0].connect_to_component(component_pin=pin,
                                                page_name=page_port_name)
            added_src.append(sparam_pins_dict[pin.name]['NetName'])
            curves2plot.append(page_port_name)
    if sparam_pins_dict[pin.name]['RefDes'] == rcvName:
        resloc = [pin.location[0]+2700,pin.location[1]*6]
        resistor = sch_circ.create_resistor(value=50,location=resloc)
        page_port_name='{}_{}'.format(sparam_pins_dict[pin.name]['RefDes'],
                                      sparam_pins_dict[pin.name]['NetName'])
        resistor.pins[1].connect_to_component(component_pin=pin,
                                              page_name=page_port_name)
        gndloc = [resloc[0]+200,resloc[1]-100]
        gnd = circ.modeler.components.create_gnd(location=gndloc)
        if sparam_pins_dict[pin.name]['isDiffPair']:
            if pin.name == sparam_pins_dict[pin.name]['posTerm']:
                pos_page_port_name = '{}_{}'.format(sparam_pins_dict[pin.name]['RefDes'],
                                         sparam_pins_dict[pin.name]['NetName'])
                neg_page_port_name = '{}_{}'.format(sparam_pins_dict[pin.name]['RefDes'],
                                         sparam_pins_dict[sparam_pins_dict[pin.name]['negTerm']]['NetName'])
                page_ports_diff.append((pos_page_port_name,neg_page_port_name,sparam_pins_dict[pin.name]['diffNet']))
            if pin.name == sparam_pins_dict[pin.name]['negTerm']:
                neg_page_port_name = '{}_{}'.format(sparam_pins_dict[pin.name]['RefDes'],
                                         sparam_pins_dict[pin.name]['NetName'])
                pos_page_port_name = '{}_{}'.format(sparam_pins_dict[pin.name]['RefDes'],
                                         sparam_pins_dict[sparam_pins_dict[pin.name]['posTerm']]['NetName'])
                page_ports_diff.append((pos_page_port_name,neg_page_port_name,sparam_pins_dict[pin.name]['diffNet']))
        else:
            curves2plot.append(page_port_name)

for trio in list(set(page_ports_diff)):
    p,n,net = trio
    if p.startswith(drvName):
        outvarname='DIFF_{}_{}'.format(drvName,net)
        if outvarname not in circ.ooutput_variable.GetOutputVariables():
            circ.ooutput_variable.CreateOutputVariable(outvarname,
                                                        'V({})-V({})'.format(p,n),
                                                        "MyTransient",
                                                        "Standard",
                                                        ["Domain:=", "Time"])
    elif p.startswith(rcvName):
        outvarname='DIFF_{}_{}'.format(rcvName,net)
        if outvarname not in circ.ooutput_variable.GetOutputVariables():
            circ.ooutput_variable.CreateOutputVariable(outvarname,
                                                        'V({})-V({})'.format(p,n),
                                                        "MyTransient",
                                                        "Standard",
                                                        ["Domain:=", "Time"])
   
curves2plot += circ.ooutput_variable.GetOutputVariables() 

delay_curves_se = [(i,o) for i,o in perm(curves2plot,2) if i[len(drvName+'_'):]==o[len(rcvName+'_'):]]            
delay_curves_df = [(i,o) for i,o in perm(curves2plot,2) if 'DIFF' in i and 'DIFF' in o and i[len('DIFF_'+drvName+'_'):]==o[len('DIFF_'+rcvName+'_'):]]

skew_curves = [(i,o) for i,o in perm(curves2plot,2) if i.startswith(rcvName) and 'DIFF_'+rcvName in o and i[len(rcvName+'_'):]!=o[len('DIFF_'+rcvName+'_'):]]

curves_for_delay_table = []
for curve in delay_curves_se:
    new_report = circ.post.reports_by_category.standard(['V({})'.format(curve[0]),
                                                         'V({})'.format(curve[1])])
    new_report.plot_name='Delay '+curve[1]
    new_report.domain = "Time"
    new_report.create()

    delay_exp_se = "abs(XAtYVal(V({0}), min(V({0}))+ pk2pk(V({0}))/2 )-XAtYVal(V({1}), min(V({1}))+pk2pk(V({1}))/2 ))"
    curves_for_delay_table.append(delay_exp_se.format(curve[0],curve[1]))

for curve in delay_curves_df:
    new_report = circ.post.reports_by_category.standard(['{}'.format(curve[0]),
                                                         '{}'.format(curve[1])])
    new_report.plot_name='Delay '+curve[1]
    new_report.domain = "Time"
    new_report.create()
    
    delay_exp_df = "abs(XAtYVal({0}, min({0})+ pk2pk({0})/2 )-XAtYVal({1}, min({1})+pk2pk({1})/2 ))"
    curves_for_delay_table.append(delay_exp_df.format(curve[0],curve[1]))
    
new_report_dt = circ.post.reports_by_category.standard(curves_for_delay_table)
new_report_dt.plot_name='Delay at '+curve[1]
new_report_dt.report_type='Data Table'				
new_report_dt.domain = "Time"
new_report_dt.create()

curves_for_skew_table = []    
for curve in skew_curves:
    new_report = circ.post.reports_by_category.standard(['V({})'.format(curve[0]),
                                                         '{}'.format(curve[1])])
    new_report.plot_name='Skew curves {} {}'.format(curve[0],curve[1])
    new_report.domain = "Time"
    new_report.create()

    skew_exp = "abs(XAtYVal(V({0}), min(V({0}))+ pk2pk(V({0}))/2 )-XAtYVal({1}, min({1})+pk2pk({1})/2 ))"
    curves_for_skew_table.append(skew_exp.format(curve[0],curve[1]))
    
new_report_dt = circ.post.reports_by_category.standard(curves_for_skew_table)
new_report_dt.plot_name='Skew Table'
new_report_dt.report_type='Data Table'				
new_report_dt.domain = "Time"
new_report_dt.create()

circ.analyze_setup("MyTransient")

circ.save_project()
desktop.release_desktop(True,True)
