# Kết quả K1 và K2 từ scalar thực tế

K1 lấy từ 5 file upstream; K2 lấy từ 5 lần chạy K2_Final. Đơn vị thống kê là một seed, n = 5.
Sai số ± dưới đây là độ lệch chuẩn mẫu giữa các seed, không phải khoảng tin cậy.

| Kịch bản | Seed | Gửi | Nhận | PDR (%) | Delay trung bình (ms) | Energy trung bình (J/sensor) | Retry |
|---|---:|---:|---:|---:|---:|---:|---:|
| K1 | 0 | 880 | 880 | 100.000000 | 1.410022 | 99.940533771 | 0 |
| K1 | 1 | 880 | 880 | 100.000000 | 1.469600 | 99.940533062 | 0 |
| K1 | 2 | 880 | 880 | 100.000000 | 1.507821 | 99.940533319 | 0 |
| K1 | 3 | 880 | 880 | 100.000000 | 1.402954 | 99.940533595 | 0 |
| K1 | 4 | 880 | 880 | 100.000000 | 1.406249 | 99.940533195 | 0 |
| K2 | 0 | 2640 | 2640 | 100.000000 | 1.431717 | 99.827200576 | 0 |
| K2 | 1 | 2640 | 2640 | 100.000000 | 1.470728 | 99.827200399 | 0 |
| K2 | 2 | 2640 | 2640 | 100.000000 | 1.521717 | 99.827200653 | 0 |
| K2 | 3 | 2640 | 2640 | 100.000000 | 1.402484 | 99.827200911 | 0 |
| K2 | 4 | 2640 | 2640 | 100.000000 | 1.458882 | 99.827200478 | 0 |

| Chỉ số | K1 mean ± SD | K2 mean ± SD |
|---|---:|---:|
| sent_packets | 880 ± 0 | 2640 ± 0 |
| received_packets | 880 ± 0 | 2640 ± 0 |
| lost_packets | 0 ± 0 | 0 ± 0 |
| pdr_pct | 100 ± 0 | 100 ± 0 |
| delay_mean_ms | 1.43932902 ± 0.047127 | 1.45710586 ± 0.0446974 |
| delay_min_ms | 1.0980692 ± 2.02802e-05 | 1.09805102 ± 0 |
| delay_max_ms | 2.12429363 ± 0.585666 | 2.70776441 ± 0.573755 |
| energy_mean_j | 99.9405334 ± 2.90393e-07 | 99.8272006 ± 1.97128e-07 |
| energy_min_j | 99.9405334 ± 2.90393e-07 | 99.8272006 ± 1.97128e-07 |
| energy_max_j | 99.9405334 ± 2.90392e-07 | 99.8272006 ± 1.97128e-07 |
| energy_common10_mean_j | 99.9405334 ± 2.90393e-07 | 99.8272006 ± 1.97128e-07 |
| energy_consumed_mean_j | 0.0594666114 ± 2.90393e-07 | 0.172799397 ± 1.97128e-07 |
| energy_consumed_total_j | 0.594666114 ± 2.90393e-06 | 5.1839819 ± 5.91385e-06 |
| payload_goodput_bps | 5006.22222 ± 0 | 15018.6667 ± 0 |
| mac_retries | 0 ± 0 | 0 ± 0 |
| mac_given_up | 0 ± 0 | 0 ± 0 |
| overheard_data_frames_mean_per_sensor | 792 ± 0 | 2552 ± 0 |

Energy là residualEnergyCapacity:last như K1, tức mẫu năng lượng được ghi cuối cùng; không tự sửa hoặc ngoại suy về đúng t = 100 s. Tiêu thụ được suy ra từ 100 J ban đầu.
Goodput payload = Received × 64 × 8 / 90 s, trên cửa sổ đo [10, 100] s. Không gọi đây là throughput tầng PHY. Packet loss không được quy đổi thành collision.
So sánh năng lượng chính dùng J/sensor; tổng tiêu thụ mạng chỉ là dữ liệu bổ sung. energy_common10_mean_j cho phép kiểm tra riêng 10 sensor được giữ nguyên.
Các tham số đã resolve của sensor cũ và gateway đã được đối chiếu tự động giữa K1 và K2 cho từng seed, bỏ qua địa chỉ tự sinh và tham số hiển thị.
