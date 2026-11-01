# WarehouseWSN kịch bản K2

K2 mở rộng cấu hình K1 của TV1 từ 10 lên 30 sensor trong kho hàng. Mỗi sensor gửi UDP trực tiếp về gateway ở góc kho. Project chạy độc lập trên máy của TV2, không cần lấy file từ thư mục K1 khi chạy.

## 1. Tên project và cấu trúc

Giữ nguyên tên project `WarehouseWSN`, package `warehousewsn.simulations`, network `WarehouseWSN`, file `WarehouseWSN.ned` và `omnetpp.ini` giống K1. File hướng dẫn, file Analysis, configuration và kết quả sử dụng tiền tố K2.

| Đường dẫn | Vai trò |
|---|---|
| `K2/WarehouseWSN/` | Thư mục project để import |
| `simulations/WarehouseWSN.ned` | Cấu trúc mạng, mặc định 30 sensor |
| `simulations/package.ned` | Khai báo package giống K1 |
| `simulations/omnetpp.ini` | Các bước kiểm tra và cấu hình K2 chính thức |
| `simulations/results/` | Nơi sinh kết quả khi bạn chạy |
| `analysis/K2_Energy_Analysis.anf` | Biểu đồ năng lượng của 30 sensor, seed 0 |
| `analysis/K2_Sensor_Coordinates.csv` | Tọa độ 30 sensor và gateway |
| `analysis/summarize_results.py` | Tổng hợp số liệu thật từ các file `.sca` |
| `images/K2_Topology.png` và `.svg` | Sơ đồ thiết kế tọa độ, chưa phải ảnh chạy mô phỏng |
| `run_k2.sh` | Cách chạy bổ sung bằng terminal OMNeT++ |

Các file thiết lập project của Eclipse/OMNeT++ được kế thừa từ K1. Makefile được IDE tạo lại trên máy bạn khi Build Project; không cần dùng Makefile có đường dẫn INET từ máy TV1.

Nguồn cấu hình K1: https://github.com/hynGithub062004/OMNET__INET/tree/main/K1/WarehouseWSN

Commit đối chiếu: `5fb146bd91d87a7eae48311a3f024531dfe9cce4`.

## 2. Tham số đối chứng với K1

| Tham số | K1 | K2 |
|---|---|---|
| Số sensor | 10 | 30 |
| Kích thước kho | 100 × 60 m | Giống K1 |
| Gateway | (5, 5, 0) m | Giữ nguyên |
| Tọa độ sensor 0–9 | Theo K1 | Giữ nguyên từng tọa độ |
| Tọa độ sensor 10–29 | Không có | Bổ sung trên cùng lưới X |
| Mobility | StationaryMobility | Giống K1 |
| App phát / nhận | UdpBasicApp / UdpSink | Giống K1 |
| Đích / cổng | gateway / 5000 | Giống K1 |
| Payload / chu kỳ gửi | 64 B / 1 s | Giống K1 |
| Start / stop, cấu hình Final | uniform(11s, 12s) / 99s | Giống K1 |
| MAC / ACK | CsmaCaMac / true | Giống K1 |
| ACK timeout / MAC header | 300 us / 23 B | Giống K1 |
| Queue / dung lượng | DropTailQueue / 50 packet | Giống K1 |
| Radio / analog model | GenericRadio / UnitDisk | Giống K1 |
| Bitrate | 1 Mbps | Giống K1 |
| Communication / interference range | 100 m / 120 m | Giống K1 |
| Bỏ qua interference | false | Giống K1 |
| Background noise | -110 dBm | Giống K1 |
| Energy storage | SimpleEpEnergyStorage, 100 J ban đầu | Giống K1 |
| Radio energy consumer | SensorStateBasedEpEnergyConsumer | Giống K1, giữ nguyên mặc định của INET 4.7.0 |
| Simulation / warm-up | 100 s / 10 s | Giống K1 |
| Replication / seed | 5 / 0–4 | Giống K1 |

