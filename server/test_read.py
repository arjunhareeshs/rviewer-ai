import os
p='C:/Users/hp/anaconda3/Lib/site-packages/livekit/agents/cli/cli.py'
print('size:', os.path.getsize(p))
with open(p, 'rb') as f:
    data = f.read()
lines = data.split(b'\n')
print('actual lines:', len(lines))
print('last 10 lines:')
print(b'\n'.join(lines[-10:]).decode('utf-8', 'replace'))
