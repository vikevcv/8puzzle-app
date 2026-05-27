import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import heapq

class Node:
    def __init__(self, state, parent, action, depth, name=""):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.name = name

def get_neighbors(node):
    neighbors = []
    state = node.state
    zero_idx = state.find('0')
    row, col = divmod(zero_idx, 3)
    
    moves = [(0, -1, "Left"), (0, 1, "Right"), (-1, 0, "Up"), (1, 0, "Down")]
    
    for r, c, act in moves:
        new_row, new_col = row + r, col + c
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_idx = new_row * 3 + new_col
            state_list = list(state)
            state_list[zero_idx], state_list[new_idx] = state_list[new_idx], state_list[zero_idx]
            new_state = "".join(state_list)
            neighbors.append((new_state, act))
    return neighbors

def get_manhattan_distance(state, goal):
    distance = 0
    for i in range(1, 9):
        char = str(i)
        curr_idx = state.find(char)
        goal_idx = goal.find(char)
        if curr_idx != -1 and goal_idx != -1:
            r1, c1 = divmod(curr_idx, 3)
            r2, c2 = divmod(goal_idx, 3)
            distance += abs(r1 - r2) + abs(c1 - c2)
    return distance

def is_in_path(node, target_state):
    curr = node
    while curr:
        if curr.state == target_state:
            return True
        curr = curr.parent
    return False

class ScrollableFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_inner_frame = tk.Frame(self.canvas, bg="white")

        self.scrollable_inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_inner_frame, anchor="nw")
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def clear(self):
        for widget in self.scrollable_inner_frame.winfo_children():
            widget.destroy()
        self.scrollable_inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)


# =========================================================================
# ================= THUẬT TOÁN ĐÃ ĐƯỢC CẬP NHẬT: A* và IDA* ===============
# =========================================================================

def a_star_algorithm(start_state, goal_state, get_name_func):
    """Thuật toán A* với g(n) cộng dồn từ node cha bằng Heuristic Manhattan"""
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    start_node.h = get_manhattan_distance(start_state, goal_state)
    start_node.g = 0 
    start_node.f = start_node.g + start_node.h
    
    counter = 0  
    frontier = []
    heapq.heappush(frontier, (start_node.f, counter, start_node))
    
    reached = {start_state: start_node.g}
    
    if start_state == goal_state:
        yield start_node, [{"name": start_node.name, "action": "Start", "state": start_state, "is_goal": True, "parent_name": "None", "cost": f"{start_node.g}+{start_node.h}"}], set(reached.keys()), start_node
        return

    while frontier:
        curr_f, _, curr = heapq.heappop(frontier)
        
        if curr.state in reached and reached[curr.state] < curr.g:
            continue

        if curr.state == goal_state:
            yield curr, [{"name": curr.name, "action": "", "state": curr.state, "is_goal": True, "parent_name": curr.parent.name if curr.parent else "None", "cost": f"{curr.g}+{curr.h}"}], set(reached.keys()), curr
            return
            
        new_frontier_logs = []
        
        for new_state, act in get_neighbors(curr):
            h_new = get_manhattan_distance(new_state, goal_state)
            # Theo yêu cầu: cộng dồn manhattan cho cả g(n) từ node cha
            g_new = curr.g + h_new
            f_new = g_new + h_new
            
            if new_state in reached and g_new >= reached[new_state]:
                continue
                
            reached[new_state] = g_new
            
            child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
            child.g = g_new
            child.h = h_new
            child.f = f_new
            
            counter += 1
            heapq.heappush(frontier, (child.f, counter, child))
            
            new_frontier_logs.append({
                "name": child.name, 
                "action": act, 
                "state": child.state, 
                "is_goal": (new_state == goal_state), 
                "parent_name": curr.name, 
                "cost": f"{child.g}+{child.h}" 
            })
            
        yield curr, new_frontier_logs, set(reached.keys()), None

