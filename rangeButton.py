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


class RangeButton(Button):
	def __init__(self, text, alpha, r, interval):
		super().__init__(text = text, font_name = "res/Aldrich", font_size = "14sp",
			font_hinting = "light", bold = True, background_color = (1,1,1,0),
			halign = "center", valign = "center", color = (255/255, 255/255, 255/255, 1))
		self.text = text
		self.alpha = alpha
		self.r = r
		self.interval = interval
		self.highlights = None
		self.active = False
		self.drawUnselected()
		self.bind(on_press = self.updateGraphRanges)
		self.bind(size = self.draw, pos = self.draw)


	def updateGraphRanges(self, itself):
		for button in self.alpha.rangeButtons:
			if button != self:
				button.active = False
				button.draw()
		self.active = True
		self.draw()
		self.alpha.stockGraph.rangeStart = self.r
		self.alpha.stockGraph.interval = self.interval
		self.alpha.stockGraph.graphValores()
		self.alpha.stockGraph.updateLine()

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
			self.drawSelected()
		else:
			self.drawUnselected()

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