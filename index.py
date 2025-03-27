import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

class DeadlockToolkit:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Prevention & Recovery Toolkit")
        self.root.geometry("700x500")
        
        tk.Label(root, text="Deadlock Prevention & Recovery Toolkit", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10)
        
        tk.Label(self.input_frame, text="Number of Processes:").grid(row=0, column=0)
        self.num_processes_entry = tk.Entry(self.input_frame)
        self.num_processes_entry.grid(row=0, column=1)
        
        tk.Label(self.input_frame, text="Number of Resources:").grid(row=1, column=0)
        self.num_resources_entry = tk.Entry(self.input_frame)
        self.num_resources_entry.grid(row=1, column=1)
        
        self.process_btn = tk.Button(self.input_frame, text="Set Matrix Inputs", command=self.set_matrices)
        self.process_btn.grid(row=2, columnspan=2, pady=5)
        
        self.detect_btn = tk.Button(root, text="Detect Deadlock", command=self.detect_deadlock)
        self.detect_btn.pack(pady=5)
        
        self.prevent_btn = tk.Button(root, text="Run Banker's Algorithm", command=self.run_bankers_algorithm)
        self.prevent_btn.pack(pady=5)
        
        self.recover_btn = tk.Button(root, text="Recover from Deadlock", command=self.recover_deadlock)
        self.recover_btn.pack(pady=5)
        
        self.graph_btn = tk.Button(root, text="Show Resource Allocation Graph", command=self.show_graph)
        self.graph_btn.pack(pady=5)
        
        self.wait_graph_btn = tk.Button(root, text="Show Wait-For Graph", command=self.show_wait_graph)
        self.wait_graph_btn.pack(pady=5)
        
        self.allocation = None
        self.maximum = None
        self.available = None
    
    def set_matrices(self):
        num_processes = int(self.num_processes_entry.get())
        num_resources = int(self.num_resources_entry.get())
        
        self.allocation = np.zeros((num_processes, num_resources), dtype=int)
        self.maximum = np.zeros((num_processes, num_resources), dtype=int)
        self.available = np.zeros(num_resources, dtype=int)
        
        self.matrix_window = tk.Toplevel(self.root)
        self.matrix_window.title("Enter Matrices")
        
        tk.Label(self.matrix_window, text="Allocation Matrix (comma-separated values per row)").pack()
        self.allocation_entries = [tk.Entry(self.matrix_window) for _ in range(num_processes)]
        for i, entry in enumerate(self.allocation_entries):
            entry.pack()
        
        tk.Label(self.matrix_window, text="Maximum Matrix (comma-separated values per row)").pack()
        self.maximum_entries = [tk.Entry(self.matrix_window) for _ in range(num_processes)]
        for i, entry in enumerate(self.maximum_entries):
            entry.pack()
        
        tk.Label(self.matrix_window, text="Available Resources (comma-separated values)").pack()
        self.available_entry = tk.Entry(self.matrix_window)
        self.available_entry.pack()
        
        tk.Button(self.matrix_window, text="Submit", command=self.save_matrices).pack()
    
    def save_matrices(self):
        try:
            for i, entry in enumerate(self.allocation_entries):
                self.allocation[i] = list(map(int, entry.get().split(',')))
            for i, entry in enumerate(self.maximum_entries):
                self.maximum[i] = list(map(int, entry.get().split(',')))
            self.available = list(map(int, self.available_entry.get().split(',')))
            self.matrix_window.destroy()
            messagebox.showinfo("Success", "Matrices updated successfully!")
        except ValueError:
            messagebox.showerror("Error", "Invalid matrix format. Use comma-separated integers.")
    
    def detect_deadlock(self):
        if self.allocation is None or self.maximum is None or self.available is None:
            messagebox.showerror("Error", "Please set matrices first.")
            return
            
        num_processes = len(self.allocation)
        num_resources = len(self.available)
        
        # Calculate need matrix
        need = self.maximum - self.allocation
        
        # Make a copy of available resources
        work = self.available.copy()
        
        # Track which processes have finished
        finish = np.zeros(num_processes, dtype=bool)
        
        # Display details in a window
        details_window = tk.Toplevel(self.root)
        details_window.title("Deadlock Detection")
        details_window.geometry("700x500")
        
        text_output = tk.Text(details_window, wrap=tk.WORD)
        text_output.pack(fill=tk.BOTH, expand=True)
        
        text_output.insert(tk.END, "Deadlock Detection Algorithm:\n\n")
        text_output.insert(tk.END, f"Initial state:\n")
        text_output.insert(tk.END, f"Available resources: {work}\n\n")
        
        # Continue until no more processes can finish
        while True:
            found = False
            
            # Try to find a process that can finish
            for i in range(num_processes):
                if not finish[i]:
                    # Check if process needs can be satisfied
                    can_finish = True
                    for j in range(num_resources):
                        if need[i][j] > work[j]:
                            can_finish = False
                            break
                    
                    # If process can finish, mark it and release its resources
                    if can_finish:
                        text_output.insert(tk.END, f"Process P{i} can finish.\n")
                        
                        finish[i] = True
                        for j in range(num_resources):
                            work[j] += self.allocation[i][j]
                        
                        text_output.insert(tk.END, f"Process P{i} finished, released resources: {self.allocation[i]}\n")
                        text_output.insert(tk.END, f"New available resources: {work}\n\n")
                        
                        found = True
                        break
            
            # If no process can finish, exit the loop
            if not found:
                break
        
        # Any processes that couldn't finish are deadlocked
        deadlocked = [i for i in range(num_processes) if not finish[i]]
        
        if deadlocked:
            text_output.insert(tk.END, f"\nDeadlock detected!\n")
            text_output.insert(tk.END, f"Deadlocked processes: {[f'P{i}' for i in deadlocked]}\n")
            messagebox.showwarning("Deadlock Detected", f"Processes {[f'P{i}' for i in deadlocked]} are deadlocked.")
        else:
            text_output.insert(tk.END, f"\nNo deadlock detected. All processes can complete.\n")
            messagebox.showinfo("Deadlock Detection", "No deadlock detected.")
     
    def run_bankers_algorithm(self):
        num_processes, num_resources = self.allocation.shape
        work = self.available.copy()
        finish = np.zeros(num_processes, dtype=bool)
        safe_sequence = []
        
        while len(safe_sequence) < num_processes:
            allocated = False
            for i in range(num_processes):
                if not finish[i] and np.all(self.maximum[i] - self.allocation[i] <= work):
                    work += self.allocation[i]
                    finish[i] = True
                    safe_sequence.append(i)
                    allocated = True
            
            if not allocated:
                messagebox.showwarning("Banker's Algorithm", "Unsafe state detected! Deadlock possible.")
                return
        
        messagebox.showinfo("Banker's Algorithm", f"Safe sequence found: {safe_sequence}")

    
    def recover_deadlock(self):
        num_processes = len(self.allocation)
        min_index = np.argmin(np.sum(self.allocation, axis=1))
        self.available += self.allocation[min_index]
        self.allocation[min_index] = np.zeros_like(self.allocation[min_index])
        messagebox.showinfo("Deadlock Recovery", f"Process {min_index} terminated, resources released.")
    
    def show_graph(self):
        if self.allocation is None:
            messagebox.showerror("Error", "Please set matrices first.")
            return
        
        G = nx.DiGraph()
        num_processes, num_resources = self.allocation.shape
        
        # Add nodes
        for p in range(num_processes):
            G.add_node(f"P{p}", bipartite=0)
        for r in range(num_resources):
            G.add_node(f"R{r}", bipartite=1)
        
        # Add edges for allocation (resource to process)
        for p in range(num_processes):
            for r in range(num_resources):
                if self.allocation[p, r] > 0:
                    G.add_edge(f"R{r}", f"P{p}", weight=self.allocation[p, r])
        
        # Add edges for requests (process to resource)
        need = self.maximum - self.allocation
        for p in range(num_processes):
            for r in range(num_resources):
                if need[p, r] > 0:
                    G.add_edge(f"P{p}", f"R{r}", weight=need[p, r])
        
        # Draw the graph
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G)
        
        # Draw process nodes
        nx.draw_networkx_nodes(G, pos, 
                               nodelist=[f"P{p}" for p in range(num_processes)],
                               node_color='lightblue', 
                               node_size=500)
        
        # Draw resource nodes
        nx.draw_networkx_nodes(G, pos, 
                               nodelist=[f"R{r}" for r in range(num_resources)],
                               node_color='lightgreen', 
                               node_size=500)
        
        # Draw edges
        allocation_edges = [(u, v) for u, v in G.edges() if u.startswith('R')]
        request_edges = [(u, v) for u, v in G.edges() if u.startswith('P')]
        
        nx.draw_networkx_edges(G, pos, 
                               edgelist=allocation_edges,
                               width=1.0, 
                               alpha=0.5,
                               edge_color='blue',
                               arrows=True)
        
        nx.draw_networkx_edges(G, pos, 
                               edgelist=request_edges,
                               width=1.0, 
                               alpha=0.5,
                               edge_color='red',
                               arrows=True)
        
        # Add labels
        nx.draw_networkx_labels(G, pos)
        
        # Add edge weights
        edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        
        # Add legend
        plt.legend(
            [plt.Line2D([0], [0], color='blue', lw=2), plt.Line2D([0], [0], color='red', lw=2)],
            ['Allocation', 'Request'],
            loc='upper right'
        )
        
        plt.title("Resource Allocation Graph")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def show_wait_graph(self):
        G = nx.DiGraph()
        num_processes = len(self.allocation)
        
        for i in range(num_processes):
            for j in range(num_processes):
                if i != j and any(self.maximum[i] - self.allocation[i] > 0):
                    G.add_edge(f"P{i}", f"P{j}")
        
        plt.figure(figsize=(5,5))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='red', edge_color='black', node_size=3000, font_size=10)
        plt.title("Wait-For Graph")
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlockToolkit(root)