def ida_star_algorithm(start_state, goal_state, get_name_func, reset_name_func=None):
    """Thuật toán Iterative Deepening A* (IDA*) với cơ chế cắt tỉa lúc sinh"""
    # Ngưỡng ban đầu là f của node start
    start_h = get_manhattan_distance(start_state, goal_state)
    threshold = start_h 
    
    while True:
        if reset_name_func:
            reset_name_func()
            
        start_node = Node(start_state, None, "Start", 0, get_name_func())
        start_node.h = start_h
        start_node.g = 0
        start_node.f = start_node.g + start_node.h
        
        frontier = [start_node]
        iteration_reached = {start_state}
        
        next_threshold = float('inf')
        cutoff_occurred = False
        
        while frontier:
            curr = frontier.pop()
            
            if curr.state == goal_state:
                parent_name = curr.parent.name if curr.parent else "None"
                yield curr, [{"name": curr.name, "action": curr.action, "state": curr.state, "is_goal": True, "parent_name": parent_name, "cost": f"{curr.g}+{curr.h}"}], iteration_reached, curr
                return
            
            new_frontier_logs = []
            for new_state, act in get_neighbors(curr):
                if not is_in_path(curr, new_state):
                    h_new = get_manhattan_distance(new_state, goal_state)
                    # Cộng dồn manhattan cho g(n) như yêu cầu
                    g_new = curr.g + h_new
                    f_new = g_new + h_new
                    
                    child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
                    child.g = g_new
                    child.h = h_new
                    child.f = f_new
                    
                    # CẬP NHẬT: Không dùng lệnh continue nữa để vẫn đưa node vào logs hiển thị
                    if f_new > threshold:
                        cutoff_occurred = True
                        next_threshold = min(next_threshold, f_new)
                        cost_str = f"{child.g}+{child.h} (Loại > Mốc {threshold})"
                    else:
                        frontier.append(child)
                        iteration_reached.add(new_state)
                        cost_str = f"{child.g}+{child.h}"
                        
                    new_frontier_logs.append({
                        "name": child.name, 
                        "action": act, 
                        "state": child.state, 
                        "is_goal": False, 
                        "parent_name": curr.name, 
                        "cost": cost_str
                    })
                    
            yield curr, new_frontier_logs, iteration_reached, None
                
        # Nâng mốc xét duyệt lên mức tối ưu kế tiếp
        if not cutoff_occurred or next_threshold == float('inf'):
            break 
            
        threshold = next_threshold


# =========================================================================
# ======================== CÁC THUẬT TOÁN CŨ ==============================
# =========================================================================

def bfs_optimized(start_state, goal_state, get_name_func):
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    frontier = deque([start_node])
    reached = {start_state}
    
    if start_state == goal_state:
        yield start_node, [{"name": start_node.name, "action": "Start", "state": start_state, "is_goal": True, "parent_name": "None", "cost": 0}], reached, start_node
        return

    while frontier:
        curr = frontier.popleft()
        new_frontier_logs = []
        
        for new_state, act in get_neighbors(curr):
            if new_state not in reached:
                reached.add(new_state)
                child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
                is_goal = (new_state == goal_state)
                
                new_frontier_logs.append({"name": child.name, "action": act, "state": child.state, "is_goal": is_goal, "parent_name": curr.name, "cost": child.depth})
                
                if is_goal:
                    yield curr, new_frontier_logs, reached, child
                    return
                frontier.append(child)
                
        yield curr, new_frontier_logs, reached, None

def bfs_classic(start_state, goal_state, get_name_func):
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    frontier = deque([start_node])
    explored = set()
    
    while frontier:
        curr = frontier.popleft()
        explored.add(curr.state)
        new_frontier_logs = []
        
        for new_state, act in get_neighbors(curr):
            in_frontier = any(n.state == new_state for n in frontier)
            if new_state not in explored and not in_frontier:
                child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
                is_goal = (new_state == goal_state)
                
                new_frontier_logs.append({"name": child.name, "action": act, "state": child.state, "is_goal": is_goal, "parent_name": curr.name, "cost": child.depth})
                
                if is_goal:
                    yield curr, new_frontier_logs, explored, child
                    return
                frontier.append(child)
                
        yield curr, new_frontier_logs, explored, None

def bfs_generic(start_state, goal_state, get_name_func):
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    frontier = deque([start_node])
    reached = set()
    
    while frontier:
        curr = frontier.popleft()
        reached.add(curr.state)
        
        if curr.state == goal_state:
            yield curr, [{"name": curr.name, "action": "", "state": curr.state, "is_goal": True, "parent_name": curr.parent.name if curr.parent else "None", "cost": curr.depth}], reached, curr
            return
            
        new_frontier_logs = []
        for new_state, act in get_neighbors(curr):
            in_frontier = any(n.state == new_state for n in frontier)
            if new_state not in reached and not in_frontier:
                child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
                new_frontier_logs.append({"name": child.name, "action": act, "state": child.state, "is_goal": False, "parent_name": curr.name, "cost": child.depth})
                frontier.append(child)
                
        yield curr, new_frontier_logs, reached, None

