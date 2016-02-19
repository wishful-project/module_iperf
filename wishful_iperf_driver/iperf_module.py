import logging
import wishful_upis as upis
import wishful_agent as wishful_module

__author__ = "Piotr Gawlowicz, Mikolaj Chwalisz"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz, chwalisz}@tkn.tu-berlin.de"


@wishful_module.build_module
class IperfModule(wishful_module.AgentUpiModule):
    def __init__(self, agentPort=None):
        super(IperfModule, self).__init__(agentPort)
        self.log = logging.getLogger('IperfModule.main')

    @wishful_module.bind_function(upis.net.start_iperf_server)
    def start_server(self, port):
        self.log.debug("Starts iperf server on port {}".format(port))

        return "Server_started"
