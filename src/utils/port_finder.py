import socket
from contextlib import closing

def find_free_port(start: int = 8501, end: int = 8510) -> int:
    """
    Find a free port in the range [start, end].
    
    Args:
        start: Starting port number.
        end: Ending port number.
        
    Returns:
        A free port number.
        
    Raises:
        RuntimeError: If no free ports are found.
    """
    for port in range(start, end + 1):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            # connect_ex returns 0 if connection is successful (port is open/used)
            # returns error code if failed (port is closed/free)
            if sock.connect_ex(('localhost', port)) != 0:
                return port
                
    raise RuntimeError(f"No free ports found in range {start}-{end}")
