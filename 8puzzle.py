import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import heapq
import random
import math
import pprint

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

def get_nondeterministic_results(state, intended_action):
    neighbors = get_neighbors(Node(state, None, None, 0))
    valid_moves = {act: s for s, act in neighbors}
    
    results = []
    if intended_action in valid_moves:
        results.append(valid_moves[intended_action])
        
    slip_map = {
        "Left": ["Up", "Down"],
        "Right": ["Up", "Down"],
        "Up": ["Left", "Right"],
        "Down": ["Left", "Right"]
    }
    
    for slip_act in slip_map.get(intended_action, []):
        if slip_act in valid_moves:
            results.append(valid_moves[slip_act])
            
    return list(set(results))

def and_or_graph_search(start_state, goal_state, get_name_func):
    plan = yield from or_search(start_state, goal_state, [], get_name_func, 0)
    return plan

def or_search(state, goal_state, path, get_name_func, depth):
    yield {"phase": "OR", "state": state, "path": path, "depth": depth}, "AND-OR", set(path), None
    if state == goal_state: return []
    if state in path: return "failure"
        
    valid_actions = [act for _, act in get_neighbors(Node(state, None, None, 0))]
    for action in valid_actions:
        result_states = get_nondeterministic_results(state, action)
        yield {"phase": "ACTION", "state": state, "action": action, "results": result_states, "depth": depth}, "AND-OR", set(path), None
        plan = yield from and_search(result_states, goal_state, path + [state], get_name_func, depth + 1)
        if plan != "failure":
            return [action, plan]
    return "failure"

def and_search(states, goal_state, path, get_name_func, depth):
    yield {"phase": "AND", "states": states, "path": path, "depth": depth}, "AND-OR", set(path), None
    plans = {}
    for s in states:
        plan_s = yield from or_search(s, goal_state, path, get_name_func, depth + 1)
        if plan_s == "failure": return "failure"
        plans[s] = plan_s
    return plans

def count_inversions(state_str):
    arr = [int(c) for c in state_str if c != '0' and c != '-']
    inv = 0
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]: inv += 1
    return inv

def csp_backtracking_generator(goal_state_str, get_name_func):
    domain = ['1', '2', '3', '4', '5', '6', '7', '8', '0']
    assignment = ['-'] * 9 
    start_str = "".join(assignment)
    start_node = Node(start_str, None, "Start CSP", 0, get_name_func())
    
    def recursive_backtrack(var_idx, curr_node):
        state_str = "".join(assignment)
        if var_idx == 9:
            inv = count_inversions(state_str)
            goal_inv = count_inversions(goal_state_str)
            if (inv % 2) == (goal_inv % 2):
                curr_node.action = "Thành công"
                yield curr_node, [{"name": curr_node.name, "action": "Chốt", "state": state_str, "is_goal": True, "parent_name": curr_node.parent.name if curr_node.parent else "None", "cost": "Hợp lệ"}], set(), curr_node
                return True
            else:
                yield curr_node, "Cutoff", set(), None 
                return False
        
        random.shuffle(domain)
        for val in domain:
            if val not in assignment:
                assignment[var_idx] = val
                new_state_str = "".join(assignment)
                child = Node(new_state_str, curr_node, f"Gán {val} vào P{var_idx}", var_idx + 1, get_name_func())
                log_item = {"name": child.name, "action": f"Gán {val}", "state": new_state_str, "is_goal": False, "parent_name": curr_node.name, "cost": "Thử"}
                
                yield curr_node, [log_item], set(), None
                
                result = yield from recursive_backtrack(var_idx + 1, child)
                if result: return True
                    
                assignment[var_idx] = '-'
                undo_str = "".join(assignment)
                yield child, [{"name": "Undo", "action": f"Gỡ {val}", "state": undo_str, "is_goal": False, "parent_name": child.name, "cost": "Lùi"}], set(), None
        return False
        
    yield from recursive_backtrack(0, start_node)

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

def get_eval_value(curr_state, new_state, goal_state, eval_type):
    if eval_type == "Số ô sai vị trí":
        return sum(1 for s, g in zip(new_state, goal_state) if s != g and s != '0')
    elif eval_type == "Giá trị ô swap":
        if not curr_state: return 9 
        zero_idx_curr = curr_state.find('0')
        return int(new_state[zero_idx_curr])
    else: 
        return get_manhattan_distance(new_state, goal_state)

def is_in_path(node, target_state):
    curr = node
    while curr:
        if curr.state == target_state: return True
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

def local_beam_search(start_state, goal_state, get_name_func, eval_type, k):
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    start_node.h = get_eval_value(None, start_state, goal_state, eval_type)
    reached = {start_state}
    if start_state == goal_state:
        yield [start_node], [{"name": start_node.name, "action": "Start", "state": start_state, "is_goal": True, "parent_name": "None", "cost": start_node.h}], reached, start_node
        return
    current_state_set = [start_node]
    while True:
        neighbor_states = []
        new_frontier_logs = []
        goal_node = None
        for state_node in current_state_set:
            for new_state, act in get_neighbors(state_node):
                if new_state not in reached:
                    child = Node(new_state, state_node, act, state_node.depth + 1, get_name_func())
                    child.h = get_eval_value(state_node.state, new_state, goal_state, eval_type)
                    neighbor_states.append(child)
                    reached.add(new_state)
                    is_goal = (new_state == goal_state)
                    new_frontier_logs.append({
                        "name": child.name, "action": act, "state": child.state, 
                        "is_goal": is_goal, "parent_name": state_node.name, "cost": child.h
                    })
                    if is_goal and not goal_node: goal_node = child
        if not neighbor_states:
            yield current_state_set, "Stuck", reached, None
            return
        yield current_state_set, new_frontier_logs, reached, goal_node
        if goal_node: return
        neighbor_states.sort(key=lambda x: x.h)
        current_state_set = neighbor_states[:k]

def simple_hill_climbing(start_state, goal_state, get_name_func, eval_type):
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    start_node.h = get_eval_value(None, start_state, goal_state, eval_type)
    curr = start_node
    reached = {start_state}
    if curr.state == goal_state:
        yield curr, [{"name": curr.name, "action": "Start", "state": curr.state, "is_goal": True, "parent_name": "None", "cost": 0}], reached, curr
        return
    while True:
        new_frontier_logs = []
        next_node = None
        for new_state, act in get_neighbors(curr):
            child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
            child.h = get_eval_value(curr.state, new_state, goal_state, eval_type)
            is_goal = (new_state == goal_state)
            new_frontier_logs.append({
                "name": child.name, "action": act, "state": child.state, 
                "is_goal": is_goal, "parent_name": curr.name, "cost": child.h
            })
            if child.h < curr.h:
                next_node = child
                break 
        yield curr, new_frontier_logs, reached, None
        if next_node is None:
            yield curr, "Stuck", reached, None
            return
        if next_node.state == goal_state:
            reached.add(next_node.state)
            yield next_node, [], reached, next_node
            return
        curr = next_node
        reached.add(curr.state)

def steepest_ascent_hill_climbing(start_state, goal_state, get_name_func, eval_type):
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    start_node.h = get_eval_value(None, start_state, goal_state, eval_type)
    curr = start_node
    reached = {start_state}
    if curr.state == goal_state:
        yield curr, [{"name": curr.name, "action": "Start", "state": curr.state, "is_goal": True, "parent_name": "None", "cost": 0}], reached, curr
        return
    while True:
        new_frontier_logs = []
        best_node = None
        best_h = float('inf')
        for new_state, act in get_neighbors(curr):
            child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
            child.h = get_eval_value(curr.state, new_state, goal_state, eval_type)
            is_goal = (new_state == goal_state)
            new_frontier_logs.append({
                "name": child.name, "action": act, "state": child.state, 
                "is_goal": is_goal, "parent_name": curr.name, "cost": child.h
            })
            if child.h < best_h:
                best_h = child.h
                best_node = child
        yield curr, new_frontier_logs, reached, None
        if best_node is None or best_h >= curr.h:
            yield curr, "Stuck", reached, None
            return
        if best_node.state == goal_state:
            reached.add(best_node.state)
            yield best_node, [], reached, best_node
            return
        curr = best_node
        reached.add(curr.state)

def stochastic_hill_climbing(start_state, goal_state, get_name_func, eval_type):
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    start_node.h = get_eval_value(None, start_state, goal_state, eval_type)
    curr = start_node
    reached = {start_state}
    if curr.state == goal_state:
        yield curr, [{"name": curr.name, "action": "Start", "state": curr.state, "is_goal": True, "parent_name": "None", "cost": 0}], reached, curr
        return
    while True:
        new_frontier_logs = []
        better_neighbors = []
        for new_state, act in get_neighbors(curr):
            child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
            child.h = get_eval_value(curr.state, new_state, goal_state, eval_type)
            is_goal = (new_state == goal_state)
            new_frontier_logs.append({
                "name": child.name, "action": act, "state": child.state, 
                "is_goal": is_goal, "parent_name": curr.name, "cost": child.h
            })
            if child.h < curr.h: better_neighbors.append(child)
        yield curr, new_frontier_logs, reached, None
        if not better_neighbors:
            yield curr, "Stuck", reached, None
            return
        next_node = random.choice(better_neighbors)
        if next_node.state == goal_state:
            reached.add(next_node.state)
            yield next_node, [], reached, next_node
            return
        curr = next_node
        reached.add(curr.state)

