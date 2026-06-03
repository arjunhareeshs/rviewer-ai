import os
p='C:/Users/hp/anaconda3/Lib/site-packages/livekit/agents/cli/cli.py'
with open(p, 'r', encoding='utf-8') as f:
    data = f.read()
print('args.mp_cch in data:', 'args.mp_cch' in data)
print('LIVEKIT_AGENTS_IPC_CHANNELS in data:', 'LIVEKIT_AGENTS_IPC_CHANNELS' in data)
