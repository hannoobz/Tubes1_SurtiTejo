#!/bin/bash

python3 main.py --logic Random --email=test@email.com --name=stima --password=123456 --team etimo &
python3 main.py --logic Random --email=test1@email.com --name=stima1 --password=123456 --team etimo &
python3 main.py --logic OldBot --email=oldasf@email.com --name=oldaf --password=123456 --team etimo &
python3 main.py --logic MainBot --email=tfafa@email.com --name=fasfasf --password=123456 --team etimo &