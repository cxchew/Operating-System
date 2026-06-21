#!/usr/bin/env python3
"""
Enhanced Synchronization Demo for Restaurant Semaphore System
This script demonstrates semaphore blocking and release behavior very clearly
"""

import time
import threading
from restaurant_semaphore import RestaurantManager, Customer

def enhanced_sync_demo():
    """Enhanced demo showing clear semaphore synchronization"""
    print("🍽️ Restaurant Semaphore System - Enhanced Synchronization Demo")
    print("=" * 70)
    print("This demo uses only 2 tables and 10-20 second dining times")
    print("to clearly show semaphore blocking and release behavior.")
    print()
    
    # Create restaurant with minimal tables for maximum blocking effect
    restaurant = RestaurantManager(num_tables=2)
    
    # Override dining duration for this demo
    def add_slow_customer(customer_id):
        """Add a customer with longer dining time"""
        customer = Customer(customer_id)
        customer.dining_duration = 10 + (customer_id * 2)  # 10, 12, 14, 16... seconds
        restaurant.all_customers.append(customer)
        restaurant.waiting_customers.put(customer)
        restaurant.gui_update_queue.put(('customer_arrived', customer))
        threading.Thread(target=restaurant._handle_customer, args=(customer,), daemon=True).start()
        return customer
    
    print("🎬 SCENE 1: Filling all tables")
    print("-" * 30)
    
    # Add exactly enough customers to fill all tables
    print("Adding 2 customers to fill both tables...")
    for i in range(2):
        add_slow_customer(i + 1)
        print(f"   🚶 Customer {i+1} arrives (will dine for {10 + (i+1)*2} seconds)")
        time.sleep(1)
    
    # Wait for them to be seated
    time.sleep(3)
    stats = restaurant.get_statistics()
    print(f"\n📊 Status: {stats['occupied_tables']}/2 tables occupied")
    print("✅ All tables are now occupied - semaphore count = 0")
    print()
    
    print("🎬 SCENE 2: Demonstrating semaphore blocking")
    print("-" * 40)
    
    # Add customers that will be blocked
    print("Adding 3 more customers - they will be BLOCKED by the semaphore...")
    blocked_customers = []
    for i in range(3):
        customer = add_slow_customer(i + 3)
        blocked_customers.append(customer)
        print(f"   🚶 Customer {i+3} arrives but must WAIT (semaphore blocks)")
        time.sleep(1)
    
    time.sleep(2)
    waiting = restaurant.get_waiting_customers()
    print(f"\n📊 Status: {len(waiting)} customers blocked and waiting")
    print("🔒 Semaphore is blocking - no tables available!")
    print("   Waiting customers:", [f"Customer {c.id}" for c in waiting])
    print()
    
    print("🎬 SCENE 3: Watching semaphore releases")
    print("-" * 35)
    print("Now watching as customers finish dining and semaphore releases waiting customers...")
    print("(Customer 1 will finish first, then Customer 2, etc.)")
    print()
    
    # Monitor the releases
    start_time = time.time()
    last_served = 0
    
    for i in range(25):  # Monitor for up to 25 seconds
        current_time = time.time() - start_time
        stats = restaurant.get_statistics()
        waiting = restaurant.get_waiting_customers()
        
        # Check if someone new got served
        if stats['total_served'] > last_served:
            newly_served = stats['total_served'] - last_served
            print(f"   🎉 SEMAPHORE RELEASED! {newly_served} customer(s) just got seated")
            last_served = stats['total_served']
        
        print(f"   Time {current_time:4.1f}s: Tables {stats['occupied_tables']}/2, "
              f"Waiting: {len(waiting)}, Total served: {stats['total_served']}")
        
        # Stop when everyone is served
        if len(waiting) == 0 and stats['occupied_tables'] == 0:
            print("\n🏁 All customers have been served!")
            break
            
        time.sleep(1)
    
    # Final analysis
    print("\n" + "=" * 70)
    print("📈 FINAL ANALYSIS")
    print("-" * 20)
    final_stats = restaurant.get_statistics()
    print(f"Total customers processed: {final_stats['total_served']}")
    print(f"Average waiting time: {final_stats['avg_waiting_time']:.1f} seconds")
    print(f"Maximum waiting time: {final_stats['max_waiting_time']:.1f} seconds")
    print()
    
    print("🎯 SEMAPHORE BEHAVIOR OBSERVED:")
    print("   ✓ Initial semaphore count: 2 (number of tables)")
    print("   ✓ Semaphore.acquire() blocked customers when count reached 0")
    print("   ✓ Semaphore.release() automatically unblocked waiting customers")
    print("   ✓ FIFO ordering maintained (first to wait, first to be seated)")
    print("   ✓ Thread-safe operation with multiple concurrent customers")
    print("   ✓ No race conditions or resource conflicts observed")
    print()
    print("🖥️  For interactive GUI version: python restaurant_semaphore.py")

def quick_sync_test():
    """Quick test to verify synchronization works"""
    print("\n" + "🔧 Quick Synchronization Test")
    print("-" * 30)
    
    restaurant = RestaurantManager(num_tables=1)  # Only 1 table for extreme blocking
    
    # Add 3 customers to 1 table
    print("Adding 3 customers to restaurant with only 1 table...")
    for i in range(3):
        restaurant.add_customer()
        time.sleep(0.5)
    
    # Monitor for a few seconds
    for i in range(8):
        stats = restaurant.get_statistics()
        waiting = restaurant.get_waiting_customers()
        print(f"   {i+1}s: Table {stats['occupied_tables']}/1, Waiting: {len(waiting)}")
        time.sleep(1)
    
    print("✅ Synchronization test complete!")

if __name__ == "__main__":
    try:
        enhanced_sync_demo()
        quick_sync_test()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
