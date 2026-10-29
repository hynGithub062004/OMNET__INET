# Kiểm chứng K2 ngày 29 tháng 10 năm 2026

- Nguồn K1: commit `4202f68` của `hynGithub062004/OMNET__INET`.
- Runtime: OMNeT++ `6.4.0`, build `260506-2cf25223fe`; INET `4.7.0`; Windows x86_64, release library `libINET.dll`.
- `K2_Final`, seed 0–4: cả 5 lần gọi `finish()` sau thông báo simulation time limit reached tại 100 s. Log đầy đủ trong `K2_all_seeds.log`.
- Mỗi run: đúng 30 sensor, 88 packet gửi/sensor; gateway nhận đủ 2.640 packet; delay statistics có 2.640 mẫu.
- So sánh tham số đã resolve của K1 và K2 theo từng seed: đạt, bao gồm tọa độ 10 sensor cũ, gateway, ứng dụng, MAC, radio và năng lượng. Bỏ qua địa chỉ tự sinh và tham số hiển thị; vẫn kiểm tra địa chỉ đích ứng dụng.
- Kiểm tra toàn bộ 5 vector file: 150 chuỗi năng lượng với 1.609.800 mẫu không tăng và 5 chuỗi delay với 13.200 mẫu không âm. Các giá trị cuối và thống kê trung bình khớp scalar. Chi tiết trong `exports/K2_vector_checks.csv`.
- `opp_scavetool query` với đúng bộ lọc của `K2_Energy_Analysis.anf`: tìm thấy 1 run, 30 vector năng lượng của seed 0.
- `run_k2.ps1 -Configuration K2_Visual -Ui Cmdenv`: chạy thử thành công đến 100 s. Đây là kiểm tra cấu hình, chưa phải kiểm chứng giao diện Qtenv bằng ảnh chụp.
- 11 kiểm tra phân tích đã đạt: đọc baseline thật; từ chối thiếu energy, run thiếu packet, received > sent, delay âm, sai seed, thiếu MAC counter, thay traffic, thay đích ứng dụng; xác nhận cấu hình/NED kế thừa nguyên vẹn; kiểm tra XML Analysis có đủ 10 input K2.
- `git diff --exit-code 4202f68 -- K1`: không có thay đổi trong K1. Hai file NED, metadata project và Makefile K2 giống K1; file ini K2 bắt đầu bằng toàn bộ nội dung ini K1 nguyên vẹn.
- Đã xem lại 3 hình PNG: topology, so sánh KPI và đường năng lượng. Topology dựng từ tham số thực tế; hình năng lượng lấy từ vector seed 0.

Tái tạo bảng: `python analysis/analyze_results.py`. Kiểm tra vector và vẽ hình: `python analysis/analyze_results.py --plots --verify-vectors` (cần matplotlib).

- Sau khi người dùng cung cấp đường dẫn project đang dùng, đã giữ bố trí hai hàng Y=8 và 52 m, chạy lại đủ 5 seed và tính lại toàn bộ bảng/hình. Log chính thức là `K2_all_seeds.log`. Bản tích hợp giữ nguyên file NED sẵn có của người dùng; xác nhận byte-identical NED ở trên chỉ áp dụng bản source K2 trong repository.
- Chạy tích hợp `K2_Final` seed 0 trực tiếp trong project samples/WarehouseWSN đến 100 s thành công; log `K2_local_integration.log`.
