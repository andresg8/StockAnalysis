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
import yfinance as yf
import numpy as np
import datetime


BOT = datetime.datetime(1980, 1, 1)
EOT = datetime.datetime(2036, 1, 1)
class StockGraph(Widget):
	def __init__(self, ticker, alpha):
		super().__init__()
		self.abbr = ticker
		self.ticker = yf.Ticker(ticker)
		self.currentPrice = self.ticker.history("1d", "1m")["Low"].values[-1]
		self.currentTime = self.ticker.history("1d", "1m")["Low"].index[-1]
		self.rangeStart = "YTD"
		self.rangeEnd = None
		self.interval = "1h"
		self.alpha = alpha
		self.display = alpha.tickerDisplay
		self.display.text = self.timeParse(self.currentTime) + "${:.2f}".format(self.currentPrice)
		self.touchLine = None
		self.color = (0/255, 255/255, 0/255, 1)
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
			result += "{:02d}:{:02d}:{:02d}".format(hour, dt.minute, dt.second) + ampm + " (EST)\n"
		return result


	def updateTicker(self, ticker):
		catchTicker = self.ticker
		self.ticker = yf.Ticker(ticker)
		catchAbbr = self.abbr
		self.abbr = ticker
		try:
			self.currentPrice = self.ticker.history(self.rangeStart, self.interval)["Low"].values[-1]
		except:
			self.ticker = catchTicker
			self.abbr = catchAbbr
			raise LookupError("Invalid Abbreviation")
		self.currentTime = self.ticker.history("1d", "1m")["Low"].index[-1]
		self.display.text = self.timeParse(self.currentTime) + "${:.2f}".format(self.currentPrice)
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
		indices = np.logical_and((history.index.tz_localize(None) > BOT), (history.index.tz_localize(None) < EOT))
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
		if avgValues[-1] >= avgValues[0]: self.color = (0/255, 255/255, 0/255, 1)
		else: self.color = (255/255, 0/255, 0/255, 1)
		self.alpha.updateColors()
		#print(dates)
		h = self.height
		w = self.width
		self.originalh = h
		self.originalw = w
		hint = h / len(avgValues)
		wint = w * .9 / len(dates)
		minh = .05 * h
		maxh = .95 * h
		l = maxh - minh
		L = max(avgValues) - min(avgValues)
		r = l / L
		if l < L: r = l / L
		offset = float(min(avgValues) - minh)
		minv = min(avgValues)
		self.xinit = w * .1
		self.ybot = float((min(avgValues)-minv)*r) + minh
		self.yavg = float(((sum(avgValues)/len(avgValues))-minv)*r) + minh
		self.ytop = float((max(avgValues)-minv)*r) + minh
		print(self.ybot, minh)
		print(self.ytop, maxh)
		points = []
		for y in range(len(avgValues)):
			currentx = self.xinit + (y * wint)
			currenty = (avgValues[y]-minv)*r + minh
			points.append(currentx)
			points.append(currenty)
		self.points = points
		self.canvas.clear()
		self.drawGraph(points, self.xinit, self.ybot, self.yavg, self.ytop)
		self.bind(pos = self.updateLine,
					size = self.updateLine)

	def updateLine(self, *args):
		rath = self.height / self.originalh
		ratw = self.width / self.originalw
		#WINDOW RESIZING
		self.originalh = self.height
		self.originalw = self.width
		for i in range(0, len(self.points), 2):
			self.points[i] *= ratw
		for i in range(1, len(self.points), 2):
			self.points[i] *= rath
		self.canvas.clear()
		self.xinit *= ratw
		self.ybot *= rath
		self.yavg *= rath
		self.ytop *= rath
		#WIDGET RELOCATION
		points = list.copy(self.points)
		for i in range(0, len(self.points), 2):
			points[i] += self.x
		for i in range(1, len(self.points), 2):
			points[i] += self.y
		xinit = self.xinit + self.x
		ybot = self.ybot + self.y
		yavg = self.yavg + self.y
		ytop = self.ytop + self.y
		self.drawGraph(points, xinit, ybot, yavg, ytop)


	def drawGraph(self, points, xinit, ybot, yavg, ytop):
		with self.canvas:
			Color(*self.color)
			self.glowLine = Line(points = points, width = 1.1, cap = 'round', joint = 'round')
			Color(*self.color)
			self.line = Line(points = points, width = .8, cap = 'round', joint = 'round')
			#minLine
			self.minLabel = Label(text = "${:.2f}".format(min(self.avgValues)), 
				color = self.color,font_size = 10, size = (xinit, "10sp"), 
				pos = (0, ybot-5), font_name = "res/Aldrich", font_hinting = "light", bold = True)
			Color(192/255, 192/255, 192/255)
			self.minLine = Line(points = [xinit, ybot, self.width, ybot])
			#avgLine
			self.avgLabel = Label(text = "${:.2f}".format(sum(self.avgValues)/len(self.avgValues)), 
				color = self.color, font_size = 10, size = (xinit, "10sp"), 
				pos = (0, yavg-5), font_name = "res/Aldrich", font_hinting = "light", bold = True)
			Color(192/255, 192/255, 192/255)
			self.avgLine = Line(points = [xinit, yavg, self.width, yavg])
			#maxLine
			self.maxLabel = Label(text = "${:.2f}".format(max(self.avgValues)), 
				color = self.color, font_size = 10, size = (xinit, "10sp"), 
				pos = (0, ytop-5), font_name = "res/Aldrich", font_hinting = "light", bold = True)
			Color(192/255, 192/255, 192/255)
			self.maxLine = Line(points = [xinit, ytop, self.width, ytop])


	def manageTouchLine(self, touch):
		if self.touchLine: self.canvas.remove(self.touchLine)
		touchLinex = self.x
		touchPrice = self.avgValues[-1]
		touchDate = self.currentTime
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
			Color(*self.color)
			self.touchLine = Line(points = [touchLinex, self.y, touchLinex, self.y+self.height], 
									width = .8, cap = 'round', joint = 'round', close = False)

	def on_touch_down(self, touch):
		if not self.inWidget(touch):
			if self.touchLine:
				self.display.text = self.timeParse(self.currentTime.to_pydatetime()) + "${:.2f}".format(self.currentPrice)
				self.canvas.remove(self.touchLine)
				self.touchLine = None
			return
		self.manageTouchLine(touch)		
		return super().on_touch_down(touch)


	def on_touch_move(self, touch):
		if not self.inWidget(touch):
			return
		self.manageTouchLine(touch)
		return super().on_touch_move(touch)

	def on_touch_up(self, touch):
		if not self.inWidget(touch):
			if self.touchLine:
				self.display.text = self.timeParse(self.currentTime.to_pydatetime()) + "${:.2f}".format(self.currentPrice)
				self.canvas.remove(self.touchLine)
				self.touchLine = None
			return
		elif self.touchLine:
			self.display.text = self.timeParse(self.currentTime.to_pydatetime()) + "${:.2f}".format(self.currentPrice)
			self.canvas.remove(self.touchLine)
			self.touchLine = None
		return super().on_touch_up(touch)

	def inWidget(self, touch):
		within = False
		if touch.x > self.x and touch.x < self.x + self.width:
			if touch.y > self.y and touch.y < self.y + self.height:
				within = True
		return within
	


