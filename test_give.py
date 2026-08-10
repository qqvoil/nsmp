import os
import sys
from dotenv import load_dotenv
sys.path.append('/Users/voil/data/nsmp/backend')
load_dotenv('/Users/voil/data/nsmp/backend/.env')
from app import execute_rcon_command, RCON_SERVERS
smp1 = RCON_SERVERS['smp1']
print('Response:', execute_rcon_command(smp1['host'], smp1['port'], smp1['pass'], 'points give voil 1000'))
