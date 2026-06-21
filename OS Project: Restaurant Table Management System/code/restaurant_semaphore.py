import threading
import time
import random
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import queue
from enum import Enum

class CustomerState(Enum):
    WAITING = "waiting"
    SEATED = "seated"
    EATING = "eating"
    FINISHED = "finished"

class Customer:
    """Represents a customer in the restaurant"""
    
    def __init__(self, customer_id):
        self.id = customer_id
        self.arrival_time = datetime.now()
        self.seated_time = None
        self.finish_time = None
        self.state = CustomerState.WAITING
        self.table_number = None
        self.dining_duration = random.uniform(8, 15)  # 8-15 seconds for better demo
    
    def get_waiting_time(self):
        """Calculate how long customer has been waiting"""
        if self.seated_time:
            return (self.seated_time - self.arrival_time).total_seconds()
        return (datetime.now() - self.arrival_time).total_seconds()
    
    def __str__(self):
        return f"Customer {self.id} ({self.state.value})"

class Table:
    """Represents a table in the restaurant"""
    
    def __init__(self, table_number):
        self.number = table_number
        self.is_occupied = False
        self.customer = None
        self.occupied_since = None
    
    def seat_customer(self, customer):
        """Seat a customer at this table"""
        self.is_occupied = True
        self.customer = customer
        self.occupied_since = datetime.now()
        customer.table_number = self.number
        customer.seated_time = datetime.now()
        customer.state = CustomerState.SEATED
    
    def free_table(self):
        """Free the table when customer leaves"""
        if self.customer:
            self.customer.finish_time = datetime.now()
            self.customer.state = CustomerState.FINISHED
        self.is_occupied = False
        self.customer = None
        self.occupied_since = None

class RestaurantManager:
    """Manages the restaurant operations using semaphore"""
    
    def __init__(self, num_tables=3):
        self.num_tables = num_tables
        self.table_semaphore = threading.Semaphore(num_tables)
        self.tables = [Table(i+1) for i in range(num_tables)]
        self.waiting_customers = queue.Queue()
        self.all_customers = []
        self.customer_counter = 0
        self.is_running = False
        self.stats_lock = threading.Lock()
        
        # Statistics
        self.total_customers_served = 0
        self.total_waiting_time = 0
        self.max_waiting_time = 0
        
        # GUI update queue
        self.gui_update_queue = queue.Queue()

        # Semaphore counter for display
        self.semaphore_counter = num_tables
    
    def add_customer(self):
        """Add a new customer to the restaurant"""
        self.customer_counter += 1
        customer = Customer(self.customer_counter)
        self.all_customers.append(customer)
        self.waiting_customers.put(customer)
        
        # Notify GUI
        self.gui_update_queue.put(('customer_arrived', customer))
        
        # Start a thread to handle this customer
        threading.Thread(target=self._handle_customer, args=(customer,), daemon=True).start()
    
    def _handle_customer(self, customer):
        """Handle a customer's complete restaurant experience"""
        try:
            # Wait for a table (acquire semaphore)
            self.gui_update_queue.put(('semaphore_acquire_attempt', customer))
            self.table_semaphore.acquire()

            # Update semaphore counter
            self.semaphore_counter -= 1
            self.gui_update_queue.put(('semaphore_acquired', customer, self.semaphore_counter))

            # Find an available table
            table = self._find_available_table()
            if table:
                # Seat the customer
                table.seat_customer(customer)
                customer.state = CustomerState.EATING

                # Update statistics
                with self.stats_lock:
                    waiting_time = customer.get_waiting_time()
                    self.total_waiting_time += waiting_time
                    self.max_waiting_time = max(self.max_waiting_time, waiting_time)

                # Notify GUI with transition
                self.gui_update_queue.put(('customer_seated', customer, table))

                # Customer eats (simulate dining time)
                time.sleep(customer.dining_duration)

                # Customer finishes and leaves
                table.free_table()

                with self.stats_lock:
                    self.total_customers_served += 1

                # Notify GUI
                self.gui_update_queue.put(('customer_left', customer, table))

        finally:
            # Release the table (release semaphore)
            self.semaphore_counter += 1
            self.table_semaphore.release()
            self.gui_update_queue.put(('semaphore_released', customer, self.semaphore_counter))
    
    def _find_available_table(self):
        """Find the first available table"""
        for table in self.tables:
            if not table.is_occupied:
                return table
        return None
    
    def get_waiting_customers(self):
        """Get list of currently waiting customers"""
        waiting = []
        temp_queue = queue.Queue()
        
        # Extract all customers from queue
        while not self.waiting_customers.empty():
            try:
                customer = self.waiting_customers.get_nowait()
                if customer.state == CustomerState.WAITING:
                    waiting.append(customer)
                temp_queue.put(customer)
            except queue.Empty:
                break
        
        # Put them back
        while not temp_queue.empty():
            self.waiting_customers.put(temp_queue.get())
        
        return waiting
    
    def get_statistics(self):
        """Get current restaurant statistics"""
        with self.stats_lock:
            avg_waiting_time = (self.total_waiting_time / self.total_customers_served 
                              if self.total_customers_served > 0 else 0)
            
            return {
                'total_served': self.total_customers_served,
                'avg_waiting_time': avg_waiting_time,
                'max_waiting_time': self.max_waiting_time,
                'current_waiting': len(self.get_waiting_customers()),
                'occupied_tables': sum(1 for table in self.tables if table.is_occupied)
            }

