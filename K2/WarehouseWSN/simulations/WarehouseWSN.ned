package warehousewsn.simulations;

import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.WirelessHost;
import inet.physicallayer.wireless.common.medium.RadioMedium;
import inet.visualizer.canvas.integrated.IntegratedCanvasVisualizer;

network WarehouseWSN
{
    parameters:
        int numSensors = default(30);
        @display("bgb=1000,600");

    submodules:
        visualizer: IntegratedCanvasVisualizer {
            @display("p=899,110");
        }

        configurator: Ipv4NetworkConfigurator {
            @display("p=620,80");
        }

        radioMedium: RadioMedium {
            @display("p=869,397");
        }

        sensor[numSensors]: WirelessHost {
            @display("p=199,240;i=device/wifilaptop");
        }

        gateway: WirelessHost {
            @display("p=259,480;i=device/accesspoint");
        }
}