K2 bổ sung ghi tổng byte nhận ở ứng dụng gateway để tính throughput. Thay đổi ghi kết quả này không thay đổi traffic hay giao thức.

Phạm vi mô hình năng lượng đang kế thừa K1 chủ yếu là radio; chưa bổ sung tải điện riêng của cảm biến vật lý hoặc CPU. Packet 64 B đại diện dữ liệu cảm biến, không phải thuật toán đo nhiệt độ/độ ẩm thật.

## 3. Import trên máy riêng

### 3.1. Chuẩn bị

1. Dùng OMNeT++ tương thích INET 4.7.0. File Analysis K1 được tạo bằng OMNeT++ 6.4; ưu tiên cùng bộ phiên bản với TV1.
2. Giải nén ZIP vào đường dẫn ngắn, ví dụ `C:/WSN/`. Sau giải nén, project nằm tại `C:/WSN/K2/WarehouseWSN/`.
3. Nếu chưa có INET trong workspace: **File > Import > General > Existing Projects into Workspace**, chọn thư mục INET 4.7.0. Import và Build INET trước.
4. Nếu workspace đã có project K1 tên `WarehouseWSN`, dùng **File > Switch Workspace > Other...** để tạo workspace riêng cho K2, rồi import INET và K2 vào đó. Không import đồng thời hai bản `WarehouseWSN` cùng tên trong một workspace.

### 3.2. Import K2

1. Chọn **File > Import > General > Existing Projects into Workspace**.
2. Chọn **Select root directory**, trỏ đến `C:/WSN/K2/WarehouseWSN/`.
3. Project tìm được phải có tên **WarehouseWSN**.
4. Giữ project tại thư mục vừa giải nén để đường dẫn bên ngoài vẫn theo `K2/WarehouseWSN`. Nếu chọn **Copy projects into workspace**, làm các thao tác tiếp theo trên bản đã được copy trong workspace.
5. Nhấn **Finish**.
6. Chuột phải `WarehouseWSN` > **Properties > Project References**, tích project INET của máy bạn. Tên tham chiếu kế thừa là `inet-4.7.0`; nếu máy bạn đặt tên khác, chọn lại đúng project INET 4.7.0.
7. Trong **Properties > OMNeT++ > NED Source Folders**, kiểm tra `simulations` là thư mục NED source.
8. Chuột phải project > **Build Project** để IDE tạo Makefile phù hợp máy bạn. Nếu IDE yêu cầu tạo lại Makefile, chấp nhận. INET và project nên dùng cùng chế độ release hoặc debug.

### 3.3. Nếu muốn tự tạo project thay vì import

1. Tạo **OMNeT++ Project**, đặt tên chính xác `WarehouseWSN`. Trong phần vị trí project, chọn thư mục `K2/WarehouseWSN` trên máy bạn.
2. Tham chiếu tới INET 4.7.0.
3. Tạo các thư mục `simulations`, `simulations/results`, `analysis`, `images`.
4. Copy ba file trong `simulations` của gói này vào đúng thư mục tương ứng.
5. Copy các file `analysis`, `images` và `README_K2.md` nếu cần.
6. Đặt `simulations` làm NED source folder rồi Build Project.

Không cần viết thêm C++ cho K2.

## 4. Chạy thử để kiểm tra topology

1. Mở `simulations/omnetpp.ini`.
2. Chọn **Run As > OMNeT++ Simulation** hoặc mở **Run > Run Configurations > OMNeT++ Simulation** và tạo cấu hình chạy.
3. Đặt các mục sau:

| Mục | Giá trị |
|---|---|
| Project | WarehouseWSN |
| Executable | opp_run, hoặc chương trình project được IDE tạo |
| Working directory | `/WarehouseWSN/simulations` |
| Ini file | `omnetpp.ini` |
| Configuration | `K2_VisualCheck` |
| Run number | 0 |
| User interface | Qtenv |
| NED path | simulations của project và src của INET |
| Additional shared library, khi dùng opp_run | Thư viện INET ở `inet-4.7.0/src/INET`, hoặc `INET_dbg` nếu chạy debug |
| Image path | Thư mục `images` của INET |

