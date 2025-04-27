import os

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
    print(f"Created logs directory at {logs_dir}")
else:
    print(f"Logs directory already exists at {logs_dir}")
