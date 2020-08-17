from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from statLayout import StatLayout
from statsGraph import StatsGraph
from rangeButton import RangeButton
from signalButton import SignalButton
from searchTree import SearchTree
from stockInfo import StockInfo
from popups import LoadingPopup, ErrorPopup
from errors import BadTickerException
import pickle


class StatsActivity(GridLayout):
	def __init__(self, app, searchDB, abbr = "GE"):
		super().__init__(cols = 1, size_hint_y = None)
		#######################################
		############ Housekeeping #############
		#######################################
		self.app = app
		self.searchDB = searchDB
		self.abbr = abbr
		self.stockGraph = None
		self.coloredWidgets = []
		self.color = (255/255, 255/255, 255/255, 1)
		self.bind(minimum_height=self.setter('height'))
		#[red, orange, yellow, green, blue, purple]
		self.colorPallete = [(255/255, 0/255, 0/255, 1), (255/255, 165/255, 0/255, 1),
			(255/255, 255/255, 0/255, 1), (0/255, 255/255, 0/255, 1), 
			(0/255, 0/255, 255/255, 1), (255/255, 0/255, 255/255, 1)]
		#######################################
		############ Search Layout ############
		#######################################
		self.searchLayout = BoxLayout(orientation='horizontal')
		self.searchText = SearchBar(self, self.searchDB)
		self.searchText.width = Window.width * .8
		self.searchText.bind(on_text_validate = self.updateLoader)
		self.searchLayout.add_widget(self.searchText)
		self.searchButton = Button(text = "Cancel",
				font_name = "res/Aldrich", font_hinting = "light", bold = True)
		self.searchButton.width = Window.width *.2
		self.searchButton.bind(on_press = self.removeText)
		self.searchLayout.add_widget(self.searchButton)
		self.add_widget(self.searchLayout)
		#######################################
		############# Data Layout #############
		#######################################
		self.dataLayout = BoxLayout(orientation = "vertical")
		self.currentLayout = self.dataLayout
		#######################################
		############ Ticker Layout ############
		#######################################
		self.tickerLayout = BoxLayout(orientation='horizontal')
		self.tickerTitle = Label(text = self.abbr, color = self.color,
			font_name = "res/Aldrich", font_hinting = "light", bold = True,
			halign = "center", valign = "center")
		def tickerTitleScale(*args):
			self.tickerTitle.text_size = self.tickerTitle.size
		self.tickerTitle.bind(size = tickerTitleScale)
		self.coloredWidgets.append(self.tickerTitle)
		self.tickerLayout.add_widget(self.tickerTitle)
		self.tickerDisplay = Label(text = "", halign = "center", color = self.color,
			font_name = "res/Aldrich", font_hinting = "light", bold = True)
		self.coloredWidgets.append(self.tickerDisplay)
		self.tickerLayout.add_widget(self.tickerDisplay)
		self.dataLayout.add_widget(self.tickerLayout)
		#######################################
		############# Stock Graph #############
		#######################################
		self.stockGraph = StatsGraph(self.abbr, self, False)
		self.dataLayout.add_widget(self.stockGraph)
		# for i in range(len(self.stockGraph.AIKB)):
		# 	button = 
		#######################################
		############ Range Options ############
		#######################################
		self.rangeLayout = BoxLayout(orientation='horizontal')
		ranges = [("1W","1wk","1d"), ("2W","2wk","1d"), ("1M","1mo","1d"), ("3M","3mo","1d"),
					("YTD","YTD","1d"), ("1Y","1y","1d"), ("2Y","2y","1d")]
		self.rangeButtons = []
		for r in ranges:
			rangeButton = RangeButton(r[0], self, r[1], r[2])
			self.rangeLayout.add_widget(rangeButton)
			if r[0]=="YTD":rangeButton.active = True
			self.rangeButtons.append(rangeButton)
		self.dataLayout.add_widget(self.rangeLayout)
		self.signalLineGrid = GridLayout(rows = 1, size_hint_y = None, height = Window.height * .1)
		self.signalButtons = []
		# No Signals, Sell Signals, Buy Signals, All Signals
		combos = [("No Signals", self, False, False), ("Sell Signals", self, False, True), 
				("Buy Signals", self, True, False), ("Both Signals", self, True, True)]
		for combo in combos:
			sb = SignalButton(*combo)
			self.signalButtons.append(sb)
			self.signalLineGrid.add_widget(sb)
		self.signalButtons[0].active = True
		self.signalButtons[0].drawSelected()
		self.dataLayout.add_widget(self.signalLineGrid)
		self.updateColors()
		self.updateInfo(self.abbr)
		self.statGrid = GridLayout(cols = 2, size_hint_y = None, height = Window.height * .5)
		self.statLayouts = []
		for k, v in self.stockGraph.stats.items():
			rng = False
			default = 0
			if k in ["Bollinger Bands", "Exponential Moving Average", "Simple Moving Average",
						"Relative Strength Index", "Average True Range", "Triple EMA"]:
				rng = True
				default = 10
			statLayout = StatLayout(k, v[1], self, v[0], rng, default)
			self.statGrid.add_widget(statLayout)
			self.statLayouts.append(statLayout)
		self.dataLayout.add_widget(self.statGrid)	
		self.add_widget(self.dataLayout)
		#######################################
		############# Ratio Setup #############
		#######################################
		self.searchLayout.size_hint_y = None
		self.searchLayout.height = Window.height * .1

		self.tickerLayout.size_hint_y = None
		self.tickerLayout.height = Window.height * .1
		self.stockGraph.size_hint_y = None
		self.stockGraph.height = Window.height * .5
		self.rangeLayout.size_hint_y = None
		self.rangeLayout.height = Window.height * .1
		self.dataLayout.size_hint_y = None
		self.dataLayout.height = (self.tickerLayout.height + self.stockGraph.height + self.rangeLayout.height + Window.height * .6)
		# self.bind(size = self.scale)

	def scale(self, *args):
		Clock.schedule_once(self.continuousHeight, 0)

	def continuousHeight(self, *args):
		self.dataLayout.height = (self.tickerLayout.height + 
			self.stockGraph.height + self.rangeLayout.height + Window.height * .6)

	def removeText(self, *args):
		# if not self.searchText.text: 
		# 	return
		self.searchText.text = ""
		self.swap()

	def updateColors(self):
		if not self.stockGraph: 
			return
		self.color = self.stockGraph.color
		for widget in self.coloredWidgets:
			widget.color = self.color
		for button in self.rangeButtons:
			button.updateColor()

	def updateLoader(self, *args):
		if not self.searchText.text: 
			return
		self.ticker = self.searchText.text.upper()
		self.searchText.text = ""
		self.loading = LoadingPopup()
		self.loading.open()
		Clock.schedule_once(self.updateGraph)

	def updateGraph(self, *args):
		try:
			for stat in self.statLayouts:
				stat.statButton.active = False
				stat.statButton.draw()
			self.stockGraph.updateTicker(self.ticker)
			self.tickerTitle.text = self.ticker
			self.updateInfo(self.ticker)
		except BadTickerException as e:
			errmsg = str(e.ticker) + " does not exist or has been delisted!"
			self.errorPopup = ErrorPopup(errmsg)
			self.errorPopup.open()
		self.loading.dismiss()

	def updateInfo(self, newTicker):
		try:
			self.stockInfo = self.stockGraph.ticker.info
		except:
			print("Unable to load info for", newTicker)
		try:
			self.tickerTitle.text = newTicker + "\n" + self.stockInfo["longName"]
		except:
			print("longName failed")

	def artificialUpdateGraph(self, ticker):
		if not ticker: 
			return
		self.ticker = ticker
		self.loading = LoadingPopup()
		self.loading.open()
		Clock.schedule_once(self.updateGraph)


	def swap(self, new = None):
		if not new:
			new = self.dataLayout
		self.remove_widget(self.currentLayout)
		self.currentLayout = new
		self.add_widget(self.currentLayout)


