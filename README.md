# Database Reverse Engineering Analysis Tool

A powerful AI-powered tool that automatically analyzes database schemas, extracts metadata, and generates comprehensive insights for reverse engineering purposes.

## Problem Statement

Build a PoC to leverage an LLM to automatically analyze sample data and database schemas, extract metadata, and generate meaningful insights. This acts as a form of reverse engineering, helping engineers quickly grasp the data model, relationships, and potential use cases without manual exploration.

## Features

- **Automatic Schema Discovery**: Automatically extracts table structures, relationships, and constraints
- **AI-Powered Analysis**: Uses Google Gemini API for intelligent schema interpretation
- **Deep Business Insights**: Identifies business domains, use cases, and data patterns
- **Architecture Analysis**: Analyzes design patterns, normalization, and scalability
- **Performance Insights**: Identifies bottlenecks and optimization opportunities
- **Migration Planning**: Provides complexity assessment and migration strategies
- **Comprehensive Reports**: Generates detailed Markdown and JSON reports
- **Batch Processing**: Analyze multiple databases simultaneously using shell script
- **Automated Dependency Management**: Installs required packages automatically

## Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <your-repo>
cd pocdatabase

# Install dependencies
pip install -r requirment.txt

# Set up your Gemini API key
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 2. Analyze Any Database

```bash
# Analyze a single database
python analyze_any_database.py path/to/your/database.db

# Analyze with custom name and description
python analyze_any_database.py path/to/database.db --name "my_database" --description "Description of what this database contains"
```

### 3. Analyze All Databases (Recommended)

```bash
# Make the script executable (first time only)
chmod +x analyze_all_databases.sh

# Run the comprehensive analysis script
./analyze_all_databases.sh
```

### 4. View Available Databases

```bash
# See what databases are available for analysis
python analyze_any_database.py
```

## Shell Script Usage

### analyze_all_databases.sh

The `analyze_all_databases.sh` script provides a comprehensive, automated way to analyze all databases in your `New_DB` folder. It handles dependency installation, environment verification, and batch processing automatically.

#### Prerequisites

1. **Environment File**: Ensure you have a `.env` file with your Gemini API key:
   ```bash
   echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
   ```

2. **Executable Permissions**: Make the script executable:
   ```bash
   chmod +x analyze_all_databases.sh
   ```

#### Running the Script

**Interactive Mode (Recommended):**
```bash
./analyze_all_databases.sh
```

This launches an interactive menu with options:
- **Option 1**: Analyze all databases in New_DB folder
- **Option 2**: View available analysis reports
- **Option 3**: Open specific report
- **Option 4**: Exit

**Non-Interactive Mode:**
```bash
echo "1" | ./analyze_all_databases.sh
```

This automatically selects option 1 and starts analyzing all databases.

#### What the Script Does

1. **System Requirements Check**: Verifies Python installation and installs missing packages
2. **Dependency Installation**: Automatically installs required Python packages:
   - python-dotenv, pandas, matplotlib, seaborn
   - sqlalchemy, pymongo, google-generativeai
   - plotly, networkx
3. **Environment Verification**: Tests Python environment and analyzer scripts
4. **API Key Validation**: Ensures your Gemini API key is configured
5. **Database Discovery**: Automatically finds all `.db`, `.sqlite`, and `.sqlite3` files
6. **Batch Analysis**: Processes each database sequentially with comprehensive analysis
7. **Report Generation**: Creates detailed reports and visualizations
8. **Cleanup**: Removes temporary files, keeping only consolidated reports

#### Expected Results

The script will analyze all databases in your `New_DB` folder and generate:

**For Each Database:**
- **Comprehensive Analysis Report**: Detailed business insights and technical analysis
- **Visual Graphs**: Entity relationship diagrams, performance charts, and schema overviews
- **JSON Data**: Structured analysis data for programmatic use
- **Markdown Reports**: Human-readable analysis summaries

