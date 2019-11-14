import WQUtil as util


class LoadData(object):
    def __init__(self,filename):
        self.file = open(filename,'r',encoding='UTF-8')

    def __del__(self):
        self.file.close()
        del self.file


class Movies(LoadData):
    def __init__(self, filename):
        util.log('Movies init','start')
        LoadData.__init__(self, filename)
        self.movieInfo = {}
        self.MNAME_KEY = 0
        self.FEATURE_KEY = 1
        self.init_param()
        util.log('Movies init', 'end, rcv num of data ' + str(len(self.movieInfo.keys())))

    def __del__(self):
        LoadData.__del__(self)
        del self.movieInfo

    def _init_info(self,mid, mname = '', feature = None):
        self.movieInfo[mid] = [mname,feature]

    def init_param(self):
        for line in self.file.readlines():
            line = line.replace('\n', '')
            elems = line.split('::')
            self._init_info(int(elems[0]),elems[1],elems[2].split('|'))


class Ratings(LoadData):
    def __init__(self,filename):
        util.log('Ratings init', 'start')
        LoadData.__init__(self,filename)
        self.rating = {} # {uid:[{movies:rating}]}
        self.MID_KEY = 1
        self.VAL_KEY = 2
        self.init_param()
        util.log('Ratings init', 'end, rcv num of data ' + str(len(self.rating.keys())))

    def __del__(self):
        LoadData.__del__(self)
        del self.rating

    def _init_info(self,uid,mid,rating):
        if not self.rating.__contains__(uid):
            self.rating[uid] = []
        self.rating[uid].append({self.MID_KEY: mid, self.VAL_KEY: rating})

    def init_param(self):
        for line in self.file.readlines():
            elems = line.split('::')
            self._init_info(int(elems[0]),int(elems[1]),int(elems[2]))



