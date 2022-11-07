$(kill `pidof python3 main.py`)
$(rm logfile.out)
$(nohup python3 main.py > /root/telegram/logfile.out 2>&1 &)
