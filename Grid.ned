
package inet.examples.ospfv2.grid;

import inet.common.misc.ThruputMeteringChannel;
import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.ethernet.EthernetSwitch;
import inet.node.inet.StandardHost;
import inet.node.ospfv2.OspfRouter;


network Grid
{
    parameters:
        @display("p=10,10;b=736,568");
        int height @prompt("Number of rows") = default(4);
        int width @prompt("Number of columns") = default(6);
    types:
        channel C extends ThruputMeteringChannel
        {
            delay = 0.1us;
            datarate = 100Mbps;
            thruputDisplayFormat = "#N";
        }
    submodules:
        N[height*width]: EthernetSwitch {
            parameters:
                @display("p=,,m,$width");
            gates:
                ethg[4];
        }
        R[height*width*2]: OspfRouter {
            parameters:
                @display("p=,,m,$width");
            gates:
                ethg[2];
        }
        //        R3: OspfRouter {
        //            parameters:
        //                @display("p=372,140");
        //            gates:
        //                ethg[2];
        //        }
        //        N6: EthernetSwitch {
        //            parameters:
        //                @display("p=448,139");
        //            gates:
        //                ethg[3];
        //        }
        //        H1: StandardHost {
        //            parameters:
        //                @display("p=594,242;i=device/laptop");
        //            gates:
        //                ethg[1];
        //        }
        //        H2: StandardHost {
        //            parameters:
        //                @display("p=218,71;i=device/laptop");
        //            gates:
        //                ethg[1];
        //        }
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
            N[i*width+j].ethg[0] <--> C <--> R[(i*width+j)*2].ethg[0];
            N[i*width+(j+1)%width].ethg[1] <--> C <--> R[(i*width+j)*2].ethg[1];

            N[i*width+j].ethg[2] <--> C <--> R[(i*width+j)*2 + 1].ethg[0];
            N[((i+1)%height)*width+j].ethg[3] <--> C <--> R[(i*width+j)*2 + 1].ethg[1];
        }
}

