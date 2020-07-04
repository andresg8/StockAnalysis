from kivy.app import App 
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
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
import yfinance as yf
import numpy as np
import datetime	
import time

class ActivitySelect(BoxLayout):
	def __init__(self, alpha):
		super().__init__(orientation = "horizontal", y = 0,
			size_hint = (1, None), height = Window.height*.1)
		self.spacing = (self.width * .2)/3
		self.alpha = alpha
		self.buttons = []
		srcs = ["search", "money", "chart", "rank"]
		funcs = [self.toSearchActivity, self.toTrackActivity,
				self.toCompareActivity, self.toRankActivity]
		for i in range(len(srcs)):
			b = IconButton(self, funcs[i], srcs[i])
			self.buttons.append(b)
			self.add_widget(b)
		self.updateSelected(self.buttons[0])

	def toSearchActivity(self, itself):
		self.updateSelected(itself)
		self.alpha.scrollView.remove_widget(self.alpha.activity)
		self.alpha.activity = self.alpha.activities["search"]
		self.alpha.scrollView.add_widget(self.alpha.activity)

	def toTrackActivity(self, itself):
		self.updateSelected(itself)
		self.alpha.scrollView.remove_widget(self.alpha.activity)
		self.alpha.activity = self.alpha.activities["track"]
		self.alpha.scrollView.add_widget(self.alpha.activity)

	def toCompareActivity(self, itself):
		self.updateSelected(itself)
		self.alpha.scrollView.remove_widget(self.alpha.activity)
		self.alpha.activity = self.alpha.activities["compare"]
		self.alpha.scrollView.add_widget(self.alpha.activity)

	def toRankActivity(self, itself):
		self.updateSelected(itself)
		self.alpha.scrollView.remove_widget(self.alpha.activity)
		self.alpha.activity = self.alpha.activities["rank"]
		self.alpha.scrollView.add_widget(self.alpha.activity)		


	def updateSelected(self, itself):
		for button in self.buttons:
			if button != itself:
				button.colorUnselected()
		itself.colorSelected()


class IconButton(Button):
	def __init__(self, layout, func, src):
		super().__init__(text = "",background_color = (1,1,1,0))
		with self.canvas:
			self.image = Image(source = "res/" + src + ".png", color = (255/255,255/255,255/255,1))
		self.drawn = None
		self.draw()
		self.func = func
		self.bind(on_press = self.func)
		self.bind(size = self.draw, pos = self.draw)

	def colorSelected(self):
		self.image.color = (1,1,1,1)

	def colorUnselected(self):
		self.image.color = (255/255,255/255,255/255,.3)

	def draw(self, *args):
		ix, iy = self.image.size
		x = self.x + self.width/2 - ix/2
		y = self.y + self.height/2 - iy/2
		self.image.pos = (x,y)
		