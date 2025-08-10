import argparse
import sys
import subprocess
from configparser import ConfigParser
from log_parser import LogParser
from mysql_handler import MySQLHandler
from generate_reports import ReportGenerator

def load_config():
    """Load configuration from config.ini"""
    try:
        config = ConfigParser()
        config.read('config.ini')
        return {
            'host': config['mysql']['host'],
            'user': config['mysql']['user'],
            'password': config['mysql']['password'],
            'database': config['mysql']['database']
        }
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Please ensure config.ini exists with proper MySQL configuration.")
        sys.exit(1)

def process_logs(file_path):
    """Process log file and store in database"""
    print(f"Processing log file: {file_path}")
    
    # Initialize components
    parser = LogParser()
    db_handler = MySQLHandler(load_config())
    
    # Connect to database
    if not db_handler.connect():
        print("Failed to connect to database. Exiting.")
        return False
    
    try:
        # Process logs in batches for better performance
        batch_size = 1000
        batch = []
        total_processed = 0
        
        for log_entry in parser.parse_file(file_path):
            batch.append(log_entry)
            
            if len(batch) >= batch_size:
                if db_handler.insert_log_entries_batch(batch):
                    total_processed += len(batch)
                    print(f"Processed {total_processed} log entries...")
                else:
                    print("Error inserting batch. Stopping.")
                    return False
                batch = []
        
        # Process remaining entries
        if batch:
            if db_handler.insert_log_entries_batch(batch):
                total_processed += len(batch)
            else:
                print("Error inserting final batch.")
                return False
        
        print(f"Successfully processed {total_processed} log entries.")
        return True
        
    except Exception as e:
        print(f"Error processing logs: {e}")
        return False
    finally:
        db_handler.disconnect()

def generate_report(report_type):
    """Generate specified report"""
    db_handler = MySQLHandler(load_config())
    
    if not db_handler.connect():
        print("Failed to connect to database. Exiting.")
        return False
    
    try:
        report_generator = ReportGenerator(db_handler)
        
        if report_type == 'top_n_ips':
            report_generator.generate_top_n_ips_report(10)
        elif report_type == 'status_codes':
            report_generator.generate_status_code_report()
        elif report_type == 'hourly_traffic':
            report_generator.generate_hourly_traffic_report()
        elif report_type == 'resource_analysis':
            report_generator.generate_resource_analysis_report(10)
        elif report_type == 'error_analysis':
            report_generator.generate_error_analysis_report()
        elif report_type == 'summary':
            report_generator.generate_summary_report()
        elif report_type == 'save_charts':
            report_generator.save_charts()
        else:
            print(f"Unknown report type: {report_type}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error generating report: {e}")
        return False
    finally:
        db_handler.disconnect()

def launch_dashboard():
    """Launch Streamlit dashboard"""
    try:
        print("Launching Log Analyzer Dashboard...")
        print("Dashboard will open in your default web browser.")
        print("Press Ctrl+C to stop the dashboard.")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_dashboard.py"])
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    except Exception as e:
        print(f"Error launching dashboard: {e}")

def main():
    parser = argparse.ArgumentParser(description='Log File Analysis & Reporting System')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process logs command
    process_parser = subparsers.add_parser('process_logs', help='Process log files and store in database')
    process_parser.add_argument('file_path', help='Path to the log file to process')
    
    # Generate report command
    report_parser = subparsers.add_parser('generate_report', help='Generate analysis reports')
    report_parser.add_argument('report_type', 
                              choices=['top_n_ips', 'status_codes', 'hourly_traffic', 
                                     'resource_analysis', 'error_analysis', 'summary', 'save_charts'],
                              help='Type of report to generate')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch interactive web dashboard')
    
    args = parser.parse_args()
    
    if args.command == 'process_logs':
        success = process_logs(args.file_path)
        sys.exit(0 if success else 1)
    
    elif args.command == 'generate_report':
        success = generate_report(args.report_type)
        sys.exit(0 if success else 1)
    
    elif args.command == 'dashboard':
        launch_dashboard()
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
