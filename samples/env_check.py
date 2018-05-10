import sys
if sys.version_info[0] == 2:
    sys.exit(0)
    
print('Expected Python 2.7, but this is Python %d.%d!' % sys.version_info[:2])
sys.exit(1)