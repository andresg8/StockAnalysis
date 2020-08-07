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
import requests

class RankActivity(GridLayout):
	def __init__(self, alpha):
		super().__init__(cols = 1, size_hint_y = None)
		self.alpha = alpha
		self.crossRefs = pickle.load(open("res/crossMark6.p", 'rb'))
		self.bind(minimum_height=self.setter('height'))
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
			stocks.append([stock["ABBR"], int(stock["OT"]), int(stock["ELAST"]), int(stock["STABLE"]), int(stock["ROI5Y"]), int(stock["ROI1Y"])])
		#stocks = sorted(stocks, key= lambda stock: sum(stock[1:]))
		return stocks

	def updateList(self, *args):
		if not self.searchText.text: 
			return
		newCat = self.searchText.text
		self.searchText.text = ""
		try:
			self.dataLayout = BoxLayout(orientation = "vertical")
			stocks = []
			if newCat in self.searchText.crossRefs:
				stocks = self.downloadCat(newCat)
			for stock in reversed(stocks):
				abbr = stock[0]
				name = self.crossRefs[abbr]
				OT, ELAST, STABLE, ROI5Y, ROI1Y = stock[1:]
				txt = (abbr + ": " + name + " - " + str(OT) + " " + str(ELAST) + " " +
						str(STABLE) + " " + str(ROI5Y) + " " + str(ROI1Y))
				b = Button(text = txt, height = Window.height * .1,
					size_hint_max_y = Window.height * .1, size_hint_min_y = Window.height * .1)
				b.abbr = abbr
				def viewGraph(itself):
					self.alpha.activities["search"].artificialUpdateGraph(itself.abbr)
					self.alpha.activitySelect.artificialClick("search")
				b.bind(on_press = viewGraph)
				self.dataLayout.add_widget(b)
			self.dataLayout.size_hint_y = None
			self.dataLayout.height = Window.height * .1 * len(stocks)
			self.swap()
		except Exception as e:
			print(e)
			return

	'''
	def updateList(self, *args):
		if not self.searchText.text: 
			return
		newCat = self.searchText.text
		self.searchText.text = ""
		try:
			self.dataLayout = BoxLayout(orientation = "vertical")
			stocks = self.searchText.crossRefs[newCat]
			for stock in stocks:
				abbr, name = stock
				b = Button(text = abbr + ": " + name, height = Window.height * .1,
					size_hint_max_y = Window.height * .1, size_hint_min_y = Window.height * .1)
				b.abbr = abbr
				def viewGraph(itself):
					self.alpha.activities["search"].artificialUpdateGraph(itself.abbr)
					self.alpha.activitySelect.artificialClick("search")
				b.bind(on_press = viewGraph)
				self.dataLayout.add_widget(b)
			self.dataLayout.size_hint_y = None
			self.dataLayout.height = Window.height * .1 * len(stocks)
			self.swap()
		except:
			print("Unga Bunga, error occured")
			return
	'''


class SearchBarCompare(TextInput):
	def __init__(self, alpha):
		super().__init__(hint_text = "Company...", background_color = (0, 0, 0, 0),
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