def dfs_algorithm(start_state, goal_state, get_name_func):
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    frontier = [start_node]
    reached = {start_state}
    
    if start_state == goal_state:
        yield start_node, [{"name": start_node.name, "action": "Start", "state": start_state, "is_goal": True, "parent_name": "None", "cost": 0}], reached, start_node
        return

    while frontier:
        curr = frontier.pop()
        new_frontier_logs = []
        
        for new_state, act in get_neighbors(curr):
            in_frontier = any(n.state == new_state for n in frontier)
            if new_state not in reached and not in_frontier:
                reached.add(new_state)
                child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
                is_goal = (new_state == goal_state)
                
                new_frontier_logs.append({"name": child.name, "action": act, "state": child.state, "is_goal": is_goal, "parent_name": curr.name, "cost": child.depth})
                
                if is_goal:
                    yield curr, new_frontier_logs, reached, child
                    return
                frontier.append(child)
                
        yield curr, new_frontier_logs, reached, None

def ids_algorithm(start_state, goal_state, get_name_func, reset_name_func=None):
    limit = 0
    
    while True:
        if reset_name_func:
            reset_name_func()
            
        start_node = Node(start_state, None, "Start", 0, get_name_func())
        frontier = [start_node]
        cutoff_occurred = False
        
        iteration_reached = {start_state}
        
        while frontier:
            curr = frontier.pop()
            
            if curr.state == goal_state:
                parent_name = curr.parent.name if curr.parent else "None"
                yield curr, [{"name": curr.name, "action": curr.action, "state": curr.state, "is_goal": True, "parent_name": parent_name, "cost": curr.depth}], iteration_reached, curr
                return
            
            if curr.depth >= limit:
                cutoff_occurred = True
                frontier_yield_data = "Cutoff"  
            
            else:
                new_frontier_logs = []
                for new_state, act in get_neighbors(curr):
                    
                    if not is_in_path(curr, new_state):
                        child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
                        new_frontier_logs.append({
                            "name": child.name, 
                            "action": act, 
                            "state": child.state, 
                            "is_goal": False, 
                            "parent_name": curr.name, 
                            "cost": child.depth
                        })
                        frontier.append(child)
                        iteration_reached.add(new_state)
                        
                frontier_yield_data = new_frontier_logs
                
            yield curr, frontier_yield_data, iteration_reached, None
            
        if not cutoff_occurred:
            break
            
        limit += 1

def ucs_algorithm(start_state, goal_state, get_name_func):
    def count_diff(state):
        return sum(1 for s, g in zip(state, goal_state) if s != g)

    start_node = Node(start_state, None, "Start", 0, get_name_func())
    start_node.path_cost = 0
    
    counter = 0  
    frontier = []
    heapq.heappush(frontier, (start_node.path_cost, counter, start_node))
    
    reached = {start_state: start_node.path_cost}
    
    if start_state == goal_state:
        yield start_node, [{"name": start_node.name, "action": "Start", "state": start_state, "is_goal": True, "parent_name": "None", "cost": start_node.path_cost}], set(reached.keys()), start_node
        return

    while frontier:
        curr_cost, _, curr = heapq.heappop(frontier)
        
        if curr.state == goal_state:
            yield curr, [{"name": curr.name, "action": "", "state": curr.state, "is_goal": True, "parent_name": curr.parent.name if curr.parent else "None", "cost": curr.path_cost}], set(reached.keys()), curr
            return
            
        new_frontier_logs = []
        
        for new_state, act in get_neighbors(curr):
            step_cost = count_diff(new_state)
            new_cost = curr.path_cost + step_cost 
            
            if new_state not in reached or new_cost < reached[new_state]:
                reached[new_state] = new_cost
                child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
                child.path_cost = new_cost
                
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, child))
                
                new_frontier_logs.append({
                    "name": child.name, 
                    "action": act, 
                    "state": child.state, 
                    "is_goal": (new_state == goal_state), 
                    "parent_name": curr.name, 
                    "cost": new_cost
                })
                
        yield curr, new_frontier_logs, set(reached.keys()), None

