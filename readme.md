# 🧩 8-Puzzle AI Visualizer

Ứng dụng mô phỏng trực quan bài toán 8-Puzzle bằng Python với giao diện đồ họa Tkinter.

Project hỗ trợ nhiều thuật toán tìm kiếm AI và hiển thị chi tiết:

- Frontier
- Reached / Explored
- Node đang xét
- Cost
- Manhattan Distance
- Đường đi tới đích

---

# ✨ Features

## 🔍 Supported Algorithms

- BFS Optimized
- BFS Classic
- BFS Generic
- DFS
- IDS
- UCS (Uniform Cost Search)
- Greedy Best First Search
- A* Search
- IDA* Search

---

## 📊 Visualization

Ứng dụng hiển thị trực quan:

- Ma trận trạng thái hiện tại
- Ma trận trạng thái đích
- Frontier
- Reached / Explored
- Node cha
- Action
- Cost
- Manhattan Distance
- Depth
- Số node đã duyệt

---

## 🎮 Interactive Controls

- Chạy từng bước
- Chạy tự động
- Reset thuật toán
- Thay đổi trạng thái đầu/cuối

---

# 🖼️ Interface

## Main UI

- Current State
- Goal State
- Control Panel
- Simulation Log
- Statistics Panel

---

# 🧠 Algorithms Explanation

## BFS

Breadth First Search sử dụng Queue FIFO.

Đảm bảo tìm lời giải ngắn nhất nếu cost các cạnh bằng nhau.

---

## DFS

Depth First Search sử dụng Stack LIFO.

Tiết kiệm bộ nhớ nhưng không đảm bảo tối ưu.

---

## UCS

Uniform Cost Search mở rộng node có path cost nhỏ nhất.

---

## Greedy Search

Sử dụng heuristic Manhattan Distance:

h(n)

để chọn node gần đích nhất.

---

## A*

Sử dụng:

f(n) = g(n) + h(n)

Trong đó:

- g(n): cost từ start
- h(n): Manhattan heuristic

---

## IDA*

Iterative Deepening A* kết hợp:

- DFS
- Heuristic A*

để giảm bộ nhớ sử dụng.

---

# 📦 Technologies Used

- Python 3
- Tkinter
- collections.deque
- heapq

---

# 🚀 Installation

## Clone repository

```bash
git clone https://github.com/your-username/8-puzzle-ai.git
cd 8-puzzle-ai