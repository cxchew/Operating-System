# 🍽️ Restaurant Table Management System - Semaphore Demo

A visual demonstration of semaphore concepts using a restaurant table management scenario. This system shows how semaphores control access to limited resources (restaurant tables) and manage waiting queues when resources are unavailable.

## 📋 Overview

This system demonstrates:
- **Semaphore**: Controls access to a limited number of restaurant tables
- **Resource Management**: Tables are finite resources that must be shared
- **Queue Management**: Customers wait in line when no tables are available
- **Thread Synchronization**: Multiple customers can arrive simultaneously
- **Visual Feedback**: Real-time GUI showing table occupancy and customer queue

## 🚀 Features

### Core Functionality
- **Limited Tables**: Configurable number of restaurant tables (default: 3)
- **Customer Simulation**: Automatic customer arrivals with configurable rates
- **Semaphore Control**: Thread-safe table allocation using Python's threading.Semaphore
- **Realistic Timing**: Random dining durations (8-15 seconds for clear demo)
- **Statistics Tracking**: Real-time metrics on service efficiency

### GUI Features
- **Visual Table Display**: Color-coded tables showing availability (green) and occupancy (pink)
- **Waiting Queue**: Live list of customers waiting for tables
- **Control Panel**: Start/stop simulation, add individual customers, reset system
- **Statistics Dashboard**: Real-time metrics including:
  - Total customers served
  - Current waiting count
  - Table occupancy
  - Average and maximum waiting times

## 🎮 How to Use

### Running the GUI Application
```bash
python restaurant_semaphore.py
```

### Control Panel Options
1. **Start Simulation**: Begin automatic customer arrivals
2. **Stop Simulation**: Pause automatic arrivals
3. **Add Customer**: Manually add a single customer
4. **Reset**: Clear all data and restart
5. **Arrival Rate**: Adjust time between automatic customer arrivals (seconds)

### Visual Elements
- **Green Tables**: Available for seating
- **Pink Tables**: Currently occupied
- **Waiting List**: Shows customer ID and waiting time
- **Statistics**: Live updates of system performance

## 🧪 Testing

Run the test suite to verify core functionality:
```bash
python test_restaurant.py
```

Run the enhanced synchronization demo:
```bash
python sync_demo.py
```

Run the quick demo:
```bash
python demo.py
```

The test suite includes:
- Basic restaurant operations
- Semaphore behavior with concurrent access
- Customer lifecycle tracking
- Enhanced synchronization demonstrations

## 🔧 Technical Implementation

### Key Components

1. **Semaphore**: `threading.Semaphore(num_tables)`
   - Controls access to limited table resources
   - Blocks customers when all tables are occupied
   - Releases resources when customers finish dining

2. **Customer Class**: Represents individual customers
   - Tracks arrival time, seating time, and dining duration
   - Manages customer state (waiting, seated, eating, finished)

3. **Table Class**: Represents restaurant tables
   - Tracks occupancy status and current customer
   - Manages seating and release operations

4. **RestaurantManager**: Core business logic
   - Handles customer arrivals and departures
   - Manages semaphore operations
   - Provides statistics and status updates

5. **RestaurantGUI**: Visual interface
   - Real-time display updates
   - User controls for simulation
   - Thread-safe GUI updates

### Thread Safety
- Uses `threading.Semaphore` for table access control
- Employs `queue.Queue` for thread-safe communication
- Implements proper locking for shared statistics

## 📊 Semaphore Concepts Demonstrated

### Resource Limitation
- **Finite Resources**: Only N tables available simultaneously
- **Mutual Exclusion**: Each table can seat only one customer at a time
- **Fair Access**: First-come, first-served table allocation

### Blocking and Signaling
- **Acquire**: Customer waits for available table (may block)
- **Release**: Customer frees table for next waiting customer
- **Queue Management**: Automatic handling of waiting customers

### Performance Metrics
- **Throughput**: Total customers served over time
- **Latency**: Average waiting time per customer
- **Utilization**: Percentage of tables occupied
- **Queue Length**: Number of customers waiting

## 🎯 Educational Value

This system helps understand:
- How semaphores prevent resource conflicts
- The relationship between resource count and system performance
- Queue formation when demand exceeds capacity
- The importance of proper resource release
- Real-world applications of synchronization primitives

## 🔄 Customization

You can modify the system by adjusting:
- Number of tables: Change `num_tables` parameter
- Dining duration: Modify `dining_duration` range in Customer class
- Arrival rate: Adjust through GUI or code
- Visual appearance: Customize colors and layout in GUI code

## 🐛 Troubleshooting

### Common Issues
1. **GUI not appearing**: Ensure tkinter is installed (`pip install tk`)
2. **Threading errors**: Check Python version (3.6+ recommended)
3. **Performance issues**: Reduce arrival rate or dining duration

### System Requirements
- Python 3.6 or higher
- tkinter (usually included with Python)
- threading module (standard library)

## 📚 Learning Extensions

Try these modifications to deepen understanding:
1. Add priority customers (VIP queue)
2. Implement table reservations
3. Add different table sizes (2-person, 4-person, etc.)
4. Create multiple restaurant locations
5. Add waiter resources as another semaphore layer

---

**Note**: This is an educational demonstration. Dining times are set to 8-15 seconds to clearly show semaphore blocking and release behavior. Use the enhanced sync demo (`python sync_demo.py`) for the clearest demonstration of synchronization concepts.
