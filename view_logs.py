import os
import base64
import glob

def list_log_files():
    """List all log files in the application data directory."""
    path = os.path.join(os.environ['APPDATA'], 'Microsoft', 'CLR')
    print(f"Log files in {path}:")
    print("-" * 30)
    
    log_files = glob.glob(os.path.join(path, "*.log"))
    if not log_files:
        print("No log files found.")
    else:
        for i, file in enumerate(log_files):
            print(f"{i}: {os.path.basename(file)}")
    
    print("-" * 30)
    return log_files

def view_log_file(filename):
    """View and decode the contents of a log file."""
    try:
        with open(filename, 'r') as file:
            encoded_data = file.read()
        
        # Decode from base64
        try:
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            
            print(f"Decoded content of {os.path.basename(filename)}:")
            print("-" * 30)
            print(decoded_data)
            print("-" * 30)
        except:
            print("Error: Could not decode the file content.")
    except:
        print(f"Error: Could not open file {filename}")

def main():
    print("Input Activity Monitor - Log Viewer")
    print("==================================")
    
    while True:
        print("\nOptions:")
        print("1. List log files")
        print("2. View a specific log file")
        print("3. Exit")
        
        try:
            choice = int(input("Enter your choice: "))
            
            if choice == 1:
                list_log_files()
            elif choice == 2:
                log_files = list_log_files()
                if log_files:
                    file_num = int(input("Enter the number of the file to view: "))
                    if 0 <= file_num < len(log_files):
                        view_log_file(log_files[file_num])
                    else:
                        print("Invalid file number.")
            elif choice == 3:
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    main()
