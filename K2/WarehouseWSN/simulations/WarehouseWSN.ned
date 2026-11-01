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
            @display("p=747,74");
        }

        configurator: Ipv4NetworkConfigurator {
            @display("p=899,77");
        }

        radioMedium: RadioMedium {
            @display("p=899,328");
        }

        sensor[numSensors]: WirelessHost {
            @display("p=265,273;i=device/wifilaptop");
        }

        gateway: WirelessHost {
            @display("p=77,540;i=device/accesspoint");
        }
}
