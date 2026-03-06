import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/david/code/WATCHER-ROS2/install/wheelchair_navigation'
