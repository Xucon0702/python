import matplotlib.pyplot as plt
import os, sys
from matplotlib.pyplot import MultipleLocator
import re
import json
import random
import numpy as np

cpu_loading = {}
dateList = []
cpu_total = []

marker = [',','o','v','^','<','>','1','2','3','4','s','p','*','h','H','+','x']
color = [
'#000000','#696969','#A52A2A','#FF0000','#FFA500','#8B4513',
'#FF8C00','#FFFF00','#556B2F','#7FFF00','#98FB98','#228B22',
'#008000','#00FF7F','#20B2AA','#008080','#1E90FF','#191970',
'#0000FF','#4B0082','#9400D3','#FF00FF','#DC143C','#FF1493',
'#CD853F','#708090','#00FF00','#FFD700','#00FFFF','#7B68EE']
linestyle = ['-','--','-.',':']

def read_cpu_loading(path):
    jump_flag = 0
    total_cpu = 0
    index_loading = {}
    with open(path) as fp:
        for line in fp:
            if "topDate:" in line:
                if(len(index_loading) > 0):
                    cpu_total.append(total_cpu)
                    cpu_loading[date] = index_loading
                first = 0
                date = line.strip()[8:]
                dateList.append(date)
                jump_flag = 4
                index_loading = dict()
                total_cpu = 0
            else:
                if(jump_flag > 0):
                    jump_flag = jump_flag - 1
                else:
                    line = re.sub(r'\s+', '*', line.strip())
                    loading = line.split("*")
                    if len(loading) < 9:
                        continue
                    #print(loading[-1], ":", loading[8])
                    if(index_loading.get(loading[-1])):
                        index_loading[loading[-1]] += float(loading[7])
                    else:
                        index_loading[loading[-1]] = float(loading[7])
                    print(f'{loading[-1]} = {loading[7]}')
                    total_cpu = total_cpu + float(loading[7])
    if(len(index_loading) > 0):
        cpu_total.append(total_cpu)
        cpu_loading[date] = index_loading
    #print(cpu_loading)
    del index_loading

def cpu_group_loading(functional_group,file):
    group_num = len(functional_group)
    #print("group_num = ", group_num)
    loading = []
    groups_loading = []
    group_loading = []

    groups = list(functional_group.keys())
    #print(groups)

    for i in range(group_num):
        loading.append([])
        group_loading.append([])
        for j in range(len(functional_group[groups[i]])):
            group_loading[i].append([])

    functionals = functional_group.values()

    for item in dateList:
        cpu_loading_item = cpu_loading[item]
        groups_total = 0
        for i in range(group_num):
            total = 0
            for j, command in enumerate(functional_group[groups[i]]):
            #for command in functional_group[groups[i]]:
                if command in cpu_loading_item:
                    #print("command:", command, "cpu_loading_item[command]:",cpu_loading_item[command])
                    total = total + cpu_loading_item[command]
                    group_loading[i][j].append(cpu_loading_item[command])
                else:
                    group_loading[i][j].append(0)
            loading[i].append(total)
            groups_total += total
        groups_loading.append(groups_total)

    fig = plt.figure(1,figsize=(16, 9), dpi=1920/16)
    lable = "cpu_total_" + str(np.mean(cpu_total))
    plt.plot(range(len(cpu_total)), cpu_total, color=random.choice(color), marker=random.choice(marker), linestyle='-', label=lable)
    label_groups = "groups_total_" + str(np.mean(groups_loading))
    plt.plot(range(len(cpu_total)), groups_loading, color=random.choice(color), marker=random.choice(marker), linestyle='-', label=label_groups)
    for i in range(group_num):
        #print(loading[i])
        lable_tag = groups[i] + "_total_" + str(np.mean(loading[i]))
        plt.plot(range(len(cpu_total)), loading[i], color=random.choice(color), marker=random.choice(marker), linestyle='-', label=lable_tag)
    plt.title("Cpu Loading", fontsize=24)
    plt.xticks(range(len(cpu_total)), dateList, rotation=70)
    plt.ylabel("cpu", fontsize=14)
    ax = plt.gca()
    plt.grid()
    plt.legend()
    #plt.get_current_fig_manager().window.showMaximized()
    #plt.get_current_fig_manager().resize(*plt.get_current_fig_manager().window.maxsize())
    plt.savefig('cpu_total'+file+'.png')
    plt.close()

    for i in range(group_num):
        fig = plt.figure(i+2,figsize=(16, 9), dpi=1920/16)
        for j, command in enumerate(functional_group[groups[i]]):
            lable = command + '_' + str(np.mean(group_loading[i][j]))
            #print("lable:", lable,  "range(len(cpu_total))", cpu_total, "group_loading[i][j]:", group_loading[i][j])
            plt.plot(range(len(cpu_total)), group_loading[i][j], color=random.choice(color), marker=random.choice(marker), linestyle='-', label=lable)
            for k in range(len(cpu_total)):
                plt.text(k, group_loading[i][j][k]+0.1, group_loading[i][j][k], fontsize=15)
        plt.title(groups[i], fontsize=24)
        plt.xticks(range(len(cpu_total)), dateList, rotation=70)
        plt.ylabel("cpu", fontsize=14)
        ax = plt.gca()
        plt.grid()
        plt.legend()
        #plt.get_current_fig_manager().window.showMaximized()
        #plt.get_current_fig_manager().resize(*plt.get_current_fig_manager().window.maxsize())
        plt.savefig(groups[i]+file+'.png')
        plt.close()

    #plt.show()
    del loading
    del group_loading
    del groups_loading
    del groups
    del functionals

def analysefile(file,config):
	read_cpu_loading(file)
	cpu_group_loading(config['functional_group'],file.split('top_')[1].split('.txt')[0])

if __name__ == '__main__':
    if(os.path.exists('config.json')):
        with open('config.json', 'r') as fp:
            js = fp.read()
        config = json.loads(js)
        print(config)
        #print(os.path.dirname(os.path.abspath(sys.argv[0])))
        for fileName in reversed(os.listdir(os.path.dirname(os.path.abspath(sys.argv[0])))):
            if(fileName.startswith("top_") and fileName.endswith(".txt")) and not os.path.exists('cpu_total'+fileName.split('top_')[1].split('.txt')[0]+'.png'):
                print(fileName)
                analysefile(fileName,config)
                del cpu_loading
                del dateList
                del cpu_total
                cpu_loading = {}
                dateList = []
                cpu_total = []
    else:
        print("please check config.json!!")
		
	
