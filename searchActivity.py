from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from stockGraph import StockGraph
from rangeButton import RangeButton
from stockInfo import StockInfo
from popups import LoadingPopup, ErrorPopup
from errors import BadTickerException
import pickle


class SearchActivity(GridLayout):
	def __init__(self, app, searchDB):
		super().__init__(cols = 1, size_hint_y = None)
		self.app = app
		self.searchDB = searchDB
		self.abbr = "GE"
		self.stockGraph = None
		self.coloredWidgets = []
		self.color = (0/255, 255/255, 0/255, 1)
		#######################################
		########### Activity Layout ###########
		#######################################
		#self.graphDataLayout = GridLayout(cols = 1, size_hint_y = None)
		self.bind(minimum_height=self.setter('height'))
		#######################################
		############ Search Layout ############
		#######################################
		self.searchLayout = BoxLayout(orientation='horizontal')
		#hint_text = "Company...", background_color = (0, 0, 0, 0),
		#	foreground_color = (1, 1, 1, 1), cursor_color = (0, 1, 0, 1),
		#	multiline = False
		self.searchText = SearchBar(self, self.searchDB)
		self.searchText.bind(on_text_validate = self.updateGraph)
		self.searchLayout.add_widget(self.searchText)
		self.searchButton = Button(text = "Cancel",
				font_name = "res/Aldrich", font_hinting = "light", bold = True)
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
		# self.dataLayout.add_widget(self.searchLayout)
		self.dataLayout.add_widget(self.tickerLayout)
		#######################################
		############# Stock Graph #############
		#######################################
		self.stockGraph = StockGraph(self.abbr, self)
		self.dataLayout.add_widget(self.stockGraph)
		#######################################
		############ Range Options ############
		#######################################
		self.rangeLayout = BoxLayout(orientation='horizontal')
		ranges = [("1D","1d","5m"), ("1W","1wk","15m"), ("1M","1mo","60m"),
					("YTD","YTD","1h"), ("1Y","1y","1d"), ("5Y","5y","1wk")]
		self.rangeButtons = []
		for r in ranges:
			rangeButton = RangeButton(r[0], self, r[1], r[2])
			self.rangeLayout.add_widget(rangeButton)
			if r[0]=="YTD":rangeButton.active = True
			self.rangeButtons.append(rangeButton)
		self.dataLayout.add_widget(self.rangeLayout)
		self.updateColors()
		self.updateInfo(self.abbr)
		self.info = StockInfo(self.stockGraph.ticker)
		self.dataLayout.add_widget(self.info)
		#######################################
		############# Ratio Setup #############
		#######################################
		self.searchLayout.size_hint_y = None
		self.searchLayout.height = Window.height * .1

		self.add_widget(self.dataLayout)
		self.info.size_hint_y = None
		self.tickerLayout.size_hint_y = None
		self.tickerLayout.height = Window.height * .1
		self.stockGraph.size_hint_y = None
		self.stockGraph.height = Window.height * .8
		self.rangeLayout.size_hint_y = None
		self.rangeLayout.height = Window.height * .1
		self.dataLayout.size_hint_y = None
		self.info.continuousHeight()
		self.dataLayout.height = (self.info.height + 
		 	self.tickerLayout.height + self.stockGraph.height + self.rangeLayout.height)
		self.bind(size = self.scale)
		Clock.schedule_once(self.continuousHeight, 0)

	def scale(self, *args):
		Clock.schedule_once(self.continuousHeight, 0)

	def continuousHeight(self, *args):
		self.dataLayout.height = (self.info.height + self.tickerLayout.height + 
			self.stockGraph.height + self.rangeLayout.height)

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

	def updateGraph(self, *args):
		if not self.searchText.text: 
			return
		self.ticker = self.searchText.text.upper()
		self.searchText.text = ""
		self.loading = LoadingPopup()
		self.loading.open()
		Clock.schedule_once(self.update)
		

	def update(self, *args):
		try:
			self.stockGraph.updateTicker(self.ticker)
			self.info.updateTicker(self.stockGraph.ticker)
			self.tickerTitle.text = self.ticker
			self.updateInfo(self.ticker)
			self.info.scale()
			self.scale()
		except BadTickerException as e:
			errmsg = str(e.ticker) + " does not exist or has been delisted!"
			self.errorPopup = ErrorPopup(errmsg)
			self.errorPopup.open()
		# except IndexError as e:

		self.loading.dismiss()

	def updateInfo(self, newTicker):
		try:
			self.stockInfo = self.stockGraph.ticker.info
		except:
			self.stockInfo = dict()
			print("Unable to load info for", newTicker)
		try:
			self.tickerTitle.text = newTicker + "\n" + self.stockInfo["longName"]
		except:
			self.tickerTitle.text = newTicker 
			print("longName failed")

	def artificialUpdateGraph(self, ticker):
		if not ticker: 
			return
		self.ticker = ticker
		self.loading = LoadingPopup()
		self.loading.open()
		Clock.schedule_once(self.update)


	def swap(self, new = None):
		if not new:
			new = self.dataLayout
		self.remove_widget(self.currentLayout)
		self.currentLayout = new
		self.add_widget(self.currentLayout)


class SearchBar(TextInput):
	def __init__(self, alpha, searchDB = None):
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
				b = Button(text = txt, height = Window.height * .1, halign = "center",
					size_hint_max_y = Window.height * .1, size_hint_min_y = Window.height * .1)
				b.text_size[0] = Window.width
				b.abbr = abbr
				def useRec(itself):
					self.text = itself.abbr
					self.alpha.swap()
					self.alpha.updateGraph()
				b.bind(on_press = useRec)
				self.searchRecLayout.add_widget(b)
			self.searchRecLayout.height = Window.height * .1 * len(recommend)
			self.alpha.swap(self.searchRecLayout)


