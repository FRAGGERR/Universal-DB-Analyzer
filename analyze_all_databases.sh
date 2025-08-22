#!/bin/bash

# Database Analysis and Viewer Script
# This script analyzes all databases in the New_DB folder and allows users to view results

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if Python and required packages are available
check_requirements() {
    print_status "Checking system requirements..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    if ! python3 -c "import dotenv" &> /dev/null; then
        print_warning "python-dotenv not found. Installing..."
        pip3 install python-dotenv
    fi
    
    if ! python3 -c "import pandas" &> /dev/null; then
        print_warning "pandas not found. Installing..."
        pip3 install pandas
    fi
    
    if ! python3 -c "import matplotlib" &> /dev/null; then
        print_warning "matplotlib not found. Installing..."
        pip3 install matplotlib
    fi
    
    if ! python3 -c "import seaborn" &> /dev/null; then
        print_warning "seaborn not found. Installing..."
        pip3 install seaborn
    fi
    
    print_status "All requirements satisfied!"
}

# Function to check if .env file exists with API key
check_api_key() {
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        echo "Please create a .env file with your Gemini API key:"
        echo "GEMINI_API_KEY=your_api_key_here"
        exit 1
    fi
    
    if ! grep -q "GEMINI_API_KEY" .env; then
        print_error "GEMINI_API_KEY not found in .env file!"
        echo "Please add GEMINI_API_KEY=your_api_key_here to your .env file"
        exit 1
    fi
    
    print_status "API key configuration found!"
}

# Function to analyze a single database
analyze_database() {
    local db_path="$1"
    local db_name="$2"
    
    print_status "Analyzing database: $db_name"
    
    # Run the analysis using the universal analyzer
    python3 universal_database_analyzer.py "$db_path" "$db_name" "" "" true false
    
    if [ $? -eq 0 ]; then
        print_status "✅ Analysis completed for $db_name"
        return 0
    else
        print_error "❌ Analysis failed for $db_name"
        return 1
    fi
}

# Function to analyze all databases in NEW_DB folder
analyze_all_databases() {
    print_header "Database Analysis"
    
    if [ ! -d "New_DB" ]; then
        print_error "New_DB folder not found!"
        exit 1
    fi
    
    # Find all database files
    local db_files=()
    local db_names=()
    
    # Look for common database file extensions
    for ext in db sqlite sqlite3; do
        while IFS= read -r -d '' file; do
            db_files+=("$file")
            db_names+=("$(basename "$file" ".$ext")")
        done < <(find "New_DB" -name "*.$ext" -print0 2>/dev/null)
    done
    
    if [ ${#db_files[@]} -eq 0 ]; then
        print_warning "No database files found in New_DB folder!"
        echo "Supported formats: .db, .sqlite, .sqlite3"
        exit 1
    fi
    
    print_status "Found ${#db_files[@]} database(s):"
    for i in "${!db_files[@]}"; do
        echo "  $((i+1)). ${db_names[$i]} (${db_files[$i]})"
    done
    
    echo
    echo "Starting analysis of all databases..."
    echo "This may take several minutes depending on database sizes..."
    echo
    
    # Analyze each database
    local successful_analyses=()
    local failed_analyses=()
    
    for i in "${!db_files[@]}"; do
        local db_path="${db_files[$i]}"
        local db_name="${db_names[$i]}"
        
        echo "🔍 Processing $((i+1))/${#db_files[@]}: $db_name"
        
        if analyze_database "$db_path" "$db_name"; then
            successful_analyses+=("$db_name")
        else
            failed_analyses+=("$db_name")
        fi
        
        echo  # Add spacing between analyses
    done
    
    # Summary
    print_header "Analysis Summary"
    echo "✅ Successful analyses: ${#successful_analyses[@]}"
    for db in "${successful_analyses[@]}"; do
        echo "   - $db"
    done
    
    if [ ${#failed_analyses[@]} -gt 0 ]; then
        echo "❌ Failed analyses: ${#failed_analyses[@]}"
        for db in "${failed_analyses[@]}"; do
            echo "   - $db"
        done
    fi
    
    echo
    print_status "All analyses completed! Consolidated reports are available in the 'consolidated_analysis' folder."
}

# Function to show available consolidated reports
show_available_reports() {
    print_header "Available Analysis Reports"
    
    if [ ! -d "consolidated_analysis" ]; then
        print_warning "No consolidated analysis folder found!"
        echo "Please run database analysis first."
        return 1
    fi
    
    local reports=()
    while IFS= read -r -d '' file; do
        if [[ "$file" == *"_consolidated_analysis.md" ]]; then
            reports+=("$file")
        fi
    done < <(find "consolidated_analysis" -name "*_consolidated_analysis.md" -print0 2>/dev/null)
    
    if [ ${#reports[@]} -eq 0 ]; then
        print_warning "No consolidated analysis reports found!"
        echo "Please run database analysis first."
        return 1
    fi
    
    echo "Available reports:"
    for i in "${!reports[@]}"; do
        local filename=$(basename "${reports[$i]}")
        local db_name=$(echo "$filename" | sed 's/_consolidated_analysis\.md$//')
        echo "  $((i+1)). $db_name"
    done
    
    return 0
}

# Function to open a specific report
open_report() {
    local db_name="$1"
    local report_path="consolidated_analysis/${db_name}_consolidated_analysis.md"
    
    if [ ! -f "$report_path" ]; then
        print_error "Report not found: $report_path"
        return 1
    fi
    
    print_status "Opening report for: $db_name"
    
    # Try to open with different applications based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v open &> /dev/null; then
            open "$report_path"
        else
            print_error "Could not open report on macOS"
            return 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open &> /dev/null; then
            xdg-open "$report_path"
        elif command -v gnome-open &> /dev/null; then
            gnome-open "$report_path"
        else
            print_error "Could not open report on Linux"
            return 1
        fi
    else
        print_warning "Unsupported OS. Please open manually: $report_path"
        return 1
    fi
    
    print_status "✅ Report opened successfully!"
}

# Function to show interactive menu
show_menu() {
    while true; do
        echo
        print_header "Database Analysis Menu"
        echo "1. Analyze all databases in New_DB folder"
        echo "2. View available analysis reports"
        echo "3. Open specific report"
        echo "4. Exit"
        echo
        read -p "Select an option (1-4): " choice
        
        case $choice in
            1)
                analyze_all_databases
                ;;
            2)
                show_available_reports
                ;;
            3)
                if show_available_reports; then
                    echo
                    read -p "Enter the database name to open (or 'back' to return): " db_name
                    if [ "$db_name" != "back" ]; then
                        open_report "$db_name"
                    fi
                fi
                ;;
            4)
                print_status "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 1-4."
                ;;
        esac
        
        echo
        read -p "Press Enter to continue..."
    done
}

# Main script execution
main() {
    print_header "Universal Database Analyzer"
    echo "This script will analyze all databases in the New_DB folder"
    echo "and generate comprehensive reports with embedded visualizations."
    echo
    
    # Check requirements
    check_requirements
    
    # Check API key
    check_api_key
    
    # Show menu
    show_menu
}

# Run main function
main "$@"
