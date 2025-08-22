# Database Reverse Engineering Analysis Tool

A powerful AI-powered tool that automatically analyzes database schemas, extracts metadata, and generates comprehensive insights for reverse engineering purposes.

## 🎯 Problem Statement

Build a PoC to leverage an LLM to automatically analyze sample data and database schemas, extract metadata, and generate meaningful insights. This acts as a form of reverse engineering, helping engineers quickly grasp the data model, relationships, and potential use cases without manual exploration.

## ✨ Features

- **🔍 Automatic Schema Discovery**: Automatically extracts table structures, relationships, and constraints
- **🤖 AI-Powered Analysis**: Uses Google Gemini API for intelligent schema interpretation
- **📊 Deep Business Insights**: Identifies business domains, use cases, and data patterns
- **🏗️ Architecture Analysis**: Analyzes design patterns, normalization, and scalability
- **📈 Performance Insights**: Identifies bottlenecks and optimization opportunities
- **🔄 Migration Planning**: Provides complexity assessment and migration strategies
- **📄 Comprehensive Reports**: Generates detailed Markdown and JSON reports

## 🚀 Quick Start

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

### 3. View Available Databases

```bash
# See what databases are available for analysis
python analyze_any_database.py
```

## 📁 Project Structure

```
pocdatabase/
├── src/                           # Core analysis engine
│   ├── analyzers/                 # AI analysis components
│   │   ├── gemini_analyzer.py    # Gemini API integration
│   │   └── pattern_analyzer.py   # Cross-database pattern analysis
│   ├── extractors/                # Schema extraction
│   │   └── schema_extractor.py   # Database schema extraction
│   └── main_analyzer.py          # Main orchestration
├── New_DB/                        # Your databases to analyze
│   ├── sakila.db                 # Sample movie rental database
│   ├── Chinook_Sqlite.sqlite     # Sample music store database
│   └── superheroes.db            # Sample superheroes database
├── analyze_any_database.py        # Main analysis tool
├── requirment.txt                 # Python dependencies
├── .env                          # API key configuration
└── README.md                     # This file
```

pocdatabase/
├── src/                           # Core analysis engine
│   ├── analyzers/                 # AI analysis components
│   ├── extractors/                # Schema extraction
│   └── main_analyzer.py          # Main orchestration
├── New_DB/                        # Your databases to analyze
│   ├── sakila.db                 # Movie rental database
│   ├── Chinook_Sqlite.sqlite     # Music store database
│   └── superheroes.db            # Superheroes database
├── analyze_any_database.py        # Universal analysis tool
├── requirment.txt                 # Dependencies
├── .env                          # API key
└── README.md                     # Updated documentation

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### API Models

The tool uses `gemini-1.5-flash` by default for optimal performance and quota management.

## 📊 Analysis Output

### Generated Reports

For each database analysis, the tool generates:

1. **`reverse_engineering_report_*.md`** - Comprehensive analysis report
2. **`*_analysis_*.json`** - Detailed AI insights in JSON format
3. **`complete_analysis_*.json`** - Full analysis data
4. **`analysis.log`** - Processing logs

### Report Contents

- **Business Domain Identification**: Primary domain, sub-domains, confidence scores
- **Data Model Architecture**: Design patterns, normalization, flexibility scores
- **Entity Relationship Mapping**: Core entities, relationships, business purposes
- **Data Quality Assessment**: Integrity, consistency, completeness metrics
- **Performance Analysis**: Bottlenecks, optimization opportunities
- **Use Case Analysis**: Primary use cases, analytics opportunities
- **Migration Insights**: Complexity assessment, effort estimates

## 🎯 Example Analysis

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

## 🔍 Supported Database Types

Currently supports:
- **SQLite** (`.db`, `.sqlite`, `.sqlite3`)

## 📋 Requirements

- Python 3.8+
- Google Gemini API key
- Dependencies listed in `requirment.txt`

## 🚀 Advanced Usage

### Batch Analysis

```bash
# Analyze multiple databases
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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different database types
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure `.env` file exists with valid `GEMINI_API_KEY`
2. **Quota Exceeded**: Switch to `gemini-1.5-flash` model (already configured)
3. **Database Not Found**: Check file path and ensure database file exists

### Getting Help

- Check the generated logs in analysis directories
- Verify your Gemini API key is valid
- Ensure database files are accessible

---

**Built with ❤️ using Google Gemini AI for intelligent database reverse engineering**
