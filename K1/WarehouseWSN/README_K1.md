# WarehouseWSN - Kịch bản K1

## 1. Mô tả

K1 là kịch bản baseline của mô hình mạng cảm biến không dây giám sát kho hàng.

Mô hình gồm:

- 10 sensor node đứng yên
- 1 gateway đặt tại góc kho
- Truyền UDP single-hop từ sensor đến gateway
- CSMA/CA và MAC ACK
- Mô hình tiêu thụ năng lượng cho sensor node
- 5 replication độc lập

## 2. Môi trường mô phỏng

- OMNeT++: phiên bản sử dụng trong project
- INET Framework: 4.7.0
- Project: WarehouseWSN
- Network: warehousewsn.simulations.WarehouseWSN
- Operating system: Windows

## 3. Cấu hình chính thức

- Configuration: K1_Final
- Simulation time: 100 s
- Warm-up period: 10 s
- Number of repetitions: 5
- Seed set: 0-4 theo repetition
- User interface: Cmdenv

## 4. Topology

- Warehouse area: 100 m x 60 m
- Number of sensor nodes: 10
- Number of gateways: 1
- Gateway position: (5 m, 5 m, 0 m)
- Mobility model: StationaryMobility

Các sensor được đặt tại:

| Node | X (m) | Y (m) |
|---|---:|---:|
| sensor[0] | 20 | 15 |
| sensor[1] | 35 | 15 |
| sensor[2] | 50 | 15 |
| sensor[3] | 65 | 15 |
| sensor[4] | 80 | 15 |
| sensor[5] | 20 | 45 |
| sensor[6] | 35 | 45 |
| sensor[7] | 50 | 45 |
| sensor[8] | 65 | 45 |
| sensor[9] | 80 | 45 |

## 5. Traffic

- Sensor application: UdpBasicApp
- Gateway application: UdpSink
- Destination: gateway
- Destination port: 5000
- Message length: 64 B
- Send interval: 1 s
- Start time: uniform(11 s, 12 s)
- Stop time: 99 s
- Packet name: SensorData

Traffic bắt đầu sau warm-up để Packet Sent và Packet Received được đo trên cùng một khoảng thời gian.

## 6. MAC và radio

- Wireless interface: WirelessInterface
- Radio: GenericRadio
- Signal analog representation: UnitDisk
- MAC: CsmaCaMac
- MAC ACK: enabled
- ACK timeout: 300 us
- MAC header length: 23 B
- Queue: DropTailQueue
- Queue capacity: 50 packets
- Bitrate: 1 Mbps
- Communication range: 100 m
- Interference range: 120 m
- Background noise: -110 dBm

## 7. Mô hình năng lượng

- Energy storage: SimpleEpEnergyStorage
- Nominal capacity: 100 J
- Initial capacity: 100 J
- Energy consumer: SensorStateBasedEpEnergyConsumer

Các statistic chính:

- residualEnergyCapacity
- powerConsumption

## 8. Kết quả baseline

| KPI | Kết quả |
|---|---:|
| Packet Sent | 880 packet/run |
| Packet Received | 880 packet/run |
| Packet Loss | 0 packet/run |
| PDR | 100 ± 0% |
| End-to-End Delay | 1.43933 ± 0.04713 ms |
| Energy Remaining | xấp xỉ 99.9405 J/sensor |

Delay nhỏ hơn ngưỡng yêu cầu 120 ms.

## 9. Cách import project

1. Cài đặt OMNeT++.
2. Import INET Framework 4.7.0.
3. Import project WarehouseWSN vào OMNeT++ IDE.
4. Mở Project Properties.
5. Thêm project reference đến INET Framework 4.7.0.
6. Build project.

Không cần sao chép project INET vào repository này.

## 10. Cách chạy K1

Thiết lập Run Configuration:

- Executable: opp_run
- Working directory: /WarehouseWSN/simulations
- Ini file: omnetpp.ini
- Configuration: K1_Final
- User interface: Cmdenv

K1_Final sẽ chạy 5 replication từ #0 đến #4.

## 11. Xem kết quả

Mở file Analysis trong thư mục: