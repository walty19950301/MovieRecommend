import numpy as np
import math
import WQUtil as util
import os
import copy

class RA(object):

    def __init__(self, movies=None, ratings=None):
        # threshold
        self.alpha = 1.2
        self.N = 20
        self.log = util.Log(os.path.join('../','result.txt'))
        self.userEvents = {} # {uid:[events_idx]}
        self.userEvaluationItems = {} # uid,{evaluation:[mids]}
        self.featureEvaluation = {} # {feature:evaluation}
        self.userItemFeatures = {} # {itemid:{features:featureM}}
        self.userEvaluationPreferenceWeight = {} # {itemid:preferenceWeight}
        self.actItemSimilar = {} # {itemid:Similar}
        self.movies = movies
        self.ratings = ratings

    def __del__(self):
        del self.log
        del self.userEvents
        del self.userEvaluationItems
        del self.featureEvaluation
        del self.userItemFeatures
        del self.userEvaluationPreferenceWeight
        del self.alpha

    def find_actived_item(self,exceptArray = None):
        util.log('RA find_actived_item', 'start')
        itemids = []
        olditemid = self.movies.movieInfo.keys()
        newExceptArr = copy.deepcopy(list(exceptArray))
        for v in olditemid:
            if newExceptArr.__contains__(v):
                newExceptArr.remove(v)
            else:
                itemids.append(v)
        util.log('RA find_actived_item', 'end')
        return itemids

    def find_the_most_active_user(self):
        # {uid:[idx]} userEvents
        util.log('RA find_the_most_active_user', 'start')
        vic = 0
        vid = 0
        for uid,rat in self.ratings.rating.items():
            t_vic = len(rat)
            if t_vic > vic:
                vic = t_vic
                vid = uid
        util.log('RA find_the_most_active_user', 'end, vid = ' + str(vid) + ', vic = ' + str(vic))
        return vid, vic

    def user_evalueItem(self,vid = 0):
        # self.userEvaluation = {} # {evaluation:[mid]}
        util.log('RA user_evalueItem', 'start')
        featureEv = {} # {feature:[]}
        for rat in self.ratings.rating[vid]:
            evaluation = rat[self.ratings.VAL_KEY]
            mid = rat[self.ratings.MID_KEY]
            if not self.userEvaluationItems.__contains__(evaluation):
                self.userEvaluationItems[evaluation] = []
            self.userEvaluationItems[evaluation].append(mid)
            for feature in self.movies.movieInfo[mid][1]:
                if not featureEv.__contains__(feature):
                    featureEv[feature] = []
                featureEv[feature].append(evaluation)
        for feature,evals in featureEv.items():
            self.featureEvaluation[feature] = np.sum(np.array(evals))
        util.log('RA user_evalueItem', 'end')

    def _dict_sort_rank(self,features = None):
        featuresV = {}
        featuresR = {}
        for fid in features.keys():
            featuresV[fid] = self.featureEvaluation[fid]
        list = sorted(featuresV.values(),reverse=True)
        preV = 0
        bias = 0
        for idx in range(len(list)):
            if preV != list[idx]:
                for fid in features.keys():
                    if list[idx] == featuresV[fid]:
                        featuresR[fid] = idx + 1 - bias
                preV = list[idx]
            else:
                bias += 1
        return featuresR

    def degree_of_preference_feature(self,vid=0):
        # self.userItemFeatures = {} # {itemid:{features:featureM}}
        util.log('RA degree_of_preference_feature', 'start')
        for rat in self.ratings.rating[vid]:
            mid = rat[self.ratings.MID_KEY]
            if not self.userItemFeatures.__contains__(mid):
                self.userItemFeatures[mid] = {}
            for feature in self.movies.movieInfo[mid][self.movies.FEATURE_KEY]:
                self.userItemFeatures[mid][feature] = 0
            features = self.userItemFeatures[mid]
            featuresR = self._dict_sort_rank(self.userItemFeatures[mid])
            length = len(features.keys())
            for fid in features.keys():
                features[fid] = featuresR[fid]/math.pow(2,math.sqrt(self.alpha*length*(featuresR[fid]-1)))
        util.log('RA degree_of_preference_feature', 'end')

    def __weight(self,itemids = None,featureid = 0):
        wt = 0
        length = len(itemids)
        for itemid in itemids:
            if self.userItemFeatures.__contains__(itemid):
                if self.userItemFeatures[itemid].__contains__(featureid):
                    wt += 1
        wt = wt / length
        return wt

    def __density(self,itemids = None,itemid = 0,featureid = 0):
        dens = 0
        length = len(itemids)
        if self.userItemFeatures.__contains__(itemid) and self.userItemFeatures[itemid].__contains__(featureid):
            for id in itemids:
                if self.userItemFeatures.__contains__(id):
                    if self.userItemFeatures[id].__contains__(featureid) and self.userItemFeatures[itemid][featureid] == self.userItemFeatures[id][featureid]:
                        dens += 1
        dens = dens/length
        return dens

    def _preference_weight(self,itemids = None,featureid=0):
        pweight = 0
        length = len(itemids)
        for itemid in itemids:
            if self.userItemFeatures.__contains__(itemid) and self.userItemFeatures[itemid].__contains__(featureid):
                pweight += self.userItemFeatures[itemid][featureid]*self.__weight(itemids,featureid)*self.__density(itemids,itemid,featureid)
        pweight = pweight / length
        return pweight

    def _social_similarity(self,itemids,itemid):
        sigma_all = 0
        sigma_preference_weight = 0
        sigma_w = 0
        item_prop = []
        if self.movies.movieInfo.__contains__(itemid):
            features = self.movies.movieInfo[itemid][self.movies.FEATURE_KEY]
            for b in features:
                if not item_prop.__contains__(b):
                    item_prop.append(b)
                    p = self._preference_weight(itemids,b)
                    ws = self.__weight(itemids,b)
                    sigma_all += p*ws
                    sigma_w += math.pow(ws,2)
                    sigma_preference_weight += math.pow(p,2)
        revalue = 0
        if sigma_preference_weight != 0 and sigma_w != 0:
            revalue = sigma_all / (math.sqrt(sigma_preference_weight) * math.sqrt(sigma_w))
        return revalue

    def process(self):
        util.log('RA process','process start')
        vid,vic = self.find_the_most_active_user()
        self.user_evalueItem(vid)
        self.degree_of_preference_feature(vid)
        util.log('RA process', 'similar process start')

        evaluation = np.max(list(self.userEvaluationItems.keys()))
        length = len(self.featureEvaluation.keys())
        index = 1
        itemids = self.userEvaluationItems[evaluation]
        out_put_evalue = {}
        for feature in list(self.featureEvaluation.keys()):
            p = self._prefereince_weight(itemids,feature)
            out_put_evalue[feature] = p
            util.log('RA process', str(index) + '/' + str(length))
            index += 1
        print(out_put_evalue)
        # out_put_similar = {}
        # out_put_name = {}
        # wqlist = sorted(self.actItemSimilar.values(),reverse=True)
        # length = len(wqlist)
        # now_value = 0
        # for idx in range(length):
        #     if wqlist[idx] != now_value:
        #         for act_itemid,similar in self.actItemSimilar.items():
        #             if similar == wqlist[idx]:
        #                 out_put_similar[act_itemid] = similar
        #                 out_put_name[act_itemid] = self.movies.movieInfo[act_itemid]
        #         now_value = wqlist[idx]
        # print(out_put_similar)
        # print(out_put_name)
        # print(self.featureEvaluation)
        util.log('RA process', 'process end')
