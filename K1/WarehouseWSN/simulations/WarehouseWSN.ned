package warehousewsn.simulations;

import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.WirelessHost;
import inet.physicallayer.wireless.common.medium.RadioMedium;
import inet.visualizer.canvas.integrated.IntegratedCanvasVisualizer;

network WarehouseWSN
{
    parameters:
        int numSensors = default(10);
        @display("bgb=1000,600");

    submodules:
        visualizer: IntegratedCanvasVisualizer {
            @display("p=900,80");
        }

        configurator: Ipv4NetworkConfigurator {
            @display("p=900,160");
        }

        radioMedium: RadioMedium {
            @display("p=900,240");
        }

        sensor[numSensors]: WirelessHost {
            @display("p=150,300;i=device/wifilaptop");
        }

        gateway: WirelessHost {
            @display("p=50,550;i=device/accesspoint");
        }
}