class SearchBar(TextInput):
	def __init__(self, alpha, searchDB):
		super().__init__(hint_text = "Company...", background_color = (0, 0, 0, 0),
			foreground_color = (1, 1, 1, 1), cursor_color = (0, 1, 0, 1),
			multiline = False)
		if not searchDB:
			searchables = pickle.load(open("res/searchables.p", 'rb'))
			self.crossRefs = pickle.load(open("res/crossMark6.p", 'rb'))
			self.searchRecs = SearchTree(searchables)
		else:
			self.crossRefs = searchDB[0]
			self.searchRecs = searchDB[1]
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
		# else:
		# 	self.alpha.swap()

	def autofill(self, *args):
		if self.searchRecLayout and args[-1]:
			self.searchRecLayout = GridLayout(cols = 1, 
				size_hint_y = None, height = Window.height * 1)
			recommend = self.searchRecs.relateItem(args[-1].upper())
			txts = []
			for r in recommend:
				cross = ""
				if r in self.crossRefs:
					cross = self.crossRefs[r]
				abbr = cross
				name = r
				if len(r) < len(cross) or not cross:
					abbr = r
					name = cross
				elif len(r) == len(cross) and r < cross:
					abbr = r
					name = cross
				if "(the)" in name.lower(): name = "The " + name[0:-6]
				txt = abbr + ": " + name
				if txt in txts:
					continue
				txts.append(txt)
				b = Button(text = txt, height = Window.height * .1,
					size_hint_max_y = Window.height * .1, size_hint_min_y = Window.height * .1)
				b.abbr = abbr
				def useRec(itself):
					self.text = itself.abbr
					self.alpha.swap()
					self.alpha.updateLoader()
				b.bind(on_press = useRec)
				self.searchRecLayout.add_widget(b)
			self.alpha.swap(self.searchRecLayout)
