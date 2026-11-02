//
// This program is free software: you can redistribute it
// and/or modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will
// be useful, but WITHOUT ANY WARRANTY; without even the implied
// warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
// PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser
// General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
//

package Warehouse;

import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.WirelessHost;
import inet.physicallayer.wireless.common.medium.RadioMedium;
import inet.visualizer.canvas.integrated.IntegratedCanvasVisualizer;

network warehousenetwork
{
    parameters:
        int numSensors = default(30);
        @display("bgb=1000,600");

    submodules:
        visualizer: IntegratedCanvasVisualizer {
            @display("p=850,70");
        }

        configurator: Ipv4NetworkConfigurator {
            @display("p=850,150");
        }

        radioMedium: RadioMedium {
            @display("p=850,230");
        }

        // Gateway được đặt ở GIỮA kho (tọa độ x=500, y=300)
        gateway: WirelessHost {
            @display("p=500,300;i=device/accesspoint");
        }

        // 30 sensor node phân bố xung quanh gateway
        sensor[numSensors]: WirelessHost {
            @display("p=265,273;i=device/wifilaptop");
        }

}