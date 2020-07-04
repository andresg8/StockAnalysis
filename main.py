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
from searchActivity import SearchActivity
from compareActivity import CompareActivity
from activitySelect import ActivitySelect
import yfinance as yf
import numpy as np
import datetime	
import time
		

class StockAnalysis(App):
	def build(self):
		self.activities = {"search": SearchActivity(), 
		"track": SearchActivity(), 
		"compare": SearchActivity(), 
		"rank":CompareActivity()}
		self.root = GridLayout(cols = 1)
		#######################################
		################ Title ################
		#######################################
		# self.titleLabel = Label(text = " StockAnalysis", color = (180/255, 180/255, 180/255, 1),#(75/255,225/255,0/255,1),
		# 	font_name = "res/Aldrich", font_hinting = "light", bold = True, halign = "left",
		# 	font_size = 36)
		# #self.coloredWidgets.append(self.titleLabel)
		# def titleScale(*args):
		# 	self.titleLabel.text_size = self.titleLabel.size
		# self.titleLabel.bind(size = titleScale)
		# self.root.add_widget(self.titleLabel)
		self.activity = self.activities["search"]
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
		self.scrollView.add_widget(self.activity)
		self.root.add_widget(self.scrollView)
		self.activitySelect = ActivitySelect(self)
		def activitySelectScale(*args):
			self.activitySelect.size = (Window.width, Window.height*.1)
			self.activitySelect.y = 0
		self.activitySelect.bind(size = activitySelectScale)
		self.root.add_widget(self.activitySelect)
		# self.root.add_widget(self.searchLayout)
		return self.root

	

if __name__ == "__main__":
	app = StockAnalysis()
	app.run()