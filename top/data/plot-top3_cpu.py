# perf utils plot_top.py
# process top data to analysis the performance of CPU
# execute command:  top -b -d 1 -i > /mnt/top.txt &
# to execute the python file : python plot_top.py top.txt
# 此脚本适用于当前TDA4 linux中的/app/tools/top 指令
# 此top功能比busybox的top更强一些
# 此脚本仅用于PC上数据分析，需要python及相应的依赖库，为便于版本管理打包在发布软件中

# from asyncio.windows_events import NULL
from ctypes import sizeof
from operator import index
import os
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
        if len(data_list) >= 8 and data_list[8] == '0%':
            continue

        # if the line with Mem/CPU/Load,write a blank line 
        if data_list[0].find("top") != -1 or data_list[0].find("Tasks:") !=-1 or data_list[0].find("%Cpu(s)") !=-1 \
            or data_list[0].find("MiB") !=-1:
            if data_list[0].find("MiB") != -1 and data_list[1].find("Swap:") != -1:
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

            # write data in 0～11 line
            if data_list[0] == '%Cpu0' or data_list[0] == '%Cpu1':
                f2 = float(data_list[2])
                f4 = float(data_list[4])
                f6 = float(data_list[6])
                f10 = float(data_list[10])
                f12 = float(data_list[12])
                f14 = float(data_list[14])
                f16 = float(data_list[16])
                data_list[8] = str(f2 + f4 + f6 + f10 + f12 + f14 + f16)
            else:
                if data_list[8] != '%CPU':
                    data_list[8] = str(float(data_list[8])/2)

            # print('xx-----')

            for i in range(11):
                    out_fileobj.write(data_list[i] + '\t')
            print(data_list)
            # for i in range(11):
            #     out_fileobj.write(data_list[i] + '\t')
            #     # if data_list[0] != '%Cpu0' and data_list[0] == '%Cpu1':
            #     #     if i != 8:
            #     #         out_fileobj.write(data_list[i] + '\t')
            #     #     else:
            #     #         out_fileobj.write(str(float(data_list[i])/2) + '\t');
            # split the 7th line to process name
            # process_name = NULL # process name
            if data_list[11].find('{') != -1:    # if find '{',then the second line is the process name
                process_name = data_list[11].split("/")[-1]
            elif data_list[11][0] == '[':  # if begin with '[' to keep the left string as process name
                process_name =  data_list[11].replace('[','')  
                process_name =  process_name.replace(']','')  
                process_name = process_name.split("/")[0]
            else: # keep the last process name
                process_name = data_list[11].split("/")[-1]   
                process_name =  process_name.replace('[','')  
                process_name =  process_name.replace(']','')


            if data_list[0].find('PID')==0:
                out_fileobj.write('COMMAND\t')
            elif data_list[11] == 'wa,':
                out_fileobj.write(str(data_list[0]) + '\t')
            else:
                out_fileobj.write(process_name + '\t')

            out_fileobj.write('\n')
        

    in_fileObj.close()
    out_fileobj.close()
    print("total "+str(count) + " seconds" )

def filter_cpu(group):
    return any('%Cpu0' and '%Cpu1' not in x for x in group)
def plot(csv_file):
    '''
    show the csv file data in plot
     Parameters:
        csv_file: the file name 
    '''
    # load mtop result
    df = pd.read_csv(csv_file, sep='\\s+', parse_dates=['TS'], names=["TS", "PID", "USER", "PR",\
            "NI", "VIRT", "RES", "SHR", "S", "%CPU", "%MEM", "TIME+", "COMMAND"])
    # filter rows which contain thread info
    df = df[df['TS'].str.match(r'[0-9][0-9]:[0-9][0-9]:[0-9][0-9]')]

    # accum cpu info by proc name
    df['%CPU'] = df['%CPU'].str.rstrip('%').astype('float')
    result = df.groupby(['TS','COMMAND'])['%CPU'].sum().unstack()
    print(df.groupby(['TS','COMMAND'])['%CPU'])
    # print('yyyy')

    # print(result)
    #result['TOTAL'] = df.groupby('TS')['%CPU'].sum() #- df.groupby(['TS','COMMAND'])['%Cpu1'] - df.groupby(['TS','COMMAND'])['%Cpu0']

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

    plt.grid(linestyle='-.')
    # plt.figure(figsize=(100, 50))
    # plt.savefig('xx.png')
    figure_size = (6, 4)

    plt.savefig(str(csv_file).split('.out')[0]+'.svg',format='svg',dpi=1200, bbox_inches='tight')
    # plt.savefig('my_plot.pdf',dpi =1200)
    plt.show()
def list_files_in_folder(folder_path):
    files = []
    for file_name in os.listdir(folder_path):
        # print(file_name)
        file_path = os.path.join(folder_path, file_name)
        # print(file_path)
        if os.path.isfile(file_path):
            files.append(file_path)
    return files
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: plot-top.py top.txt")
    else:
        # trans_csv(sys.argv[1], "tmp_top.txt")
        # plot("tmp_top.txt")
        folder_path = list_files_in_folder(sys.argv[1])
        for k in folder_path:
            if '.txt' in str(k):
                print('trans file:'+k)
                print('out file:'+str(k).split('.txt')[0]+'.out')
                trans_csv(k, str(k).split('.txt')[0]+'.out')
                # print(k)
                # print("out"+k)
                plot(str(k).split('.txt')[0]+'.out')
                print('svgfile:'+k+'.out.svg')


    # # 指定文件夹路径
    # folder_path = 'E:\\code\\python\\top2\\topdata'
    # # 列出文件夹内的所有文件
    # files = list_files_in_folder(folder_path)
    # # 打印文件列表
    # for file_name in files:
    #     print(file_name)