IDE thường tự lấy NED path và thư viện từ project reference. Kiểm tra phần tham số được IDE tạo nếu không tìm thấy module INET. Không trộn `opp_run` release với thư viện `INET_dbg`.

4. Trong Qtenv, chạy qua mốc **12 giây**. Cấu hình Final bắt đầu gửi sau warm-up, nên trước giây 11 chưa có traffic là bình thường.
5. Xác nhận đúng **30 sensor + 1 gateway**. Các module visualizer, configurator và radioMedium không phải sensor.
6. Gateway phải ở `(5, 5)` m. Tọa độ lấy từ `mobility`, không lấy tọa độ hiển thị ban đầu trong `@display` làm tọa độ vật lý.
7. Kiểm tra số nhận của `gateway.app[0]` tăng và năng lượng sensor giảm.
8. Chụp topology, packet flow và thông tin gateway làm minh chứng. Lưu ảnh vào `images`.

`K2_VisualCheck` chỉ bật lại hiển thị, dùng cùng traffic và tham số với K2_Final. File kết quả mang tên riêng để không ghi đè kết quả chính thức.

## 5. Chạy đủ năm seed chính thức

1. Tạo hoặc sửa Run Configuration, chọn **Configuration = K2_Final**.
2. Chọn **User interface = Cmdenv**.
3. Chạy cả năm run **0, 1, 2, 3, 4**. Trong mục chọn run, dùng `0..4` hoặc chọn tất cả 5 run mà IDE liệt kê. Chỉ chạy run 0 sẽ chưa đủ thí nghiệm.
4. Chờ mỗi run kết thúc ở **100 giây mô phỏng**. Thời gian này không phải 100 giây đồng hồ.
5. Trong `simulations/results`, phải có các file `.sca` với tiền tố `K2_Final-0` đến `K2_Final-4`, cùng các file `.vec` tương ứng. IDE có thể tạo thêm `.vci`.

Quy tắc tên: `K2_Final-${repetition}.sca` và `K2_Final-${repetition}.vec`, giống cách đặt tên của K1.

Với traffic hiện tại, mỗi sensor dự kiến gửi **88 gói**, tổng **2.640 gói/run** nếu ứng dụng hoạt động đủ thời gian. Đây là số kiểm tra dự kiến, chưa phải kết quả đã chạy. Số nhận và các KPI phụ thuộc mô phỏng thực tế; không đặt sẵn PDR bằng 100%.

## 6. Chạy bằng terminal OMNeT++ khi cần

Đây là cách bổ sung, không bắt buộc nếu bạn đã chạy được bằng IDE. Trên Windows, mở `mingwenv.cmd` của OMNeT++, không chạy các lệnh bash bên dưới trực tiếp trong PowerShell.

Sửa ví dụ dưới đây theo đường dẫn INET và project trên máy bạn:

```bash
export INET_ROOT=/c/omnetpp/samples/inet-4.7.0
cd /c/WSN/K2/WarehouseWSN
bash run_k2.sh K2_VisualCheck Qtenv
```

Chạy chính thức, script tự gọi lần lượt năm run:

```bash
bash run_k2.sh K2_Final Cmdenv
```

Nếu bạn chỉ build INET chế độ debug:

```bash
BUILD_MODE=debug bash run_k2.sh K2_Final Cmdenv
```

Script nạp thư viện INET vào opp_run và không phụ thuộc một executable C++ riêng của WarehouseWSN. INET phải được build trước. Mỗi run cũng lưu log console tại `simulations/results/K2_Final-0.log` đến `K2_Final-4.log` để gửi phân tích khi cần.

## 7. Tổng hợp kết quả thật

