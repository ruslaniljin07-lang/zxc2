import sys, os
os.chdir(r'C:\Users\rusla\.cline\data\workspaces\chat\zxc2')
sys.path.insert(0, os.getcwd())
from app import app
app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
