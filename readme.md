# 🧩 8-Puzzle AI Visualizer

Ứng dụng mô phỏng trực quan bài toán 8-Puzzle viết bằng Python và giao diện Tkinter.

Ứng dụng này minh hoạ nhiều thuật toán tìm kiếm và tối ưu hoá, đồng thời hiển thị thông tin chi tiết về Frontiers, Reached/Explored, node hiện tại, độ sâu, chi phí và đường đi tìm được.

---

## ✨ Tính năng chính

- Hỗ trợ nhiều thuật toán tìm kiếm:
  - `BFS Tối ưu` (Early Goal + Reached sớm)
  - `BFS Cổ điển` (Early Goal + Explored muộn)
  - `BFS Generic` (Late Goal + Reached muộn)
  - `DFS` (LIFO stack)
  - `IDS` (Iterative Deepening Search)
  - `UCS` (Uniform Cost Search)
  - `Greedy Search`
  - `A*` (A Star)
  - `IDA*` (Iterative Deepening A*)
  - `Leo núi đơn giản` (Simple Hill Climbing)
  - `Leo núi dốc nhất` (Steepest-Ascent Hill Climbing)
  - `Leo núi ngẫu nhiên` (Stochastic Hill Climbing)
  - `Leo núi khởi động lại ngẫu nhiên` (Random Restart Hill Climbing)
  - `Local Beam Search`
- Có thể chọn loại heuristic / cost (cho các thuật toán dựa trên chi phí):
  - `Khoảng cách Manhattan`
  - `Số ô sai vị trí`
  - `Giá trị ô swap`
- Tương tác bằng UI: chọn thuật toán, chọn heuristic, nhập trạng thái bắt đầu và đích, điều chỉnh số lần khởi động lại và tham số K của Beam Search.
- Chạy từng bước hoặc chạy tự động và tạm dừng khi cần.
- Hiển thị log trực quan với:
  - `Current Node` / node hiện tại
  - `Frontier` / các node sắp được duyệt
  - `Reached` / các trạng thái đã thăm
  - mini-board cho từng node và trạng thái
- Hiển thị thống kê: heuristic/cost ban đầu, độ sâu hiện tại, số bước đã duyệt và trạng thái tìm kiếm.

---

## 🧠 Ghi chú thuật toán

- `UCS` và `A*` sử dụng chi phí thực (`cost`) khi bạn chọn `Số ô sai vị trí` hoặc `Giá trị ô swap`.
- `Greedy Search` chọn node dựa trên heuristic nhỏ nhất.
- `A*` dùng `f(n) = g(n) + h(n)`.
- `IDA*` thực hiện iterative deepening với ngưỡng `f = g + h`, giúp giảm bộ nhớ so với A*.
- `Simple Hill Climbing` chỉ chọn lân cận đầu tiên tốt hơn và dừng khi không tìm được cải thiện.
- `Steepest-Ascent Hill Climbing` tìm tất cả lân cận rồi chọn lân cận có giá trị tốt nhất.
- `Stochastic Hill Climbing` chọn ngẫu nhiên trong số các lân cận tốt hơn.
- `Random Restart Hill Climbing` thử lại nhiều lần khi leo núi gặp cực đại cục bộ.
- `Local Beam Search` giữ `K` node tốt nhất hiện tại và mở rộng tất cả lân cận của chúng.
- Thứ tự sinh nước đi trong mô phỏng là: `Left`, `Right`, `Up`, `Down` (Trái, Phải, Trên, Dưới).

---

## 🖥️ Giao diện & điều khiển

- Hai bảng chính: `Current State` và `Goal State`.
- Bảng điều khiển cho phép:
  - chọn thuật toán tìm kiếm
  - chọn loại cost / heuristic
  - nhập trạng thái bắt đầu / trạng thái đích (chuỗi 9 ký tự gồm số `0`-`8`)
  - điều chỉnh `MAX_RESTART` cho Hill Climbing
  - điều chỉnh `K` cho Local Beam Search
- Các nút điều khiển:
  - `Khởi tạo lại`
  - `Chạy 1 Bước`
  - `Chạy Tự Động` / `Tạm Dừng`
- Khu vực log hiển thị từng bước duyệt, frontier và tập reached dưới dạng mini-board.
- UI tự động bật/tắt các điều khiển phù hợp với thuật toán đang chọn.

---

## ✅ Yêu cầu

- Python 3.8 trở lên
- Tkinter (thường có sẵn trên Windows/Mac; trên Linux có thể cần cài `python3-tk`)

---

## 🚀 Chạy ứng dụng

1. Mở terminal tại thư mục chứa file.

```bash
python 8puzzle.py
```

2. Nhập trạng thái bắt đầu và trạng thái đích dưới dạng chuỗi 9 ký tự.

Ví dụ:

- Start: `123406758`
- Goal:  `123456780`

3. Chọn thuật toán và nhấn `Chạy 1 Bước` hoặc `Chạy Tự Động`.

---

## 📌 Lưu ý

- `0` đại diện cho ô trống.
- Chuỗi trạng thái phải đủ 9 ký tự và chỉ chứa các số từ `0` đến `8`.
- Nếu thuật toán không tiến lên được, sẽ hiển thị trạng thái `Stuck` hoặc `Cutoff` trong log.

---

## 📂 File chính

- `8puzzle.py` — mã nguồn chính chứa cả thuật toán và giao diện.
- `readme.md` — hướng dẫn này.

---

Nếu bạn muốn tôi cập nhật thêm phần giải thích thuật toán, thêm ảnh chụp màn hình, hoặc tạo `requirements.txt`, hãy cho biết.
