from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from stockGraph import StockGraph
from rangeButton import RangeButton
from searchTree import SearchTree
import pickle
import requests

class RankActivity(GridLayout):
	def __init__(self, alpha):
		super().__init__(cols = 1, size_hint_y = None)
		self.alpha = alpha
		self.crossRefs = pickle.load(open("res/crossMark6.p", 'rb'))
		self.bind(minimum_height=self.setter('height'))
		self.newCat = ""
		self.sortby = 1
		self.titleText = "Signal Rankings"
		self.titleLabel = Label(text = self.titleText, font_name = "res/Aldrich", font_hinting = "light",
								height = Window.height * .1, size_hint_y = None, halign = "left", font_size = 24)
		self.add_widget(self.titleLabel)
		self.sortLayout = BoxLayout(orientation = 'horizontal', size_hint_y = None, height = Window.height * .1)
		self.sortLabel = Label(text = "Sort by:", font_name = "res/Aldrich", font_hinting = "light",
								height = Window.height * .1, size_hint_y = None, halign = "left", size_hint_x = .5)
		self.sortLabel.text_size[0] = self.sortLabel.width
		self.sortLayout.add_widget(self.sortLabel)
		self.sortByBuy = Button(text = "Buy", font_name = "res/Aldrich", font_hinting = "light",
								height = Window.height * .1, size_hint_y = None, size_hint_x = .25, 
								background_color = (0, 1, 0, 1))
		self.sortByBuy.bind(on_press = self.setToBuy)
		self.sortLayout.add_widget(self.sortByBuy)
		self.sortBySell = Button(text = "Sell", font_name = "res/Aldrich", font_hinting = "light",
								height = Window.height * .1, size_hint_y = None, size_hint_x = .25,
								background_color = (1, 1, 1, 0))
		self.sortBySell.bind(on_press = self.setToSell)
		self.sortLayout.add_widget(self.sortBySell)
		self.add_widget(self.sortLayout)

		self.searchLayout = BoxLayout(orientation='horizontal')
		self.searchText = SearchBarCompare(self)
		self.searchText.bind(on_text_validate = self.updateList)
		self.searchLayout.add_widget(self.searchText)
		self.searchButton = Button(text = "Cancel",
				font_name = "res/Aldrich", font_hinting = "light", bold = True)
		self.searchButton.bind(on_press = self.removeText)
		self.searchLayout.add_widget(self.searchButton)
		self.add_widget(self.searchLayout)
		self.dataLayout = BoxLayout(orientation = "vertical")
		self.currentLayout = self.dataLayout
		self.add_widget(self.dataLayout)
		self.searchLayout.size_hint_y = None
		self.searchLayout.height = Window.height * .1
		self.dataLayout.size_hint_y = None
		self.dataLayout.height = Window.height * 1

	def setToBuy(self, *args):
		self.sortByBuy.background_color = (0, 1, 0, 1)
		self.sortBySell.background_color = (1, 1, 1, 0)
		self.sortby = 1
		self.resortList()

	def setToSell(self, *args):
		self.sortByBuy.background_color = (1, 1, 1, 0)
		self.sortBySell.background_color = (1, 0, 0, 1)
		self.sortby = 2
		self.resortList()

	def removeText(self, *args):
		if not self.searchText.text: 
			return
		self.searchText.text = ""
		self.searchText.focus = False

	def swap(self, new = None):
		if not new:
			new = self.dataLayout
		self.remove_widget(self.currentLayout)
		self.currentLayout = new
		self.add_widget(self.currentLayout)

	def downloadCat(self, cat):
		db = "http://ec2-3-15-144-165.us-east-2.compute.amazonaws.com/getCategory.php?catName="
		cat = cat.replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace("/", "")
		db += cat
		response = requests.get(db)
		jstocks = response.json()
		stocksDict = jstocks["Stocks"]
		stocks = []
		for stock in stocksDict:
			stocks.append([stock["ABBR"], float(stock["BUY"]), float(stock["SELL"])])
		stocks = sorted(stocks, key= lambda stock: stock[self.sortby])
		return stocks

	def resortList(self):
		if not self.newCat:
			return
		try:
			self.dataLayout = BoxLayout(orientation = "vertical")
			stocks = []
			if self.newCat in self.searchText.crossRefs:
				stocks = self.downloadCat(self.newCat)
				self.titleLabel.text = self.newCat + " " + self.titleText
			for stock in reversed(stocks):
				abbr = stock[0]
				buy = stock[1]
				sell = stock[2]
				if abbr in self.crossRefs:
					name = self.crossRefs[abbr]
				elif abbr[:-1] in self.crossRefs:
					name = self.crossRefs[abbr[:-1]]
				else:
					continue
				txt = (abbr + ": " + name )
				if self.sortby == 1:
					txt += " +" + str(buy)
				if self.sortby == 2:
					txt += " -" + str(sell)
				b = Button(text = txt, height = Window.height * .1,
					size_hint_max_y = Window.height * .1, size_hint_min_y = Window.height * .1)
				b.abbr = abbr
				def viewGraph(itself):
					if "stats" not in self.alpha.activities:
						self.alpha.activitySelect.makeCompareActivityExceptImAHomelessManThatDoesntKnowHowToCode(itself.abbr)
						self.alpha.activitySelect.artificialClick("stats")
					else:
						self.alpha.activities["stats"].artificialUpdateGraph(itself.abbr)
						self.alpha.activities["stats"].removeText()
						self.alpha.activitySelect.artificialClick("stats")
				b.bind(on_press = viewGraph)
				self.dataLayout.add_widget(b)
			self.dataLayout.size_hint_y = None
			self.dataLayout.height = Window.height * .1 * len(stocks)
			self.swap()
		except Exception as e:
			print(e)
			return

	def updateList(self, *args):
		if not self.searchText.text: 
			return
		self.newCat = self.searchText.text
		self.searchText.text = ""
		try:
			self.dataLayout = BoxLayout(orientation = "vertical")
			stocks = []
			if self.newCat in self.searchText.crossRefs:
				stocks = self.downloadCat(self.newCat)
				self.titleLabel.text = self.newCat + " " + self.titleText
			for stock in reversed(stocks):
				abbr = stock[0]
				buy = stock[1]
				sell = stock[2]
				if abbr in self.crossRefs:
					name = self.crossRefs[abbr]
				elif abbr[:-1] in self.crossRefs:
					name = self.crossRefs[abbr[:-1]]
				else:
					continue
				txt = (abbr + ": " + name)
				if self.sortby == 1:
					txt += " +" + str(buy)
				if self.sortby == 2:
					txt += " -" + str(sell)	
				b = Button(text = txt, height = Window.height * .1,
					size_hint_max_y = Window.height * .1, size_hint_min_y = Window.height * .1)
				b.abbr = abbr
				def viewGraph(itself):
					if "stats" not in self.alpha.activities:
						self.alpha.activitySelect.makeCompareActivityExceptImAHomelessManThatDoesntKnowHowToCode(itself.abbr)
						self.alpha.activitySelect.artificialClick("stats")
					else:
						self.alpha.activities["stats"].artificialUpdateGraph(itself.abbr)
						self.alpha.activities["stats"].removeText()
						self.alpha.activitySelect.artificialClick("stats")
				b.bind(on_press = viewGraph)
				self.dataLayout.add_widget(b)
			self.dataLayout.size_hint_y = None
			self.dataLayout.height = Window.height * .1 * len(stocks)
			self.swap()
		except Exception as e:
			print(e)
			return



