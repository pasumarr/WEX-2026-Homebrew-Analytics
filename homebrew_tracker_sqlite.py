#!/usr/bin/env python3
"""
Homebrew Package Tracker with SQLite Database
==============================================
This is the CORRECT version that stores data in a SQLite database.

Database Structure:
- snapshots table: Records each time we run the script
- packages table: Stores package data for each snapshot

Why SQLite?
- It's a real database (like what companies use)
- Stores data properly with relationships
- Easy to query and analyze
- Can handle lots of data
- Works with DB Browser for SQLite (visual tool)
"""

import requests
import sqlite3
from datetime import datetime
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "https://formulae.brew.sh/api/analytics/install/30d.json"
DATABASE_FILE = "homebrew_analytics.db"
TOP_N = 5

# ============================================================================
# DATABASE SETUP
# ============================================================================

def setup_database():
    """
    Create the database and tables if they don't exist.
    
    This creates two tables:
    1. snapshots - One row for each time we run the script
    2. packages - One row for each package in each snapshot
    
    This is called a "relational database" because the tables are related!
    """
    print("📊 Setting up database...")
    
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create snapshots table
    # This stores metadata about each time we collected data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            total_packages INTEGER,
            api_start_date TEXT,
            api_end_date TEXT
        )
    ''')
    
    # Create packages table
    # This stores the actual package data
    # snapshot_id is a "foreign key" - it links to the snapshots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER NOT NULL,
            package_name TEXT NOT NULL,
            install_count INTEGER NOT NULL,
            percentage TEXT,
            rank INTEGER,
            FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
        )
    ''')
    
    # Create an index to make queries faster
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_snapshot_id 
        ON packages(snapshot_id)
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database ready: {DATABASE_FILE}")

# ============================================================================
# API FUNCTIONS
# ============================================================================

def fetch_api_data():
    """Fetch data from Homebrew API."""
    print("\n📡 Fetching data from Homebrew API...")
    print(f"   URL: {API_URL}")
    
    try:
        response = requests.get(API_URL, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Got {len(data.get('items', []))} packages")
            return data
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def save_snapshot(api_data):
    """
    Save a new snapshot to the database.
    
    This is a "transaction" - either all the data gets saved, or none of it.
    That's important for data integrity!
    """
    print("\n💾 Saving snapshot to database...")
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        # Insert snapshot record
        cursor.execute('''
            INSERT INTO snapshots (timestamp, date, total_packages, api_start_date, api_end_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            datetime.now().strftime('%Y-%m-%d'),
            api_data.get('total_items', 0),
            api_data.get('start_date'),
            api_data.get('end_date')
        ))
        
        # Get the ID of the snapshot we just inserted
        snapshot_id = cursor.lastrowid
        print(f"   Created snapshot #{snapshot_id}")
        
        # Insert top N packages for this snapshot
        items = api_data.get('items', [])[:TOP_N]
        
        for item in items:
            cursor.execute('''
                INSERT INTO packages (snapshot_id, package_name, install_count, percentage, rank)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                snapshot_id,
                item['formula'],
                int(item['count'].replace(',', '')),
                item['percent'],
                item['number']
            ))
            
            print(f"   └─ Saved: {item['formula']} ({item['count']} installs)")
        
        # Commit the transaction (save everything)
        conn.commit()
        print("✅ Snapshot saved successfully!")
        
        return snapshot_id
    
    except Exception as e:
        # If anything goes wrong, rollback (undo everything)
        conn.rollback()
        print(f"❌ Error saving snapshot: {e}")
        return None
    
    finally:
        conn.close()

def get_snapshot_count():
    """Get the total number of snapshots in the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM snapshots')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

def show_database_summary():
    """Display a summary of what's in the database."""
    print("\n" + "=" * 60)
    print("📊 DATABASE SUMMARY")
    print("=" * 60)
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Get total snapshots
    cursor.execute('SELECT COUNT(*) FROM snapshots')
    snapshot_count = cursor.fetchone()[0]
    
    # Get date range
    cursor.execute('SELECT MIN(date), MAX(date) FROM snapshots')
    first_date, last_date = cursor.fetchone()
    
    print(f"Total snapshots: {snapshot_count}")
    if snapshot_count > 0:
        print(f"Date range: {first_date} to {last_date}")
    
    # Get latest top packages
    cursor.execute('''
        SELECT p.rank, p.package_name, p.install_count, p.percentage
        FROM packages p
        JOIN snapshots s ON p.snapshot_id = s.id
        WHERE s.id = (SELECT MAX(id) FROM snapshots)
        ORDER BY p.rank
    ''')
    
    print(f"\nLatest Top {TOP_N} Packages:")
    for rank, name, count, pct in cursor.fetchall():
        print(f"  #{rank}: {name:20} - {count:,} installs ({pct}%)")
    
    # Show trend if we have multiple snapshots
    if snapshot_count >= 2:
        print("\n📈 TREND (First vs Latest):")
        
        # This is a more complex SQL query - it compares first and last snapshots
        cursor.execute('''
            WITH first_snapshot AS (
                SELECT package_name, install_count
                FROM packages
                WHERE snapshot_id = (SELECT MIN(id) FROM snapshots)
            ),
            last_snapshot AS (
                SELECT package_name, install_count
                FROM packages
                WHERE snapshot_id = (SELECT MAX(id) FROM snapshots)
            )
            SELECT 
                l.package_name,
                f.install_count as first_count,
                l.install_count as last_count,
                l.install_count - COALESCE(f.install_count, 0) as change
            FROM last_snapshot l
            LEFT JOIN first_snapshot f ON l.package_name = f.package_name
            ORDER BY l.install_count DESC
        ''')
        
        for name, first, last, change in cursor.fetchall():
            if change > 0:
                print(f"  {name:20} ↗ +{change:,}")
            elif change < 0:
                print(f"  {name:20} ↘ {change:,}")
            else:
                print(f"  {name:20} → No change")
    
    conn.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 60)
    print("🍺 HOMEBREW ANALYTICS TRACKER")
    print("   Using SQLite Database")
    print("=" * 60)
    
    # Step 1: Setup database
    setup_database()
    
    # Step 2: Fetch API data
    api_data = fetch_api_data()
    
    if not api_data:
        print("\n❌ Failed to fetch API data. Exiting.")
        return
    
    # Step 3: Save to database
    snapshot_id = save_snapshot(api_data)
    
    if not snapshot_id:
        print("\n❌ Failed to save snapshot. Exiting.")
        return
    
    # Step 4: Show summary
    show_database_summary()
    
    # Step 5: Instructions
    print("\n" + "=" * 60)
    print("✨ NEXT STEPS:")
    print("=" * 60)
    print("1. Run this script daily to collect more snapshots")
    print("2. Open the database with DB Browser for SQLite:")
    print(f"   File: {DATABASE_FILE}")
    print("3. You can run SQL queries to analyze the data")
    print("4. Next: Build a web app to visualize this data!")
    print("=" * 60)

if __name__ == "__main__":
    main()
