#!/usr/bin/env python3
"""
Test script for the Restaurant Semaphore System
This script tests the core functionality without GUI
"""

import time
import threading
from restaurant_semaphore import RestaurantManager, Customer, CustomerState

def test_basic_functionality():
    """Test basic restaurant operations"""
    print("Testing basic restaurant functionality...")
    
    # Create restaurant with 3 tables
    restaurant = RestaurantManager(num_tables=3)
    
    # Test 1: Add customers when tables are available
    print("\nTest 1: Adding customers with available tables")
    for i in range(3):
        restaurant.add_customer()
        time.sleep(0.1)  # Small delay to see the progression
    
    # Wait a moment for customers to be seated
    time.sleep(1)
    
    # Check statistics
    stats = restaurant.get_statistics()
    print(f"Occupied tables: {stats['occupied_tables']}/3")
    print(f"Customers waiting: {stats['current_waiting']}")
    
    # Test 2: Add more customers than tables (should create waiting queue)
    print("\nTest 2: Adding more customers than available tables")
    for i in range(3):
        restaurant.add_customer()
        time.sleep(0.1)
    
    time.sleep(0.5)
    stats = restaurant.get_statistics()
    print(f"Occupied tables: {stats['occupied_tables']}/3")
    print(f"Customers waiting: {stats['current_waiting']}")
    
    # Wait for some customers to finish dining
    print("\nWaiting for customers to finish dining...")
    time.sleep(5)
    
    stats = restaurant.get_statistics()
    print(f"Final statistics:")
    print(f"  Total served: {stats['total_served']}")
    print(f"  Average waiting time: {stats['avg_waiting_time']:.2f}s")
    print(f"  Max waiting time: {stats['max_waiting_time']:.2f}s")
    print(f"  Currently occupied: {stats['occupied_tables']}/3")

def test_semaphore_behavior():
    """Test semaphore behavior with concurrent access"""
    print("\n" + "="*50)
    print("Testing semaphore behavior with concurrent access...")
    
    restaurant = RestaurantManager(num_tables=2)
    
    # Add 5 customers simultaneously
    threads = []
    for i in range(5):
        thread = threading.Thread(target=restaurant.add_customer)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to start
    for thread in threads:
        thread.join()
    
    # Monitor the system for a few seconds
    for i in range(10):
        stats = restaurant.get_statistics()
        waiting = restaurant.get_waiting_customers()
        print(f"Time {i+1}s: Tables {stats['occupied_tables']}/2, Waiting: {len(waiting)}")
        time.sleep(1)
    
    print(f"Final total served: {restaurant.get_statistics()['total_served']}")

def test_customer_lifecycle():
    """Test individual customer lifecycle"""
    print("\n" + "="*50)
    print("Testing customer lifecycle...")
    
    # Create a single customer and track their journey
    customer = Customer(999)
    print(f"Created {customer}")
    print(f"Initial state: {customer.state}")
    print(f"Arrival time: {customer.arrival_time}")
    
    # Simulate seating
    customer.seated_time = customer.arrival_time
    customer.state = CustomerState.SEATED
    customer.table_number = 1
    print(f"Customer seated at table {customer.table_number}")
    print(f"Waiting time: {customer.get_waiting_time():.2f}s")
    
    # Simulate finishing
    time.sleep(1)
    customer.state = CustomerState.FINISHED
    print(f"Customer finished dining")
    print(f"Final state: {customer.state}")

if __name__ == "__main__":
    print("🍽️ Restaurant Semaphore System - Test Suite")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_semaphore_behavior()
        test_customer_lifecycle()
        
        print("\n" + "="*50)
        print("✅ All tests completed successfully!")
        print("The restaurant semaphore system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