**Consolidated Output:**
- **consolidated_analysis/** folder containing all final reports
- **HTML Reports**: Interactive analysis reports with embedded visualizations
- **Graph Images**: PNG files showing database relationships and metrics

#### Analysis Time

- **Small databases** (1-5 tables): 1-3 minutes
- **Medium databases** (6-15 tables): 3-8 minutes  
- **Large databases** (15+ tables): 8-15 minutes

Total time depends on database complexity and API response times.

## Project Structure

```
pocdatabase/
├── src/                           # Core analysis engine
│   ├── analyzers/                 # AI analysis components
│   │   ├── gemini_analyzer.py    # Gemini API integration
│   │   └── pattern_analyzer.py   # Cross-database pattern analysis
│   ├── extractors/                # Schema extraction
│   │   └── schema_extractor.py   # Database schema extraction
│   ├── visualizers/               # Report and graph generation
│   │   ├── consolidated_report_generator.py
│   │   └── graph_generator.py
│   └── main_analyzer.py          # Main orchestration
├── New_DB/                        # Your databases to analyze
│   ├── sakila.db                 # Sample movie rental database
│   ├── Chinook_Sqlite.sqlite     # Sample music store database
│   └── superheroes.db            # Sample superheroes database
├── analyze_any_database.py        # Single database analysis tool
├── analyze_all_databases.sh       # Batch analysis shell script
├── universal_database_analyzer.py # Universal analysis tool
├── requirment.txt                 # Python dependencies
├── .env                          # API key configuration
└── README.md                     # This file
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### API Models

The tool uses `gemini-1.5-flash` by default for optimal performance and quota management.

## Analysis Output

### Generated Reports

For each database analysis, the tool generates:

1. **`reverse_engineering_report_*.md`** - Comprehensive analysis report
2. **`*_analysis_*.json`** - Detailed AI insights in JSON format
3. **`complete_analysis_*.json`** - Full analysis data
4. **`analysis.log`** - Processing logs
5. **`*_consolidated_analysis.md`** - Final consolidated reports
6. **`*_consolidated_analysis.json`** - Structured analysis data

### Report Contents

- **Business Domain Identification**: Primary domain, sub-domains, confidence scores
- **Data Model Architecture**: Design patterns, normalization, flexibility scores
- **Entity Relationship Mapping**: Core entities, relationships, business purposes
- **Data Quality Assessment**: Integrity, consistency, completeness metrics
- **Performance Analysis**: Bottlenecks, optimization opportunities
- **Use Case Analysis**: Primary use cases, analytics opportunities
- **Migration Insights**: Complexity assessment, effort estimates

## Example Analysis

### Sakila Database (Movie Rental)

```bash
python analyze_any_database.py New_DB/sakila.db
```

**Generated Insights:**
- **Business Domain**: Video Rental Store (98% confidence)
- **Architecture**: Traditional Relational with Entity-Relationship Model
- **Core Entities**: Film, Customer, Staff, Inventory, Rental, Payment
- **Relationships**: Film↔Actor (M:N), Customer↔Rental (1:M)
- **Use Cases**: Film rental, inventory management, CRM, financial reporting

### Superheroes Database

**Generated Insights:**
- **Business Domain**: Superhero Database (90% confidence)
- **Architecture**: Simple Entity Model
- **Core Entities**: Superhero profiles with appearance tracking
- **Use Cases**: Character lookup, statistical analysis, media tracking

### Chinook Database (Music Store)

**Generated Insights:**
- **Business Domain**: Music Sales and Streaming (98% confidence)
- **Architecture**: Traditional Relational with proper normalization
- **Core Entities**: Artist, Album, Track, Customer, Invoice
- **Use Cases**: Music sales, playlist management, customer analytics

## Supported Database Types

Currently supports:
- **SQLite** (`.db`, `.sqlite`, `.sqlite3`)

## Requirements

- Python 3.8+
- Google Gemini API key
- Dependencies listed in `requirment.txt`
- Bash shell (for shell script execution)

## Advanced Usage

### Batch Analysis

```bash
# Use the shell script for comprehensive batch analysis
./analyze_all_databases.sh

# Or analyze multiple databases manually
for db in New_DB/*.db; do
    python analyze_any_database.py "$db"
done
```

### Custom Analysis

The tool automatically detects:
- Table structures and relationships
- Foreign key constraints
- Indexes and performance indicators
- Data patterns and business logic
- Integration opportunities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different database types
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure `.env` file exists with valid `GEMINI_API_KEY`
2. **Quota Exceeded**: Switch to `gemini-1.5-flash` model (already configured)
3. **Database Not Found**: Check file path and ensure database file exists
4. **Permission Denied**: Make script executable with `chmod +x analyze_all_databases.sh`
5. **Missing Dependencies**: The shell script will automatically install required packages

### Getting Help

- Check the generated logs in analysis directories
- Verify your Gemini API key is valid
- Ensure database files are accessible
- Review the analysis.log files for detailed error information

---

**Built with Google Gemini AI for intelligent database reverse engineering**