class SearchBarCompare(TextInput):
	def __init__(self, alpha):
		super().__init__(hint_text = "Category...", background_color = (0, 0, 0, 0),
			foreground_color = (1, 1, 1, 1), cursor_color = (0, 1, 0, 1),
			multiline = False)
		self.crossRefs = pickle.load(open("res/catDict.p", 'rb'))
		searchables = list(self.crossRefs.keys())
		self.searchRecs = SearchTree(searchables)
		self.alpha = alpha
		self.scrollView = None
		self.searchRecLayout = None
		self.bind(focus = self.updateAFBox)
		self.bind(text = self.autofill)

	def updateAFBox(self, *args):
		if args[-1]:
			self.searchRecLayout = GridLayout(cols = 1, 
				size_hint_y = None, height = Window.height * 1)
			if self.text:
				self.autofill(self.text)
			self.alpha.swap(self.searchRecLayout)
		else:
			self.alpha.swap()

	def autofill(self, *args):
		if self.searchRecLayout and args[-1]:
			self.searchRecLayout = GridLayout(cols = 1, 
				size_hint_y = None, height = Window.height * 1)
			recommend = self.searchRecs.relateItem(args[-1].upper())
			for cat in recommend:
				b = Button(text = cat, height = Window.height * .1,
					size_hint_max_y = Window.height * .1, size_hint_min_y = Window.height * .1)
				b.cat = cat
				def useRec(itself):
					self.text = itself.cat
					self.alpha.updateList()
				b.bind(on_press = useRec)
				self.searchRecLayout.add_widget(b)
			self.alpha.swap(self.searchRecLayout)