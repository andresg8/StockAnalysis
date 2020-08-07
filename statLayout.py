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
import yfinance as yf
import numpy as np
import datetime

class StatLayout(GridLayout):
	def __init__(self, text, color, activity, func, rng = False, default = 0):
		super().__init__(rows = 1, size_hint_y = None, height = Window.height * .1)
		self.bind(minimum_height=self.setter('height'))
		self.statButton = StatButton(text, color, activity, self, func, rng)
		self.add_widget(self.statButton)
		if rng:
			self.rngEntry = TextInput(text = str(default), background_color = (0, 0, 0, 0),
			foreground_color = (1, 1, 1, 1), cursor_color = (0, 1, 0, 1),
			multiline = False)
			self.rngEntry.width = Window.width * .06
			self.rngEntry.height = Window.height * .075
			self.add_widget(self.rngEntry)


class StatButton(Button):
	def __init__(self, text, color, activity, master, func, rng = False):
		super().__init__(text = text, font_name = "res/Aldrich", 
			font_hinting = "light", bold = True, background_color = (1,1,1,0),
			halign = "left", valign = "center", size_hint_y = None, size_hint_x = None,
			height = Window.height * .1, width = Window.width * .44)
		self.text = text
		self.highlighter = color
		self.activity = activity
		self.master = master
		self.func = func
		self.rng = rng
		self.highlights = None
		self.active = False
		#self.drawUnselected()
		self.bind(on_press = self.updateActiveStats)
		self.bind(size = self.draw, pos = self.draw)


	def updateActiveStats(self, itself):
		if not self.active:
			# try:
			if self.rng:
				stat = self.func(int(self.master.rngEntry.text))
			else:
				stat = self.func()
			if not stat:
				raise Exception
			if type(stat[0]) == list:
				for s in stat:
					if not s: raise Exception
			
			self.activity.stockGraph.addActiveStats(self.text, stat)
			self.active = True
			self.draw()
			# except:
			# 	print("Insufficient Data Points")
		elif self.active:
			self.active = False
			self.draw()
			self.activity.stockGraph.removeActiveStats(self.text)


	def updateColor(self):
		if self.highlights:
			self.canvas.remove(self.highlights)
			wp = self.width * .225
			hp = self.height * .225
			args = (self.x+wp, self.y+hp*1.05, self.width-wp*2, self.height-hp*2, 12, 100)
			with self.canvas:
				Color(*self.alpha.color)
				self.highlights = Line(rounded_rectangle=args, width = 1.2)

	def draw(self, *args):
		if self.active:
			# self.drawSelected()
			delta = (1, 1, 1, .86)
			x = tuple(delta[i] * self.highlighter[i] for i in range(len(delta)))
			self.background_color = x
		else:
			# self.drawUnselected()
			self.background_color = (1,1,1,0)

	def drawUnselected(self):
		if self.highlights:
			self.canvas.remove(self.highlights)
			self.highlights = None
	
	def drawSelected(self):
		if self.highlights:
			self.canvas.remove(self.highlights)
			self.highlights = None
		if not self.highlights:
			wp = self.width * .25
			hp = self.height * .25
			args = (self.x+wp, self.y+hp*1.05, self.width-wp*2, self.height-hp*2, 12, 100)
			with self.canvas:
				Color(*self.alpha.color)
				self.highlights = Line(rounded_rectangle=args, width = 1.2)