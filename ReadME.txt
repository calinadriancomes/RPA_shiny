
# Run the command
# Prerequisites on Winddows 11

reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f

# for long file names

shiny run --reload app.py

# 
# Open
# http://localhost:8000
# in your browser.
#
