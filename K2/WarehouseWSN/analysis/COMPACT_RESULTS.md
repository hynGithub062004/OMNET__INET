# Kết quả K2 gọn cho OMNeT++

## Makefile
Giữ file Makefile không có đuôi số: đây là file dùng để build. Sáu file Makefile.<timestamp> và các bản sao cấu hình cũ đã được dọn khỏi project. Chúng không được dùng làm input của Analysis và không gây lag chart.

## Cấu hình chạy
K2_Charts kế thừa K2_Final; chỉ thay tùy chọn ghi kết quả, không thay topology, traffic, radio, MAC hoặc năng lượng. Chọn Cmdenv và runs 0..4. Kết quả đã chạy sẵn nằm trong simulations/results/light.

- Scalar của đủ 30 sensor: packetSent, năng lượng còn lại, packetReceived và tổng byte tại gateway, delay stats. Goodput = byte nhận x 8 / 90 s.
- Vector năng lượng nguyên mẫu của sensor[0], sensor[14], sensor[29]. Không ghi vector công suất radio, hàng đợi hoặc delay từng gói trong cấu hình này.
- Không ghi tham số NED vào kết quả gọn; có thể tra từ INI hoặc kết quả đầy đủ. Các file K2_Final được giữ nguyên.

## Mở biểu đồ
Refresh project bằng F5. Mở analysis/K2_Compact_Analysis.anf, chọn Charts, mở K2_Energy_Compact. Analysis này chỉ đọc file K2_Charts-0.vec và hiển thị ba node đại diện với toàn bộ mẫu năng lượng đã ghi, không phải toàn bộ 30 đường.
Muốn xem đủ 30 đường ở dạng lấy thưa mẫu, dùng K2_Energy_Preview.anf đã có. Không chọn cả thư mục results làm input khi chỉ cần một chart.

## Bảng đủ 30 node và bốn KPI
Các bảng CSV có tại analysis/exports/compact. Tạo lại bằng:
python analysis/summarize_compact.py
Bộ gọn có n=5, seed 0..4. Đã đối chiếu PDR, delay và 30 scalar năng lượng với K2_Final seed 1..4; khớp trong dung sai số học. K2_Final-0.sca hiện thiếu nên không tuyên bố đã đối chiếu seed 0 với file gốc.
Vector mỗi run khoảng 1,4 MB, scalar khoảng 44 KB. Chưa kiểm chứng thao tác mở chart trên GUI của máy; cú pháp và input đã được kiểm tra bằng opp_scavetool.

## Dọn project ngày 31/10/2026
Đã bỏ 6 bản Makefile cũ, 4 bản sao cấu hình và 6 file kết quả Visual khỏi project. Các kết quả chính K2_Final và K2_Charts được giữ nguyên. ZIP khôi phục nằm trên máy tại C:/Users/5501/OneDrive/Documents/ChatGPT/wsn/output/WarehouseWSN_removed_files_20261031.zip, không đưa bản sao thừa này vào Git. Giữ Makefile chính, out và hai executable để build/chạy.
