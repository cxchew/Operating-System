#!/usr/bin/env python3
"""
Quick demonstration of the Restaurant Semaphore System
This script shows a brief automated demo of the system
"""

import time
from restaurant_semaphore import RestaurantManager

def run_demo():
    """Run a quick demonstration of the restaurant system"""
    print("🍽️ Restaurant Semaphore System - Quick Demo")
    print("=" * 50)
    print("This demo shows how semaphores control access to limited restaurant tables.")
    print()
    
    # Create restaurant with 2 tables for better demo
    restaurant = RestaurantManager(num_tables=2)
    
    print("📊 Initial State:")
    stats = restaurant.get_statistics()
    print(f"   Tables available: {2 - stats['occupied_tables']}/2")
    print(f"   Customers waiting: {stats['current_waiting']}")
    print()

    # Phase 1: Add customers equal to table count
    print("🚶 Phase 1: Adding 2 customers (equal to table count)")
    for i in range(2):
        restaurant.add_customer()
        print(f"   Customer {i+1} added")
        time.sleep(1)

    time.sleep(2)
    stats = restaurant.get_statistics()
    print(f"   Result: {stats['occupied_tables']}/2 tables occupied, {stats['current_waiting']} waiting")
    print("   ✓ All tables are now occupied - semaphore will block new customers")
    print()

    # Phase 2: Add more customers than tables
    print("🚶🚶 Phase 2: Adding 5 more customers (exceeding table capacity)")
    print("   Watch how semaphore blocks these customers until tables become free...")
    for i in range(5):
        restaurant.add_customer()
        print(f"   Customer {i+3} added (will wait for table)")
        time.sleep(1)

    time.sleep(2)
    stats = restaurant.get_statistics()
    waiting = restaurant.get_waiting_customers()
    print(f"   Result: {stats['occupied_tables']}/2 tables occupied, {len(waiting)} customers waiting")
    print("   Waiting customers:", [f"Customer {c.id}" for c in waiting])
    print("   ⚠️  Semaphore is blocking - customers must wait!")
    print()

    # Phase 3: Monitor as customers finish dining
    print("⏰ Phase 3: Monitoring as customers finish dining (8-15 second meals)...")
    print("   Watch how semaphore automatically releases waiting customers:")
    for i in range(20):
        stats = restaurant.get_statistics()
        waiting = restaurant.get_waiting_customers()
        print(f"   Time {i+1}s: Tables {stats['occupied_tables']}/2, Waiting: {len(waiting)}")
        if len(waiting) == 0 and stats['occupied_tables'] == 0:
            print("   🎉 All customers served!")
            break
        time.sleep(1)
    
    # Final statistics
    print()
    print("📈 Final Statistics:")
    stats = restaurant.get_statistics()
    print(f"   Total customers served: {stats['total_served']}")
    print(f"   Average waiting time: {stats['avg_waiting_time']:.2f} seconds")
    print(f"   Maximum waiting time: {stats['max_waiting_time']:.2f} seconds")
    print(f"   Current table occupancy: {stats['occupied_tables']}/2")
    print()

    print("🎯 Key Semaphore Concepts Demonstrated:")
    print("   ✓ Resource limitation (only 2 tables available)")
    print("   ✓ Blocking behavior (customers wait when tables full)")
    print("   ✓ Automatic queue management (FIFO ordering)")
    print("   ✓ Resource release (tables freed when customers finish)")
    print("   ✓ Thread safety (concurrent customer handling)")
    print("   ✓ Longer dining times (8-15 seconds) show clear synchronization")
    print()
    
    print("🖥️  To see the full GUI version, run: python restaurant_semaphore.py")

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