Nếu máy có Python 3.9 trở lên, mở PowerShell hoặc Command Prompt tại thư mục `WarehouseWSN` và chạy:

```powershell
py analysis/summarize_results.py
```

Nếu máy nhận lệnh `python` thay vì `py`, dùng:

```powershell
python analysis/summarize_results.py
```

Không cần cài pandas hay thư viện Python ngoài. Công cụ kiểm tra đủ năm seed, đúng số sensor, số gói gửi/nhận, số mẫu delay và số liệu năng lượng trước khi xuất:

- `analysis/K2_Final_KPI_PerRun.csv`: kết quả từng seed.
- `analysis/K2_Final_KPI_Summary.csv`: trung bình, độ lệch chuẩn mẫu, min và max qua năm seed.
- `analysis/K2_Final_Energy_PerSensor.csv`: năng lượng và số gói gửi của từng sensor trong từng seed.

PDR = số gói nhận ở `gateway.app[0]` / tổng số gói gửi ở `sensor[*].app[0]` × 100%.

Delay lấy từ `gateway.app[0].endToEndDelay:stats`, đổi giây sang mili giây; chỉ tính các gói nhận thành công.

Energy Remaining lấy `residualEnergyCapacity:last` của từng sensor. Bảng tổng hợp có trung bình mỗi sensor và sensor còn ít năng lượng nhất. Không dùng tổng năng lượng còn lại của 30 sensor để so trực tiếp với tổng của 10 sensor.

Throughput ứng dụng = tổng byte payload nhận × 8 / **90 giây**, với cửa sổ đo cố định sau warm-up từ giây 10 đến 100. Chỉ số này không tính overhead UDP/IP/MAC, và không đồng nhất với vector throughput tức thời. K1 cũng phải dùng cùng cửa sổ 90 giây khi đối chiếu.

Độ lệch chuẩn trong `KPI_Summary` là độ lệch chuẩn giữa các lần chạy. Nó khác độ lệch chuẩn delay giữa các packet trong một run. Nếu không nhận gói, delay là `nan`, không tự thay bằng 0.

Nếu không có Python, mở `.sca` bằng Analysis Tool của OMNeT++ và lấy các statistic trên để lập bảng thủ công.

## 8. Xem biểu đồ năng lượng giống K1

1. Chạy xong K2_Final để có `.sca` và `.vec`.
2. Mở `analysis/K2_Energy_Analysis.anf`.
3. Tab Inputs dùng đường dẫn workspace `/WarehouseWSN/simulations/results/K2_Final-*.sca` và `.vec`, giống quy ước K1. Nếu IDE không tự tìm thấy, dùng Add/Browse để chọn file ở `WarehouseWSN/simulations/results`, sau đó refresh.
4. Mở chart `K2_Energy_Remaining`. Bộ lọc chọn riêng seed 0 để hiển thị 30 đường thay vì trộn 150 đường của năm seed.
5. Các đường có thể chồng lên nhau nếu mức tiêu thụ gần giống nhau. Khi cần, lọc riêng một vài sensor để nhìn rõ.

File `.anf` cần Python/scave đi kèm OMNeT++ IDE để vẽ. Công cụ tổng hợp CSV ở mục 7 chỉ dùng Python tiêu chuẩn.

## 9. Đối chiếu K1 với K2

So sánh theo cùng seed 0–4 và cùng đơn vị đo. Các chỉ số chính là PDR, delay trung bình, năng lượng còn lại mỗi sensor; throughput là chỉ số hỗ trợ thứ tư.

K2 có tải payload trong giai đoạn gửi khoảng **15.360 bit/s**, gấp ba K1 **5.120 bit/s**. Các giá trị này chưa tính overhead, ACK, backoff và truyền lại; không được dùng trực tiếp làm mức sử dụng kênh thực tế.

