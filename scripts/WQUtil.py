import time


def log(tag='',msg=''):
    print(time.strftime("[%Y-%m-%d %H:%M:%S]",time.localtime()) + '{' + tag + '}' + msg)

class Log(object):
    def __init__(self,filename):
        self.savefile = open(filename,'w')

    def write_line(self,str=''):
        self.savefile.writelines(str)

    def __del__(self):
        self.savefile.close()
