# 🧩 8-Puzzle AI Visualizer

Ứng dụng mô phỏng trực quan bài toán 8-Puzzle viết bằng Python và giao diện Tkinter.

Ứng dụng này minh hoạ nhiều thuật toán tìm kiếm và tối ưu hoá, đồng thời hiển thị thông tin chi tiết về Frontier, Reached/Explored, node hiện tại, cost, Manhattan distance và đường đi tìm được.

---

## ✨ Tính năng chính

- Hỗ trợ nhiều thuật toán: BFS (Optimized / Classic / Generic), DFS, IDS, UCS, Greedy (Manhattan), A*, IDA*, Simple Hill Climbing, Steepest-Ascent Hill Climbing.
- Visual logs: hiển thị node hiện tại, danh sách frontier, tập reached, mini-board cho từng node.
- Bảng điều khiển tương tác: chọn thuật toán, nhập trạng thái đầu và đích, chạy từng bước hoặc tự động, reset.
- Hiển thị thống kê: Manhattan distance, depth, số node đã duyệt và trạng thái tìm kiếm.

---

## 🧠 Ghi chú thuật toán (những điểm đáng chú ý)

- Simple Hill Climbing: cost được tính bằng giá trị ô vừa đổi chỗ với '0' (giá trị nhỏ hơn tốt hơn). Thuật toán dừng khi không tìm được lân cận tốt hơn.
- Steepest-Ascent Hill Climbing: sinh tất cả lân cận, chọn lân cận có cost nhỏ nhất.
- Greedy: dùng Manhattan heuristic để chọn node gần đích nhất.
- A*: dùng f(n) = g(n) + h(n) với h là Manhattan distance.
- IDA*: Iterative Deepening kết hợp heuristic để giảm bộ nhớ so với A*.
- Lưu ý: trong mô phỏng, thứ tự sinh nước đi là: Left, Right, Up, Down (Trái, Phải, Trên, Dưới).

---

## 🖥️ Giao diện & Điều khiển

- Two main boards: `Current State` và `Goal State`.
- Control panel: chọn thuật toán, thiết lập `start`/`goal` (chuỗi 9 ký tự gồm các số 0-8; `0` đại diện ô trống).
- Buttons: `Khởi tạo lại`, `Chạy 1 Bước`, `Chạy Tự Động` / `Tạm Dừng`.
- Simulation log: từng hàng hiển thị Node hiện tại, Frontier (mini-boards), và Reached set.

---

## ✅ Yêu cầu

- Python 3.8+ (đã thử với Python 3.10+)
- Tkinter (thường có sẵn với Python trên Windows/Mac; trên Linux có thể cần cài gói `python3-tk`).

---

## 🚀 Chạy ứng dụng

1. Mở terminal tại thư mục chứa file.

```bash
python 8puzzle.py
```

2. Nhập trạng thái bắt đầu và trạng thái đích dưới dạng chuỗi 9 ký tự (ví dụ `123406758` và `123456780`). `0` là ô trống.

---

## 🔎 Ví dụ nhanh

- Start: `123406758`
- Goal:  `123456780`
- Chọn thuật toán A* hoặc IDA* để tìm đường đi hiệu quả với heuristic Manhattan.

---

## 📂 File chính

- [8puzzle.py](8puzzle.py) — mã nguồn chính chứa cả thuật toán và UI.
- [readme.md](readme.md) — hướng dẫn này.

---

Nếu bạn muốn tôi cập nhật thêm phần giải thích thuật toán, thêm ảnh chụp màn hình, hoặc tạo `requirements.txt`, hãy cho biết.