Tăng số sensor không bắt buộc làm PDR giảm rõ hoặc delay vượt ngưỡng. Nếu kết quả gần K1, giải thích theo tải nhỏ, tầm phủ và cơ chế MAC; không đổi tham số chỉ để tạo ra kết quả xấu hơn.

UnitDisk đang mô hình hóa tầm truyền, không mô hình hóa chi tiết suy hao theo khoảng cách. Không kết luận gateway ở giữa chắc chắn làm công suất phát hoặc năng lượng giảm. Nếu nhóm sau này đổi radio/path loss, phải cập nhật và chạy lại cả K1, K2, K3 theo cùng mô hình.

## 10. Bàn giao cho thành viên làm K3

- Bàn giao NED, INI, bảng tọa độ và cấu hình năng lượng của K2.
- K3 giữ nguyên tất cả tọa độ `sensor[0]` đến `sensor[29]`.
- Với kho 100 × 60 m, tâm hình học là `(50, 30)` m; K3 chỉ đổi tọa độ gateway sang vị trí đã thống nhất.
- Giữ nguyên traffic, MAC, ACK, radio, năng lượng, thời gian và seed.
- Không đồng thời thay đổi mô hình vô tuyến khi so sánh K2–K3.

## 11. File cần giữ sau khi chạy

- Project nguồn và README này.
- Năm file `.sca`, năm file `.vec` và `.vci` nếu có.
- Ba bảng CSV sau khi tổng hợp.
- Ảnh topology, packet flow và biểu đồ cần dùng trong báo cáo.
- Ghi lại phiên bản OMNeT++, INET và chế độ build.

File `.gitignore` kế thừa K1 bỏ qua `.vec` và `.vci` khi commit. Các file này vẫn được tạo và lưu trên máy bạn; giữ bản sao để mở lại biểu đồ. Nếu cần nộp kết quả đầy đủ, đóng ZIP riêng, không chỉ gửi các file Git đang theo dõi.

## 12. Xử lý lỗi thường gặp

| Hiện tượng | Kiểm tra |
|---|---|
| Không import được vì tên WarehouseWSN đã tồn tại | Dùng workspace riêng cho K2 |
| Không tìm thấy WirelessHost hoặc RadioMedium | INET 4.7.0 đã import, build, được tham chiếu và có src trong NED path |
| Không tìm thấy network warehousewsn.simulations.WarehouseWSN | `simulations` là NED source; ba file NED/INI có đúng vị trí |
| Không tìm thấy lớp C++ của module INET | Thư viện INET chưa được nạp vào opp_run hoặc build mode không khớp |
| Makefile trỏ sai đường dẫn INET | Sửa Project References, để IDE tạo lại Makefile trên máy hiện tại |
| Trước giây 11 chưa thấy gói gửi | Đúng thiết kế startTime sau warm-up; chạy qua giây 12 |
| Chỉ có một file K2_Final-0.sca | Chưa chạy đủ run 0–4 |
| Analysis không có dữ liệu | Chạy xong, kiểm tra `.vec`, sửa Inputs nếu cần và refresh |
| Script báo thiếu sensor hoặc seed | Kiểm tra đúng K2_Final, chạy đủ 30 sensor và đủ năm run, không trộn file từ project khác |

## 13. Trạng thái kiểm tra và nguồn kỹ thuật

Đã kiểm tra tĩnh cấu hình K2 so với K1 và kiểm thử công cụ tổng hợp trên năm file `.sca` thật của K1. Môi trường tạo gói không có OMNeT++; chưa chạy mô phỏng K2. Thư mục results ban đầu để trống, không kèm số liệu K2 giả lập.

- OMNeT++ 6.4 Launching and Debugging: https://docs.omnetpp.org/6.4/userguide/launcher
- OMNeT++ 6.4 Analyzing the Results: https://docs.omnetpp.org/6.4/userguide/result-analysis
- INET 4.7 UdpSink, các statistic nhận gói và delay: https://inet.omnetpp.org/inet/docs/4.7/api/types/inet.applications.udpapp.UdpSink.html
