import logging
import iperf3
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


    @wishful_module.bind_function(upis.net.create_packetflow_sink)
    def start_server(self, port):
        self.log.debug("Starts iperf server on port {}".format(port))
        
        server = iperf3.Server()
        server.port = port
        server.verbose = False
        server.run()
        
        return "Server_started"

    @wishful_module.bind_function(upis.net.destroy_packetflow_sink)
    def stop_server(self):
        self.log.debug("Stops iperf server.")

        return "Server stops automatically after one client test"


    @wishful_module.bind_function(upis.net.start_packetflow)
    def start_packetflow(self, dest_ip, port):
        self.log.debug("Start iperf client.")
        client = iperf3.Client()
        client.duration = 10
        client.server_hostname = dest_ip
        client.port = port
        client.protocol = 'tcp'
        self.log.debug('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
        result = client.run()

        if result.error:
            return result.error
        else:
            output = ""
            output+="Test completed: \n started at: "
            output+= str(result.time)
            output+="\n bytes transmitted: "
            output+= str(result.bytes)
            output+="\n jitter (ms): "
            output+= str(result.jitter_ms)
            output+="\n avg cpu load: "
            output+= str(result.local_cpu_total)
            output+="\nMegabits per second  (Mbps): "
            output+= str(result.Mbps)
            return output

    @wishful_module.bind_function(upis.net.stop_packetflow)
    def stop_packetflow(self):
        self.log.debug("Stops iperf client.")

        return "Client stopped"

