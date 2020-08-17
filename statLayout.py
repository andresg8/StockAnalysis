from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import *
from popups import ErrorPopup

class StatLayout(GridLayout):
	def __init__(self, text, color, activity, func, rng = False, default = 0):
		super().__init__(rows = 1, size_hint_y = None, height = Window.height * .1)
		self.bind(minimum_height=self.setter('height'))
		self.statButton = StatButton(text, color, activity, self, func, rng)
		self.add_widget(self.statButton)
		self.rng = rng
		if rng:
			self.rngEntry = TextInput(text = str(default), background_color = (0, 0, 0, 0),
			foreground_color = (1, 1, 1, 1), cursor_color = (0, 1, 0, 1),
			multiline = False, padding = [6, (Window.height * .05) - 10], hint_text = "10")
			self.rngEntry.width = Window.width * .1
			self.rngEntry.height = Window.height * .1
			self.add_widget(self.rngEntry)
		# self.bind(pos = self.draw, size = self.draw)

	def draw(self, *args):
		#self.height = Window.height * .1
		self.statButton.width = Window.width * .4
		self.statButton.height = Window.height * .1
		self.statButton.draw()
		if self.rng:
			self.rngEntry.width = Window.width * .1
			self.rngEntry.height = Window.height * .1
			self.rngEntry.padding = [6, (Window.height * .05) - 10]


class StatButton(Button):
	def __init__(self, text, color, activity, master, func, rng = False):
		super().__init__(text = text, font_name = "res/Aldrich", 
			font_hinting = "light", bold = True, background_color = (1,1,1,0),
			halign = "center", valign = "center", size_hint_y = None, size_hint_x = None,
			height = Window.height * .1, width = Window.width * .4)
		self.text_size[0] = self.width
		self.text = text
		self.highlighter = color
		self.activity = activity
		self.master = master
		self.func = func
		self.rng = rng
		self.highlights = None
		self.outlines = []
		self.active = False
		#self.drawUnselected()
		with self.canvas:
			# Color(236/255,236/255,255/255, 1)
			# self.outlines.append(Line(points = [self.x + .1 * self.width, self.y, self.x + self.width, self.y], 
			# 						width = .5, cap = 'round', joint = 'round', close = False))
			Color(*self.highlighter)
			self.outlines.append(Line(points = [self.x, self.y + self.height * .1, self.x, self.y + self.height * .9], 
									width = .5, cap = 'round', joint = 'round', close = False))
			Color(*self.highlighter)
			self.outlines.append(Line(points = [self.x + self.width, self.y + self.height * .1, self.x + self.width, self.y + self.height * .9], 
									width = .5, cap = 'round', joint = 'round', close = False))
		self.bind(on_press = self.updateActiveStats)
		self.bind(size = self.draw, pos = self.draw)


	def updateActiveStats(self, itself):
		if not self.active:
			try:
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
			except Exception as e:
				# print(e)
				errorPopup = ErrorPopup("There aren't enough data points to materialize this statistic!")
				errorPopup.open()
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
		for line in self.outlines:
			if line in self.canvas.children: self.canvas.remove(line)
		
		if self.active:
			# self.drawSelected()
			delta = (1, 1, 1, 1)
			x = tuple(delta[i] * self.highlighter[i] for i in range(len(delta)))
			self.background_color = x
		else:
			# self.drawUnselected()
			self.background_color = (1,1,1,0)
			with self.canvas:
				# Color(236/255,236/255,255/255, 1)
				# self.outlines.append(Line(points = [self.x + .1 * self.width, self.y, self.x + self.width*.9, self.y], 
				# 						width = .5, cap = 'round', joint = 'round', close = False))
				Color(*self.highlighter)
				self.outlines.append(Line(points = [self.x, self.y + self.height * .1, self.x, self.y + self.height * .9], 
										width = .5, cap = 'round', joint = 'round', close = False))
				Color(*self.highlighter)
				self.outlines.append(Line(points = [self.x + self.width, self.y + self.height * .1, self.x + self.width, self.y + self.height * .9], 
										width = .5, cap = 'round', joint = 'round', close = False))

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