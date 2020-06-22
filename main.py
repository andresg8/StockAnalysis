from kivy.app import App 
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
import datetime
BOT = datetime.datetime(1980, 1, 1)
EOT = datetime.datetime(2036, 1, 1)
class StockGraph(Widget):
	def __init__(self, ticker, display):
		super().__init__()
		self.abbr = ticker
		self.ticker = yf.Ticker(ticker)
		self.currentPrice = self.ticker.history("1d", "1m")["Low"].values[-1]
		self.rangeStart = "YTD"
		self.rangeEnd = None
		self.interval = "1d"
		self.display = display
		self.display.text = self.timeParse(datetime.datetime.now()) + "${:.2f}".format(self.currentPrice)
		self.touchLine = None
		self.graphValores()

	def timeParse(self, dt):
		result = ""
		months = ["E","Jan", "Feb", "Mar", "Apr", 
					"May", "Jun", "Jul", "Aug", 
					"Sep", "Oct", "Nov", "Dec"]
		result += months[dt.month] + " " + str(dt.day) + ", " + str(dt.year) + "\n"
		ampm = "am"
		hour = dt.hour
		if not hour: hour = 12
		if dt.hour > 12:
			ampm = "pm"
			hour = (hour % 12)
		if dt.hour or dt.minute or dt.second:
			result += "{:02d}:{:02d}:{:02d}".format(hour, dt.minute, dt.second) + ampm + "\n"
		return result


	def updateTicker(self, ticker):
		self.abbr = ticker
		self.ticker = yf.Ticker(ticker)
		self.currentPrice = self.ticker.history("1d", "1m")["Low"].values[-1]
		self.display.text = self.timeParse(datetime.datetime.now()) + "${:.2f}".format(self.currentPrice)
		self.graphValores()
		self.updateLine()

	def getAvgs(self, history):
		lows = history["Low"].values
		highs = history["High"].values
		return (lows + highs) / 2 

	def getRangeIntData(self, start, end, interval):
		if end:
			raise Exception("Not yet Implemented!")
		history = self.ticker.history(start, interval)
		indices = np.logical_and((history.index > BOT), (history.index < EOT))
		dates = history.index[indices]
		values = history[indices]
		avgValues = self.getAvgs(values)
		clean = np.logical_not(np.isnan(avgValues))
		avgValues = avgValues[clean]
		dates = dates[clean]
		return dates, avgValues

	def graphValores(self):
		dates, avgValues = self.getRangeIntData(self.rangeStart, self.rangeEnd, self.interval)
		self.dates = dates
		self.avgValues = avgValues
		#print(dates)
		h = self.height
		w = self.width
		self.originalh = h
		self.originalw = w
		hint = h / len(avgValues)
		wint = w * .9 / len(dates)
		ymin = min(avgValues) - max(avgValues) * .05
		ymax = max(avgValues) * 1.05
		self.xinit = w * .1 
		self.yinit = float((min(avgValues)-ymin)*(h/(ymax-ymin)))
		self.yavg = float(((sum(avgValues)/len(avgValues))-ymin)*(h/(ymax-ymin)))
		self.ytop = float((max(avgValues)-ymin)*(h/(ymax-ymin)))
		points = []
		for y in range(len(avgValues)):
			currentx = self.xinit + (y * wint)
			currenty = ((avgValues[y]-ymin)*(h/(ymax-ymin)))
			points.append(currentx)
			points.append(currenty)
		self.points = points
		self.canvas.clear()
		self.drawGraph(points, self.xinit, self.yinit, self.yavg, self.ytop)
		# with self.canvas:
		# 	#stockLine
		# 	Color(0/255, 255/255, 0/255, 1)
		# 	self.glowLine = Line(points = points, width = 1.1, cap = 'round', joint = 'round')
		# 	Color(0/255, 255/255, 0/255, 1)
		# 	self.line = Line(points = points, width = .8, cap = 'round', joint = 'round')
		# 	#minLine
		# 	self.minLabel = Label(text = "${:.2f}".format(min(avgValues)), color = (43/255, 255/255, 36/255, 1),
		# 		font_size = 10, size = (self.xinit, "10sp"), pos = (0, self.yinit-5))
		# 	self.minLine = Line(points = [self.xinit, self.yinit, w, self.yinit])
		# 	#avgLine
		# 	self.avgLabel = Label(text = "${:.2f}".format(sum(avgValues)/len(avgValues)), color = (43/255, 255/255, 36/255, 1),
		# 		font_size = 10, size = (self.xinit, "10sp"), pos = (0, self.yavg-5))
		# 	self.avgLine = Line(points = [self.xinit, self.yavg, w, self.yavg])
		# 	#maxLine
		# 	self.maxLabel = Label(text = "${:.2f}".format(max(avgValues)), color = (43/255, 255/255, 36/255, 1),
		# 		font_size = 10, size = (self.xinit, "10sp"), pos = (0, self.ytop-5))
		# 	self.maxLine = Line(points = [self.xinit, self.ytop, w, self.ytop])
		self.bind(pos = self.updateLine,
					size = self.updateLine)

	def updateLine(self, *args):
		rath = self.height / self.originalh
		ratw = self.width / self.originalw
		print(rath, ratw)
		#WINDOW RESIZING
		self.originalh = self.height
		self.originalw = self.width
		for i in range(0, len(self.points), 2):
			self.points[i] *= ratw
		for i in range(1, len(self.points), 2):
			self.points[i] *= rath
		self.canvas.clear()
		self.xinit *= ratw
		self.yinit *= rath
		self.yavg *= rath
		self.ytop *= rath
		#WIDGET RELOCATION
		points = list.copy(self.points)
		for i in range(0, len(self.points), 2):
			points[i] += self.x
		for i in range(1, len(self.points), 2):
			points[i] += self.y
		xinit = self.xinit + self.x
		yinit = self.yinit + self.y
		yavg = self.yavg + self.y
		ytop = self.ytop + self.y
		self.drawGraph(points, xinit, yinit, yavg, ytop)


	def drawGraph(self, points, xinit, yinit, yavg, ytop):
		with self.canvas:
			Color(0/255, 255/255, 0/255, 1)
			self.glowLine = Line(points = points, width = 1.1, cap = 'round', joint = 'round')
			Color(0/255, 255/255, 0/255, 1)
			self.line = Line(points = points, width = .8, cap = 'round', joint = 'round')
			#minLine
			self.minLabel = Label(text = "${:.2f}".format(min(self.avgValues)), color = (43/255, 255/255, 36/255, 1),
				font_size = 10, size = (xinit, "10sp"), pos = (0, yinit-5),
				font_name = "res/Aldrich", font_hinting = "light", bold = True)
			Color(192/255, 192/255, 192/255)
			self.minLine = Line(points = [xinit, yinit, self.width, yinit])
			#avgLine
			self.avgLabel = Label(text = "${:.2f}".format(sum(self.avgValues)/len(self.avgValues)), color = (43/255, 255/255, 36/255, 1),
				font_size = 10, size = (xinit, "10sp"), pos = (0, yavg-5),
				font_name = "res/Aldrich", font_hinting = "light", bold = True)
			Color(192/255, 192/255, 192/255)
			self.avgLine = Line(points = [xinit, yavg, self.width, yavg])
			#maxLine
			self.maxLabel = Label(text = "${:.2f}".format(max(self.avgValues)), color = (43/255, 255/255, 36/255, 1),
				font_size = 10, size = (xinit, "10sp"), pos = (0, ytop-5),
				font_name = "res/Aldrich", font_hinting = "light", bold = True)
			Color(192/255, 192/255, 192/255)
			self.maxLine = Line(points = [xinit, ytop, self.width, ytop])


	def on_touch_down(self, touch):
		if not self.inWidget(touch):
			return
		if self.touchLine: self.canvas.remove(self.touchLine)
		touchLinex = self.x
		touchPrice = self.avgValues[-1]
		touchDate = type(self.dates[0])(datetime.datetime.now())
		hint = self.points[2] - self.points[0]
		if touch.x > self.points[-2]: touchLinex = self.points[-2]
		else:
			for i in range(2, len(self.points), 2):
				if touch.x < self.points[i]:
					if touch.x + hint/2 > self.points[i]:
						touchLinex = self.points[i]
						touchPrice = self.avgValues[i//2]
						touchDate = self.dates[i//2]
					else:
						touchLinex = self.points[i-2]
						touchPrice = self.avgValues[(i-2)//2]
						touchDate = self.dates[(i-2)//2]
					break
		self.display.text = self.timeParse(touchDate.to_pydatetime()) + "${:.2f}".format(touchPrice)
		with self.canvas:
			Color(0/255, 255/255, 0/255, 1)
			self.touchLine = Line(points = [touchLinex, self.y, touchLinex, self.y+self.height], width = .8, cap = 'round', joint = 'round', close = False)
		#return super().on_touch_down(touch)

	def on_touch_move(self, touch):
		if not self.inWidget(touch):
			return
		self.on_touch_down(touch)

	def on_touch_up(self, touch):
		if not self.inWidget(touch):
			return
		elif self.touchLine:
			self.display.text = self.timeParse(datetime.datetime.now()) + "${:.2f}".format(self.currentPrice)
			self.canvas.remove(self.touchLine)
			self.touchLine = None

	def inWidget(self, touch):
		within = False
		if touch.x > self.x and touch.x < self.x + self.width:
			if touch.y > self.y and touch.y < self.y + self.height:
				within = True
		return within

class StockAnalysis(App):
	def build(self):
		defaultTicker = "GE"
		self.rootLayout = GridLayout(cols = 1)
		
		self.tickerLayout = BoxLayout(orientation='horizontal')
		self.tickerTitle = Label(text = defaultTicker,
			font_name = "res/Aldrich", font_hinting = "light", bold = True)
		self.tickerLayout.add_widget(self.tickerTitle)

		self.tickerDisplay = Label(text = "", halign = "center",
			font_name = "res/Aldrich", font_hinting = "light", bold = True)
		self.tickerLayout.add_widget(self.tickerDisplay)

		self.rootLayout.add_widget(self.tickerLayout)
		
		self.stockGraph = StockGraph(defaultTicker, self.tickerDisplay)
		self.rootLayout.add_widget(self.stockGraph)
		
		self.searchLayout = BoxLayout(orientation='horizontal')
		self.searchText = TextInput(hint_text = "Company...", background_color = (0, 0, 0, 0),
			foreground_color = (1, 1, 1, 1), cursor_color = (0, 1, 0, 1),
			multiline = False)
		self.searchLayout.add_widget(self.searchText)

		self.searchButton = Button(text = "Search")
		self.searchButton.bind(on_press = self.updateGraph)
		self.searchLayout.add_widget(self.searchButton)

		self.rootLayout.add_widget(self.searchLayout)
		return self.rootLayout

	def updateGraph(self, *args):
		newTicker = self.searchText.text
		self.searchText.text = ""
		try:
			self.stockGraph.updateTicker(newTicker)
			self.tickerTitle.text = newTicker
		except:
			print("Unga Bunga, error occured")

if __name__ == "__main__":
	StockAnalysis().run()