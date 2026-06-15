# 🧩 8-Puzzle AI Visualizer

Ứng dụng GUI mô phỏng 8-Puzzle, triển khai nhiều thuật toán tìm kiếm và tối ưu hoá. README này phản ánh chính xác giao diện, thuật toán và các tham số trong `8puzzle.py`.

---

## Tổng quan

Ứng dụng cho phép quan sát trực quan tiến trình tìm kiếm: Current Node, Frontier, Reached, cùng mini-board hiển thị trạng thái. Hỗ trợ chạy từng bước hoặc chạy tự động.

---

## Thuật toán có sẵn (giá trị trong combobox `Thuật toán:`)

- BFS Tối ưu (Early Goal + Reached Sớm)
- BFS Cổ điển (Early Goal + Explored Muộn)
- BFS Generic (Late Goal + Reached Muộn)
- DFS (LIFO Stack)
- IDS
- UCS (Uniform Cost Search)
- Greedy Search (Tham lam - Heuristic)
- A* (A Star)
- IDA* (Iterative Deepening A*)
- Leo núi đơn giản (Simple Hill Climbing)
- Leo núi dốc nhất (Steepest-Ascent Hill Climbing)
- Leo núi ngẫu nhiên (Stochastic Hill Climbing)
- Leo núi khởi động lại ngẫu nhiên (Random Restart HC)
- Local Beam Search (Tìm kiếm chùm cục bộ)
- Simulated Annealing (SA - Ủ mô phỏng)
- Belief State BFS (Đa trạng thái)
- AND-OR Graph Search (Không xác định)
- CSP Backtracking (Cơ bản)
- CSP Backtracking (Forward Checking)

## Heuristic / Cost (combobox `Cost / Heuristic:`)

- Khoảng cách Manhattan
- Số ô sai vị trí
- Giá trị ô swap

---

## Giao diện & tham số quan trọng

- Trạng thái đầu / Trạng thái đích: nhập chuỗi 9 ký tự (ví dụ mặc định `Start: 123406758`, `Goal: 123456780`).
- Nút: `Khởi tạo lại`, `Chạy 1 Bước`, `Chạy Tự Động`.
- `MAX_RESTART`: dùng cho "Leo núi khởi động lại ngẫu nhiên".
- `K`: dùng cho `Local Beam Search`.
- SA (Simulated Annealing) controls: `SA T₀` (initial temp), `SA α` (cooling rate), `SA T_min`, `SA Max Restart`.
- Belief State: `Số belief states`, `Số goal states`, và nút `Sinh ngẫu nhiên` để tạo belief/goals.
- CSP: hai chế độ — Cơ bản và Forward Checking (FC).

---

## Chạy ứng dụng

1. Mở terminal vào thư mục dự án.

```bash
python 8puzzle.py
```

2. (GUI) Thay đổi trạng thái bắt đầu/đích nếu cần, chọn thuật toán và tham số.
3. Nhấn `Chạy 1 Bước` để quan sát từng bước, hoặc `Chạy Tự Động` để chạy liên tục (có thể tạm dừng).

---

## Hành vi và đầu ra

- Khi tìm thấy goal, bảng log sẽ hiển thị path và cost; cho các thuật toán chi phí (UCS/A*), `cost` hiển thị là `g+h` hoặc `path_cost` tuỳ thuật toán.
- Các trạng thái đặc biệt được hiển thị trong log: `Stuck`, `Cutoff`, `Cutoff_FC`, `SA_stuck`.
- `AND-OR Graph Search` trả về một contingency plan mở ra trong cửa sổ riêng.

---

## Yêu cầu

- Python 3.8+
- Tkinter (Linux: `sudo apt-get install python3-tk` nếu cần)

---

## File chính

- `8puzzle.py` — mã nguồn (UI + thuật toán)

---

Nếu bạn muốn tôi cập nhật README bằng ảnh chụp màn hình, thêm `requirements.txt`, hoặc dịch sang English, tôi sẽ thực hiện tiếp.
