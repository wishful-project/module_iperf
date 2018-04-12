import logging
import iperf3
import gevent
import _thread
import wishful_upis as upis
import wishful_framework as wishful_module

__author__ = "Piotr Gawlowicz, Mikolaj Chwalisz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, chwalisz}@tkn.tu-berlin.de"

'''
    Packet flows are generated using IPerf tool.
'''


@wishful_module.build_module
class IperfModule(wishful_module.AgentModule):
    def __init__(self):
        super(IperfModule, self).__init__()
        self.log = logging.getLogger('IperfModule.main')
        self.packetflow_sink_active = False
        self.packetflow_client_active = False

    def worker(self, port):
        """thread worker function"""
        self.log.debug("Thread is started")
        server = iperf3.Server()
        server.port = port
        server.verbose = False
        #while self.packetflow_sink_active:
        server.run()

    @wishful_module.bind_function(upis.net.create_packetflow_sink)
    def start_server(self, port):
        self.log.debug("Starts iperf server on port {}".format(port))
        self.packetflow_sink_active = True
        _thread.start_new_thread(self.worker, (port,))
        self.log.debug("Server thread is started")
        return "Server_started"

    @wishful_module.bind_function(upis.net.destroy_packetflow_sink)
    def stop_server(self):
        self.log.debug("Stops iperf server.")
        self.packetflow_sink_active = False
        return "Server stops automatically after one client test"

    def client_worker(self, dest_ip, port):
        client = iperf3.Client()
        client.duration = 10
        client.server_hostname = dest_ip
        client.port = port
        client.protocol = 'tcp'
        self.log.debug('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
        # while self.packetflow_client_active:
        result = client.run()
        cmdDesc = wishful_module.CmdDesc()
        cmdDesc.type = "net"
        cmdDesc.func_name = "start_packetflow"
        #cmdDesc.interface = self.interface
        cmdDesc.serialization_type = wishful_module.CmdDesc.PICKLE
        cmdDesc.repeat_number = 0
        output = ""
        if result.error:
            self.log.debug('Connection failed {0}:{1}'.format(client.server_hostname, client.port))
            output = result.error
        else:
            output = ""
            output += "=====Test SUCCESS: "
            #output += "\n MBit\s sent: "
            output += str(result.sent_Mbps)
            #output += "\n MBit\s recv: "
            output += " , "
            output += str(result.received_Mbps)
            output += "=====\n"
                # output += "\n jitter (ms): "
                # output += str(result.jitter_ms)
                # output += "\n avg cpu load: "
                # output += str(result.local_cpu_total)
                # output += "\nMegabits per second  (Mbps): "
                # output += str(result.Mbps)
        self.agent.send_upstream(["controller", cmdDesc, output])

    @wishful_module.bind_function(upis.net.start_packetflow)
    def start_packetflow(self, dest_ip, port):
        self.log.debug("Start iperf client.")
        self.packetflow_client_active = True
        _thread.start_new_thread(self.client_worker, (dest_ip, port))
        self.log.debug("Started iperf client.")
        return "Client_started"

    @wishful_module.bind_function(upis.net.stop_packetflow)
    def stop_packetflow(self):
        self.log.debug("Stops iperf client.")
        self.packetflow_client_active = False
        return "Client stopped"
