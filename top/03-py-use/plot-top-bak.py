# perf utils plot_top.py
# process top data to analysis the performance of CPU
# execute command:  top -b -d 1 > /mnt/top.txt &
# to execute the python file : python plot_top.py top.txt
# 此脚本适用于当前TDA4 linux中的系统自带的top输出数据格式处理
# 即busybox的简版top指令
# 此脚本仅用于PC上数据分析，需要python及相应的依赖库，为便于版本管理打包在发布软件中

# from asyncio.windows_events import NULL
from operator import index
import sys
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from mplcursors import cursor
from optparse import OptionParser
import datetime
import re

def trans_csv(in_file,out_file):
    '''
    transport data of top to 
     Parameters:
        in_file: file name of input
        out_file: file name of output
    '''
    # create output file
    out_fileobj = open( out_file, 'w',encoding = 'utf-8' )

    # read data in line
    in_fileObj = open(in_file, "r", encoding='utf8')
    count = 0

    strTime = '00:00:00'  # default init time
    startTime = datetime.datetime.strptime(strTime, "%H:%M:%S")  

    for line in in_fileObj.readlines():
        data_list = line.split()  # split string with blank char

        # pass the blank line
        if len(data_list) < 3:
            continue
        
        # pass the line with %CPU == 0
        if data_list[6] == '0%':
            continue

        # if the line with Mem/CPU/Load,write a blank line 
        if data_list[0].find("Mem:") != -1 or data_list[0].find("CPU:") !=-1 or data_list[0].find("Load") !=-1:
            if data_list[0].find("Mem:") != -1:
                out_fileobj.write('\n')
                count += 1
        else:            
            # add the first line with TS data 
            if data_list[0].find('PID')==0:
                out_fileobj.write('TS\t')
            else:
                # translate count to time with format HH:MM:SS  
                startTime2 = (startTime + datetime.timedelta(seconds=count)).strftime("%H:%M:%S")
                # write time line
                out_fileobj.write(startTime2 + '\t')

            # write data in 0～6 line
            for i in range(7):                            
                out_fileobj.write(data_list[i] + '\t')

            # split the 7th line to process name
            # process_name = NULL # process name
            if data_list[7].find('{') != -1:    # if find '{',then the second line is the process name
                process_name = data_list[8].split("/")[-1]
            elif data_list[7][0] == '[':  # if begin with '[' to keep the left string as process name
                process_name =  data_list[7].replace('[','')  
                process_name =  process_name.replace(']','')  
                process_name = process_name.split("/")[0]
            else: # keep the last process name
                process_name = data_list[7].split("/")[-1]   
                process_name =  process_name.replace('[','')  
                process_name =  process_name.replace(']','')   

            if data_list[0].find('PID')==0:
                out_fileobj.write('COMMAND\t')       
            else:
                out_fileobj.write(process_name + '\t')

            out_fileobj.write('\n')

    in_fileObj.close()
    out_fileobj.close()
    print("total "+str(count) + " seconds" )


def plot(csv_file):
    '''
    show the csv file data in plot
     Parameters:
        csv_file: the file name 
    '''
    # load mtop result
    df = pd.read_csv(csv_file, sep='\s+', parse_dates=['TS'], names=["TS", "PID", "PPID", "USER",\
            "STAT", "VSZ", "%VSZ", "%CPU", "COMMAND"])

    # filter rows which contain thread info
    df = df[df['TS'].str.match(r'[0-9][0-9]:[0-9][0-9]:[0-9][0-9]')]
    
    # accum cpu info by proc name
    df['%CPU'] = df['%CPU'].str.rstrip('%').astype('float')
    result = df.groupby(['TS','COMMAND'])['%CPU'].sum().unstack()
    result['TOTAL'] = df.groupby('TS')['%CPU'].sum()

    parser = OptionParser()
    parser.add_option('-v', action='store_true', dest='verbose', default=False)
    opts, args = parser.parse_args()

    # change plot layout when needed
    layout = 12, 5

    if opts.verbose:
        result.plot(subplots=True, layout=layout, legend=True)
    else:
        result.plot(subplots=False, layout=layout, legend=True)

    cursor(hover=True)

    plt.ylabel('CPU Loading')
    plt.xlabel('Time')

    plt.show()    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: plot-top.py top.txt")
    else:        
        trans_csv(sys.argv[1],"tmp_top.txt")
        plot("tmp_top.txt")
