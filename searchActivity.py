from kivy.app import App 
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import *
from stockGraph import StockGraph
from rangeButton import RangeButton
from searchTree import SearchTree
import yfinance as yf
import numpy as np
import datetime	
import pickle


class SearchActivity(GridLayout):
	def __init__(self):
		super().__init__(cols = 1, size_hint_y = None)
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
		self.searchText = SearchBar(self)
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
			font_name = "res/Aldrich", font_hinting = "light", bold = True)
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
		#######################################
		############# Ratio Setup #############
		#######################################
		self.searchLayout.size_hint_y = None
		self.searchLayout.height = Window.height * .1

		self.add_widget(self.dataLayout)
		self.dataLayout.size_hint_y = None
		self.dataLayout.height = Window.height * 1
		self.tickerLayout.size_hint_y = None
		self.tickerLayout.height = Window.height * .1
		self.stockGraph.size_hint_y = None
		self.stockGraph.height = Window.height * .8
		self.rangeLayout.size_hint_y = None
		self.rangeLayout.height = Window.height * .1

	def removeText(self, *args):
		if not self.searchText.text: 
			return
		self.searchText.text = ""
		self.searchText.focus = False

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
		newTicker = self.searchText.text
		self.searchText.text = ""
		try:
			self.stockGraph.updateTicker(newTicker)
			self.tickerTitle.text = newTicker
		except:
			print("Unga Bunga, error occured")
			return

	def swap(self, new = None):
		if not new:
			new = self.dataLayout
		self.remove_widget(self.currentLayout)
		self.currentLayout = new
		self.add_widget(self.currentLayout)


class SearchBar(TextInput):
	def __init__(self, alpha):
		super().__init__(hint_text = "Company...", background_color = (0, 0, 0, 0),
			foreground_color = (1, 1, 1, 1), cursor_color = (0, 1, 0, 1),
			multiline = False)
		searchables = pickle.load(open("res/searchables.p", 'rb'))
		self.crossRefs = pickle.load(open("res/crossMark6.p", 'rb'))
		self.searchRecs = SearchTree(searchables)
		self.alpha = alpha
		self.scrollView = None
		self.searchRecLayout = None
		self.bind(focus = self.updateAFBox)
		self.bind(text = self.autofill)

	def updateAFBox(self, *args):
		if args[-1]:
			#print(args)
			#generateAFBox()
			self.searchRecLayout = GridLayout(cols = 1, 
				size_hint_y = None, height = Window.height * 1)
			if self.text:
				self.autofill(self.text)
			self.alpha.swap(self.searchRecLayout)
		else:
			self.alpha.swap()

	def autofill(self, *args):
		if self.searchRecLayout and args[-1]:
			#print("trying to populate")
			self.searchRecLayout = GridLayout(cols = 1, 
				size_hint_y = None, height = Window.height * 1)
			recommend = self.searchRecs.relateItem(args[-1].upper())
			for r in recommend:
				#print(r)
				cross = ""
				if r in self.crossRefs:
					cross = self.crossRefs[r]
				if len(r) <= len(cross) or not cross:
					abbr = r
					name = cross
				elif len(r) > len(cross):
					abbr = cross
					name = r
				b = Button(text = abbr + ": " + name, height = Window.height * .1,
					size_hint_max_y = Window.height * .1, size_hint_min_y = Window.height * .1)
				b.abbr = abbr
				def useRec(itself):
					self.text = itself.abbr
					self.alpha.updateGraph()
				b.bind(on_press = useRec)
				self.searchRecLayout.add_widget(b)
			self.alpha.swap(self.searchRecLayout)
