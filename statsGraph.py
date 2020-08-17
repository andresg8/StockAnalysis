from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import *
from collections import defaultdict
from errors import BadTickerException
import yfinance as yf
import numpy as np
import datetime	
import math

BOT = datetime.datetime(1980, 1, 1)
EOT = datetime.datetime(2036, 1, 1)
class StatsGraph(Widget):
	def __init__(self, ticker, alpha, dynamic = True):
		super().__init__()
		self.abbr = ticker
		self.ticker = yf.Ticker(ticker)
		self.sixYearDaily = self.ticker.history("4Y", "1d")
		self.dynamic = dynamic
		self.colorPallete = defaultdict(list)
		self.stats = {"Bollinger Bands": (self.bollingerBands, (52/255, 204/255, 255/255, 1)),
		"Exponential Moving Average": (self.exponentialMovingAverage, (0/255, 255/255, 255/255, 1)),
		"Simple Moving Average": (self.simpleMovingAverage,  (0/255, 112/255, 255/255, 1)),
		"Relative Strength Index": (self.getRSI, (227/255, 0/255, 34/255, 1)),
		"Average True Range": (self.getATR,  (204/255, 85/255, 0/255, 1)),
		"Triple EMA": (self.tripleEMA,  (255/255, 0/255, 255/255, 1)),
		"On Balance Volume": (self.getOnBalanceVolume,  (0/255, 128/255, 0/255, 1)),
		"Chaikin Oscillator": (self.getChaikinOscillator, (0/255, 168/255, 107/255, 1)),
		"Klinger Oscillator": (self.getKlingerOscillator,  (141/255, 182/255, 0/255, 1))
		}
		self.signalLines = dict()
		self.buyLines = False
		self.sellLines = False
		self.currentPrice = self.ticker.history("1d", "1m")["Low"].values[-1]
		self.currentTime = self.ticker.history("1d", "1m")["Low"].index[-1]
		self.activeStats = defaultdict(list)
		self.rangeStart = "YTD"
		self.rangeEnd = None
		self.interval = "1d"
		self.alpha = alpha
		self.display = alpha.tickerDisplay
		self.display.text = self.timeParse(self.currentTime) + "${:.2f}".format(self.currentPrice)
		self.touchLine = None
		self.color = (1, 1, 1, 1)
		self.graphValores()
		self.bind(pos = self.updateLine,
					size = self.updateLine)

	def addActiveStats(self, statLabel, stats):
		if type(stats[0]) != list:
			stats = [stats]
		lastOne = stats[-1]
		for stat in stats:
			if stat == lastOne and min(stat) in [0, -1] and max(stat) in [0, 1]:
				self.signalLines[statLabel] = stat
				continue
			self.activeStats[statLabel].append(stat)
			self.colorPallete[statLabel].append(self.stats[statLabel][1])
		self.graphValores()
		self.updateLine()

	def removeActiveStats(self, statLabel):
		self.activeStats.pop(statLabel)
		self.colorPallete.pop(statLabel)
		if statLabel in self.signalLines: self.signalLines.pop(statLabel)
		self.graphValores()
		self.updateLine()

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
			self.sixYearDaily = self.ticker.history("4Y", "1d")
			if len(self.sixYearDaily) < 14:
				raise Exception()
		except:
			self.ticker = catchTicker
			self.abbr = catchAbbr
			e = BadTickerException(ticker)
			raise e
		self.display.text = self.timeParse(self.currentTime) + "${:.2f}".format(self.currentPrice)
		self.activeStats = defaultdict(list)
		self.colorPallete = defaultdict(list)
		self.signalLines = dict()
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

	def classifyIntersections(self, minor, major, sensitivity = 0):
		'''
		minor: dataset describing the moving average with less lag (less days)
		major: dataset describing the moving average with more lag (more days)
		-
		intersectMagnitudes: all intersections rated (-)1||(-)2||(-)3 describing strong||weak||epsilon
		'''
		assert(len(major) == len(minor))
		intersects = []
		for v in range(1, len(minor)):
			intersectFlag = False
			yesterday = minor[v-1] - major[v-1]
			today = minor[v] - major[v]
			if yesterday < 0:
				# means the stock is below its laggier average
				if today >= 0:
					# means this is an intersection day, the stock has risen above its laggier average
					if today > major[v] * sensitivity:
						intersects.append(1)
						intersectFlag = True
			elif yesterday > 0:
				# means the stock is above its laggier average
				if today <= 0:
					# means this is an intersection day, the stock has fallen below its laggier average
					if today < major[v] * -sensitivity:
						intersects.append(-1)
						intersectFlag = True
			if not intersectFlag:
				intersects.append(0)
		return intersects

	def graphValores(self):
		dates, avgValues = self.getRangeIntData(self.rangeStart, self.rangeEnd, self.interval)
		self.dates = dates
		self.avgValues = avgValues
		#self.activeStats = [bollingerData, COData...]
		self.statLines = []
		self.spanConsiderable = [list(self.avgValues)]
		match = len(avgValues)
		for k, v in self.activeStats.items():
			for stat in v:
				self.statLines.append(stat[-match:])
			if k in ["Bollinger Bands", "Exponential Moving Average", "Simple Moving Average", "Triple EMA"]:
				for stat in v:
					self.spanConsiderable.append(list(stat[-match:]))
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
		maxValue = max(avgValues)
		minValue = min(avgValues)
		for line in self.spanConsiderable:
			tmax = max(line)
			tmin = min(line)
			if tmax > maxValue: maxValue = tmax
			if tmin < minValue: minValue = tmin
		self.maxValue = maxValue
		self.minValue = minValue
		l = maxh - minh
		L = maxValue - minValue
		r = l / L
		if l < L: r = l / L
		offset = float(minValue - minh)
		minv = minValue
		self.xinit = w * .1
		self.ybot = float((minValue-minv)*r) + minh
		# self.yavg = float(((sum(avgValues)/len(avgValues))-minv)*r) + minh
		self.ytop = float((maxValue-minv)*r) + minh
		allPoints = []
		trueRange = maxValue - minValue
		translate = 0
		proportion = 0
		for line in [self.avgValues] + self.statLines:
			points = []
			xinit = w * .1
			diff = len(self.avgValues) - len(line)
			if diff > 0:
				xinit += (diff * wint)
			if list(line) in self.spanConsiderable:
				for y in range(len(line)):
					currentx = xinit + (y * wint)
					currenty = (line[y]-minv)*r + minh
					points.append(currentx)
					points.append(currenty)
			else:
				dataRange = max(line) - min(line)
				if not dataRange:
					y = line[0] * proportion
					y = y - translate
					y = (y-minv)*r + minh
					points = [xinit, y, xinit + (w * .9), y]
				else:
					RSIFlag = False
					if "Relative Strength Index" in self.activeStats:
						for l in self.activeStats["Relative Strength Index"]:
							if line == l[-match:]: 
								RSIFlag = True
								dataRange = max(line + [70]) - min(line + [30])
					proportion = trueRange / dataRange
					for y in range(len(line)):
						line[y] *= proportion
					translate = min(line) - minValue
					if RSIFlag:
						translate = min(line + [30 * proportion]) - minValue
					for y in range(len(line)):
						line[y] -= translate
					for y in range(len(line)):
						currentx = xinit + (y * wint)
						currenty = (line[y]-minv)*r + minh
						points.append(currentx)
						points.append(currenty)
			# self.points = points
			self.canvas.clear()
			allPoints.append(points)
		self.signalPoints = []
		self.signalColors = []
		for line in self.signalLines.values():
			xinit = w * .1
			diff = len(self.avgValues) - len(line)
			if diff > 0:
				xinit += (diff * wint)
			current = line[-match:]
			current = np.asarray(current)
			buyLines = np.where(current > 0)
			sellLines = np.where(current < 0)
			if self.buyLines:
				for x in buyLines[0]:
					points = [xinit + (x * wint), maxh, xinit + (x * wint), minh]
					allPoints.append(points)
					self.signalColors.append((0, 1, 0, 1))
			if self.sellLines:
				for x in sellLines[0]:
					points = [xinit + (x * wint), maxh, xinit + (x * wint), minh]
					allPoints.append(points)
					self.signalColors.append((1, 0, 0, 1))
		self.drawGraph(allPoints, self.xinit, self.ybot, self.ytop)
		self.allPoints = allPoints

	def updateLine(self, *args):
		rath = self.height / self.originalh
		ratw = self.width / self.originalw
		#WINDOW RESIZING
		self.originalh = self.height
		self.originalw = self.width
		for points in self.allPoints:
			for i in range(0, len(points), 2):
				points[i] *= ratw
			for i in range(1, len(points), 2):
				points[i] *= rath
		self.canvas.clear()
		self.xinit *= ratw
		self.ybot *= rath
		# self.yavg *= rath
		self.ytop *= rath
		#WIDGET RELOCATION
		scaledPoints = []
		for points in self.allPoints:
			p = list.copy(points)
			for i in range(0, len(points), 2):
				p[i] += self.x
			for i in range(1, len(points), 2):
				p[i] += self.y
			xinit = self.xinit + self.x
			ybot = self.ybot + self.y
			# yavg = self.yavg + self.y
			ytop = self.ytop + self.y
			scaledPoints.append(p)
		self.drawGraph(scaledPoints, xinit, ybot, ytop)


	def drawGraph(self, allPoints, xinit, ybot, ytop):
		fs = 14
		i = 0
		colorPallete = [self.color]
		for pallete in self.colorPallete.values():
			for color in pallete:
				colorPallete.append(color)
		colorPallete += self.signalColors
		with self.canvas:
			for points in allPoints:
				# print(points[:20])
				color = colorPallete[i]
				i += 1
				Color(*color)
				Line(points = points, width = 1.1, cap = 'round', joint = 'round')
				Color(*color)
				Line(points = points, width = .8, cap = 'round', joint = 'round')
				#minLine
			self.minLabel = Label(text = "${:.2f}".format(self.minValue), 
				color = self.color,font_size = fs, size = (xinit, str(fs)+"sp"), 
				pos = (0, ybot-fs/2), font_name = "res/Aldrich", font_hinting = "light", bold = True)
			Color(192/255, 192/255, 192/255)
			self.minLine = Line(points = [xinit, ybot, self.width, ybot])
			#avgLine
			# self.avgLabel = Label(text = "${:.2f}".format(sum(self.avgValues)/len(self.avgValues)), 
			# 	color = self.color, font_size = fs, size = (xinit, str(fs)+"sp"), 
			# 	pos = (0, yavg-fs/2), font_name = "res/Aldrich", font_hinting = "light", bold = True)
			# Color(192/255, 192/255, 192/255)
			# self.avgLine = Line(points = [xinit, yavg, self.width, yavg])
			#maxLine
			self.maxLabel = Label(text = "${:.2f}".format(self.maxValue), 
				color = self.color, font_size = fs, size = (xinit, str(fs)+"sp"), 
				pos = (0, ytop-fs/2), font_name = "res/Aldrich", font_hinting = "light", bold = True)
			Color(192/255, 192/255, 192/255)
			self.maxLine = Line(points = [xinit, ytop, self.width, ytop])


	def manageTouchLine(self, touch):
		if self.touchLine: self.canvas.remove(self.touchLine)
		touchLinex = self.x
		touchPrice = self.avgValues[-1]
		touchDate = self.currentTime
		self.points = self.allPoints[0]
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




	def getAvgs(self, history):
		lows = history["Low"].values
		highs = history["High"].values
		return (lows + highs) / 2

	def getRangeData(self, data, start, end):
		indices = np.logical_and((data.index.tz_localize(None) >= start), (data.index.tz_localize(None) <= end))
		dates = data.index[indices]
		values = data[indices]
		#Stock values have a daily low and daily high, getAvgs gets the avgs...
		avgValues = self.getAvgs(values)
		clean = np.logical_not(np.isnan(avgValues))
		avgValues = avgValues[clean]
		dates = dates[clean]
		return dates, avgValues

	def simpleMovingAverage(self, rng):
		# rngPlusMonth = rng + 261
		dates, avgValues = self.getRangeData(self.sixYearDaily, BOT, EOT)
		# avgValues = avgValues[-rngPlusMonth:]
		# dates = dates[-rngPlusMonth:]
		# span = len(avgValues) - 261
		span = rng
		moving = []
		movingAverage = []
		movingDates = []
		for v in range(len(avgValues)):
			moving.append(avgValues[v])
			if len(moving) >= span:
				moving = moving[1:]
				movingAverage.append(sum(moving)/len(moving))
				movingDates.append(dates[v])
		avgValues = avgValues[-len(movingAverage):]
		signals = self.classifyIntersections(avgValues, movingAverage)
		return movingAverage, signals

	def getOnBalanceVolume(self):
		dates, lows, highs, opens, closes = self.getCandles(self.sixYearDaily)
		volumes = self.sixYearDaily["Volume"].values
		clean = np.logical_not(np.isnan(volumes))
		volumes = volumes[clean]
		assert(len(dates) == len(volumes))
		OBV = [0]
		OBVSlopes = [0]
		for d in range(1, len(dates)):
			delta = closes[d]-closes[d-1]
			if delta > 0:
				OBV.append(OBV[-1] + volumes[d])
				OBVSlopes.append(volumes[d])
			elif delta < 0:
				OBV.append(OBV[-1] - volumes[d])
				OBVSlopes.append(-1*volumes[d])
			else:
				OBV.append(OBV[-1])
				OBVSlopes.append(0)
		assert(len(dates) == len(OBV))
		assert(len(dates) == len(OBVSlopes))
		return OBV

	def getChaikinOscillator(self):
		dates, lows, highs, opens, closes = self.getCandles(self.sixYearDaily)
		volumes = self.sixYearDaily["Volume"].values
		clean = np.logical_not(np.isnan(volumes))
		volumes = volumes[clean]
		assert(len(dates) == len(volumes))
		N = ((closes - lows) - (highs - closes)) / (highs - lows)
		N = np.asarray([x if np.isfinite(x) else 0 for x in N])
		M = N * volumes
		ADL = [0]
		for d in range(1, len(M)):
			ADL.append(M[d-1] + M[d])
		EMA3 = self.calcEMA(ADL, 6)
		EMA10 = self.calcEMA(ADL, 20)
		dates = dates[19:]
		match = len(EMA3) - len(EMA10)
		EMA3 = EMA3[match:]
		chaikinOscillator = []
		for i in range(len(EMA3)):
			chaikinOscillator.append(EMA3[i] - EMA10[i])
		assert(len(dates) == len(chaikinOscillator))
		signalLine = [0 for x in range(len(chaikinOscillator))]
		signals = self.classifyIntersections(chaikinOscillator, signalLine)
		return chaikinOscillator, signalLine, signals

	def getKlingerOscillator(self):
		dates, lows, highs, opens, closes = self.getCandles(self.sixYearDaily)
		volumes = self.sixYearDaily["Volume"].values
		clean = np.logical_not(np.isnan(volumes))
		volumes = volumes[clean]
		assert(len(dates) == len(volumes))
		trend = [0] 
		# HAD TO REVERSE TREND POLARITY TO MATCH REALITY? 
		# NOT SURE WHY IT WORKS BUT IT DOES SEEM TO
		for d in range(1, len(dates)):
			yesterday = highs[d-1] + lows[d-1] + closes[d-1]
			today = highs[d] + lows[d] + closes[d]
			if today > yesterday:
				trend.append(-1)
			else:
				trend.append(1)
		dm = highs - lows
		cm = [0]
		for d in range(1, len(dm)):
			if trend[d] == trend[d-1]:
				cm.append(cm[-1] + dm[d])
			else:
				cm.append(dm[d-1] + dm[d])
		volumeForce = [0]
		for d in range(1, len(volumes)):
			volumeForce.append(volumes[d] * 2 * ((dm[d]/cm[d])-1) * trend[d] * 100)
		volumeForce = np.asarray([x if np.isfinite(x) else 0 for x in volumeForce])
		EMA34 = self.calcEMA(volumeForce, 34)
		EMA55 = self.calcEMA(volumeForce, 55)
		match = len(EMA34) - len(EMA55)
		EMA34 = EMA34[match:]
		dates = dates[54:]
		trend = trend[54:]
		klingerOscillator = []
		for d in range(len(EMA34)):
			klingerOscillator.append(EMA34[d] - EMA55[d])
		signalLine = self.calcEMA(klingerOscillator, 13)
		klingerOscillator = klingerOscillator[-len(signalLine):]
		dates = dates[-len(signalLine):]
		assert(len(dates) == len(klingerOscillator))
		assert(len(klingerOscillator) == len(signalLine))
		signals = self.classifyIntersections(klingerOscillator, signalLine)
		return klingerOscillator, signalLine, signals

	def getATR(self, rng = 14):
		dates, lows, highs, opens, closes = self.getCandles(self.sixYearDaily)
		TR = [0]
		for d in range(1, len(dates)):
			c1 = highs[d] - lows[d]
			c2 = abs(highs[d] - closes[d-1])
			c3 = abs(lows[d] - closes[d-1])
			TR.append(max(c1, c2, c3))
		ATR = []
		moving = []
		for d in range(len(TR)):
			moving.append(TR[d])
			if len(moving) >= rng:
				ATR.append(sum(moving)/rng)
				moving = moving[1:]
		dates = dates[rng-1:]
		assert(len(dates) == len(ATR))
		return ATR

	def bollingerBands(self, rng, m=2):
		#MA+/-m∗σ
		#MA = SMA
		#m = 2 (num of std dev away)
		#σ = std dev
		# rngPlusMonth = rng + 261
		dates, avgValues = self.getRangeData(self.sixYearDaily, BOT, EOT)
		# avgValues = avgValues[-rngPlusMonth:]
		# dates = dates[-rngPlusMonth:]
		# span = len(avgValues) - 261
		span = rng
		moving = []
		movingAverage = []
		bbTop = []
		bbBot = []
		movingDates = []
		volatility = []
		smoothing = 2
		first = True
		days = rng
		for v in range(len(avgValues)):
			moving.append(avgValues[v])
			if len(moving) >= span:
				if first:
					moving = moving[1:]
					movingAverage.append(sum(moving)/len(moving))
					first = False
				else:
					moving = moving[1:]
					movingAverage.append((avgValues[v]*(smoothing/(1+days)) + (movingAverage[-1]*(1-(smoothing/(1+days))))))
				avg = movingAverage[-1]
				summation = 0
				for xi in moving:
					summation += (xi - avg) ** 2
				stdDev = math.sqrt(summation/len(moving))
				bbTop.append(avg + (m * stdDev))
				bbBot.append(avg - (m * stdDev))
				volatility.append(2*(m * stdDev))
				movingDates.append(dates[v])
		return movingAverage, bbTop, bbBot

	def tripleEMA(self, rng = 10):
		dates, avgValues = self.getRangeData(self.sixYearDaily, BOT, EOT)
		EMA1 = self.calcEMA(avgValues, rng)
		EMA2 = self.calcEMA(EMA1, rng)
		EMA3 = self.calcEMA(EMA2, rng)
		EMA1 = EMA1[-len(EMA3):]
		EMA2 = EMA2[-len(EMA3):]
		TEMA = []
		for i in range(len(EMA3)):
			TEMA.append(3*EMA1[i] - 3*EMA2[i] + EMA3[i])
		avgValues = avgValues[-len(TEMA):]
		signals = self.classifyIntersections(avgValues, TEMA)
		return TEMA, signals

	def exponentialMovingAverage(self, rng):
		# past = 261
		# rngPlusMonth = rng + past
		dates, avgValues = self.getRangeData(self.sixYearDaily, BOT, EOT)
		# avgValues = avgValues[-rngPlusMonth:]
		# dates = dates[-rngPlusMonth:]
		# span = len(avgValues) - past
		span = rng
		moving = []
		movingAverage = self.calcEMA(avgValues, rng)
		movingDates = dates[rng-1:]
		avgValues = avgValues[-len(movingAverage):]
		signals = self.classifyIntersections(avgValues, movingAverage)
		return movingAverage, signals

	def calcEMA(self, data, rng, smoothing = 2):
		moving = []
		movingAverage = []
		for v in range(len(data)):
			if not movingAverage:
				moving.append(data[v])
			if len(moving) >= rng:
				if not movingAverage:
					#moving = moving[1:]
					movingAverage.append(sum(moving)/len(moving))
					moving.append(0)
				else:
					movingAverage.append((data[v]*(smoothing/(1+rng)) + (movingAverage[-1]*(1-(smoothing/(1+rng))))))
		return movingAverage

	def getRSI(self, rng):
		# CURRENTLY UNUSABLE FOR PRODUCTION WITHOUT DOUBLE TIME
		# NEED SELF REFERENCE TO BE USEFUL, NO TIME NOW
		# https://www.investopedia.com/terms/r/rsi.asp
		dates, lows, highs, opens, closes = self.getCandles(self.sixYearDaily)
		rsis = []
		rsiDates = []
		first = True
		deltas = []
		for d in range(1, len(dates)):
			delta = (closes[d] - closes[d-1]) / closes[d]
			if first: deltas.append(delta)
			if len(deltas) >= rng:
				if first:
					gains = sum([d for d in deltas if d > 0]) / rng
					losses = sum([d for d in deltas if d < 0]) / rng
					if not losses: losses = gains / 100
					rsi = 100-(100/(1+ (gains/abs(losses))))
					rsiDates.append(dates[d])
					rsis.append(rsi)
					first = False
				else:
					if delta > 0: 
						gains = (gains * (rng-1) + delta) / rng
					if delta < 0: 
						losses = (losses * (rng-1) + delta) / rng
					if not losses: losses = gains / 100
					rsi = 100-(100/(1+ (gains/abs(losses))))
					rsiDates.append(dates[d])
					rsis.append(rsi)
				assert(gains >= 0)
				assert(losses <= 0)
		rsiSimps = [] # -1 if below 50, 1 if above
		for r in rsis:
			if r < 50:
				rsiSimps.append(-1)
			else:
				rsiSimps.append(1)
		buySignalLine = [30 for x in range(len(rsis))]
		signals1 = self.classifyIntersections(rsis, buySignalLine)
		sellSignalLine = [70 for x in range(len(rsis))]
		signals2 = self.classifyIntersections(rsis, sellSignalLine)
		signals = []
		# midLine = [50 for x in range(len(rsis))]
		for i in range(len(signals1)):
			if signals1[i] > 0:
				signals.append(1)
			elif signals2[i] < 0:
				signals.append(-1)
			else:
				signals.append(0)
		return rsis, buySignalLine, sellSignalLine, signals

	def getCandles(self, history):
		indices = np.logical_and((history.index.tz_localize(None) >= BOT), (history.index.tz_localize(None) <= EOT))
		dates = history.index[indices]
		values = history[indices]
		lows = history["Low"].values
		highs = history["High"].values
		opens = history["Open"].values
		closes = history["Close"].values
		cleanLow = np.logical_not(np.isnan(lows))
		cleanHigh = np.logical_not(np.isnan(highs))
		cleanOpen = np.logical_not(np.isnan(opens))
		cleanClose = np.logical_not(np.isnan(closes))
		nans = [cleanLow, cleanHigh, cleanOpen, cleanClose]
		clean = cleanLow
		cleanLen = len(clean)
		for nan in nans:
			if len(nan) < cleanLen:
				clean = nan
				cleanLen = len(clean)
		lows = lows[clean]
		highs = highs[clean]
		opens = opens[clean]
		closes = closes[clean]
		dates = dates[clean]
		return dates, lows, highs, opens, closes
