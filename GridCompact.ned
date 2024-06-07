
package inet.examples.ospfv2.grid;

import inet.common.misc.ThruputMeteringChannel;
import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.ethernet.EthernetSwitch;
import inet.node.inet.StandardHost;
import inet.node.ospfv2.OspfRouter;


network GridCompact
{
    parameters:
        @display("p=10,10;b=736,568");
        int height @prompt("Number of rows") = default(20);
        int width @prompt("Number of columns") = default(20);
    types:
        channel C extends ThruputMeteringChannel
        {
            delay = 0.1us;
            datarate = 100Mbps;
            thruputDisplayFormat = "#N";
        }
    submodules:
        R[height*width]: OspfRouter {
            parameters:
                @display("p=,,m,$width");
            gates:
                ethg[4];
        }
        configurator: Ipv4NetworkConfigurator {
            parameters:
				assignAddresses = default(true);
                config = default(xml("<config><interface hosts='**' address='10.x.x.x' netmask='255.x.x.x'/></config>"));
                addStaticRoutes = false;
                addDefaultRoutes = false;
                @display("p=100,100;is=s");
        }
    connections:
        for i=0..height-1, for j=0..width-1 {
            R[i*width+j].ethg[0] <--> C <--> R[i*width+(j+1)%width].ethg[2];
            R[i*width+j].ethg[1] <--> C <--> R[((i+1)%height)*width+j].ethg[3];
        }
}

