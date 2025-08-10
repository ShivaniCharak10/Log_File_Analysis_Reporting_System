import re
from datetime import datetime

class LogParser:
    def __init__(self):
        # Apache Common Log Format pattern
        self.log_pattern = re.compile(
            r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<timestamp>[^\]]+)\] '
            r'"(?P<method>\w+) (?P<resource>[^"]*)" (?P<status>\d+) (?P<size>\d+|-)'
        )
    
    def parse_line(self, line):
        """Parse a single log line and return structured data"""
        match = self.log_pattern.match(line.strip())
        if not match:
            return None
        
        try:
            # Extract matched groups
            ip_address = match.group('ip')
            timestamp_str = match.group('timestamp')
            method = match.group('method')
            resource = match.group('resource')
            status = int(match.group('status'))
            size_str = match.group('size')
            
            # Parse timestamp
            timestamp = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
            
            # Handle response size
            response_size = 0 if size_str == '-' else int(size_str)
            
            return {
                'ip_address': ip_address,
                'timestamp': timestamp,
                'request_method': method,
                'resource': resource,
                'status_code': status,
                'response_size': response_size,
                'request_time': timestamp  # Using timestamp as request_time
            }
        except (ValueError, AttributeError) as e:
            print(f"Error parsing line: {line.strip()[:100]}... - {e}")
            return None
    
    def parse_file(self, file_path):
        """Parse entire log file and yield structured data"""
        parsed_count = 0
        error_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line_num, line in enumerate(file, 1):
                    if line.strip():  # Skip empty lines
                        parsed_data = self.parse_line(line)
                        if parsed_data:
                            parsed_count += 1
                            yield parsed_data
                        else:
                            error_count += 1
                            if error_count <= 10:  # Show first 10 errors
                                print(f"Failed to parse line {line_num}: {line.strip()[:100]}...")
        
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return
        except Exception as e:
            print(f"Error reading file '{file_path}': {e}")
            return
        
        print(f"Parsing complete: {parsed_count} lines parsed successfully, {error_count} errors")
