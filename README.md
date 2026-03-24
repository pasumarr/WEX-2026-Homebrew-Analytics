# Homebrew Analytics Tracker

A data pipeline that collects and analyzes Homebrew package installation statistics over time using the Homebrew API.

## Project Overview

This project fetches data from the [Homebrew Analytics API](https://formulae.brew.sh/analytics/) and tracks the top 5 most-installed packages daily, storing snapshots in a SQLite database. The goal is to identify trending packages and understand installation patterns over time.

## Features

- **Automated Data Collection**: Fetches top package data from Homebrew API
- **SQLite Database Storage**: Stores historical snapshots with proper relational structure
- **Trend Analysis**: Compares package popularity across different time periods
- **Web Visualization**: Flask-based web application to display trends (coming soon)

## Technology Stack

- **Language**: Python 3
- **Database**: SQLite
- **Web Framework**: Flask (planned)
- **Visualization**: Chart.js (planned)
- **API**: [Homebrew Formulae Analytics API](https://formulae.brew.sh/api/analytics/install/30d.json)

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/homebrew-analytics.git
cd homebrew-analytics
```

2. Install required dependencies:
```bash
pip install requests
```

3. Run the tracker:
```bash
python3 homebrew_tracker_sqlite.py
```

## Usage

### Manual Collection
Run the script manually to collect a snapshot:
```bash
python3 homebrew_tracker_sqlite.py
```

Or use the convenient run script:
```bash
python3 run_collection.py
```

### Automated Collection (Optional)

**Mac/Linux (Cron):**
```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

**Windows (Task Scheduler):**
See `WINDOWS_SCHEDULER_GUIDE.md` for detailed instructions.

## Database Structure

The SQLite database (`homebrew_analytics.db`) contains two tables:

### `snapshots` table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| timestamp | TEXT | When the snapshot was taken |
| date | TEXT | Date of snapshot (YYYY-MM-DD) |
| total_packages | INTEGER | Total packages in API response |
| api_start_date | TEXT | Start date of API data range |
| api_end_date | TEXT | End date of API data range |

### `packages` table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| snapshot_id | INTEGER | Foreign key to snapshots table |
| package_name | TEXT | Name of the package |
| install_count | INTEGER | Number of installations |
| percentage | TEXT | Percentage of total installs |
| rank | INTEGER | Rank in top packages |

## Viewing the Data

### Option 1: DB Browser for SQLite
Download [DB Browser for SQLite](https://sqlitebrowser.org/) to visually explore the database.

### Option 2: SQL Queries
Connect to the database and run queries:
```bash
sqlite3 homebrew_analytics.db
```

Example queries:
```sql
-- View all snapshots
SELECT * FROM snapshots ORDER BY date DESC;

-- View latest top 5 packages
SELECT p.package_name, p.install_count, p.rank
FROM packages p
JOIN snapshots s ON p.snapshot_id = s.id
WHERE s.id = (SELECT MAX(id) FROM snapshots)
ORDER BY p.rank;

-- Compare first vs latest snapshot
SELECT 
    l.package_name,
    f.install_count as first_count,
    l.install_count as latest_count,
    l.install_count - f.install_count as change
FROM packages l
JOIN packages f ON l.package_name = f.package_name
WHERE l.snapshot_id = (SELECT MAX(id) FROM snapshots)
  AND f.snapshot_id = (SELECT MIN(id) FROM snapshots)
ORDER BY l.rank;
```

## Project Goals

This project demonstrates:
1. **API Integration**: How to fetch and parse data from external APIs
2. **Data Pipeline**: Building a system that collects, processes, and stores data
3. **Database Design**: Proper relational database structure with foreign keys
4. **Data Analysis**: Identifying trends and patterns over time
5. **Web Development**: Creating a web interface for data visualization (in progress)

## Roadmap

- [x] Basic API data collection
- [x] SQLite database implementation
- [x] Trend analysis functionality
- [ ] Flask web application
- [ ] Interactive charts and graphs
- [ ] Date range filtering
- [ ] Export functionality (CSV/Excel)

## Learning Outcomes

Through this project, I learned:
- How RESTful APIs work and how to consume them
- Database design principles (normalization, foreign keys, indexes)
- SQL queries for data analysis
- Python best practices (error handling, modularity)
- Data pipeline architecture
- The importance of data validation and storage

## API Reference

**Endpoint**: `https://formulae.brew.sh/api/analytics/install/30d.json`

**Response Structure**:
```json
{
  "category": "formula_install",
  "total_items": 22771,
  "start_date": "2026-02-18",
  "end_date": "2026-03-20",
  "items": [
    {
      "number": 1,
      "formula": "openssl",
      "count": "515827",
      "percent": "1.89"
    }
  ]
}
```

## Contributing

This is a learning project for understanding web development and APIs. Feedback and suggestions are welcome!

## License

MIT License - feel free to use this for your own learning.

## Acknowledgments

- [Homebrew](https://brew.sh/) for providing the analytics API
- Falcon Technologies internship program
- Course instructor for project guidance

## Contact

[Your Name]  
[Your Email]  
[LinkedIn Profile]

---

**Note**: This project is part of my web development learning journey at Falcon Technologies. The goal is to understand how APIs, databases, and web applications work together to create data-driven applications.
