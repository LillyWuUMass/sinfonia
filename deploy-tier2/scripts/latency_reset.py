import time
import subprocess


NETWORK_INTERFACES = ['eno1', 'kilo0']

    
for itf in NETWORK_INTERFACES:
    cmd = ([
        'sudo',
        'tc',
        'qdisc',
        'del',
        'dev',
        f'{itf}',
        'root',
        'netem',
        ])
    subprocess.run(cmd)
    time.sleep(1)
        