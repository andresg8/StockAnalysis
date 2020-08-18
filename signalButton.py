from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import *


class SignalButton(Button):
	def __init__(self, text, alpha, buy, sell):
		super().__init__(text = text, font_name = "res/Aldrich", 
			font_hinting = "light", bold = True, background_color = (1,1,1,0),
			halign = "center", valign = "center", color = (255/255, 255/255, 255/255, 1))
		self.text = text
		self.alpha = alpha
		self.buy = buy
		self.sell = sell
		self.highlights = None
		self.active = False
		self.drawUnselected()
		self.bind(on_press = self.updateSignalLines)
		self.bind(size = self.draw, pos = self.draw)


	def updateSignalLines(self, itself):
		for button in self.alpha.signalButtons:
			if button != self:
				button.active = False
				button.draw()
		self.active = True
		self.draw()
		self.alpha.stockGraph.buyLines = self.buy
		self.alpha.stockGraph.sellLines = self.sell
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
		self.text_size[0] = self.width
		if self.active:
			self.drawSelected()
		else:
			self.drawUnselected()

	def drawUnselected(self):
		self.background_color = (1,1,1,0)
		# if self.highlights:
		# 	self.canvas.remove(self.highlights)
		# 	self.highlights = None
	
	def drawSelected(self):
		self.background_color = (236/255,236/255,255/255, 1)
		# if self.highlights:
		# 	self.canvas.remove(self.highlights)
		# 	self.highlights = None
		# if not self.highlights:
		# 	wp = self.width * .25
		# 	hp = self.height * .25
		# 	args = (self.x+wp, self.y+hp*1.05, self.width-wp*2, self.height-hp*2, 12, 100)
		# 	with self.canvas:
		# 		Color(*self.alpha.color)
		# 		self.highlights = Line(rounded_rectangle=args, width = 1.2)