class RestaurantGUI:
    """GUI for the restaurant semaphore simulation"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Restaurant Table Management - Semaphore Demo")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')

        self.restaurant = RestaurantManager(num_tables=3)
        self.customer_arrival_thread = None
        self.gui_update_thread = None
        self.is_simulation_running = False

        # Visual transition tracking
        self.transitioning_customers = {}  # customer_id -> transition_info

        self.animation_canvas = None  # Will be set in setup_gui

        self.setup_gui()
        self.start_gui_update_thread()

    def setup_gui(self):
        """Setup the GUI components"""
        # Main title
        title_label = tk.Label(self.root, text="🍽️ Restaurant Table Management System",
                              font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=10)

        # Create main frames
        self.create_control_frame()
        self.create_semaphore_frame()
        self.create_restaurant_frame()
        self.create_statistics_frame()
        self.create_log_frame()

    def create_control_frame(self):
        """Create control panel"""
        control_frame = tk.Frame(self.root, bg='#e0e0e0', relief='raised', bd=2)
        control_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(control_frame, text="Control Panel", font=('Arial', 12, 'bold'),
                bg='#e0e0e0').pack(pady=5)

        button_frame = tk.Frame(control_frame, bg='#e0e0e0')
        button_frame.pack(pady=5)

        self.start_button = tk.Button(button_frame, text="Start Simulation",
                                     command=self.start_simulation, bg='#4CAF50',
                                     fg='white', font=('Arial', 10, 'bold'))
        self.start_button.pack(side='left', padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop Simulation",
                                    command=self.stop_simulation, bg='#f44336',
                                    fg='white', font=('Arial', 10, 'bold'), state='disabled')
        self.stop_button.pack(side='left', padx=5)

        self.add_customer_button = tk.Button(button_frame, text="Add Customer",
                                           command=self.add_single_customer,
                                           bg='#2196F3', fg='white', font=('Arial', 10, 'bold'))
        self.add_customer_button.pack(side='left', padx=5)

        self.reset_button = tk.Button(button_frame, text="Reset",
                                     command=self.reset_simulation, bg='#FF9800',
                                     fg='white', font=('Arial', 10, 'bold'))
        self.reset_button.pack(side='left', padx=5)

        # Settings frame
        settings_frame = tk.Frame(control_frame, bg='#e0e0e0')
        settings_frame.pack(pady=5)

        tk.Label(settings_frame, text="Customer Arrival Rate (seconds):",
                bg='#e0e0e0').pack(side='left')
        self.arrival_rate_var = tk.StringVar(value="3")
        arrival_rate_entry = tk.Entry(settings_frame, textvariable=self.arrival_rate_var, width=5)
        arrival_rate_entry.pack(side='left', padx=5)

    def create_semaphore_frame(self):
        """Create semaphore counter display"""
        semaphore_frame = tk.Frame(self.root, bg='#e8f4fd', relief='raised', bd=2)
        semaphore_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(semaphore_frame, text="🔢 Semaphore Status", font=('Arial', 12, 'bold'),
                bg='#e8f4fd').pack(pady=5)

        status_frame = tk.Frame(semaphore_frame, bg='#e8f4fd')
        status_frame.pack(pady=5)

        # Semaphore counter
        tk.Label(status_frame, text="Available Tables (Semaphore Counter, decrements on acquire, increments on release):",
                font=('Arial', 10), bg='#e8f4fd').pack(side='left', padx=5)

        self.semaphore_count_label = tk.Label(status_frame, text="3",
                                            font=('Arial', 14, 'bold'),
                                            bg='#e8f4fd', fg='#2196F3',
                                            relief='sunken', bd=2, padx=10)
        self.semaphore_count_label.pack(side='left', padx=5)

        # Status indicator
        tk.Label(status_frame, text="Status:", font=('Arial', 10),
                bg='#e8f4fd').pack(side='left', padx=(20, 5))

        self.semaphore_status_label = tk.Label(status_frame, text="AVAILABLE",
                                             font=('Arial', 10, 'bold'),
                                             bg='#e8f4fd', fg='#4CAF50')
        self.semaphore_status_label.pack(side='left', padx=5)

    def create_restaurant_frame(self):
        """Create the main restaurant visualization"""
        restaurant_frame = tk.Frame(self.root, bg='#f0f0f0')
        restaurant_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Tables section
        tables_frame = tk.LabelFrame(restaurant_frame, text="Restaurant Tables",
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0')
        tables_frame.pack(side='left', fill='both', expand=True, padx=5)

        # Animation canvas inside tables_frame, above tables_grid
        self.animation_canvas = tk.Canvas(tables_frame, width=500, height=120, bg='#f0f0f0', highlightthickness=0)
        self.animation_canvas.pack(pady=(10, 0))

        self.table_widgets = {}
        tables_grid = tk.Frame(tables_frame, bg='#f0f0f0')
        tables_grid.pack(pady=10)

        for i, table in enumerate(self.restaurant.tables):
            row = i // 3
            col = i % 3

            table_frame = tk.Frame(tables_grid, bg='#90EE90', relief='raised',
                                 bd=3, width=120, height=100)
            table_frame.grid(row=row, column=col, padx=10, pady=10)
            table_frame.pack_propagate(False)

            table_label = tk.Label(table_frame, text=f"Table {table.number}",
                                 font=('Arial', 10, 'bold'), bg='#90EE90')
            table_label.pack(pady=5)

            status_label = tk.Label(table_frame, text="Available",
                                  font=('Arial', 9), bg='#90EE90')
            status_label.pack()

            customer_label = tk.Label(table_frame, text="",
                                    font=('Arial', 8), bg='#90EE90')
            customer_label.pack()

            self.table_widgets[table.number] = {
                'frame': table_frame,
                'status': status_label,
                'customer': customer_label
            }

        # Waiting area section
        waiting_frame = tk.LabelFrame(restaurant_frame, text="Waiting Area",
                                    font=('Arial', 12, 'bold'), bg='#f0f0f0')
        waiting_frame.pack(side='right', fill='both', expand=True, padx=5)

        self.waiting_listbox = tk.Listbox(waiting_frame, height=15, font=('Arial', 10))
        waiting_scrollbar = tk.Scrollbar(waiting_frame, orient='vertical')
        self.waiting_listbox.config(yscrollcommand=waiting_scrollbar.set)
        waiting_scrollbar.config(command=self.waiting_listbox.yview)

        self.waiting_listbox.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        waiting_scrollbar.pack(side='right', fill='y')

    def create_statistics_frame(self):
        """Create statistics display"""
        stats_frame = tk.LabelFrame(self.root, text="Statistics",
                                  font=('Arial', 12, 'bold'), bg='#f0f0f0')
        stats_frame.pack(fill='x', padx=10, pady=5)

        stats_grid = tk.Frame(stats_frame, bg='#f0f0f0')
        stats_grid.pack(pady=5)

        self.stats_labels = {}
        stats_items = [
            ('Total Customers Served', 'total_served'),
            ('Currently Waiting', 'current_waiting'),
            ('Occupied Tables', 'occupied_tables'),
            ('Avg Waiting Time', 'avg_waiting_time'),
            ('Max Waiting Time', 'max_waiting_time')
        ]

        for i, (label_text, key) in enumerate(stats_items):
            tk.Label(stats_grid, text=f"{label_text}:", font=('Arial', 10),
                    bg='#f0f0f0').grid(row=0, column=i*2, padx=5, sticky='e')

            value_label = tk.Label(stats_grid, text="0", font=('Arial', 10, 'bold'),
                                 bg='#f0f0f0', fg='#2196F3')
            value_label.grid(row=0, column=i*2+1, padx=5, sticky='w')

            self.stats_labels[key] = value_label

    def create_log_frame(self):
        """Create activity log frame"""
        log_frame = tk.LabelFrame(self.root, text="Activity Log",
                                font=('Arial', 12, 'bold'), bg='#f0f0f0')
        log_frame.pack(fill='x', padx=10, pady=5)

        # Create scrollable text widget
        log_container = tk.Frame(log_frame, bg='#f0f0f0')
        log_container.pack(fill='x', padx=5, pady=5)

        self.log_text = tk.Text(log_container, height=6, font=('Arial', 9),
                               bg='#ffffff', fg='#333333', wrap=tk.WORD)
        log_scrollbar = tk.Scrollbar(log_container, orient='vertical')
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)

        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')

        # Configure text tags for colored output
        self.log_text.tag_configure('arrival', foreground='#2196F3')
        self.log_text.tag_configure('waiting', foreground='#FF9800')
        self.log_text.tag_configure('seated', foreground='#4CAF50', font=('Arial', 9, 'bold'))
        self.log_text.tag_configure('seated_bold', foreground='#388E3C', font=('Arial', 10, 'bold', 'underline'))
        self.log_text.tag_configure('left', foreground='#9E9E9E')
        self.log_text.tag_configure('semaphore', foreground='#9C27B0', font=('Arial', 9, 'bold'))

        # Add initial message
        self.add_log_message("🍽️ Restaurant system ready. Start simulation to see activity!", 'semaphore')

    def add_log_message(self, message, tag=None):
        """Add a message to the activity log"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, full_message, tag)
        self.log_text.see(tk.END)  # Auto-scroll to bottom

        # Limit log size (keep last 100 lines)
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 100:
            self.log_text.delete("1.0", f"{len(lines)-100}.0")

        self.root.update_idletasks()

    def start_simulation(self):
        """Start the automatic customer arrival simulation"""
        if not self.is_simulation_running:
            self.is_simulation_running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')

            # Start customer arrival thread
            self.customer_arrival_thread = threading.Thread(target=self._customer_arrival_loop, daemon=True)
            self.customer_arrival_thread.start()

    def stop_simulation(self):
        """Stop the automatic customer arrival simulation"""
        self.is_simulation_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def add_single_customer(self):
        """Add a single customer manually"""
        self.restaurant.add_customer()

    def reset_simulation(self):
        """Reset the entire simulation"""
        self.stop_simulation()

        # Create new restaurant manager
        self.restaurant = RestaurantManager(num_tables=3)

        # Reset visual state
        self.transitioning_customers = {}

        # Reset GUI
        self.update_table_display()
        self.update_waiting_list()
        self.update_statistics()
        self.update_semaphore_display(3)

        # Clear log
        self.log_text.delete("1.0", tk.END)
        self.add_log_message("🔄 System reset. Ready for new simulation!", 'semaphore')

    def _customer_arrival_loop(self):
        """Background thread for automatic customer arrivals"""
        while self.is_simulation_running:
            try:
                arrival_rate = float(self.arrival_rate_var.get())
                time.sleep(arrival_rate)
                if self.is_simulation_running:
                    self.restaurant.add_customer()
            except ValueError:
                time.sleep(2)  # Default if invalid input

    def start_gui_update_thread(self):
        """Start the GUI update thread"""
        self.gui_update_thread = threading.Thread(target=self._gui_update_loop, daemon=True)
        self.gui_update_thread.start()

    def _gui_update_loop(self):
        """Background thread for updating GUI"""
        while True:
            try:
                # Process GUI updates from restaurant manager
                while not self.restaurant.gui_update_queue.empty():
                    update = self.restaurant.gui_update_queue.get_nowait()
                    self.root.after(0, self._process_gui_update, update)

                # Regular updates
                self.root.after(0, self.update_display)
                time.sleep(0.5)  # Update every 500ms

            except Exception as e:
                print(f"GUI update error: {e}")
                time.sleep(1)

    def _process_gui_update(self, update):
        """Process specific GUI updates from restaurant events"""
        event_type = update[0]

        if event_type == 'customer_arrived':
            customer = update[1]
            self.add_log_message(f"🚶 Customer {customer.id} arrived and joined waiting queue", 'arrival')

        elif event_type == 'semaphore_acquire_attempt':
            customer = update[1]
            self.add_log_message(f"⏳ Customer {customer.id} attempting to acquire table (semaphore.acquire())", 'waiting')

        elif event_type == 'semaphore_acquired':
            customer = update[1]
            semaphore_count = update[2]
            self.add_log_message(f"🔓 Customer {customer.id} acquired semaphore! Count: {semaphore_count}", 'semaphore')
            self.update_semaphore_display(semaphore_count)
            # Mark customer as transitioning
            self.transitioning_customers[customer.id] = {'status': 'acquiring', 'time': time.time()}

        elif event_type == 'customer_seated':
            customer = update[1]
            table = update[2]
            self.add_log_message(f"🪑 Customer {customer.id} SEATED at Table {table.number}! (Transition complete)", 'seated')
            # Extra visible log
            self.add_log_message(f"✅ Customer {customer.id} SEATED!", 'seated_bold')
            # Remove from transitioning and highlight the transition
            if customer.id in self.transitioning_customers:
                del self.transitioning_customers[customer.id]
            self.highlight_customer_transition(customer, table)

        elif event_type == 'customer_left':
            customer = update[1]
            table = update[2]
            self.add_log_message(f"👋 Customer {customer.id} finished dining and left Table {table.number}", 'left')

        elif event_type == 'semaphore_released':
            customer = update[1]
            semaphore_count = update[2]
            self.add_log_message(f"🔓 Table released! Semaphore count: {semaphore_count} (semaphore.release())", 'semaphore')
            self.update_semaphore_display(semaphore_count)

    def update_semaphore_display(self, count):
        """Update the semaphore counter display"""
        self.semaphore_count_label.config(text=str(count))

        # Update status and color based on count
        if count == 0:
            self.semaphore_status_label.config(text="BLOCKED", fg='#f44336')
            self.semaphore_count_label.config(fg='#f44336')
        elif count == 1:
            self.semaphore_status_label.config(text="CRITICAL", fg='#FF9800')
            self.semaphore_count_label.config(fg='#FF9800')
        else:
            self.semaphore_status_label.config(text="AVAILABLE", fg='#4CAF50')
            self.semaphore_count_label.config(fg='#2196F3')

    def walk_customer_to_table(self, customer, table_number, callback=None):
        """Animate a customer walking from the left edge to the actual table widget using a person emoji"""
        canvas = self.animation_canvas
        canvas.delete('all')
        canvas.update()
        # Get the canvas width/height
        canvas_width = int(canvas['width'])
        canvas_height = int(canvas['height'])
        # Find the table widget's center position relative to the canvas
        table_widget = self.table_widgets[table_number]['frame']
        table_abs_x = table_widget.winfo_rootx()
        table_abs_y = table_widget.winfo_rooty()
        canvas_abs_x = canvas.winfo_rootx()
        canvas_abs_y = canvas.winfo_rooty()
        table_width = table_widget.winfo_width()
        table_height = table_widget.winfo_height()
        end_x = table_abs_x - canvas_abs_x + table_width // 2
        end_y = table_abs_y - canvas_abs_y + table_height // 2
        # Start position: left edge, same vertical as table (clamped to canvas)
        start_x = 20
        # Clamp end_y to canvas height
        end_y = max(30, min(end_y, canvas_height - 30))
        start_y = end_y
        # Draw customer as a person emoji with their number
        person = canvas.create_text(start_x, start_y, text=f"🚶 {customer.id}", font=('Arial', 22, 'bold'))
        # Animation steps
        steps = 30
        dx = (end_x - start_x) / steps
        dy = 0  # Only move horizontally
        def animate(step=0):
            if step <= steps:
                canvas.move(person, dx, dy)
                canvas.update()
                self.root.after(20, lambda: animate(step+1))
            else:
                canvas.delete(person)
                if callback:
                    callback()
        animate()

    def highlight_customer_transition(self, customer, table):
        """Highlight customer transition from waiting to seated, with walking animation"""
        def after_walk():
            # Flash the table that just got occupied
            table_widget = self.table_widgets[table.number]
            original_bg = table_widget['frame'].cget('bg')
            def flash_table(count=0):
                if count < 6:  # Flash 3 times
                    color = '#FFD700' if count % 2 == 0 else original_bg  # Gold flash
                    table_widget['frame'].config(bg=color)
                    table_widget['status'].config(bg=color)
                    table_widget['customer'].config(bg=color)
                    self.root.after(200, lambda: flash_table(count + 1))
            flash_table()
        # Animate walking, then flash
        self.walk_customer_to_table(customer, table.number, callback=after_walk)

    def update_display(self):
        """Update all GUI displays"""
        self.update_table_display()
        self.update_waiting_list()
        self.update_statistics()

    def update_table_display(self):
        """Update the table visualization"""
        for table in self.restaurant.tables:
            widget = self.table_widgets[table.number]

            if table.is_occupied:
                # Table is occupied
                widget['frame'].config(bg='#FFB6C1')  # Light pink
                widget['status'].config(text="Occupied", bg='#FFB6C1')
                widget['customer'].config(text=f"Customer {table.customer.id}", bg='#FFB6C1')
            else:
                # Table is available
                widget['frame'].config(bg='#90EE90')  # Light green
                widget['status'].config(text="Available", bg='#90EE90')
                widget['customer'].config(text="", bg='#90EE90')

    def update_waiting_list(self):
        """Update the waiting customers list with visual indicators"""
        self.waiting_listbox.delete(0, tk.END)

        waiting_customers = self.restaurant.get_waiting_customers()
        for i, customer in enumerate(waiting_customers):
            waiting_time = customer.get_waiting_time()

            # Check if customer is transitioning
            if customer.id in self.transitioning_customers:
                # Show transition state
                display_text = f"🔄 Customer {customer.id} → BEING SEATED! (waited {waiting_time:.1f}s)"
            else:
                # Normal waiting state
                if waiting_time > 10:
                    display_text = f"⏰ Customer {customer.id} (waiting {waiting_time:.1f}s) - LONG WAIT"
                elif waiting_time > 5:
                    display_text = f"⏳ Customer {customer.id} (waiting {waiting_time:.1f}s)"
                else:
                    display_text = f"🚶 Customer {customer.id} (waiting {waiting_time:.1f}s)"

            self.waiting_listbox.insert(tk.END, display_text)

            # Color code based on waiting time
            if customer.id in self.transitioning_customers:
                self.waiting_listbox.itemconfig(i, {'fg': '#4CAF50', 'selectforeground': '#4CAF50'})
                # Optional: fade out effect (simulate by graying out after short delay)
                def fade_out(idx=i):
                    self.waiting_listbox.itemconfig(idx, {'fg': '#BDBDBD', 'selectforeground': '#BDBDBD'})
                self.root.after(400, fade_out)
            elif waiting_time > 10:
                self.waiting_listbox.itemconfig(i, {'fg': '#f44336', 'selectforeground': '#f44336'})
            elif waiting_time > 5:
                self.waiting_listbox.itemconfig(i, {'fg': '#FF9800', 'selectforeground': '#FF9800'})
            else:
                self.waiting_listbox.itemconfig(i, {'fg': '#2196F3', 'selectforeground': '#2196F3'})

    def update_statistics(self):
        """Update the statistics display"""
        stats = self.restaurant.get_statistics()

        self.stats_labels['total_served'].config(text=str(stats['total_served']))
        self.stats_labels['current_waiting'].config(text=str(stats['current_waiting']))
        self.stats_labels['occupied_tables'].config(text=f"{stats['occupied_tables']}/3")
        self.stats_labels['avg_waiting_time'].config(text=f"{stats['avg_waiting_time']:.1f}s")
        self.stats_labels['max_waiting_time'].config(text=f"{stats['max_waiting_time']:.1f}s")

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function to run the restaurant simulation"""
    print("🍽️ Starting Restaurant Table Management System")
    print("This system demonstrates semaphore concepts using a restaurant scenario.")
    print("- Semaphore controls access to limited tables")
    print("- Customers wait when no tables are available")
    print("- Visual feedback shows table occupancy and customer queue")
    print()

    app = RestaurantGUI()
    app.run()

if __name__ == "__main__":
    main()
