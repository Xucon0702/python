import sys

# file=open(r'C:\Users\hp\Desktop\1001.hea','r')    #打开hea目标文件
# file_contents=file.readlines()                    #按行读取全部内容

# pH_label_file=open(r'C:\Users\hp\Desktop\pH_label.txt','w')
# #打开要写入数据的txt目标文件

# for content in file_contents:     #逐行读取
#     if  'pH' in content:          #检查包含pH的那行数据
#         print(content)            #打印，看效果
#         pH_label_file.write(content)   #将符合要求的内容写入文件

def test():
    print("this is func test")
    return 0

writePath = "./tracks_after_trim.txt"     #剪贴后的txt
key_words_traks = ""
key_words_dr = "alg_dr:"     #包括了planInit和Alg两个过程,init时为0

if __name__ == "__main__":
    argvstr = sys.argv
    if len(argvstr) < 2:
        print ("need input file name")
        # with open(argvstr[1], 'rb') as f:
        #     map = f.read()
        exit()
    else:        
        if argvstr[1][:11] == "mv_decision":    #判断两个str的前11个字符是否完全一致
            print("The file is decision log")
        else:
            print("The file is not decision log")

        with open(argvstr[1], 'rb') as f:
            # totalData = f.read()
            file_contents=f.readlines() 
            # f.closed

    fWrite = open(writePath,'w')
    # num = fWrite.write("this is my test")
    # print(num)

    for content in file_contents:   #content为bytes
        if key_words_dr.encode() in content:
            # print("key_words_dr: ",key_words_dr)
            # print(content.decode().split(key_words_dr))
            str_decision_dr_split1 = content.decode().split(key_words_dr)
            str_decision_dr_split2 = str_decision_dr_split1[1].split(',')               #结果
            # print(str_decision_dr_split1[1].split(','))

            num = fWrite.write(str_decision_dr_split2[0])


            
            num = fWrite.write(' ')
            num = fWrite.write(str_decision_dr_split2[1])
            num = fWrite.write(' ')
            num = fWrite.write(str_decision_dr_split2[2])

            fWrite.write('\r\n')            #换行
            # num = fWrite.write(content.decode())    #write str

    fWrite.close()
    f.closed


    test()
    print("end")
    

    

    
            