class StockAnalysis(App):
	def build(self):
		self.abbr = "GE"
		self.root = GridLayout(cols = 1)
		self.stockGraph = None
		self.coloredWidgets = []
		#Master Layout
		self.color = (0/255, 255/255, 0/255, 1)
		self.graphDataLayout = GridLayout(cols = 1, size_hint_y = None)
		self.graphDataLayout.bind(minimum_height=self.graphDataLayout.setter('height'))
		#Title
		self.titleLabel = Label(text = " StockAnalysis", color = (180/255, 180/255, 180/255, 1),#(75/255,225/255,0/255,1),
			font_name = "res/Aldrich", font_hinting = "light", bold = True, halign = "left",
			font_size = 36)
		#self.coloredWidgets.append(self.titleLabel)
		def titleScale(*args):
			self.titleLabel.text_size = self.titleLabel.size
		self.titleLabel.bind(size = titleScale)
		self.graphDataLayout.add_widget(self.titleLabel)
		#Ticker Layout
		self.tickerLayout = BoxLayout(orientation='horizontal')
		self.tickerTitle = Label(text = defaultTicker, color = self.color,
			font_name = "res/Aldrich", font_hinting = "light", bold = True)
		self.coloredWidgets.append(self.tickerTitle)
		self.tickerLayout.add_widget(self.tickerTitle)
		self.tickerDisplay = Label(text = "", halign = "center", color = self.color,
			font_name = "res/Aldrich", font_hinting = "light", bold = True)
		self.coloredWidgets.append(self.tickerDisplay)
		self.tickerLayout.add_widget(self.tickerDisplay)
		self.graphDataLayout.add_widget(self.tickerLayout)
		#Stock Graph
		self.stockGraph = StockGraph(defaultTicker, self)
		self.graphDataLayout.add_widget(self.stockGraph)
		#Range Options
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
		#Search Layout
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
	# def searchFunc(self):
	# 	def updateGraphRanges(itself):
	# 		for button in self.rangeButtons:
	# 			if button != itself:
	# 				#button.
	# 				pass
	# 		self.stockGraph.rangeStart = r
	# 		self.stockGraph.interval = interval
	# 		self.stockGraph.graphValores()
	# 		self.stockGraph.updateLine()
	# 	return updateGraphRanges



				

			



# rangeButton = Button(text = r[0],
# 				font_name = "res/Aldrich", font_hinting = "light", bold = True)
# 			func = self.makeRangeFunc(r[1], r[2])
# 			rangeButton.bind(on_press = func)
# 			self.rangeLayout.add_widget(rangeButton)
# 			self.rangeButtons.append(rangeButton)


if __name__ == "__main__":
	StockAnalysis().run()