def greedy_algorithm(start_state, goal_state, get_name_func):
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    
    counter = 0  
    frontier = []
    
    h_start = get_manhattan_distance(start_state, goal_state)
    heapq.heappush(frontier, (h_start, counter, start_node))
    
    in_frontier = {start_state}
    reached = set()
    
    if start_state == goal_state:
        yield start_node, [{"name": start_node.name, "action": "Start", "state": start_state, "is_goal": True, "parent_name": "None", "cost": h_start}], reached, start_node
        return

    while frontier:
        curr_h, _, curr = heapq.heappop(frontier)
        in_frontier.remove(curr.state)
        
        reached.add(curr.state)
        
        if curr.state == goal_state:
            yield curr, [{"name": curr.name, "action": "", "state": curr.state, "is_goal": True, "parent_name": curr.parent.name if curr.parent else "None", "cost": curr_h}], reached, curr
            return
            
        new_frontier_logs = []
        
        for new_state, act in get_neighbors(curr):
            if new_state not in reached and new_state not in in_frontier:
                child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
                
                h = get_manhattan_distance(new_state, goal_state)
                
                counter += 1
                heapq.heappush(frontier, (h, counter, child))
                in_frontier.add(new_state)
                
                new_frontier_logs.append({
                    "name": child.name, 
                    "action": act, 
                    "state": child.state, 
                    "is_goal": (new_state == goal_state), 
                    "parent_name": curr.name, 
                    "cost": h 
                })
                
        yield curr, new_frontier_logs, reached, None

