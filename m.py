import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import math


class DeliveryPoint:
    def __init__(self, x, y, demand):
        self.x = x
        self.y = y
        self.demand = demand

class Truck:
    def __init__(self, capacity):
        self.capacity = capacity
        self.route = []

def distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def initial_solution(delivery_points, trucks):
    random.shuffle(delivery_points)  
    for truck in trucks:
        truck.route = [] 
    current_truck = 0  
    for point in delivery_points:
        if trucks[current_truck].capacity >= point.demand:
            
            trucks[current_truck].route.append(point)
            trucks[current_truck].capacity -= point.demand
        else:
           
            current_truck += 1
            if current_truck >= len(trucks):
                
                return False
           
            trucks[current_truck].route.append(point)
            trucks[current_truck].capacity -= point.demand
    return True  


def total_distance(trucks, depot):
    total = 0
    for truck in trucks:
        if truck.route:
            total += distance(depot, truck.route[0])
            for i in range(len(truck.route) - 1):
                total += distance(truck.route[i], truck.route[i + 1])
            total += distance(truck.route[-1], depot)
    return total


def neighbor_solution(trucks):
    new_trucks = [Truck(truck.capacity) for truck in trucks]
    for i in range(len(trucks)):
        new_trucks[i].route = trucks[i].route[:]
    truck1, truck2 = random.sample(range(len(trucks)), 2)
    if new_trucks[truck1].route and new_trucks[truck2].route:
        point1 = random.randint(0, len(new_trucks[truck1].route) - 1)
        point2 = random.randint(0, len(new_trucks[truck2].route) - 1)
        new_trucks[truck1].route[point1], new_trucks[truck2].route[point2] = new_trucks[truck2].route[point2], new_trucks[truck1].route[point1]
    return new_trucks

def simulated_annealing(delivery_points, trucks, depot, max_iterations, cooling_rate, output_text, iteration_offset, best_solution, best_distance):
    current_solution = trucks[:]
    current_distance = total_distance(current_solution, depot)

    temperature = 1.0
    if best_solution is None:
        best_solution = current_solution[:]
        best_distance = current_distance


    for iteration in range(iteration_offset, iteration_offset + max_iterations):
        new_solution = neighbor_solution(current_solution)
        new_distance = total_distance(new_solution, depot)

        if new_distance < current_distance or random.random() < math.exp((current_distance - new_distance) / temperature):
            current_solution = new_solution
            current_distance = new_distance

            if new_distance < best_distance:
                best_solution = new_solution
                best_distance = new_distance

        temperature *= cooling_rate
        output_text.insert(tk.END, f"Iteration: {iteration}, Current Distance: {current_distance:.2f}, Best Distance: {best_distance:.2f}\n")
        output_text.see(tk.END)

    return best_solution, best_distance

class VRPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vehicle Routing Problem - Simulated Annealing")
        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.delivery_points = []
        self.trucks = []
        self.depot = DeliveryPoint(300, 200, 0)
        self.canvas.create_oval(295, 195, 305, 205, fill="red")
        self.canvas.bind("<Button-1>", self.add_point)
        self.cooling_rate = 0.995
        self.iteration_count = 1
        self.best_solution = None
        self.best_distance = float('inf')

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(side=tk.TOP, pady=10)

        self.create_controls()

    def create_controls(self):
       
        control_labels = ["Number of Trucks:", "Truck Capacity:", "Temperature:", "Cooling Rate:"]
        initial_values = ["3", "50", "1000", "0.995"]
        self.control_entries = []
        for i, (label_text, initial_value) in enumerate(zip(control_labels, initial_values)):
            label = tk.Label(self.controls_frame, text=label_text)
            label.grid(row=i // 2, column=(i % 2) * 2, padx=5, pady=5, sticky='e')
            entry = tk.Entry(self.controls_frame)
            entry.insert(0, initial_value)
            entry.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=5, pady=5)
            self.control_entries.append(entry)

        tk.Label(self.controls_frame, text="Best Distance:").grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.best_distance_display_value = tk.Label(self.controls_frame, text="N/A", relief="sunken", width=10)
        self.best_distance_display_value.grid(row=0, column=5, padx=5, pady=5)

        self.start_button = tk.Button(self.controls_frame, text="Start Optimization", command=self.start_optimization)
        self.start_button.grid(row=1, column=4, columnspan=2, padx=5, pady=5)

        buttons = [
            ("Single Step", 1),
            ("100 Steps", 100),
            ("1000 Steps", 1000),
            ("10000 Steps", 10000)
        ]
        for i, (text, steps) in enumerate(buttons):
            button = tk.Button(self.controls_frame, text=text, command=lambda s=steps: self.solve_vrp(s))
            button.grid(row=2 + i // 2, column=(i % 2) * 3, columnspan=3, padx=5, pady=5)

        self.output_frame = tk.Frame(self.root)
        self.output_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.output_text = tk.Text(self.output_frame, height=20, relief="sunken", borderwidth=2)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_scroll = tk.Scrollbar(self.output_frame, command=self.output_text.yview)
        self.output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=self.output_scroll.set)

    def add_point(self, event):
        demand = simpledialog.askinteger("Input", "Enter demand for this point", minvalue=1)
        if demand:
            point = DeliveryPoint(event.x, event.y, demand)
            self.delivery_points.append(point)
            self.canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill="blue")
            self.canvas.create_text(event.x, event.y, text=str(demand), anchor=tk.NW)

    def start_optimization(self):
        try:
            num_trucks = int(self.control_entries[0].get())
            truck_capacity = int(self.control_entries[1].get())
            temperature = float(self.control_entries[2].get())
            cooling_rate = float(self.control_entries[3].get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all input fields.")
            return

        if num_trucks <= 0 or truck_capacity <= 0 or temperature <= 0 or not (0 < cooling_rate < 1):
            messagebox.showerror("Error", "Please ensure all inputs are positive and cooling rate is between 0 and 1.")
            return

        total_demand = sum(point.demand for point in self.delivery_points)
        total_capacity = num_trucks * truck_capacity

        if total_demand > total_capacity:
            messagebox.showerror("Error", "Total truck capacity is not enough to meet all delivery points' demands.")
            return

        self.trucks = [Truck(truck_capacity) for _ in range(num_trucks)]
        self.temperature = temperature
        self.cooling_rate = cooling_rate
        self.iteration_count = 1
        self.best_solution = None
        self.best_distance = float('inf')

        if not initial_solution(self.delivery_points, self.trucks):
            messagebox.showerror("Error", "Failed to generate an initial solution. Check the capacities and demands.")
            return

        self.best_solution = self.trucks[:]
        self.best_distance = total_distance(self.best_solution, self.depot)

        self.output_text.delete(1.0, tk.END)
        self.solve_vrp(1)

    def solve_vrp(self, iterations):
        self.best_solution, self.best_distance = simulated_annealing(
            self.delivery_points, self.trucks, self.depot, iterations, self.cooling_rate,
            self.output_text, self.iteration_count, self.best_solution, self.best_distance
        )
        if self.best_solution is None:
            messagebox.showerror("Error", "Not enough truck capacity for all delivery points.")
            return

        self.iteration_count += iterations
        self.best_distance_display_value.config(text=f"{self.best_distance:.2f}")
        self.display_solution(self.best_solution)

    def display_solution(self, solution):
        self.canvas.delete("route")
        colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'orange', 'purple', 'pink', 'brown']
        for idx, truck in enumerate(solution):
            if truck.route:
                points = [(self.depot.x, self.depot.y)] + [(p.x, p.y) for p in truck.route] + [(self.depot.x, self.depot.y)]
                for i in range(len(points) - 1):
                    self.canvas.create_line(points[i], points[i + 1], fill=colors[idx % len(colors)], tags="route")

if __name__ == "__main__":
    root = tk.Tk()
    app = VRPApp(root)
    root.mainloop()
