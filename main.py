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
from rankActivity import RankActivity
from activitySelect import ActivitySelect
from statsActivity import StatsActivity
from trackActivity import TrackActivity
from searchTree import SearchTree
import yfinance as yf
import numpy as np
import datetime	
import pickle
import time
		

class StockAnalysis(App):
	def build(self):
		searchables = pickle.load(open("res/searchables.p", 'rb'))
		self.crossRefs = pickle.load(open("res/crossMark6.p", 'rb'))
		self.searchRecs = SearchTree(searchables)
		self.searchDB = (self.crossRefs, self.searchRecs)
		self.activities = {"search": SearchActivity(self, self.searchDB),
		"track": TrackActivity(self, self.searchDB),
		"stats": StatsActivity(self, self.searchDB),
		"rank": RankActivity(self)}
		self.root = GridLayout(cols = 1)
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
		return self.root

	

if __name__ == "__main__":
	app = StockAnalysis()
	app.run()