# =========================================================================
# =============================== LỚP UI ==================================
# =========================================================================

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mô phỏng 8-Puzzle - Ma trận Đồ họa Toàn phần")
        self.root.geometry("1500x850")
        self.root.configure(bg="#ecf0f1")
        
        self.node_counter = 0
        self.generator = None
        self.auto_id = None
        self.is_auto_running = False  
        self.is_solved = False
        self.total_popped = 0
        
        self.setup_ui()
        self.reset_search()

    def get_next_name(self):
        num = self.node_counter
        self.node_counter += 1
        res = ""
        n = num
        while n >= 0:
            res = chr(65 + (n % 26)) + res
            n = n // 26 - 1
        return res

    def reset_name_counter(self):
        self.node_counter = 0

    def setup_ui(self):
        self.left_frame = tk.Frame(self.root, bg="#ecf0f1")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        
        self.boards_frame = tk.Frame(self.left_frame, bg="#ecf0f1")
        self.boards_frame.pack(pady=10)
        
        curr_frame, self.curr_board_canvas = self.create_board_ui(self.boards_frame, "Trạng thái Hiện Tại")
        curr_frame.grid(row=0, column=0, padx=10)
        
        goal_frame, self.goal_board_canvas = self.create_board_ui(self.boards_frame, "Trạng thái Đích")
        goal_frame.grid(row=0, column=1, padx=10)

        self.controls_frame = tk.LabelFrame(self.left_frame, text="Bảng Điều Khiển", font=("Arial", 12, "bold"), bg="white", padx=15, pady=15)
        self.controls_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(self.controls_frame, text="Thuật toán:", bg="white", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
        self.algo_var = tk.StringVar()
        self.algo_cb = ttk.Combobox(self.controls_frame, textvariable=self.algo_var, state="readonly", width=40)
        
        self.algo_cb['values'] = (
            "BFS Tối ưu (Early Goal + Reached Sớm)",
            "BFS Cổ điển (Early Goal + Explored Muộn)",
            "BFS Generic (Late Goal + Reached Muộn)",
            "DFS (LIFO Stack)",
            "IDS" ,
            "UCS (Uniform Cost Search)",
            "Greedy Search (Tham lam - Manhattan)",
            "A* (A Star)",
            "IDA* (Iterative Deepening A*)"
        )
        self.algo_cb.current(0)
        self.algo_cb.grid(row=0, column=1, columnspan=2, pady=5)
        self.algo_cb.bind("<<ComboboxSelected>>", lambda e: self.reset_search())
        
        tk.Label(self.controls_frame, text="Trạng thái đầu:", bg="white").grid(row=1, column=0, sticky="w")
        self.start_entry = tk.Entry(self.controls_frame, width=20, font=("Arial", 12))
        self.start_entry.insert(0, "123406758")
        self.start_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(self.controls_frame, text="Trạng thái đích:", bg="white").grid(row=2, column=0, sticky="w")
        self.goal_entry = tk.Entry(self.controls_frame, width=20, font=("Arial", 12))
        self.goal_entry.insert(0, "123456780")
        self.goal_entry.grid(row=2, column=1, pady=5)
        
        self.btn_reset = tk.Button(self.controls_frame, text="Khởi tạo lại", bg="#3498db", fg="white", font=("Arial", 10, "bold"), command=self.reset_search)
        self.btn_reset.grid(row=3, column=0, pady=10, padx=5)
        
        self.btn_step = tk.Button(self.controls_frame, text="Chạy 1 Bước", bg="#f39c12", fg="white", font=("Arial", 10, "bold"), command=self.step_search)
        self.btn_step.grid(row=3, column=1, pady=10, padx=5)
        
        self.btn_auto = tk.Button(self.controls_frame, text="Chạy Tự Động", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), command=self.toggle_auto)
        self.btn_auto.grid(row=3, column=2, pady=10, padx=5)

        self.info_frame = tk.LabelFrame(self.left_frame, text="Thống kê", font=("Arial", 12, "bold"), bg="#d1d8e0", padx=15, pady=15)
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.lbl_manhattan = tk.Label(self.info_frame, text="Manhattan Distance tới Đích: 0", bg="#d1d8e0", font=("Arial", 11, "bold"), fg="#c0392b")
        self.lbl_manhattan.pack(anchor="w", pady=2)
        
        self.lbl_depth = tk.Label(self.info_frame, text="Độ sâu hiện tại (Depth): 0", bg="#d1d8e0", font=("Arial", 11))
        self.lbl_depth.pack(anchor="w", pady=2)
        
        self.lbl_popped = tk.Label(self.info_frame, text="Số Node đã duyệt (Pop): 0", bg="#d1d8e0", font=("Arial", 11))
        self.lbl_popped.pack(anchor="w", pady=2)

        self.lbl_status = tk.Label(self.info_frame, text="Trạng thái: Đang chờ chạy", bg="#d1d8e0", font=("Arial", 11, "bold"), fg="#2980b9")
        self.lbl_status.pack(anchor="w", pady=10)

        self.right_frame = tk.Frame(self.root, bg="white", bd=2, relief="groove")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(self.right_frame, text="MÔ PHỎNG", font=("Arial", 14, "bold"), bg="#2c3e50", fg="white", pady=10).pack(fill=tk.X)
        
        header_frame = tk.Frame(self.right_frame, bg="#bdc3c7")
        header_frame.pack(fill=tk.X)
        header_frame.columnconfigure(0, weight=1, minsize=100)
        header_frame.columnconfigure(1, weight=5, minsize=450)
        header_frame.columnconfigure(2, weight=3, minsize=300)
        
        tk.Label(header_frame, text="Node", font=("Arial", 11, "bold"), bg="#bdc3c7", pady=5).grid(row=0, column=0, sticky="w", padx=10)
        tk.Label(header_frame, text="Frontier", font=("Arial", 11, "bold"), bg="#bdc3c7", pady=5).grid(row=0, column=1, sticky="w", padx=10)
        tk.Label(header_frame, text="Reached", font=("Arial", 11, "bold"), bg="#bdc3c7", pady=5).grid(row=0, column=2, sticky="w", padx=10)
        
        self.log_scroll = ScrollableFrame(self.right_frame)
        self.log_scroll.pack(fill=tk.BOTH, expand=True)

    def create_board_ui(self, parent, title):
        frame = tk.Frame(parent, bg="#ecf0f1")
        tk.Label(frame, text=title, font=("Arial", 12, "bold"), bg="#ecf0f1").pack()
        canvas = tk.Canvas(frame, width=160, height=160, bg="#34495e", highlightthickness=0)
        canvas.pack(pady=5)
        return frame, canvas

    def draw_state_to_canvas(self, canvas, state_str):
        canvas.delete("all")
        if len(state_str) != 9: return
        for i, char in enumerate(state_str):
            r, c = divmod(i, 3)
            x0, y0 = c * 50 + 5, r * 50 + 5
            x1, y1 = x0 + 45, y0 + 45
            
            if char == '0':
                canvas.create_rectangle(x0, y0, x1, y1, fill="#34495e", outline="#34495e")
            else:
                canvas.create_rectangle(x0, y0, x1, y1, fill="#ecf0f1", outline="#bdc3c7", width=2)
                canvas.create_text(x0+22, y0+22, text=char, font=("Arial", 18, "bold"), fill="#2c3e50")

    def create_mini_board_canvas(self, parent, state_str, title="", is_goal=False):
        canvas = tk.Canvas(parent, width=54, height=75 if title else 58, bg="white", highlightthickness=0)
        
        y_offset = 2
        if title:
            color = "#27ae60" if is_goal else "#2980b9"
            canvas.create_text(27, 10, text=title, font=("Arial", 9, "bold"), fill=color)
            y_offset = 20
            
        for i, char in enumerate(state_str):
            r, c = divmod(i, 3)
            x0 = c * 18
            y0 = y_offset + r * 18
            x1 = x0 + 18
            y1 = y0 + 18
            
            if char == '0':
                canvas.create_rectangle(x0, y0, x1, y1, fill="#34495e", outline="#2c3e50")
            else:
                canvas.create_rectangle(x0, y0, x1, y1, fill="#ecf0f1", outline="#bdc3c7")
                canvas.create_text(x0+9, y0+9, text=char, font=("Arial", 8, "bold"), fill="#2c3e50")
                
        return canvas

    def add_log_row(self, curr_node, frontier_list, reached_set):
        row_frame = tk.Frame(self.log_scroll.scrollable_inner_frame, bg="white", highlightbackground="#ecf0f1", highlightthickness=1)
        row_frame.pack(fill=tk.X, pady=3, padx=5)
        
        row_frame.columnconfigure(0, weight=1, minsize=100)
        row_frame.columnconfigure(1, weight=5, minsize=450)
        row_frame.columnconfigure(2, weight=3, minsize=300)
        
        f_node = tk.Frame(row_frame, bg="white")
        f_node.grid(row=0, column=0, sticky="nw", padx=10, pady=5)
        if curr_node:
            mb = self.create_mini_board_canvas(f_node, curr_node.state, title=f"Node {curr_node.name}")
            mb.pack()
            
        f_front = tk.Frame(row_frame, bg="white")
        f_front.grid(row=0, column=1, sticky="nw", padx=10, pady=5)
        
        if frontier_list == "Cutoff":
            tk.Label(f_front, text="CUTOFF (Sinh ra nhưng vượt mốc)", bg="white", fg="#e74c3c", font=("Arial", 11, "bold")).pack(anchor="w")
        elif not frontier_list:
            tk.Label(f_front, text="(Không được thêm vào Frontier)", bg="white", fg="gray", font=("Arial", 10, "italic")).pack(anchor="w")
        else:
            for item in frontier_list:
                item_frame = tk.Frame(f_front, bg="white")
                item_frame.pack(anchor="w", pady=4)
                
                tk.Label(item_frame, text="{ ", bg="white", font=("Courier New", 14, "bold"), fg="#34495e").pack(side="left")
                mb = self.create_mini_board_canvas(item_frame, item['state'])
                mb.pack(side="left", padx=2)
                
                act_char = item['action'][0] if item['action'] else ""
                info_text = f" , {item['parent_name']} , {act_char} , {item['cost']} }} ➔ Node {item['name']}"
                
                # CẬP NHẬT: Ép str() để đảm bảo các thuật toán cũ lưu int không bị sập hàm
                is_loai = "Loại" in str(item['cost'])
                if is_loai:
                    color = "#e74c3c"
                elif item['is_goal']:
                    color = "#27ae60"
                else:
                    color = "#2c3e50"
                    
                if item['is_goal']:
                    info_text += " ★"
                    
                tk.Label(item_frame, text=info_text, bg="white", font=("Courier New", 12, "bold"), fg=color).pack(side="left")
                
        f_set = tk.Frame(row_frame, bg="white")
        f_set.grid(row=0, column=2, sticky="nw", padx=10, pady=5)
        
        set_wrap = tk.Frame(f_set, bg="white")
        set_wrap.pack(fill=tk.X)
        for i, state in enumerate(sorted(list(reached_set))):
            mb = self.create_mini_board_canvas(set_wrap, state)
            mb.grid(row=i//5, column=i%5, padx=3, pady=3)
            
        self.root.update_idletasks()
        self.log_scroll.canvas.yview_moveto(1)

    def stop_auto(self):
        self.is_auto_running = False
        if self.auto_id:
            self.root.after_cancel(self.auto_id)
            self.auto_id = None
        self.btn_auto.config(text="Chạy Tự Động", bg="#2ecc71")

    def toggle_auto(self):
        if self.is_auto_running:
            self.stop_auto()
        else:
            self.is_auto_running = True
            self.btn_auto.config(text="Tạm Dừng", bg="#e74c3c")
            self.auto_step()

    def auto_step(self):
        if self.is_auto_running and not self.is_solved:
            self.step_search()
            if self.is_auto_running and not self.is_solved:
                self.auto_id = self.root.after(350, self.auto_step)

    def reset_search(self):
        self.stop_auto() 
        
        start_state = self.start_entry.get().strip()
        goal_state = self.goal_entry.get().strip()
        
        if len(start_state) != 9 or len(goal_state) != 9:
            messagebox.showerror("Lỗi", "Trạng thái phải là chuỗi đúng 9 số từ 0-8!")
            return
            
        self.node_counter = 0
        self.total_popped = 0
        self.is_solved = False
        
        self.draw_state_to_canvas(self.curr_board_canvas, start_state)
        self.draw_state_to_canvas(self.goal_board_canvas, goal_state)
        
        self.log_scroll.clear()
            
        algo = self.algo_var.get()
        if "Tối ưu" in algo:
            self.generator = bfs_optimized(start_state, goal_state, self.get_next_name)
        elif "Cổ điển" in algo:
            self.generator = bfs_classic(start_state, goal_state, self.get_next_name)
        elif "Generic" in algo:
            self.generator = bfs_generic(start_state, goal_state, self.get_next_name)
        elif "IDA*" in algo:
            self.generator = ida_star_algorithm(start_state, goal_state, self.get_next_name, self.reset_name_counter)
        elif "IDS" in algo:
            self.generator = ids_algorithm(start_state, goal_state, self.get_next_name, self.reset_name_counter)
        elif "UCS" in algo: 
            self.generator = ucs_algorithm(start_state, goal_state, self.get_next_name)
        elif "Greedy" in algo:
            self.generator = greedy_algorithm(start_state, goal_state, self.get_next_name)
        elif "A*" in algo:
            self.generator = a_star_algorithm(start_state, goal_state, self.get_next_name)
        else:
            self.generator = dfs_algorithm(start_state, goal_state, self.get_next_name)

        self.btn_step.config(state="normal")
        self.btn_auto.config(state="normal")
        self.lbl_status.config(text="Trạng thái: Đã khởi tạo.", fg="#2980b9")
        
        md = get_manhattan_distance(start_state, goal_state)
        self.lbl_manhattan.config(text=f"Manhattan Distance tới Đích: {md}")
        self.lbl_depth.config(text="Độ sâu hiện tại (Depth): 0")
        self.lbl_popped.config(text="Số Node đã duyệt (Pop): 0")

    def step_search(self):
        if self.is_solved or not self.generator:
            return
            
        try:
            curr_node, frontier_logs, reached_set, goal_node = next(self.generator)
            self.total_popped += 1
            self.draw_state_to_canvas(self.curr_board_canvas, curr_node.state)
            
            self.add_log_row(curr_node, frontier_logs, reached_set)
            
            md = get_manhattan_distance(curr_node.state, self.goal_entry.get().strip())
            self.lbl_manhattan.config(text=f"Manhattan Distance tới Đích: {md}")
            self.lbl_depth.config(text=f"Độ sâu hiện tại (Depth): {curr_node.depth}")
            self.lbl_popped.config(text=f"Số Node đã duyệt (Pop): {self.total_popped}")
            
            if goal_node:
                self.is_solved = True
                path = self.trace_path(goal_node)
                self.lbl_status.config(text=f"🎉 Đã tìm thấy Đích!\nCost: {goal_node.depth} bước\nĐường đi: {path}", fg="#27ae60")
                
                self.btn_step.config(state="disabled")
                self.stop_auto()
                self.btn_auto.config(state="disabled")
                
        except StopIteration:
            self.lbl_status.config(text="❌ Thất bại: Đã duyệt hết không gian trạng thái!", fg="#c0392b")
            self.is_solved = True
            
            self.btn_step.config(state="disabled")
            self.stop_auto()
            self.btn_auto.config(state="disabled")
                
    def trace_path(self, node):
        path = []
        curr = node
        while curr:
            if curr.action != "Start":
                path.append(f"{curr.action[0]}")

            curr = curr.parent
        return " -> ".join(path[::-1])

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()