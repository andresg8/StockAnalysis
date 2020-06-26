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
from rangeButton import RangeButton
from stockGraph import StockGraph
import yfinance as yf
import numpy as np
import datetime	

class StockAnalysis(App):
	def build(self):
		self.abbr = "GE"
		self.root = GridLayout(cols = 1)
		self.stockGraph = None
		self.coloredWidgets = []
		#######################################
		############ Feature Layout ###########
		#######################################
		self.color = (0/255, 255/255, 0/255, 1)
		self.graphDataLayout = GridLayout(cols = 1, size_hint_y = None)
		self.graphDataLayout.bind(minimum_height=self.graphDataLayout.setter('height'))
		#######################################
		################ Title ################
		#######################################
		self.titleLabel = Label(text = " StockAnalysis", color = (180/255, 180/255, 180/255, 1),#(75/255,225/255,0/255,1),
			font_name = "res/Aldrich", font_hinting = "light", bold = True, halign = "left",
			font_size = 36)
		#self.coloredWidgets.append(self.titleLabel)
		def titleScale(*args):
			self.titleLabel.text_size = self.titleLabel.size
		self.titleLabel.bind(size = titleScale)
		self.graphDataLayout.add_widget(self.titleLabel)
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
		self.graphDataLayout.add_widget(self.tickerLayout)
		#######################################
		############# Stock Graph #############
		#######################################
		self.stockGraph = StockGraph(self.abbr, self)
		self.graphDataLayout.add_widget(self.stockGraph)
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
		self.graphDataLayout.add_widget(self.rangeLayout)
		#######################################
		############ Search Layout ############
		#######################################
		self.searchLayout = BoxLayout(orientation='horizontal')
		self.searchText = TextInput(hint_text = "Company...", background_color = (0, 0, 0, 0),
			foreground_color = (1, 1, 1, 1), cursor_color = (0, 1, 0, 1),
			multiline = False)
		self.searchText.bind(on_text_validate = self.updateGraph)
		self.searchLayout.add_widget(self.searchText)
		self.searchButton = Button(text = "Search",
				font_name = "res/Aldrich", font_hinting = "light", bold = True)
		self.searchButton.bind(on_press = self.updateGraph)
		self.searchLayout.add_widget(self.searchButton)
		#self.graphDataLayout.add_widget(self.searchLayout)
		self.updateColors()
		#######################################
		############# Ratio Setup #############
		#######################################
		self.titleLabel.size_hint_y = None
		self.titleLabel.height = Window.height * .1
		self.tickerLayout.size_hint_y = None
		self.tickerLayout.height = Window.height * .15
		self.stockGraph.size_hint_y = None
		self.stockGraph.height = Window.height * .5
		self.rangeLayout.size_hint_y = None
		self.rangeLayout.height = Window.height * .1
		self.searchLayout.size_hint_y = None
		self.searchLayout.height = Window.height * .1
		#######################################
		############# Scroll View #############
		#######################################
		self.scrollView = ScrollView(size_hint = (1, None), do_scroll_x = False,
			do_scroll_y = True, size = (Window.width, Window.height*.9), scroll_timeout = 88,
			y = Window.height*.1)
		def scrollViewScale(*args):
			self.scrollView.size = (Window.width, Window.height*.9)
			self.scrollView.y = Window.height*.1
		self.scrollView.bind(size = scrollViewScale)
		self.scrollView.add_widget(self.graphDataLayout)
		self.root.add_widget(self.scrollView)
		self.root.add_widget(self.searchLayout)
		return self.root

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

if __name__ == "__main__":
	StockAnalysis().run()