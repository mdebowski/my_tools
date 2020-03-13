import re
import numpy as np

logfile = 'logfile.log'

pattern = 'PERF: .*\:\-(.*)(\[.*\]).* (\d*)'

'''
The script was created to find stored procedure(s) that have the most impact to the time of
execution of the whole use case in some application. To achieve the goal the average time of execution
of each stored procedure is counted among other numbers like total occurences of stored procedures,
max and min time of execution, standard deviation for time.

The sample output looks like below:
------------------------------------------------------------------------------------------
RPCName                        AvgTime(ms) Occurences    St.Dev.    MaxTime    MinTime
------------------------------------------------------------------------------------------
procedure_name                     130.00           1       0.00     130.00     130.00

This is the sample line of log we have in log file.
(2019-03-05 04:41:33,922) 388584651 [ajp-0.0.0.0-8100-11] INFO  com.xxx.yyy:104  - PERF: (S) RPC zzzzz user_name :-procedure_name[1, 2019-02-07 10:34:33.0, 0] 130
'''

def search1(path, print_out=True, ):
    # array of tuples (procedure name, time, parameters) populated during file processing
    ntp = []
    with open(path, 'r', newline='') as f1:
        for line in f1:
            m = re.search(pattern, line)
            if m:
                proc_name = m.group(1)
                time = m.group(3)
                params = m.group(2)
                ntp.append((proc_name.strip(), time, params))

    ntp_np = np.array(ntp)
    unique_names = set(ntp_np[:,0])
    name_mean = [(str(u),
                  round(ntp_np[ntp_np[:,0]==u,:][:,1].astype(int).mean(0), 2),
                  ntp_np[ntp_np[:,0]==u,:].shape[0],
                  round(ntp_np[ntp_np[:, 0] == u, :][:, 1].astype(int).std(0), 2),
                  ntp_np[ntp_np[:, 0] == u, :][:, 1].astype('float64').min(0),
                  ntp_np[ntp_np[:, 0] == u, :][:, 1].astype('float64').max(0)
                  ) for u in unique_names]

    # sort by time in descending way
    sorted_rpc = sorted(name_mean, key=lambda tup: int(tup[1]), reverse=True)

    if (print_out):
        dash = '-' * 90
        print(dash)
        print('{:<30s} {:>10s} {:>10s} {:>10s} {:>10s} {:>10s}'.format('RPCName', 'AvgTime(ms)', 'Occurences', 'St.Dev.', 'MaxTime', 'MinTime'))
        print(dash)
        for item in sorted_rpc:
            print ('{0:<30} {1:>10.2f}  {2:>10} {3:>10.2f} {4:>10.2f} {5:>10.2f}'.format(*item))

    return sorted_rpc


sorted_rpc = search1(logfile)

