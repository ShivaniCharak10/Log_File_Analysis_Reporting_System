from mysql_handler import MySQLHandler
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class ReportGenerator:
    def __init__(self, db_handler):
        self.db = db_handler
    
    def generate_top_n_ips_report(self, n=10):
        """Generate report for top N IP addresses"""
        print(f"\n{'='*50}")
        print(f"TOP {n} IP ADDRESSES BY REQUEST COUNT")
        print(f"{'='*50}")
        
        data = self.db.get_top_n_ips(n)
        if not data:
            print("No data available.")
            return
        
        print(f"{'Rank':<6} {'IP Address':<15} {'Request Count':<15}")
        print("-" * 40)
        
        for i, row in enumerate(data, 1):
            print(f"{i:<6} {row['ip_address']:<15} {row['request_count']:<15}")
        
        return data
    
    def generate_status_code_report(self):
        """Generate HTTP status code distribution report"""
        print(f"\n{'='*50}")
        print("HTTP STATUS CODE DISTRIBUTION")
        print(f"{'='*50}")
        
        data = self.db.get_status_code_distribution()
        if not data:
            print("No data available.")
            return
        
        print(f"{'Status Code':<12} {'Count':<10} {'Percentage':<12}")
        print("-" * 35)
        
        for row in data:
            print(f"{row['status_code']:<12} {row['count']:<10} {row['percentage']:<12}%")
        
        return data
    
    def generate_hourly_traffic_report(self):
        """Generate hourly traffic distribution report"""
        print(f"\n{'='*50}")
        print("HOURLY TRAFFIC DISTRIBUTION")
        print(f"{'='*50}")
        
        data = self.db.get_hourly_traffic()
        if not data:
            print("No data available.")
            return
        
        print(f"{'Hour':<6} {'Request Count':<15} {'Bar Chart':<30}")
        print("-" * 55)
        
        max_count = max(row['request_count'] for row in data) if data else 1
        
        for row in data:
            hour = f"{row['hour']:02d}:00"
            count = row['request_count']
            bar_length = int((count / max_count) * 20)
            bar = "█" * bar_length
            print(f"{hour:<6} {count:<15} {bar:<30}")
        
        return data
    
    def generate_resource_analysis_report(self, n=10):
        """Generate top requested resources report"""
        print(f"\n{'='*50}")
        print(f"TOP {n} REQUESTED RESOURCES")
        print(f"{'='*50}")
        
        data = self.db.get_resource_analysis(n)
        if not data:
            print("No data available.")
            return
        
        print(f"{'Rank':<6} {'Resource':<40} {'Count':<10} {'Avg Size':<12}")
        print("-" * 70)
        
        for i, row in enumerate(data, 1):
            resource = row['resource'][:37] + "..." if len(row['resource']) > 40 else row['resource']
            avg_size = f"{row['avg_size']:.2f}" if row['avg_size'] else "0"
            print(f"{i:<6} {resource:<40} {row['request_count']:<10} {avg_size:<12}")
        
        return data
    
    def generate_error_analysis_report(self):
        """Generate error analysis report"""
        print(f"\n{'='*50}")
        print("ERROR ANALYSIS (4xx & 5xx STATUS CODES)")
        print(f"{'='*50}")
        
        data = self.db.get_error_analysis()
        if not data:
            print("No errors found in the logs.")
            return
        
        print(f"{'Status Code':<12} {'Error Count':<12} {'Sample Resources':<40}")
        print("-" * 65)
        
        for row in data:
            sample_resources = row['sample_resources'][:37] + "..." if row['sample_resources'] and len(row['sample_resources']) > 40 else row['sample_resources']
            print(f"{row['status_code']:<12} {row['error_count']:<12} {sample_resources or 'N/A':<40}")
        
        return data
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print(f"\n{'='*60}")
        print("LOG ANALYSIS SUMMARY REPORT")
        print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Get database stats
        stats = self.db.get_database_stats()
        
        print(f"\nDATABASE STATISTICS:")
        print(f"Total log entries: {stats.get('total_records', 0):,}")
        print(f"Unique IP addresses: {stats.get('unique_ips', 0):,}")
        
        if stats.get('earliest_log') and stats.get('latest_log'):
            earliest = stats['earliest_log']
            latest = stats['latest_log']
            duration = latest - earliest
            print(f"Log period: {earliest.strftime('%Y-%m-%d %H:%M:%S')} to {latest.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Duration: {duration.days} days, {duration.seconds // 3600} hours")
        
        # Generate sub-reports
        self.generate_top_n_ips_report(5)
        self.generate_status_code_report()
        self.generate_hourly_traffic_report()
        self.generate_error_analysis_report()
        
        print(f"\n{'='*60}")
        print("END OF REPORT")
        print(f"{'='*60}")
    
    def save_charts(self, output_dir="charts"):
        """Generate and save visualization charts"""
        import os
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        
        # Top IPs chart
        top_ips_data = self.db.get_top_n_ips(10)
        if top_ips_data:
            df = pd.DataFrame(top_ips_data)
            plt.figure(figsize=(12, 6))
            plt.bar(df['ip_address'], df['request_count'])
            plt.title('Top 10 IP Addresses by Request Count')
            plt.xlabel('IP Address')
            plt.ylabel('Request Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/top_ips.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # Status code distribution
        status_data = self.db.get_status_code_distribution()
        if status_data:
            df = pd.DataFrame(status_data)
            plt.figure(figsize=(10, 6))
            plt.pie(df['count'], labels=df['status_code'], autopct='%1.1f%%')
            plt.title('HTTP Status Code Distribution')
            plt.savefig(f"{output_dir}/status_codes.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # Hourly traffic
        hourly_data = self.db.get_hourly_traffic()
        if hourly_data:
            df = pd.DataFrame(hourly_data)
            plt.figure(figsize=(12, 6))
            plt.plot(df['hour'], df['request_count'], marker='o', linewidth=2, markersize=6)
            plt.title('Hourly Traffic Distribution')
            plt.xlabel('Hour of Day')
            plt.ylabel('Request Count')
            plt.grid(True, alpha=0.3)
            plt.xticks(range(0, 24))
            plt.tight_layout()
            plt.savefig(f"{output_dir}/hourly_traffic.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"Charts saved to '{output_dir}' directory")
