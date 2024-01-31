from kivymd.app import MDApp
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList
from kivy.uix.image import Image, AsyncImage
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivymd.uix.swiper import MDSwiper, MDSwiperItem
from kivy.clock import Clock
from kivymd.uix.textfield import MDTextField
from kivy.uix.button import Button
import requests

import os
from kivy.core.window import Window

internet = False
internetFailedKV = """
#:import MDLabel kivymd.uix.label.MDLabel
MDBoxLayout:
    MDLabel:
        font_size: 28
        valign: 'center'
        halign: 'center'
        text: 'Internet Connection Failed.\\nPlease Reload App.'
        text_color: 0,0,0,1"""

class MyTab(Button):
    pass

class MyScroller(MDGridLayout):
    pass

class MySwiper(MDSwiperItem):
    pass

#When the image is clicked or tapped, the FitImage cycles through the images for that item
class MyImage(FitImage):
    itemSelected = 0
    item = {}
    finalPrice = 0
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if(len(self.item)<2):
                return
            self.itemSelected+=1
            if(self.itemSelected>=len(self.item)):
                self.itemSelected = 1
            self.source = self.item[self.itemSelected]
class MyLabel(MDLabel):
    pass

class MyApp(MDApp):
    #Stats: Player Stat Dict
    #ItemDict: Dict for every Item
    #ListHeight: Height of ScrollView List
    #UsedItemNames: Items that have already been used on the current ScrollView List
    stats = {}
    itemDict = {}
    listHeight = 0
    usedItemNames = []
    statTextMultiplier = .2

    #Generates the 'All' Tab above the ScrollView List
    def generateAllTab(self):
        allTab = MyTab()
        allTab.text = 'All'
        self.root.ids.tabs.add_widget(allTab)

    #Generates the rest of the category tabs above the ScrollView List
    #Carries on to display the 'All' category for the ScrollView List
    def generateTabsAndBoxes(self):
        self.listHeight = 0
        self.usedItemNames = []
        for layout, items in self.itemDict.items():
            tab = MyTab()
            tab.text = layout
            self.root.ids.tabs.add_widget(tab)
            self.generateBoxes(items)
        self.root.ids.scroller.height=self.listHeight

    #Generates the current ScrollView List based on the items provided
    def generateBoxes(self,items):
        index = 0
        storedHeight = 0
        for key, value in items.items():
            if not key in self.usedItemNames:
                self.usedItemNames.append(key)
                box = MyScroller()
                image = MyImage()
                image.source = value['mainImage']
                image.item = list(value.values())
                label = MyLabel()
                label.text = key
                label.color = [1,1,1,1]
                labelHeight = max(min(len(key.split('\n'))+1,7)*58,75)
                label.size_hint_max_y = labelHeight
                label.text_size_y = labelHeight
                image.size_hint_max_x = 550-labelHeight
                image.height = (image.width/(image.height/image.width))
                box.add_widget(image)
                box.add_widget(label)
                self.root.ids.scroller.add_widget(box)
                if(index==0):
                    storedHeight = image.height+label.height
                else:
                    self.listHeight+= max(image.height+label.height,storedHeight)*2
                index= (index+1)%2
        if(index==1):
            self.listHeight+= storedHeight*2

    #Builds on App Start
    def build(self):
        global internet
        if(os.name=='nt'):
            self.statTextMultiplier = .1
            Window.size = (1080, 2115)
        else:
            print(Window.size)
        if(internet):
            usedItemNames = []
            self.root = Builder.load_file('main.kv')
            self.generateAllTab()
            self.generateTabsAndBoxes()
            self.findStats('Wh34tl3y')
        else:
            self.root = Builder.load_string(internetFailedKV)
        return self.root

    #Changes the ScrollView List Items depending on the category of the tab selected
    def changeLayout(self,text):
        self.usedItemNames = []
        self.listHeight = 0
        images = self.root.ids.scroller
        images.clear_widgets()
        if(text=="All"):
            for layout, items in self.itemDict.items():
                self.generateBoxes(items)
        else:
            self.generateBoxes(self.itemDict[text])
        self.root.ids.scroller.height=self.listHeight
        self.root.ids.scroller.parent.scroll_to(self.root.ids.scroller.children[-1])
        return self.root

    #Shortens code segments by cycling through the tags provided
    # and finding the best image, or text for the current item
    def bestFit(self,item,tags):
        for key,values in tags.items():
            if(key in item):
                if(item[key]!=None):
                    if(values==None):
                        return item[key]
                    if(type(values)==str):
                        return item[key][values]
                    for layout, value in values.items():
                        if(value==None):
                            if item[key][layout]!=None:
                                return item[key][layout]
                        elif(type(value)==str):
                            return item[key][layout][value]
                        else:
                            for l, v in value.items():
                                if item[key][layout][l]!=None:
                                    return item[key][layout][l][v]

    #Finds the main image, category/layoutName, itemName, 
    # other images, and finalPrice for the item provided
    def itemInit(self,layoutName,itemName,item):
        mainImages = self.bestFit(item,{'newDisplayAsset':'materialInstances','brItems':None,'items':None})[0]['images']

        if not layoutName in self.itemDict.keys():
            self.itemDict[layoutName] = {}
        if not itemName in self.itemDict[layoutName].keys():
            self.itemDict[layoutName][itemName] = {}

        self.itemDict[layoutName][itemName]['finalPrice'] = item['finalPrice']
        self.itemDict[layoutName][itemName]['mainImage'] = self.bestFit(mainImages,{'Background':None,'featured':None})
        
        if('items' in item):
            for itemImages in item['items']:
                if 'images' in itemImages:
                    imageSet = itemImages['images']
                    for key, image in imageSet.items():
                        if key.lower().find('icon')==-1 and key.lower().find('feature')==-1:
                            if imageSet[key]!=None:
                                if 'large' in imageSet[key]:
                                    self.itemDict[layoutName][itemName][key] = imageSet[key]['large']
                                    self.checkLayout(imageSet[key]['large'],itemName,key)
                                else:
                                    self.checkLayout(imageSet[key],itemName,key)
                    if itemImages['variants']!=None:
                        for variants in itemImages['variants']:
                            if variants['options']!=None:
                                for finalImg in variants['options']:
                                    self.checkLayout(finalImg['image'],itemName,finalImg['tag'])

    #adds img to any layout that has name in it using key
    def checkLayout(self,img,name,key):
        for keys, values in self.itemDict.items():
            if(name in values):
                if not key in values:
                    self.itemDict[keys][name][key] = img

    #Divideds the items by category, and
    # changes the names for the jam tracks and bundles appropriately
    # Uses itemInit() for each item at the end
    def splitItems(self,items):
        for item in items :
            itemName = ""
            layoutName = "ZZZLast"
            layoutName = self.bestFit(item,{'brItems':{0:{'type':'displayValue'}},'layout':'name'})
            if('layoutId' in item):
                if('Jam' in item['layoutId']):
                    for tracks in item['tracks']:
                        if(len(tracks['title'])>30 or len(tracks['artist'])>35):
                            temp = tracks['title'] + ' by ' + tracks['artist']
                            itemName += temp[0:25] + temp[25:30].replace(' ','\n',1) + temp[30:]+'\n'
                        else:
                            itemName += tracks['title'] + ' by ' + tracks['artist'] + '\n'
                    itemName+= str(item['finalPrice']) + ' Vbucks'
                    self.itemInit(layoutName,itemName,item)
                else:
                    if(item['bundle']!=None):
                        itemName = str(item['bundle']['name']) + '\n' + str(item['finalPrice']) + ' VBucks'
                    else:
                        itemName = shortenName(item['devName'],item['finalPrice'])
            else:
                if(item['bundle']!=None):
                    itemName = str(item['bundle']['name']) + '\n' + str(item['finalPrice']) + ' VBucks'
                else:
                    itemName = shortenName(item['devName'],item['finalPrice'])
            self.itemInit(layoutName,itemName,item)

    #Gets both list of item entries using fortnite-api and getResponse()
    def findItems(self):
        global internet
        data = getResponse('http://fortnite-api.com/v2/shop')
        if(data!=None):
            internet = True
            items = data['entries']
            self.splitItems(items)
        data = getResponse('http://fortnite-api.com/v2/shop/br')
        if(data!=None):
            internet = True
            items = data['featured']['entries']
            self.splitItems(items)
        else:
            internet=False
        temp_dict = self.itemDict
        self.itemDict = dict(sorted(temp_dict.items()))
    
    #Gets the Player Stats for the gamertag name provided no matter the platform
    # raises error in textfield if the gamertag is not found on the site
    def findStats(self,name):
        self.root.ids.search.error = False
        self.root.ids.search.helper_text= ""
        headers = {'Authorization' : 'a760eb7f-2f6b-4eab-80c0-a2053a58dc5e'}
        param = {}
        param['name'] = name
        accountTypes = ['epic','psn','xbl']
        connected = False
        for type in accountTypes:
           param['accountType'] = type
           url = 'http://fortnite-api.com/v2/stats/br/v2'
           try:
            response = requests.get(url,params=param,headers=headers)
            if(response.json()['status']==200):
                self.setStats(response.json()['data'])
                self.root.ids.gamerTag.text = name
                connected = True
                break
           except requests.RequestException as e:
               continue
        global internet
        internet = connected
        if not connected:
            self.root.ids.search.helper_text= "GamerTag Not Found"
            self.root.ids.search.error = True
            print("Could not find user")
        
    #Sets the Stats View based on overall, solo, duos, and squads stats.
    # Keys can be changed to show other stats stored in the data
    # Trios are not displayed, because it is always equal to None in the fortnite-api
    def setStats(self,data):
        overallData = data['stats']['all']['overall']
        soloData = data['stats']['all']['solo']
        duoData = data['stats']['all']['duo']
        squadData = data['stats']['all']['squad']
        self.stats['overall'] = ''
        self.stats['solos'] = ''
        self.stats['duos'] = ''
        self.stats['squads'] = ''
        keys = ['score','wins','winRate','kills','matches','kd','killsPerMatch','playersOutlived']
        self.stats['overall'] = getStatData(keys,overallData)
        self.stats['solos'] = getStatData(keys,soloData)
        self.stats['duos'] = getStatData(keys,duoData)
        self.stats['squads'] = getStatData(keys,squadData)
        self.root.ids.overall.text = self.stats['overall']
        self.root.ids.solos.text = self.stats['solos']
        self.root.ids.duos.text = self.stats['duos']
        self.root.ids.squads.text = self.stats['squads']

#Makes the name apearance nicer
def shortenName(name,price):
    name = name[(str(name).find(']')+1):]
    name = name.replace('MtxCurrency','VBucks')
    name = name[0:-15] + name[-15:].replace('for ','\n')
    name = name.replace('-1',str(price))
    if('vtid' in name):
        name = name[14:].replace('vtid_body_','')
        name = name.replace('1 x ','')
        return name
    name = name.replace('1 x ','')
    return name
#Gets the request Response to the findItems() function
def getResponse(url):
    global internet
    headers = {'Authorization' : 'a760eb7f-2f6b-4eab-80c0-a2053a58dc5e'}
    try:
        response = requests.get(url, headers=headers)
        if(response.status_code!=200):
            raise requests.RequestException("Error Connecting")
        else:
            internet=True
            return response.json()['data']
    except requests.RequestException as e:
        print(e)
        internet=False

#Shortens the setStats() function by retrieving the stats for each stat type individually
def getStatData(keys,data):
    stats = ""
    for dataKey in keys:
        if dataKey in data:
            stats += dataKey + '\n' + str(data[dataKey]) + '\n'
    return stats.replace('kd','K/D')

#Loads the items
MyApp().findItems()
#Runs/Builds the App
MyApp().run()