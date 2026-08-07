@echo off
title SMP (Port 25590)
echo Starting SMP1 server on port 25590...
java -Xmx6G -Xms5G -jar server.jar nogui
pause