def random_restart_hill_climbing(start_state, goal_state, get_name_func, eval_type, max_restart):
    reached = set()
    for i in range(1, max_restart + 1):
        start_node = Node(start_state, None, f"Start (Lượt {i})", 0, get_name_func())
        start_node.h = get_eval_value(None, start_state, goal_state, eval_type)
        curr = start_node
        reached.add(curr.state)
        if curr.state == goal_state:
            yield curr, [{"name": curr.name, "action": curr.action, "state": curr.state, "is_goal": True, "parent_name": "None", "cost": curr.h}], reached, curr
            return
        while True:
            new_frontier_logs = []
            better_neighbors = []
            for new_state, act in get_neighbors(curr):
                child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
                child.h = get_eval_value(curr.state, new_state, goal_state, eval_type)
                is_goal = (new_state == goal_state)
                new_frontier_logs.append({
                    "name": child.name, "action": act, "state": child.state, 
                    "is_goal": is_goal, "parent_name": curr.name, "cost": child.h
                })
                if child.h < curr.h: better_neighbors.append(child)
            yield curr, new_frontier_logs, reached, None
            if not better_neighbors:
                yield curr, "Stuck", reached, None 
                break 
            next_node = random.choice(better_neighbors)
            if next_node.state == goal_state:
                reached.add(next_node.state)
                yield next_node, [], reached, next_node
                return
            curr = next_node
            reached.add(curr.state)

def a_star_algorithm(start_state, goal_state, get_name_func, eval_type):
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    start_node.h = get_eval_value(None, start_state, goal_state, eval_type)
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
        if curr.state in reached and reached[curr.state] < curr.g: continue
        if curr.state == goal_state:
            yield curr, [{"name": curr.name, "action": "", "state": curr.state, "is_goal": True, "parent_name": curr.parent.name if curr.parent else "None", "cost": f"{curr.g}+{curr.h}"}], set(reached.keys()), curr
            return
        new_frontier_logs = []
        for new_state, act in get_neighbors(curr):
            h_new = get_eval_value(curr.state, new_state, goal_state, eval_type)
            step_cost = get_eval_value(curr.state, new_state, goal_state, "Giá trị ô swap") if eval_type == "Giá trị ô swap" else 1
            g_new = curr.g + step_cost
            f_new = g_new + h_new
            if new_state in reached and g_new >= reached[new_state]: continue
            reached[new_state] = g_new
            child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
            child.g = g_new; child.h = h_new; child.f = f_new
            counter += 1
            heapq.heappush(frontier, (child.f, counter, child))
            new_frontier_logs.append({
                "name": child.name, "action": act, "state": child.state, 
                "is_goal": (new_state == goal_state), "parent_name": curr.name, 
                "cost": f"{child.g}+{child.h}" 
            })
        yield curr, new_frontier_logs, set(reached.keys()), None

def ida_star_algorithm(start_state, goal_state, get_name_func, reset_name_func, eval_type):
    start_h = get_eval_value(None, start_state, goal_state, eval_type)
    threshold = start_h 
    while True:
        if reset_name_func: reset_name_func()
        start_node = Node(start_state, None, "Start", 0, get_name_func())
        start_node.h = start_h; start_node.g = 0; start_node.f = start_node.g + start_node.h
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
                    h_new = get_eval_value(curr.state, new_state, goal_state, eval_type)
                    step_cost = get_eval_value(curr.state, new_state, goal_state, "Giá trị ô swap") if eval_type == "Giá trị ô swap" else 1
                    g_new = curr.g + step_cost
                    f_new = g_new + h_new
                    child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
                    child.g = g_new; child.h = h_new; child.f = f_new
                    if f_new > threshold:
                        cutoff_occurred = True
                        next_threshold = min(next_threshold, f_new)
                        cost_str = f"{child.g}+{child.h} (Loại > Mốc {threshold})"
                    else:
                        frontier.append(child)
                        iteration_reached.add(new_state)
                        cost_str = f"{child.g}+{child.h}"
                    new_frontier_logs.append({
                        "name": child.name, "action": act, "state": child.state, 
                        "is_goal": False, "parent_name": curr.name, "cost": cost_str
                    })
            yield curr, new_frontier_logs, iteration_reached, None
        if not cutoff_occurred or next_threshold == float('inf'): break 
        threshold = next_threshold

def ucs_algorithm(start_state, goal_state, get_name_func, eval_type):
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
            step_cost = get_eval_value(curr.state, new_state, goal_state, eval_type)
            new_cost = curr.path_cost + step_cost 
            if new_state not in reached or new_cost < reached[new_state]:
                reached[new_state] = new_cost
                child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
                child.path_cost = new_cost
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, child))
                new_frontier_logs.append({
                    "name": child.name, "action": act, "state": child.state, 
                    "is_goal": (new_state == goal_state), "parent_name": curr.name, 
                    "cost": new_cost
                })
        yield curr, new_frontier_logs, set(reached.keys()), None

def greedy_algorithm(start_state, goal_state, get_name_func, eval_type):
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    counter = 0  
    frontier = []
    h_start = get_eval_value(None, start_state, goal_state, eval_type)
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
                h = get_eval_value(curr.state, new_state, goal_state, eval_type)
                counter += 1
                heapq.heappush(frontier, (h, counter, child))
                in_frontier.add(new_state)
                new_frontier_logs.append({
                    "name": child.name, "action": act, "state": child.state, 
                    "is_goal": (new_state == goal_state), "parent_name": curr.name, 
                    "cost": h 
                })
        yield curr, new_frontier_logs, reached, None

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
        if reset_name_func: reset_name_func()
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
                            "name": child.name, "action": act, "state": child.state, 
                            "is_goal": False, "parent_name": curr.name, "cost": child.depth
                        })
                        frontier.append(child)
                        iteration_reached.add(new_state)
                frontier_yield_data = new_frontier_logs
            yield curr, frontier_yield_data, iteration_reached, None
        if not cutoff_occurred:
            break
        limit += 1

def simulated_annealing(start_state, goal_state, get_name_func, eval_type,
                        initial_temp=100, cooling_rate=0.95,
                        min_temp=0.1, max_restart=3):
    start_cost = get_manhattan_distance(start_state, goal_state)
    start_node = Node(start_state, None, "Start", 0, get_name_func())
    start_node.cost = start_cost
    if start_state == goal_state:
        data = {"current": start_node, "candidate": None, "best": start_node,
                "temperature": initial_temp, "accept_prob": 1.0,
                "delta": 0, "accepted": True, "action": "",
                "cost_history": [start_cost],
                "temp_history": [initial_temp], "accepted_history": [True],
                "iteration": 0,
                "initial_temp": initial_temp,
                "restart_count": 0, "max_restart": max_restart,
                "min_temp": min_temp}
        yield data, "SA", {start_state}, start_node
        return
    curr = start_node
    best = start_node
    T = initial_temp
    cost_history = [start_cost]
    temp_history = [initial_temp]
    accepted_history = [True]
    iteration = 0
    restart_count = 0
    reached = {start_state}
    while True:
        neighbors = get_neighbors(curr)
        if not neighbors:
            data = {"current": curr, "candidate": None, "best": best,
                    "temperature": T, "accept_prob": 0, "delta": 0,
                    "accepted": False, "action": "",
                    "cost_history": cost_history, "temp_history": temp_history,
                    "accepted_history": accepted_history, "iteration": iteration,
                    "initial_temp": initial_temp, "restart_count": restart_count,
                    "max_restart": max_restart, "min_temp": min_temp}
            yield data, "SA_stuck", reached, None
            return
        new_state, act = random.choice(neighbors)
        new_cost = get_manhattan_distance(new_state, goal_state)
        delta = new_cost - curr.cost
        accept_prob = min(1.0, math.exp(-delta / max(T, 0.001))) if delta > 0 else 1.0
        iteration += 1
        accepted = False
        next_node = None
        T *= cooling_rate
        if delta < 0 or random.random() < accept_prob:
            child = Node(new_state, curr, act, curr.depth + 1, get_name_func())
            child.cost = new_cost
            next_node = child
            reached.add(new_state)
            accepted = True
            if new_cost < best.cost: best = child
        cost_history.append(new_cost)
        temp_history.append(T)
        accepted_history.append(accepted)
        candidate_node = Node(new_state, curr, act, curr.depth + 1, "?")
        candidate_node.cost = new_cost
        is_goal = (new_state == goal_state)
        data = {"current": curr, "candidate": candidate_node, "next": next_node,
                "best": best, "temperature": T, "accept_prob": accept_prob,
                "delta": delta, "accepted": accepted, "action": act,
                "cost_history": cost_history, "temp_history": temp_history,
                "accepted_history": accepted_history, "iteration": iteration,
                "initial_temp": initial_temp, "restart_count": restart_count,
                "max_restart": max_restart, "min_temp": min_temp}
        final_node = next_node if accepted else curr
        yield data, "SA", reached, (final_node if is_goal else None)
        if is_goal: return
        if next_node: curr = next_node
        if T <= min_temp:
            if restart_count < max_restart - 1:
                restart_count += 1; T = initial_temp; curr = start_node
                cost_history.append(best.cost); temp_history.append(T); accepted_history.append(True)
            else:
                yield data, "SA_stuck", reached, None
                return

