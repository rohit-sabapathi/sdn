from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
import time

class DynamicRouting(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DynamicRouting, self).__init__(*args, **kwargs)
        self.datapaths = {}
        
        # Explicitly configured paths
        # Format: dpid: {in_port: out_port, ...} for both directions
        # Primary: h1 <-> s1(port 2) <-> s2 <-> s4(port 1) <-> h2
        self.primary_path = {
            1: {1: 2, 2: 1}, # s1
            2: {1: 2, 2: 1}, # s2
            4: {1: 3, 3: 1}  # s4
        }
        
        # Alternate: h1 <-> s1(port 3) <-> s3 <-> s4(port 2) <-> h2
        self.alternate_path = {
            1: {1: 3, 3: 1}, # s1
            3: {1: 2, 2: 1}, # s3
            4: {2: 3, 3: 2}  # s4
        }
        
        self.current_path = 'primary'

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.datapaths[datapath.id] = datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        
        self.logger.info("Switch s%s connected.", datapath.id)
        
        # When all 4 switches are connected, install primary path
        if len(self.datapaths) == 4:
            self.logger.info("All switches connected. Initializing paths.")
            self.install_path('primary')

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)
        
    def clear_flows(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        empty_match = parser.OFPMatch()
        instructions = []
        flow_mod = parser.OFPFlowMod(datapath, 0, 0, 0,
                                     ofproto.OFPFC_DELETE, 0, 0,
                                     1,
                                     ofproto.OFPCML_NO_BUFFER,
                                     ofproto.OFPP_ANY,
                                     ofproto.OFPG_ANY, 0,
                                     empty_match, instructions)
        datapath.send_msg(flow_mod)
        
        # Re-install table miss
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def install_path(self, path_name):
        self.logger.info("--- Switching to %s path ---", path_name.upper())
        self.current_path = path_name
        path_config = self.primary_path if path_name == 'primary' else self.alternate_path
        
        # Clear existing flows
        for dp_id, dp in self.datapaths.items():
            self.clear_flows(dp)
            
        time.sleep(0.5) # Allow time for deletion to process
        
        # Install new proactive forwarding rules
        for dp_id, dp in self.datapaths.items():
            if dp_id in path_config:
                parser = dp.ofproto_parser
                for in_port, out_port in path_config[dp_id].items():
                    match = parser.OFPMatch(in_port=in_port)
                    actions = [parser.OFPActionOutput(out_port)]
                    self.add_flow(dp, 10, match, actions)
                    
        self.logger.info("--- %s path installed successfully ---", path_name.upper())

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofproto = dp.ofproto
        port = msg.desc
        
        if msg.reason == ofproto.OFPPR_MODIFY:
            is_down = (port.state & ofproto.OFPPS_LINK_DOWN) != 0
            if is_down:
                self.logger.warning("Link DOWN detected! Switch s%s Port %s", dp.id, port.port_no)
                if self.current_path == 'primary':
                    if (dp.id == 1 and port.port_no == 2) or \
                       (dp.id == 2 and (port.port_no == 1 or port.port_no == 2)) or \
                       (dp.id == 4 and port.port_no == 1):
                        self.logger.warning("Primary path compromised! Triggering failover.")
                        self.install_path('alternate')
            else:
                self.logger.info("Link UP detected! Switch s%s Port %s", dp.id, port.port_no)
                if self.current_path == 'alternate':
                    if (dp.id == 1 and port.port_no == 2) or \
                       (dp.id == 2 and (port.port_no == 1 or port.port_no == 2)) or \
                       (dp.id == 4 and port.port_no == 1):
                        self.logger.info("Primary path restored! Reverting back to primary.")
                        self.install_path('primary')
