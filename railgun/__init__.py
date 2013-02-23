# --encoding=utf-8
__author__ = 'haku'
import railgun
import requests
from bs4 import BeautifulSoup


class RailGun():
    def __init__(self):
        self.configdata = dict([])
        self.nodegroups = dict([])

    def settask(self, taskdata):
        self.taskdata = dict(taskdata)

    def setconfig(self, config_key, config_value):
        self.configdata[config_key] = config_value

    def fire(self):
        self.__parserNodes(self.taskdata)
        return self.nodegroups

    def __parserNodes(self, taskentry):
        if (None == taskentry):
            return
        if (isinstance(taskentry, unicode)):
            return
            # do current action
        actionname = taskentry["action"].strip()
        if actionname == 'main':
            taskentry = self.__main(taskentry)
        if actionname == 'node':
            taskentry = self.__createnode(taskentry)
        if actionname == 'fakenode':
            pass
        if actionname == 'fetcher':
            taskentry = self.__fetch(taskentry)
        if actionname == 'parser':
            taskentry = self.__parser(taskentry)
        if (None == taskentry.get('subaction')):
            return
        for subtask in taskentry['subaction']:
            # if entry is not fakednode and entry has datas then copy to subtask
            if (subtask['action'] != 'fakenode' and taskentry.get('datas') != None):
                subtask['datas'] = taskentry.get('datas')
                # ignore datas field
            if str(subtask) == 'datas':
                continue;
            # passed to subtask
            if taskentry.get('nodegroup') != None:
                subtask['nodegroup'] = taskentry.get('nodegroup')
            if taskentry.get('nodeid') != None:
                subtask['nodeid'] = taskentry.get('nodeid')
            self.__parserNodes(subtask)
        return

    def __main(self, taskentry):
        print taskentry['name'], "运行"
        return taskentry

    def __fetch(self, taskentry):
        s = requests.session()
        url = taskentry['url'].strip()
        print "fetching ",url
        data = s.get(url)
        taskentry['datas'] = [data.text]
        return taskentry

    def __parser(self, taskentry):
        rule = taskentry['rule'].strip()
        print "parsing with rule ", rule
        datas = taskentry.get('datas')
        parseddatas = []
        for data in datas:
            soup = BeautifulSoup(data)
            parseddatasels = soup.select(rule)
            for tag in parseddatasels:
                parseddatas.append(unicode(tag))
        print "after parsing", len(parseddatas)
        # set data to node
        if taskentry.get('nodegroup') != None and taskentry.get('setField') != None:
            nodegroup = taskentry['nodegroup']
            nodeid = taskentry['nodeid']
            fieldname = taskentry.get('setField')
            print "node [group:id]=[]"
            self.nodegroups[nodegroup][nodeid][fieldname] = parseddatas
        taskentry['datas'] = parseddatas
        return taskentry

    def __createnode(self, taskentry):
        datas = taskentry.get('datas')
        # every node has one data
        subacts = []
        print len(datas)," nodes created"
        nodegroup = taskentry.get('group', 'default')
        nodeid = 0
        self.nodegroups[nodegroup] = dict({})
        for data in datas:
            nodeid += 1
            # init node
            self.nodegroups[nodegroup][nodeid] = dict([])
            # task entry splited into pieces
            # sub actions = now sub * node num
            subact = {
                "action": "fakenode",
                "nodegroup": nodegroup,
                "nodeid": nodeid,
                "datas" : [data],
                "subaction": taskentry["subaction"]
            }
            subacts.append(subact)
        taskentry["subaction"] = subacts
        return taskentry

    def getnodes(self, groupname = 'default'):
        return self.nodegroups.get(groupname)