def generate_random_states(count, mode="belief", base_goal="123456780"):
    if mode == "goal":
        states = []
        for _ in range(count):
            state = base_goal
            num_moves = random.randint(0, 3)
            for _ in range(num_moves):
                neighbors = get_neighbors(Node(state, None, None, 0))
                if neighbors: state, _ = random.choice(neighbors)
            states.append(state)
        return states
    if mode == "belief":
        if count <= 0: return []
        base_state = base_goal
        num_moves = random.randint(15, 35)
        for _ in range(num_moves):
            neighbors = get_neighbors(Node(base_state, None, None, 0))
            if neighbors: base_state, _ = random.choice(neighbors)
        states = [base_state]
        for _ in range(count - 1):
            s = base_state
            extra = random.randint(1, 3)
            for _ in range(extra):
                neighbors = get_neighbors(Node(s, None, None, 0))
                if neighbors: s, _ = random.choice(neighbors)
            states.append(s)
        return states
    return []

def belief_state_bfs(start_states, goal_states, get_name_func, max_depth=15):
    goal_set = frozenset(goal_states)
    n = len(start_states)
    frontiers = [deque([(s, 0, [])]) for s in start_states]
    explored_list = [{s} for s in start_states]
    solved = [s in goal_set for s in start_states]
    target_goal = None
    state_names = {s: get_name_func() for s in start_states}
    all_reached = set(start_states)
    restart_flag = False; restart_reason = ""
    round_robin_idx = 0
    for i, s in enumerate(start_states):
        if solved[i]: target_goal = s; break

    while not all(solved):
        found = False
        for _ in range(n):
            i = round_robin_idx % n
            round_robin_idx += 1
            if solved[i]: continue
            if not frontiers[i]: continue
            found = True
            curr_state, depth, path = frontiers[i].popleft()
            if depth >= max_depth: continue
            frontier_logs = []
            for act_name in ["Left", "Right", "Up", "Down"]:
                neighbors = get_neighbors(Node(curr_state, None, None, 0))
                matching = [ns for ns, a in neighbors if a == act_name]
                if not matching: continue
                new_state = matching[0]
                if new_state not in explored_list[i]:
                    explored_list[i].add(new_state)
                    all_reached.add(new_state)
                    new_path = path + [act_name]
                    is_goal = (new_state == target_goal) if target_goal is not None else (new_state in goal_set)
                    if new_state not in state_names: state_names[new_state] = get_name_func()
                    frontier_logs.append({
                        "state": new_state, "action": act_name, "from_state": curr_state,
                        "is_goal": is_goal, "depth": depth + 1,
                        "name": state_names[new_state], "belief_idx": i
                    })
                    if is_goal:
                        if target_goal is None:
                            target_goal = new_state
                            restart_flag = True
                            restart_reason = f"S{i+1} found goal {new_state}, other states continue toward target..."
                        solved[i] = True
                    if not is_goal and depth + 1 < max_depth:
                        frontiers[i].append((new_state, depth + 1, new_path))
            curr_states = []
            queues = []
            for j in range(n):
                if solved[j]:
                    curr_states.append(target_goal if target_goal else start_states[j])
                    queues.append([])
                elif frontiers[j]:
                    f0 = frontiers[j][0]
                    curr_states.append(f0[0] if f0 else start_states[j])
                    queues.append([(s, d, p) for s, d, p in list(frontiers[j])[:6]])
                else:
                    curr_states.append(start_states[j])
                    queues.append([])
            curr_states = tuple(sorted(curr_states))
            display_data = {
                "belief": curr_states, "depth": depth + 1, "solved": solved[:],
                "expanding": i, "expanding_state": curr_state,
                "frontier_logs": frontier_logs, "explored_sets": explored_list,
                "all_reached": all_reached, "queues": queues,
                "target_goal": target_goal, "restart_reason": restart_reason, "restart_flag": restart_flag
            }
            yield display_data, frontier_logs, all_reached, None
            restart_flag = False; restart_reason = ""
            if all(solved):
                yield display_data, frontier_logs, all_reached, start_states
                return
            break
        if not found: break

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
        self.is_sa_mode = False
        self.is_belief_mode = False
        self.belief_generated_states = None
        self.belief_generated_goals = None
        self.total_popped = 0
        self.belief_step_count = 0
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
            "IDS",
            "UCS (Uniform Cost Search)",
            "Greedy Search (Tham lam - Heuristic)",
            "A* (A Star)",
            "IDA* (Iterative Deepening A*)",
            "Leo núi đơn giản (Simple Hill Climbing)",
            "Leo núi dốc nhất (Steepest-Ascent Hill Climbing)",
            "Leo núi ngẫu nhiên (Stochastic Hill Climbing)",
            "Leo núi khởi động lại ngẫu nhiên (Random Restart HC)",
            "Local Beam Search (Tìm kiếm chùm cục bộ)",
            "Simulated Annealing (SA - Ủ mô phỏng)",
            "Belief State BFS (Đa trạng thái)",
            "AND-OR Graph Search (Không xác định)",
            "CSP Backtracking (Sinh trạng thái hợp lệ)"
        )
        self.algo_cb.current(0)
        self.algo_cb.grid(row=0, column=1, columnspan=2, pady=5)
        self.algo_cb.bind("<<ComboboxSelected>>", lambda e: self.reset_search())
        
        tk.Label(self.controls_frame, text="Cost / Heuristic (Từ UCS):", bg="white", font=("Arial", 10)).grid(row=1, column=0, sticky="w")
        self.eval_var = tk.StringVar()
        self.eval_cb = ttk.Combobox(self.controls_frame, textvariable=self.eval_var, state="readonly", width=40)
        self.eval_cb['values'] = ("Khoảng cách Manhattan", "Số ô sai vị trí", "Giá trị ô swap")
        self.eval_cb.current(0)
        self.eval_cb.grid(row=1, column=1, columnspan=2, pady=5)
        self.eval_cb.bind("<<ComboboxSelected>>", lambda e: self.reset_search())

        tk.Label(self.controls_frame, text="MAX_RESTART (Restart HC):", bg="white", font=("Arial", 10)).grid(row=2, column=0, sticky="w")
        self.max_restart_var = tk.StringVar(value="3")
        self.max_restart_sb = ttk.Spinbox(self.controls_frame, from_=1, to=100, textvariable=self.max_restart_var, width=10, state="disabled")
        self.max_restart_sb.grid(row=2, column=1, sticky="w", pady=5)
        self.max_restart_sb.bind("<KeyRelease>", lambda e: self.reset_search())
        self.max_restart_sb.bind("<<Increment>>", lambda e: self.reset_search())
        self.max_restart_sb.bind("<<Decrement>>", lambda e: self.reset_search())
        
        tk.Label(self.controls_frame, text="K (Local Beam Search):", bg="white", font=("Arial", 10)).grid(row=3, column=0, sticky="w")
        self.k_var = tk.StringVar(value="3")
        self.k_sb = ttk.Spinbox(self.controls_frame, from_=1, to=100, textvariable=self.k_var, width=10, state="disabled")
        self.k_sb.grid(row=3, column=1, sticky="w", pady=5)
        self.k_sb.bind("<KeyRelease>", lambda e: self.reset_search())
        self.k_sb.bind("<<Increment>>", lambda e: self.reset_search())
        self.k_sb.bind("<<Decrement>>", lambda e: self.reset_search())

        tk.Label(self.controls_frame, text="SA T₀:", bg="white", font=("Arial", 10)).grid(row=4, column=0, sticky="w")
        self.sa_initial_temp_var = tk.StringVar(value="100")
        self.sa_initial_temp_sb = ttk.Spinbox(self.controls_frame, from_=1, to=1000, textvariable=self.sa_initial_temp_var, width=8, state="disabled")
        self.sa_initial_temp_sb.grid(row=4, column=1, sticky="w", pady=2)
        self.sa_initial_temp_sb.bind("<KeyRelease>", lambda e: self.reset_search())
        
        tk.Label(self.controls_frame, text="  SA α:", bg="white", font=("Arial", 10)).grid(row=4, column=2, sticky="w")
        self.sa_cooling_rate_var = tk.StringVar(value="0.95")
        self.sa_cooling_rate_sb = ttk.Spinbox(self.controls_frame, from_=0.01, to=0.99, increment=0.01, textvariable=self.sa_cooling_rate_var, width=7, state="disabled")
        self.sa_cooling_rate_sb.grid(row=4, column=3, sticky="w", pady=2)
        self.sa_cooling_rate_sb.bind("<KeyRelease>", lambda e: self.reset_search())

        tk.Label(self.controls_frame, text="SA T_min:", bg="white", font=("Arial", 10)).grid(row=5, column=0, sticky="w")
        self.sa_min_temp_var = tk.StringVar(value="0.1")
        self.sa_min_temp_sb = ttk.Spinbox(self.controls_frame, from_=0.001, to=10, increment=0.1, textvariable=self.sa_min_temp_var, width=8, state="disabled")
        self.sa_min_temp_sb.grid(row=5, column=1, sticky="w", pady=2)
        self.sa_min_temp_sb.bind("<KeyRelease>", lambda e: self.reset_search())

        tk.Label(self.controls_frame, text="SA Max Restart:", bg="white", font=("Arial", 10)).grid(row=5, column=2, sticky="w")
        self.sa_max_restart_var = tk.StringVar(value="3")
        self.sa_max_restart_sb = ttk.Spinbox(self.controls_frame, from_=1, to=50, textvariable=self.sa_max_restart_var, width=8, state="disabled")
        self.sa_max_restart_sb.grid(row=5, column=3, sticky="w", pady=2)
        self.sa_max_restart_sb.bind("<KeyRelease>", lambda e: self.reset_search())

        tk.Label(self.controls_frame, text="Số belief states:", bg="white", font=("Arial", 10)).grid(row=6, column=0, sticky="w")
        self.belief_count_var = tk.StringVar(value="2")
        self.belief_count_sb = ttk.Spinbox(self.controls_frame, from_=2, to=10, textvariable=self.belief_count_var, width=8, state="disabled")
        self.belief_count_sb.grid(row=6, column=1, sticky="w", pady=2)

        tk.Label(self.controls_frame, text="Số goal states:", bg="white", font=("Arial", 10)).grid(row=6, column=2, sticky="w")
        self.belief_goal_count_var = tk.StringVar(value="1")
        self.belief_goal_count_sb = ttk.Spinbox(self.controls_frame, from_=1, to=5, textvariable=self.belief_goal_count_var, width=7, state="disabled")
        self.belief_goal_count_sb.grid(row=6, column=3, sticky="w", pady=2)

        self.belief_gen_btn = tk.Button(self.controls_frame, text="Sinh ngẫu nhiên", bg="#9b59b6", fg="white", font=("Arial", 9, "bold"), state="disabled", command=self.generate_belief_states)
        self.belief_gen_btn.grid(row=7, column=0, columnspan=2, pady=3, padx=5)

        self.belief_state_frame = tk.Frame(self.controls_frame, bg="white")
        self.belief_state_frame.grid(row=8, column=0, columnspan=4, pady=2, sticky="ew")
        self.belief_state_label = tk.Label(self.belief_state_frame, text="", bg="white", font=("Arial", 8))
        self.belief_state_label.pack()

        self.belief_goal_frame = tk.Frame(self.controls_frame, bg="white")
        self.belief_goal_frame.grid(row=9, column=0, columnspan=4, pady=2, sticky="ew")
        self.belief_goal_label = tk.Label(self.belief_goal_frame, text="", bg="white", font=("Arial", 8))
        self.belief_goal_label.pack()

        tk.Label(self.controls_frame, text="Trạng thái đầu:", bg="white").grid(row=10, column=0, sticky="w")
        self.start_entry = tk.Entry(self.controls_frame, width=20, font=("Arial", 12))
        self.start_entry.insert(0, "123406758")
        self.start_entry.grid(row=10, column=1, pady=5)
        
        tk.Label(self.controls_frame, text="Trạng thái đích:", bg="white").grid(row=11, column=0, sticky="w")
        self.goal_entry = tk.Entry(self.controls_frame, width=20, font=("Arial", 12))
        self.goal_entry.insert(0, "123456780")
        self.goal_entry.grid(row=11, column=1, pady=5)
        
        self.btn_reset = tk.Button(self.controls_frame, text="Khởi tạo lại", bg="#3498db", fg="white", font=("Arial", 10, "bold"), command=self.reset_search)
        self.btn_reset.grid(row=12, column=0, pady=10, padx=5)
        self.btn_step = tk.Button(self.controls_frame, text="Chạy 1 Bước", bg="#f39c12", fg="white", font=("Arial", 10, "bold"), command=self.step_search)
        self.btn_step.grid(row=12, column=1, pady=10, padx=5)
        self.btn_auto = tk.Button(self.controls_frame, text="Chạy Tự Động", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), command=self.toggle_auto)
        self.btn_auto.grid(row=12, column=2, pady=10, padx=5)

        self.info_frame = tk.LabelFrame(self.left_frame, text="Thống kê", font=("Arial", 12, "bold"), bg="#d1d8e0", padx=15, pady=15)
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.lbl_manhattan = tk.Label(self.info_frame, text="Chi phí / Heuristic tới Đích: 0", bg="#d1d8e0", font=("Arial", 11, "bold"), fg="#c0392b")
        self.lbl_manhattan.pack(anchor="w", pady=2)
        self.lbl_depth = tk.Label(self.info_frame, text="Độ sâu hiện tại (Depth): 0", bg="#d1d8e0", font=("Arial", 11))
        self.lbl_depth.pack(anchor="w", pady=2)
        self.lbl_popped = tk.Label(self.info_frame, text="Số Node đã duyệt (Pop): 0", bg="#d1d8e0", font=("Arial", 11))
        self.lbl_popped.pack(anchor="w", pady=2)
        self.lbl_status = tk.Label(self.info_frame, text="Trạng thái: Đang chờ chạy", bg="#d1d8e0", font=("Arial", 11, "bold"), fg="#2980b9")
        self.lbl_status.pack(anchor="w", pady=10)

        self.right_frame = tk.Frame(self.root, bg="white", bd=2, relief="groove")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.right_title = tk.Label(self.right_frame, text="MÔ PHỎNG", font=("Arial", 14, "bold"), bg="#2c3e50", fg="white", pady=10)
        self.right_title.pack(fill=tk.X)
        self.right_header = tk.Frame(self.right_frame, bg="#bdc3c7")
        self.right_header.pack(fill=tk.X)
        self.right_header.columnconfigure(0, weight=1, minsize=100)
        self.right_header.columnconfigure(1, weight=5, minsize=450)
        self.right_header.columnconfigure(2, weight=3, minsize=300)
        tk.Label(self.right_header, text="Current Node", font=("Arial", 11, "bold"), bg="#bdc3c7", pady=5).grid(row=0, column=0, sticky="w", padx=10)
        tk.Label(self.right_header, text="Frontier", font=("Arial", 11, "bold"), bg="#bdc3c7", pady=5).grid(row=0, column=1, sticky="w", padx=10)
        tk.Label(self.right_header, text="Reached", font=("Arial", 11, "bold"), bg="#bdc3c7", pady=5).grid(row=0, column=2, sticky="w", padx=10)
        
        self.log_scroll = ScrollableFrame(self.right_frame)
        self.log_scroll.pack(fill=tk.BOTH, expand=True)
        self.sa_frame = tk.Frame(self.right_frame, bg="white")

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
            elif char == '-':
                canvas.create_rectangle(x0, y0, x1, y1, fill="#ecf0f1", outline="#95a5a6", width=2, dash=(4, 4))
                canvas.create_text(x0+22, y0+22, text="?", font=("Arial", 16, "bold"), fill="#7f8c8d")
            else:
                canvas.create_rectangle(x0, y0, x1, y1, fill="#ecf0f1", outline="#bdc3c7", width=2)
                canvas.create_text(x0+22, y0+22, text=char, font=("Arial", 18, "bold"), fill="#2c3e50")

    def create_mini_board_canvas(self, parent, state_str, title="", is_goal=False):
        canvas = tk.Canvas(parent, width=54, height=75 if title else 58, bg="white", highlightthickness=0)
        y_offset = 2
        if title:
            color = "#27ae60" if is_goal else "#2980b9"
            canvas.create_text(27, 15, text=title, font=("Arial", 9, "bold"), fill=color, justify="center")
            y_offset = 25
            
        for i, char in enumerate(state_str):
            r, c = divmod(i, 3)
            x0 = c * 18; y0 = y_offset + r * 18
            x1 = x0 + 18; y1 = y0 + 18
            
            if char == '0':
                canvas.create_rectangle(x0, y0, x1, y1, fill="#34495e", outline="#2c3e50")
            elif char == '-':
                canvas.create_rectangle(x0, y0, x1, y1, fill="#ecf0f1", outline="#95a5a6", dash=(2, 2))
                canvas.create_text(x0+9, y0+9, text="?", font=("Arial", 8, "bold"), fill="#7f8c8d")
            else:
                canvas.create_rectangle(x0, y0, x1, y1, fill="#ecf0f1", outline="#bdc3c7")
                canvas.create_text(x0+9, y0+9, text=char, font=("Arial", 8, "bold"), fill="#2c3e50")
        return canvas

    def build_sa_ui(self):
        for w in self.sa_frame.winfo_children(): w.destroy()
        top = tk.Frame(self.sa_frame, bg="white")
        top.pack(fill=tk.X, pady=10)

        curr_f = tk.LabelFrame(top, text="Current State", font=("Arial", 10, "bold"), bg="white")
        curr_f.pack(side=tk.LEFT, padx=10)
        self.sa_curr_canvas = tk.Canvas(curr_f, width=140, height=140, bg="#34495e", highlightthickness=0)
        self.sa_curr_canvas.pack(pady=5)
        self.sa_curr_cost_label = tk.Label(curr_f, text="Cost: -", bg="white", font=("Arial", 10, "bold"), fg="#2980b9")
        self.sa_curr_cost_label.pack()

        arrow_f = tk.Frame(top, bg="white")
        arrow_f.pack(side=tk.LEFT, padx=5)
        tk.Label(arrow_f, text="  ➜  ", font=("Arial", 28, "bold"), bg="white", fg="#7f8c8d").pack(expand=True)

        cand_f = tk.LabelFrame(top, text="Candidate", font=("Arial", 10, "bold"), bg="white")
        cand_f.pack(side=tk.LEFT, padx=10)
        self.sa_cand_canvas = tk.Canvas(cand_f, width=140, height=140, bg="#34495e", highlightthickness=0)
        self.sa_cand_canvas.pack(pady=5)
        self.sa_cand_cost_label = tk.Label(cand_f, text="Cost: -", bg="white", font=("Arial", 10, "bold"), fg="#e67e22")
        self.sa_cand_cost_label.pack()
        self.sa_cand_action_label = tk.Label(cand_f, text="", bg="white", font=("Arial", 9))
        self.sa_cand_action_label.pack()

        arrow2_f = tk.Frame(top, bg="white")
        arrow2_f.pack(side=tk.LEFT, padx=5)
        tk.Label(arrow2_f, text="  ➜  ", font=("Arial", 28, "bold"), bg="white", fg="#7f8c8d").pack(expand=True)

        best_f = tk.LabelFrame(top, text="Best Found", font=("Arial", 10, "bold"), bg="white")
        best_f.pack(side=tk.LEFT, padx=10)
        self.sa_best_canvas = tk.Canvas(best_f, width=140, height=140, bg="#34495e", highlightthickness=0)
        self.sa_best_canvas.pack(pady=5)
        self.sa_best_cost_label = tk.Label(best_f, text="Cost: -", bg="white", font=("Arial", 10, "bold"), fg="#27ae60")
        self.sa_best_cost_label.pack()

        mid = tk.Frame(self.sa_frame, bg="white")
        mid.pack(fill=tk.X, pady=8, padx=20)
        gauge_f = tk.LabelFrame(mid, text="Temperature", font=("Arial", 10, "bold"), bg="white")
        gauge_f.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.sa_gauge_canvas = tk.Canvas(gauge_f, width=400, height=40, bg="white", highlightthickness=0)
        self.sa_gauge_canvas.pack(pady=5, padx=10)
        self.sa_temp_label = tk.Label(gauge_f, text="T = 100.0°C", bg="white", font=("Arial", 10, "bold"))
        self.sa_temp_label.pack()

        info_f = tk.LabelFrame(mid, text="Decision", font=("Arial", 10, "bold"), bg="white")
        info_f.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        self.sa_delta_label = tk.Label(info_f, text="ΔE = 0", bg="white", font=("Arial", 10))
        self.sa_delta_label.pack(anchor="w", padx=10)
        self.sa_prob_label = tk.Label(info_f, text="Accept P = 0.00", bg="white", font=("Arial", 10))
        self.sa_prob_label.pack(anchor="w", padx=10)
        self.sa_accepted_label = tk.Label(info_f, text="Accepted: -", bg="white", font=("Arial", 10, "bold"))
        self.sa_accepted_label.pack(anchor="w", padx=10)

        chart_f = tk.LabelFrame(self.sa_frame, text="Cost over Iterations", font=("Arial", 10, "bold"), bg="white")
        chart_f.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        self.sa_chart_canvas = tk.Canvas(chart_f, width=700, height=200, bg="white", highlightthickness=1, highlightbackground="#bdc3c7")
        self.sa_chart_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        stats_f = tk.Frame(self.sa_frame, bg="white")
        stats_f.pack(fill=tk.X, pady=5, padx=20)
        self.sa_iter_label = tk.Label(stats_f, text="Iter: 0", bg="white", font=("Arial", 10), fg="#2980b9")
        self.sa_iter_label.pack(side=tk.LEFT, padx=15)
        self.sa_best_cost_stat = tk.Label(stats_f, text="Best: -", bg="white", font=("Arial", 10), fg="#27ae60")
        self.sa_best_cost_stat.pack(side=tk.LEFT, padx=15)
        self.sa_temp_stat = tk.Label(stats_f, text="Temp: 100.0°C", bg="white", font=("Arial", 10))
        self.sa_temp_stat.pack(side=tk.LEFT, padx=15)
        self.sa_restart_stat = tk.Label(stats_f, text="Restart: 0/3", bg="white", font=("Arial", 10))
        self.sa_restart_stat.pack(side=tk.LEFT, padx=15)

    def update_sa_display(self, data):
        if not self.is_sa_mode: return
        curr = data.get("current")
        candidate = data.get("candidate")
        next_node = data.get("next")
        best = data.get("best")
        accepted = data.get("accepted", False)

        if curr:
            self.draw_state_to_canvas(self.sa_curr_canvas, curr.state)
            self.sa_curr_cost_label.config(text=f"Cost: {curr.cost}")
        if candidate:
            self.draw_state_to_canvas(self.sa_cand_canvas, candidate.state)
            self.sa_cand_cost_label.config(text=f"Cost: {candidate.cost}")
            self.sa_cand_action_label.config(text=f"Move: {data.get('action', '')}")
        if best:
            self.draw_state_to_canvas(self.sa_best_canvas, best.state)
            self.sa_best_cost_label.config(text=f"Cost: {best.cost}")
            self.sa_best_cost_stat.config(text=f"Best: {best.cost}")

        T = data.get("temperature", 0)
        initial_temp = data.get("initial_temp", 100)
        self.sa_temp_label.config(text=f"T = {T:.1f}°C")
        self.sa_temp_stat.config(text=f"Temp: {T:.1f}°C")

        gauge_w = 380
        fraction = min(1.0, T / max(initial_temp, 0.01))
        self.sa_gauge_canvas.delete("all")
        self.sa_gauge_canvas.create_rectangle(10, 10, 10 + gauge_w, 30, fill="#ecf0f1", outline="#bdc3c7", width=2)
        if T > 0:
            color = "#e74c3c" if fraction > 0.5 else ("#f39c12" if fraction > 0.2 else "#2ecc71")
            self.sa_gauge_canvas.create_rectangle(10, 10, 10 + int(gauge_w * fraction), 30, fill=color, outline="")
        self.sa_gauge_canvas.create_text(10 + gauge_w // 2, 20, text=f"{T:.1f}°C / {initial_temp:.0f}°C", font=("Arial", 9, "bold"), fill="white")

        self.sa_delta_label.config(text=f"ΔE = {data.get('delta', 0):+d}")
        self.sa_prob_label.config(text=f"Accept P = {data.get('accept_prob', 0):.4f}")
        if accepted:
            self.sa_accepted_label.config(text="Decision: ✅ Accepted", fg="#27ae60")
        else:
            self.sa_accepted_label.config(text="Decision: ❌ Rejected", fg="#e74c3c")

        self.draw_sa_chart(data.get("cost_history", []))
        self.sa_iter_label.config(text=f"Iter: {data.get('iteration', 0)}")
        self.sa_restart_stat.config(text=f"Restart: {data.get('restart_count', 0)}/{data.get('max_restart', 3)}")

    def draw_sa_chart(self, cost_history):
        c = self.sa_chart_canvas
        c.delete("all")
        if len(cost_history) < 2: return
        cw = max(c.winfo_width() - 40, 600)
        ch = max(c.winfo_height() - 40, 160)
        margin = 30
        max_cost = max(cost_history)
        min_cost = min(cost_history)
        cost_range = max_cost - min_cost if max_cost != min_cost else 1
        n = len(cost_history)

        for i in range(5):
            y = margin + (ch - margin) * i // 4
            c.create_line(margin, y, margin + cw - margin, y, fill="#ecf0f1", width=1)
            val = max_cost - (cost_range * i // 4)
            c.create_text(margin - 5, y, text=str(val), anchor="e", font=("Arial", 8), fill="#7f8c8d")

        points = []
        for i, cost in enumerate(cost_history):
            x = margin + (cw - margin) * i // max(n - 1, 1)
            y = margin + (ch - margin) - int((cost - min_cost) / cost_range * (ch - margin - 10))
            points.extend([x, y])

        if len(points) >= 4:
            c.create_line(points, fill="#e74c3c", width=2, smooth=True)
            c.create_oval(points[-2] - 4, points[-1] - 4, points[-2] + 4, points[-1] + 4, fill="#c0392b", outline="")
        c.create_text(margin + (cw - margin) // 2, ch + 5, text="Iteration", font=("Arial", 9), fill="#7f8c8d")
        c.create_text(10, margin + (ch - margin) // 2, text="Cost", font=("Arial", 9), fill="#7f8c8d", angle=90)

    def destroy_sa_ui(self):
        self.sa_frame.pack_forget()
        self.right_title.config(text="MÔ PHỎNG")
        self.right_header.pack(fill=tk.X)
        self.log_scroll.pack(fill=tk.BOTH, expand=True)

    def generate_belief_states(self):
        try:
            n_states = int(self.belief_count_var.get())
            n_goals = int(self.belief_goal_count_var.get())
        except ValueError: return
        self.belief_generated_states = generate_random_states(n_states, mode="belief")
        self.belief_generated_goals = generate_random_states(n_goals, mode="goal")

        for w in self.belief_state_frame.winfo_children():
            if w != self.belief_state_label: w.destroy()
        for w in self.belief_goal_frame.winfo_children():
            if w != self.belief_goal_label: w.destroy()

        states_row = tk.Frame(self.belief_state_frame, bg="white")
        states_row.pack()
        tk.Label(states_row, text="Belief: ", bg="white", font=("Arial", 8, "bold")).pack(side=tk.LEFT)
        for s in self.belief_generated_states:
            mb = self.create_mini_board_canvas(states_row, s)
            mb.pack(side=tk.LEFT, padx=2)

        goals_row = tk.Frame(self.belief_goal_frame, bg="white")
        goals_row.pack()
        tk.Label(goals_row, text="Goals:  ", bg="white", font=("Arial", 8, "bold")).pack(side=tk.LEFT)
        for g in self.belief_generated_goals:
            mb = self.create_mini_board_canvas(goals_row, g)
            mb.pack(side=tk.LEFT, padx=2)
        self.reset_search()

    def build_belief_ui(self):
        for w in self.sa_frame.winfo_children(): w.destroy()
        status_f = tk.LabelFrame(self.sa_frame, text="Belief State Status", font=("Arial", 12, "bold"), bg="white")
        status_f.pack(fill=tk.X, pady=5, padx=10)
        self.belief_curr_frame = tk.Frame(status_f, bg="white")
        self.belief_curr_frame.pack(pady=8)
        self.belief_canvases = []
        self.belief_status_label = tk.Label(status_f, text="Solved: 0/0  |  Goals: 0", bg="white", font=("Arial", 10, "bold"))
        self.belief_status_label.pack(pady=2)

        info_f = tk.Frame(self.sa_frame, bg="white")
        info_f.pack(fill=tk.X, pady=2, padx=10)
        self.belief_depth_label = tk.Label(info_f, text="Depth: 0", bg="white", font=("Arial", 10), fg="#2980b9")
        self.belief_depth_label.pack(side=tk.LEFT, padx=15)
        self.belief_front_count = tk.Label(info_f, text="Frontier: 0", bg="white", font=("Arial", 10))
        self.belief_front_count.pack(side=tk.LEFT, padx=15)
        self.belief_explored_count = tk.Label(info_f, text="Explored: 0", bg="white", font=("Arial", 10))
        self.belief_explored_count.pack(side=tk.LEFT, padx=15)

        queue_f = tk.LabelFrame(self.sa_frame, text="BFS Queue (Frontier)", font=("Arial", 12, "bold"), bg="white")
        queue_f.pack(fill=tk.X, pady=5, padx=10)
        self.belief_queue_canvas = tk.Canvas(queue_f, bg="white", highlightthickness=0, height=100)
        self.belief_queue_scroll = ttk.Scrollbar(queue_f, orient="horizontal", command=self.belief_queue_canvas.xview)
        self.belief_queue_inner = tk.Frame(self.belief_queue_canvas, bg="white")
        self.belief_queue_inner.bind("<Configure>", lambda e: self.belief_queue_canvas.configure(scrollregion=self.belief_queue_canvas.bbox("all")))
        self.belief_queue_canvas.create_window((0, 0), window=self.belief_queue_inner, anchor="nw")
        self.belief_queue_canvas.pack(fill=tk.X, expand=True)
        self.belief_queue_scroll.pack(fill=tk.X)

    def update_belief_display(self, data):
        if not self.is_belief_mode: return
        states = data.get("belief", ())
        solved_list = data.get("solved", [])
        expanding_idx = data.get("expanding", -1)
        curr_state = data.get("expanding_state", "")
        frontier_list = data.get("frontier_logs", [])
        explored_sets = data.get("explored_sets", [])
        all_reached = data.get("all_reached", set())
        queues = data.get("queues", [])

        for c in self.belief_canvases: c.destroy()
        self.belief_canvases = []

        for i, s in enumerate(states):
            solved = i < len(solved_list) and solved_list[i]
            title = f"#{i+1} {'✓' if solved else '○'}"
            mb = self.create_mini_board_canvas(self.belief_curr_frame, s, title=title)
            mb.pack(side=tk.LEFT, padx=3)
            self.belief_canvases.append(mb)

        solved_count = sum(solved_list) if solved_list else 0
        total = len(states)
        goal_count = len(self.belief_generated_goals or [])
        self.belief_depth_label.config(text=f"Depth: {data.get('depth', 0)}")
        total_explored = sum(len(es) for es in explored_sets) if explored_sets else len(all_reached or set())
        self.belief_explored_count.config(text=f"Explored: {total_explored}")
        self.belief_front_count.config(text=f"Frontier: {sum(len(q) for q in queues)}")

        restart_reason = data.get("restart_reason", "")
        restart_flag = data.get("restart_flag", False)
        target_goal = data.get("target_goal", None)

        if frontier_list:
            sep_f = tk.Frame(self.log_scroll.scrollable_inner_frame, bg="#bdc3c7", height=2)
            sep_f.pack(fill=tk.X, pady=4, padx=5)
            step_lbl = tk.Frame(self.log_scroll.scrollable_inner_frame, bg="#f8f9fa")
            step_lbl.pack(fill=tk.X, pady=0, padx=5)
            tk.Label(step_lbl, text=f"───── Bước {self.belief_step_count+1} | S{expanding_idx+1} ─────", bg="#f8f9fa", fg="#7f8c8d", font=("Arial", 8, "bold")).pack()

            if restart_flag and restart_reason:
                restart_f = tk.Frame(self.log_scroll.scrollable_inner_frame, bg="#fff3cd", highlightbackground="#ffc107", highlightthickness=1)
                restart_f.pack(fill=tk.X, pady=2, padx=5)
                tk.Label(restart_f, text=f"🔄 {restart_reason}", bg="#fff3cd", fg="#856404", font=("Arial", 9, "bold"), wraplength=400).pack(padx=10, pady=4)

            for item in frontier_list:
                self.add_belief_log_row(
                    item.get("belief_idx", 0), item.get("from_state", curr_state),
                    item.get("action", ""), item.get("state", ""), item.get("is_goal", False),
                    solved_count, total
                )
            self.belief_step_count += 1

        target_text = f"  |  Target: {target_goal}" if target_goal else f"  |  Goals: {goal_count}"
        self.belief_status_label.config(text=f"Solved: {solved_count}/{total}{target_text}", fg="#27ae60" if solved_count == total else "#2980b9")

        for w in self.belief_queue_inner.winfo_children(): w.destroy()
        if queues:
            for qi, q in enumerate(queues):
                q_row = tk.Frame(self.belief_queue_inner, bg="white")
                q_row.pack(side=tk.LEFT, padx=10, pady=5)
                status = "✓" if (qi < len(solved_list) and solved_list[qi]) else ""
                tk.Label(q_row, text=f"S{qi+1}{status}:", bg="white", font=("Arial", 9, "bold"), fg="#27ae60" if status else "#2980b9").pack(anchor="w")
                items_f = tk.Frame(q_row, bg="white")
                items_f.pack(fill=tk.X)

                if qi == expanding_idx and curr_state:
                    pop_f = tk.Frame(items_f, bg="white", highlightbackground="#e74c3c", highlightthickness=2)
                    pop_f.pack(side=tk.LEFT, padx=2)
                    mb = self.create_mini_board_canvas(pop_f, curr_state, title="POP")
                    mb.pack(padx=2, pady=2)
                    if items_f.winfo_children():
                        tk.Label(items_f, text="↓", bg="white", fg="#7f8c8d", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=2)

                if q:
                    for qs, qd, _ in q:
                        mb = self.create_mini_board_canvas(items_f, qs, title=f"d={qd}")
                        mb.pack(side=tk.LEFT, padx=1)
                else:
                    tk.Label(items_f, text="(trống)", bg="white", font=("Arial", 8), fg="#95a5a6").pack(side=tk.LEFT, padx=3)
            self.belief_queue_canvas.xview_moveto(0)

    def add_log_row(self, curr_node_data, frontier_list, reached_set):
        row_frame = tk.Frame(self.log_scroll.scrollable_inner_frame, bg="white", highlightbackground="#ecf0f1", highlightthickness=1)
        row_frame.pack(fill=tk.X, pady=3, padx=5)
        row_frame.columnconfigure(0, weight=1, minsize=100)
        row_frame.columnconfigure(1, weight=5, minsize=450)
        row_frame.columnconfigure(2, weight=3, minsize=300)

        f_node = tk.Frame(row_frame, bg="white")
        f_node.grid(row=0, column=0, sticky="nw", padx=10, pady=5)
        if isinstance(curr_node_data, list):
            for node in curr_node_data:
                mb = self.create_mini_board_canvas(f_node, node.state, title=f"Node {node.name}\ncost: {node.h}")
                mb.pack(pady=4)
        elif curr_node_data:
            mb = self.create_mini_board_canvas(f_node, curr_node_data.state, title=f"Node {curr_node_data.name}")
            mb.pack(pady=4)

        f_front = tk.Frame(row_frame, bg="white")
        f_front.grid(row=0, column=1, sticky="nw", padx=10, pady=5)
        if frontier_list == "Cutoff":
            tk.Label(f_front, text="CUTOFF (Vi phạm ràng buộc CSP hoặc vượt mốc)", bg="white", fg="#e74c3c", font=("Arial", 11, "bold")).pack(anchor="w")
        elif frontier_list == "Stuck":
            tk.Label(f_front, text="KẸT (Đạt cực đại/tiểu cục bộ) ➔ Dừng lại hoặc Restart...", bg="white", fg="#d35400", font=("Arial", 11, "bold")).pack(anchor="w")
        elif not frontier_list:
            tk.Label(f_front, text="(Không được thêm vào / Thoát vòng lặp)", bg="white", fg="gray", font=("Arial", 10, "italic")).pack(anchor="w")
        else:
            for item in frontier_list:
                item_frame = tk.Frame(f_front, bg="white")
                item_frame.pack(anchor="w", pady=4)
                tk.Label(item_frame, text="{ ", bg="white", font=("Courier New", 14, "bold"), fg="#34495e").pack(side="left")
                mb = self.create_mini_board_canvas(item_frame, item['state'])
                mb.pack(side="left", padx=2)
                act_char = item['action'][0] if item['action'] else ""
                info_text = f" , {item['parent_name']} , {act_char} , {item['cost']} }} ➔ Node {item['name']}"
                is_loai = "Loại" in str(item['cost'])
                if is_loai or "Lùi" in str(item['cost']):
                    color = "#e74c3c"
                elif item['is_goal'] or "Hợp lệ" in str(item['cost']):
                    color = "#27ae60"
                else:
                    color = "#2c3e50"
                if item['is_goal']: info_text += " ★"
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

    def add_belief_log_row(self, belief_idx, curr_state, action, new_state, is_goal, solved, total):
        row_frame = tk.Frame(self.log_scroll.scrollable_inner_frame, bg="white", highlightbackground="#ecf0f1", highlightthickness=1)
        row_frame.pack(fill=tk.X, pady=3, padx=5)
        row_frame.columnconfigure(0, weight=1, minsize=80)
        row_frame.columnconfigure(1, weight=4, minsize=350)
        row_frame.columnconfigure(2, weight=2, minsize=200)

        f_idx = tk.Frame(row_frame, bg="white")
        f_idx.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        tk.Label(f_idx, text=f"S{belief_idx+1}", font=("Arial", 10, "bold"), fg="#2980b9", bg="white").pack(anchor="w")
        mb = self.create_mini_board_canvas(f_idx, curr_state)
        mb.pack(pady=2)

        f_front = tk.Frame(row_frame, bg="white")
        f_front.grid(row=0, column=1, sticky="nw", padx=5, pady=5)
        item_frame = tk.Frame(f_front, bg="white")
        item_frame.pack(anchor="w", pady=4)
        tk.Label(item_frame, text=f"{action}  →  ", bg="white", font=("Arial", 10, "bold"), fg="#34495e").pack(side=tk.LEFT)
        mb2 = self.create_mini_board_canvas(item_frame, new_state)
        mb2.pack(side=tk.LEFT, padx=2)
        if is_goal: tk.Label(item_frame, text="★ GOAL", bg="white", fg="#27ae60", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)

        f_status = tk.Frame(row_frame, bg="white")
        f_status.grid(row=0, column=2, sticky="nw", padx=5, pady=5)
        color = "#27ae60" if solved >= total else "#e67e22"
        tk.Label(f_status, text=f"Solved: {solved}/{total}", bg="white", font=("Arial", 10, "bold"), fg=color).pack(anchor="w")
        if solved >= total: tk.Label(f_status, text="🎉 ALL SOLVED!", bg="white", fg="#27ae60", font=("Arial", 11, "bold")).pack(anchor="w")

        self.root.update_idletasks()
        self.log_scroll.canvas.yview_moveto(1)

    def add_and_or_log_row(self, data):
        phase = data.get("phase")
        depth = data.get("depth", 0)
        row_frame = tk.Frame(self.log_scroll.scrollable_inner_frame, bg="white", highlightbackground="#ecf0f1", highlightthickness=1)
        row_frame.pack(fill=tk.X, pady=3, padx=5)
        
        if phase == "OR":
            tk.Label(row_frame, text=f"[Độ sâu {depth}] Pha OR - Tại trạng thái:", font=("Arial", 10, "bold"), bg="white", fg="#2980b9").pack(anchor="w", padx=5)
            mb = self.create_mini_board_canvas(row_frame, data["state"])
            mb.pack(anchor="w", padx=20, pady=2)
        elif phase == "ACTION":
            tk.Label(row_frame, text=f"[Độ sâu {depth}] OR Quyết định: Thử hành động '{data['action']}'", font=("Arial", 10, "bold"), bg="white", fg="#e67e22").pack(anchor="w", padx=5)
            states_frame = tk.Frame(row_frame, bg="white")
            states_frame.pack(anchor="w", padx=20, pady=2)
            tk.Label(states_frame, text="↳ Môi trường trượt ra các rủi ro: ", bg="white", font=("Arial", 9)).pack(side=tk.LEFT)
            for s in data["results"]:
                mb = self.create_mini_board_canvas(states_frame, s)
                mb.pack(side=tk.LEFT, padx=3)
        elif phase == "AND":
            tk.Label(row_frame, text=f"[Độ sâu {depth}] Pha AND - Yêu cầu giải quyết TẤT CẢ các rủi ro trên!", font=("Arial", 10, "bold"), bg="white", fg="#8e44ad").pack(anchor="w", padx=5)
            
        self.root.update_idletasks()
        self.log_scroll.canvas.yview_moveto(1)

    def show_contingency_plan(self, plan):
        formatted_plan = pprint.pformat(plan, indent=4)
        top = tk.Toplevel(self.root)
        top.title("Kế hoạch Dự Phòng (Contingency Plan)")
        top.geometry("600x500")
        top.configure(bg="white")
        tk.Label(top, text="LỜI GIẢI AND-OR GRAPH SEARCH", font=("Arial", 14, "bold"), bg="white", fg="#2c3e50").pack(pady=10)
        tk.Label(top, text="Dưới đây là cây quyết định bảo đảm bạn đến đích dù bị trượt.", bg="white").pack(anchor="w", padx=10)
        txt = tk.Text(top, font=("Courier New", 11), bg="#f8f9fa", fg="#2c3e50", wrap="word")
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        txt.insert(tk.END, formatted_plan)
        txt.config(state=tk.DISABLED)

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
        algo_idx = self.algo_cb.current()
        algo = self.algo_var.get()
        eval_type = self.eval_var.get()
        is_sa = "Simulated Annealing" in algo
        is_belief = "Belief State BFS" in algo

        if self.is_sa_mode and not is_sa:
            self.destroy_sa_ui()
            self.is_sa_mode = False

        if self.is_belief_mode and not is_belief:
            self.sa_frame.pack_forget()
            self.right_title.config(text="MÔ PHỎNG")
            self.right_header.pack(fill=tk.X)
            self.is_belief_mode = False

        if is_sa and not self.is_sa_mode:
            if self.is_belief_mode:
                self.sa_frame.pack_forget()
                self.is_belief_mode = False
            self.right_header.pack_forget()
            self.log_scroll.pack_forget()
            self.right_title.config(text="MÔ PHỎNG - SIMULATED ANNEALING")
            self.is_sa_mode = True
            self.sa_frame.pack(fill=tk.BOTH, expand=True)
            self.build_sa_ui()
        elif is_sa and self.is_sa_mode:
            self.build_sa_ui()

        if is_belief and not self.is_belief_mode:
            if self.is_sa_mode:
                self.sa_frame.pack_forget()
                self.is_sa_mode = False
            self.right_header.pack_forget()
            self.right_title.config(text="MÔ PHỎNG - BELIEF STATE BFS")
            self.is_belief_mode = True
            self.belief_step_count = 0
            self.sa_frame.pack(fill=tk.X)
            self.log_scroll.pack(fill=tk.BOTH, expand=True)
            self.log_scroll.clear()
            self.build_belief_ui()
        elif is_belief and self.is_belief_mode:
            self.belief_step_count = 0
            self.log_scroll.clear()
            self.build_belief_ui()

        belief_ctrls = [self.belief_count_sb, self.belief_goal_count_sb, self.belief_gen_btn]
        if is_belief:
            for ctrl in belief_ctrls: ctrl.config(state="normal")
            self.start_entry.config(state="disabled")
            self.goal_entry.config(state="disabled")
        else:
            for ctrl in belief_ctrls: ctrl.config(state="disabled")
            self.start_entry.config(state="normal")
            self.goal_entry.config(state="normal")

        start_state = self.start_entry.get().strip()
        goal_state = self.goal_entry.get().strip()
        
        if not is_belief and "CSP Backtracking" not in algo:
            if len(start_state) != 9 or len(goal_state) != 9:
                messagebox.showerror("Lỗi", "Trạng thái phải là chuỗi đúng 9 số từ 0-8!")
                return
            
        self.node_counter = 0
        self.total_popped = 0
        self.is_solved = False
        
        if not is_belief:
            start_to_draw = "---------" if "CSP Backtracking" in algo else start_state
            self.draw_state_to_canvas(self.curr_board_canvas, start_to_draw)
            self.draw_state_to_canvas(self.goal_board_canvas, goal_state)
        
        if not is_sa and not is_belief: self.log_scroll.clear()
        
        if algo_idx >= 5 or is_sa: self.eval_cb.config(state="readonly")
        elif not is_belief: self.eval_cb.config(state="disabled")
        else: self.eval_cb.config(state="disabled")
            
        if "Leo núi khởi động lại ngẫu nhiên" in algo:
            self.max_restart_sb.config(state="normal")
            try: max_res = int(self.max_restart_var.get())
            except ValueError: max_res = 3
        else:
            self.max_restart_sb.config(state="disabled")
            max_res = 1 
            
        if "Local Beam Search" in algo:
            self.k_sb.config(state="normal")
            try: k_val = int(self.k_var.get())
            except ValueError: k_val = 3
        else:
            self.k_sb.config(state="disabled")
            k_val = 1

        sa_controls = [self.sa_initial_temp_sb, self.sa_cooling_rate_sb, self.sa_min_temp_sb, self.sa_max_restart_sb]
        if is_sa:
            for ctrl in sa_controls: ctrl.config(state="normal")
            try:
                initial_temp = float(self.sa_initial_temp_var.get())
                cooling_rate = float(self.sa_cooling_rate_var.get())
                min_temp = float(self.sa_min_temp_var.get())
                max_restart_sa = int(self.sa_max_restart_var.get())
            except ValueError:
                initial_temp, cooling_rate, min_temp, max_restart_sa = 100, 0.95, 0.1, 3
        else:
            for ctrl in sa_controls: ctrl.config(state="disabled")
            initial_temp = cooling_rate = min_temp = max_restart_sa = None
            
        if "Tối ưu" in algo: self.generator = bfs_optimized(start_state, goal_state, self.get_next_name)
        elif "Cổ điển" in algo: self.generator = bfs_classic(start_state, goal_state, self.get_next_name)
        elif "Generic" in algo: self.generator = bfs_generic(start_state, goal_state, self.get_next_name)
        elif "IDA*" in algo: self.generator = ida_star_algorithm(start_state, goal_state, self.get_next_name, self.reset_name_counter, eval_type)
        elif "IDS" in algo: self.generator = ids_algorithm(start_state, goal_state, self.get_next_name, self.reset_name_counter)
        elif "UCS" in algo: self.generator = ucs_algorithm(start_state, goal_state, self.get_next_name, eval_type)
        elif "Greedy" in algo: self.generator = greedy_algorithm(start_state, goal_state, self.get_next_name, eval_type)
        elif "A*" in algo: self.generator = a_star_algorithm(start_state, goal_state, self.get_next_name, eval_type)
        elif "Leo núi đơn giản" in algo: self.generator = simple_hill_climbing(start_state, goal_state, self.get_next_name, eval_type)
        elif "Leo núi dốc nhất" in algo: self.generator = steepest_ascent_hill_climbing(start_state, goal_state, self.get_next_name, eval_type)
        elif "Leo núi ngẫu nhiên" in algo: self.generator = stochastic_hill_climbing(start_state, goal_state, self.get_next_name, eval_type)
        elif "Leo núi khởi động lại ngẫu nhiên" in algo: self.generator = random_restart_hill_climbing(start_state, goal_state, self.get_next_name, eval_type, max_res)
        elif "Local Beam Search" in algo: self.generator = local_beam_search(start_state, goal_state, self.get_next_name, eval_type, k_val)
        elif is_sa: self.generator = simulated_annealing(start_state, goal_state, self.get_next_name, eval_type, initial_temp, cooling_rate, min_temp, max_restart_sa)
        elif "AND-OR" in algo: self.generator = and_or_graph_search(start_state, goal_state, self.get_next_name)
        elif "CSP Backtracking" in algo: self.generator = csp_backtracking_generator(goal_state, self.get_next_name)
        elif is_belief:
            if self.belief_generated_states and self.belief_generated_goals:
                self.generator = belief_state_bfs(self.belief_generated_states, self.belief_generated_goals, self.get_next_name)
            else:
                self.generator = None
                messagebox.showinfo("Belief State", "Hãy nhấn 'Sinh ngẫu nhiên' trước!")
        else:
            self.generator = dfs_algorithm(start_state, goal_state, self.get_next_name)

        self.btn_step.config(state="normal" if self.generator else "disabled")
        self.btn_auto.config(state="normal" if self.generator else "disabled")
        self.lbl_status.config(text="Trạng thái: Đã khởi tạo.", fg="#2980b9")
        
        md = get_eval_value(None, start_state, goal_state, eval_type) if (algo_idx >= 5 or is_sa) else get_manhattan_distance(start_state, goal_state)
        self.lbl_manhattan.config(text=f"Chi phí / Heuristic ban đầu: {md}")
        self.lbl_depth.config(text="Độ sâu hiện tại (Depth): 0")
        self.lbl_popped.config(text="Số Node đã duyệt (Pop): 0")

    def step_search(self):
        if self.is_solved or not self.generator: return
        try:
            yielded_data = next(self.generator)
            curr_data, frontier_logs, reached_set, goal_node = yielded_data
            self.total_popped += 1

            if self.is_sa_mode:
                self.update_sa_display(curr_data)
                if frontier_logs == "SA_stuck":
                    self.lbl_status.config(text="❌ SA kết thúc: Đạt T_min hoặc không tìm thấy lời giải!", fg="#c0392b")
                    self.is_solved = True
                    self.btn_step.config(state="disabled"); self.stop_auto(); self.btn_auto.config(state="disabled")
                elif goal_node:
                    self.is_solved = True
                    self.lbl_status.config(text=f"🎉 SA tìm thấy Đích! Best cost: {goal_node.cost}", fg="#27ae60")
                    self.btn_step.config(state="disabled"); self.stop_auto(); self.btn_auto.config(state="disabled")
                else:
                    self.lbl_status.config(text=f"Trạng thái: SA đang chạy (Iter {curr_data.get('iteration', 0)})", fg="#2980b9")
                return

            if self.is_belief_mode:
                if isinstance(frontier_logs, str) and frontier_logs == "Belief_limit":
                    self.is_solved = True
                    self.lbl_status.config(text="❌ Belief BFS: Đạt giới hạn độ sâu!", fg="#c0392b")
                    self.btn_step.config(state="disabled"); self.stop_auto(); self.btn_auto.config(state="disabled")
                    return
                belief_data = {"belief": curr_data.get("belief", ()), "depth": curr_data.get("depth", 0), "solved": curr_data.get("solved", []),
                               "expanding": curr_data.get("expanding", -1), "expanding_state": curr_data.get("expanding_state", ""),
                               "frontier_logs": frontier_logs if isinstance(frontier_logs, list) else [], "explored_sets": curr_data.get("explored_sets", []),
                               "all_reached": reached_set, "queues": curr_data.get("queues", []), "target_goal": curr_data.get("target_goal", None),
                               "restart_reason": curr_data.get("restart_reason", ""), "restart_flag": curr_data.get("restart_flag", False)}
                self.update_belief_display(belief_data)
                if goal_node:
                    self.is_solved = True
                    solved_count = sum(curr_data.get('solved', []))
                    total = len(curr_data.get('solved', []))
                    self.lbl_status.config(text=f"🎉 Belief BFS: {solved_count}/{total} states đã tìm thấy goal!", fg="#27ae60")
                    self.btn_step.config(state="disabled"); self.stop_auto(); self.btn_auto.config(state="disabled")
                else:
                    solved_count = sum(curr_data.get('solved', []))
                    total = len(curr_data.get('solved', []))
                    self.lbl_status.config(text=f"Trạng thái: Belief BFS ({solved_count}/{total} solved, Depth {curr_data.get('depth', 0)})", fg="#2980b9")
                return
            
            if frontier_logs == "AND-OR":
                self.add_and_or_log_row(curr_data)
                phase = curr_data.get("phase")
                if phase == "OR":
                    self.draw_state_to_canvas(self.curr_board_canvas, curr_data["state"])
                    self.lbl_status.config(text=f"Trạng thái: Đang xét Pha OR (Tìm hành động)")
                elif phase == "ACTION":
                    self.lbl_status.config(text=f"Trạng thái: Thử hành động {curr_data['action']} (Phát sinh {len(curr_data['results'])} trạng thái)")
                elif phase == "AND":
                    self.lbl_status.config(text=f"Trạng thái: Đang xét Pha AND (Duyệt các nhánh rủi ro)")
                self.lbl_depth.config(text=f"Độ sâu đệ quy: {curr_data.get('depth', 0)}")
                self.lbl_popped.config(text=f"Số bước mô phỏng: {self.total_popped}")
                return

            if isinstance(curr_data, list):
                best_node = curr_data[0] if curr_data else None
            else:
                best_node = curr_data
            
            if best_node: self.draw_state_to_canvas(self.curr_board_canvas, best_node.state)
            self.add_log_row(curr_data, frontier_logs, reached_set)
            
            if best_node:
                algo_idx = self.algo_cb.current()
                eval_type = self.eval_var.get()
                md = get_eval_value(best_node.state, best_node.state, self.goal_entry.get().strip(), eval_type) if algo_idx >= 5 else get_manhattan_distance(best_node.state, self.goal_entry.get().strip())
                self.lbl_manhattan.config(text=f"Chi phí / Heuristic tới Đích: {md}")
                self.lbl_depth.config(text=f"Độ sâu hiện tại (Depth): {best_node.depth}")
            self.lbl_popped.config(text=f"Số Bước đã duyệt: {self.total_popped}")
            
            if goal_node:
                self.is_solved = True
                if "CSP" in self.algo_var.get():
                    self.lbl_status.config(text=f"🎉 CSP đã tạo thành công bàn cờ hợp lệ!", fg="#27ae60")
                else:
                    path = self.trace_path(goal_node)
                    self.lbl_status.config(text=f"🎉 Đã tìm thấy Đích!\nCost: {goal_node.depth} bước\nĐường đi: {path}", fg="#27ae60")
                self.btn_step.config(state="disabled"); self.stop_auto(); self.btn_auto.config(state="disabled")
                
        except StopIteration as e:
            if "AND-OR" in self.algo_var.get():
                plan = e.value
                self.is_solved = True
                self.stop_auto(); self.btn_step.config(state="disabled"); self.btn_auto.config(state="disabled")
                if plan == "failure" or plan is None:
                    self.lbl_status.config(text="❌ Thất bại: Không tìm được Contingency Plan an toàn!", fg="#c0392b")
                else:
                    self.lbl_status.config(text="🎉 Đã tìm thấy Contingency Plan! (Mở cửa sổ mới)", fg="#27ae60")
                    self.show_contingency_plan(plan)
                return

            if "CSP Backtracking" in self.algo_var.get():
                self.lbl_status.config(text="❌ CSP Thất bại: Cạn kiệt không gian mẫu!", fg="#c0392b")
            elif self.is_sa_mode:
                self.lbl_status.config(text="❌ SA kết thúc: Không thể tiếp tục!", fg="#c0392b")
            elif self.is_belief_mode:
                self.lbl_status.config(text="❌ Belief BFS: Không tìm thấy lời giải!", fg="#c0392b")
            else:
                self.lbl_status.config(text="❌ Thất bại: Đạt cực đại cục bộ / Đã duyệt hết!", fg="#c0392b")
            self.is_solved = True
            self.btn_step.config(state="disabled"); self.stop_auto(); self.btn_auto.config(state="disabled")
                
    def trace_path(self, node):
        path = []
        curr = node
        while curr:
            if curr.action and not curr.action.startswith("Start") and curr.action != "Start":
                path.append(f"{curr.action[0]}")
            curr = curr.parent
        return " -> ".join(path[::-1])

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()