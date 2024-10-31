. venv/bin/activate
python kill.py
ps -ef | grep main.py | grep -v grep | awk '{print $2}' | xargs kill