from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from errors import BadTickerException
from kivy.graphics import *
import yfinance as yf
import numpy as np
import datetime	


BOT = datetime.datetime(1980, 1, 1)
EOT = datetime.datetime(2036, 1, 1)
class StockGraph(Widget):
	def __init__(self, ticker, alpha, dynamic = True):
		super().__init__()
		self.abbr = ticker
		self.ticker = yf.Ticker(ticker)
		self.dynamic = dynamic
		self.currentPrice = self.ticker.history("1d", "1m")["Low"].values[-1]
		self.currentTime = self.ticker.history("1d", "1m")["Low"].index[-1]
		self.rangeStart = "YTD"
		self.rangeEnd = None
		self.interval = "1h"
		self.alpha = alpha
		self.display = alpha.tickerDisplay
		self.display.text = self.timeParse(self.currentTime) + "${:.2f}".format(self.currentPrice)
		self.touchLine = None
		self.color = (255/255, 255/255, 255/255, 1)
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
			self.currentTime = self.ticker.history("1d", "1m")["Low"].index[-1]
			oneYearDaily = self.ticker.history("1Y", "1d")
			if len(oneYearDaily) < 14:
				raise Exception()
		except:
			self.ticker = catchTicker
			self.abbr = catchAbbr
			e = BadTickerException(ticker)
			raise e
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
		if self.dynamic:
			if avgValues[-1] >= avgValues[0]: self.color = (0/255, 255/255, 0/255, 1)
			else: self.color = (255/255, 0/255, 0/255, 1)
		self.alpha.updateColors()
		#print(dates)
		h = self.height
		w = self.width
		self.originalh = h
		self.originalw = w
		hint = h / len(avgValues)
		wint = w * .85 / (len(dates) - 1)
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
		fs = 10
		with self.canvas:
			Color(*self.color)
			self.glowLine = Line(points = points, width = 1.1, cap = 'round', joint = 'round')
			Color(*self.color)
			self.line = Line(points = points, width = .8, cap = 'round', joint = 'round')
			#minLine
			self.minLabel = Label(text = "${:.2f}".format(min(self.avgValues)), 
				color = self.color,font_size = str(fs)+"sp", size = (xinit, str(fs)+"sp"), 
				pos = (0, ybot-fs/2), font_name = "res/Aldrich", font_hinting = "light", bold = True)
			Color(192/255, 192/255, 192/255)
			self.minLine = Line(points = [xinit, ybot, self.width, ybot])
			#avgLine
			self.avgLabel = Label(text = "${:.2f}".format(sum(self.avgValues)/len(self.avgValues)), 
				color = self.color, font_size = str(fs)+"sp", size = (xinit, str(fs)+"sp"), 
				pos = (0, yavg-fs/2), font_name = "res/Aldrich", font_hinting = "light", bold = True)
			Color(192/255, 192/255, 192/255)
			self.avgLine = Line(points = [xinit, yavg, self.width, yavg])
			#maxLine
			self.maxLabel = Label(text = "${:.2f}".format(max(self.avgValues)), 
				color = self.color, font_size = str(fs)+"sp", size = (xinit, str(fs)+"sp"), 
				pos = (0, ytop-fs/2), font_name = "res/Aldrich", font_hinting = "light", bold = True)
			Color(192/255, 192/255, 192/255)
			self.maxLine = Line(points = [xinit, ytop, self.width, ytop])


	def manageTouchLine(self, touch):
		if self.touchLine: self.canvas.remove(self.touchLine)
		touchLinex = self.x
		touchPrice = self.avgValues[-1]
		touchDate = self.currentTime
		hint = self.points[2] - self.points[0]
		if touch.x >= self.points[-2]: touchLinex = self.points[-2]
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