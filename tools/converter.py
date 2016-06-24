import numpy as np
import pdb

def log_to_summary(fin, fout):
    ml = np.loadtxt(fin, delimiter=',')
    #succ:1, reward:2, turn:4
    ml = ml[:, 1]
    rows = 40
    cols = ml.shape[0]/rows
    ml = ml.reshape((rows, cols), order='F')
    np.savetxt(fout, ml, fmt='%.3f', delimiter=',')

if (__name__ == '__main__'):    
    log_to_summary('run3log.csv', 'summary.csv')
