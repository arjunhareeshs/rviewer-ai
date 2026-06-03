import multiprocessing as mp
import sys

def f():
    print('f() started')
    import tensorflow as tf
    print('tf imported')

if __name__ == '__main__':
    mp.freeze_support()
    p = mp.Process(target=f)
    p.start()
    p.join()
    print('exit code:', p.exitcode)
