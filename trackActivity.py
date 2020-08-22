from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.graphics import *
from kivy.core.window import Window
from stockGraph import StockGraph
from rangeButton import RangeButton
from searchTree import SearchTree
from stockInfo import StockInfo
from popups import SurePopup, LoadingPopup
import yfinance as yf
import pickle


class TrackActivity(GridLayout):
	def __init__(self, app, searchDB):
		super().__init__(cols = 1, size_hint_y = None)
		self.bind(minimum_height=self.setter('height'))
		self.app = app
		self.searchDB = searchDB
		self.titleLabel = Label(text = "Portfolios", font_name = "res/Aldrich", 
			font_hinting = "light", bold = True, italic = True, font_size = "24sp",
			halign = "center", height = Window.height * .1, size_hint_y = None)
		self.titleLabel.text_size[0] = Window.width
		self.add_widget(self.titleLabel)
		try:
			self.portfolios = pickle.load(open("res/userPortfolios.p", 'rb'))
		except:
			self.portfolios = []
		self.portfoliosLayout = PortfolioWidgetsLayout(self.portfolios, self)
		self.focusLayout = self.portfoliosLayout
		self.add_widget(self.focusLayout)

	def swap(self, new = None):
		if not new:
			new = self.portfoliosLayout
		self.remove_widget(self.focusLayout)
		self.focusLayout = new
		self.add_widget(self.focusLayout)

class PortfolioWidgetsLayout(GridLayout):
	def __init__(self, portfolios, activity):
		super().__init__(cols = 1, size_hint_y = None)
		self.bind(minimum_height=self.setter('height'))
		self.portfolios = portfolios
		self.activity = activity
		self.pWidgets = []
		self.updateLayout = GridLayout(rows = 1, size_hint_y = None, 
			height = Window.height * .1)
		self.updateSpacer = Label(text = "", size_hint_y = None, size_hint_x = None,
			height = Window.height * .1, width = Window.width * .85)
		self.updateLayout.add_widget(self.updateSpacer)
		self.updateButton = IconButton(self.updateLoader, "sync")
		self.updateLayout.add_widget(self.updateButton)
		self.add_widget(self.updateLayout)
		for portfolio in self.portfolios:
			pWidget = PortfolioWidget(portfolio, self, self.activity)
			self.pWidgets.append(pWidget)
			self.add_widget(pWidget)
		self.centeringLayout = GridLayout(rows = 1, size_hint_y = None)
		self.centeringLabel = Label(text = "", size_hint_y = None, size_hint_x = None, 
			height = Window.height * .1, width = Window.width *.45)
		self.centeringLayout.add_widget(self.centeringLabel)
		self.addPortfolioButton = IconButton(self.addPortfolio, "add", (0, 1, 0, .6))
		self.centeringLayout.add_widget(self.addPortfolioButton)
		self.add_widget(self.centeringLayout)
		# self.bind(pos = self.manageConduit, size = self.manageConduit)

	def manageConduit(self, *args):
		self.activity.app.conduit = None

	def updateLoader(self, *args):
		self.loading = LoadingPopup()
		self.loading.open()
		Clock.schedule_once(self.update)

	def update(self, *args):
		for portfolio in self.portfolios:
			portfolio.update()
		pickle.dump(self.portfolios, open("res/userPortfolios.p", 'wb'))
		self.redraw()
		self.loading.dismiss()

	def redraw(self):
		self.clear_widgets()
		self.pWidgets = []
		self.add_widget(self.updateLayout)
		for portfolio in self.portfolios:
			pWidget = PortfolioWidget(portfolio, self, self.activity)
			self.pWidgets.append(pWidget)
			self.add_widget(pWidget)
		self.add_widget(self.centeringLayout)

	def addPortfolio(self, *args):
		newPortfolio = Portfolio()
		self.activity.portfolios.append(newPortfolio)
		self.remove_widget(self.centeringLayout)
		pWidget = PortfolioWidget(newPortfolio, self, self.activity)
		self.add_widget(pWidget)
		self.add_widget(self.centeringLayout)
		pickle.dump(self.portfolios, open("res/userPortfolios.p", 'wb'))

class PortfolioWidget(GridLayout):
	def __init__(self, portfolio, master, activity):
		super().__init__(rows = 1, size_hint_y = None)
		self.bind(minimum_height=self.setter('height'))
		self.portfolio = portfolio
		self.activity = activity
		self.master = master
		fs = "12sp"
		self.seppukuButton = IconButton(self.seppukuHandler, "delete", (1, 69/255, 0, .7))
		self.add_widget(self.seppukuButton)
		self.abbrLabel = Label(text = portfolio.name, font_name = "res/Aldrich", font_hinting = "light",
								font_size = fs, height = Window.height * .1, size_hint_y = None,
								width = Window.width * .18, size_hint_x = None, halign = "center")
		self.abbrLabel.text_size[0] = self.abbrLabel.width
		self.add_widget(self.abbrLabel)
		self.detailLayout = GridLayout(cols = 1, height = Window.height * .1, size_hint_y = None)
		self.valueLayout = GridLayout(rows = 1, height = Window.height * .05, size_hint_y = None)
		self.avgCostLabel = Label(text = "Initial Cost: ${0:.2f}".format(portfolio.entryFee), font_name = "res/Aldrich", font_hinting = "light",
								font_size = fs, height = Window.height * .05, size_hint_y = None,
								width = Window.width * .36, size_hint_x = None,
								halign = "center", valign = "center")
		self.avgCostLabel.text_size[0] = self.avgCostLabel.width
		self.valueLayout.add_widget(self.avgCostLabel)
		self.valueLabel = Label(text = "Current Value: ${0:.2f}".format(portfolio.currentPrice), font_name = "res/Aldrich", font_hinting = "light",
								font_size = fs, height = Window.height * .05, size_hint_y = None,
								width = Window.width * .36, size_hint_x = None,
								halign = "center", valign = "center")
		self.valueLabel.text_size[0] = self.valueLabel.width
		self.valueLayout.add_widget(self.valueLabel)
		self.detailLayout.add_widget(self.valueLayout)
		self.profitLayout = GridLayout(rows = 1, height = Window.height * .05, size_hint_y = None)
		self.flatLabel = Label(text = "Profit: ${0:.2f}".format(portfolio.flatProfit), font_name = "res/Aldrich", font_hinting = "light",
								font_size = fs, height = Window.height * .05, size_hint_y = None,
								width = Window.width * .36, size_hint_x = None,
								halign = "center", valign = "center")
		self.flatLabel.text_size[0] = self.flatLabel.width
		self.profitLayout.add_widget(self.flatLabel)
		self.percentLabel = Label(text = "Percent Change: {0:.2f}%".format(portfolio.avgPercentChange), font_name = "res/Aldrich", font_hinting = "light",
								font_size = fs, height = Window.height * .05, size_hint_y = None,
								width = Window.width * .36, size_hint_x = None,
								halign = "center", valign = "center")
		self.percentLabel.text_size[0] = self.percentLabel.width
		self.profitLayout.add_widget(self.percentLabel)
		self.detailLayout.add_widget(self.profitLayout)
		self.add_widget(self.detailLayout)
		with self.canvas:
			Color(100/255, 149/255, 237/255, .86)
			self.underLine = Line(points = [self.x + .1 * self.width, self.y, self.x + .9 * self.width, self.y], 
									width = .5, cap = 'round', joint = 'round', close = False)
		self.bind(pos = self.manageLine, size = self.manageLine)
		self.touchDown = False

	def manageLine(self, *args):
		self.canvas.remove(self.underLine)
		with self.canvas:
			Color(100/255, 149/255, 237/255, .86)
			self.underLine = Line(points = [self.x + .1 * self.width, self.y, self.x + .9 * self.width, self.y], 
									width = .5, cap = 'round', joint = 'round', close = False)


	def inWidget(self, touch):
		within = False
		if touch.x > self.x and touch.x < self.x + self.width:
			if touch.y > self.y and touch.y < self.y + self.height:
				within = True
		return within

	def on_touch_down(self, touch):
		if self.inWidget(touch):
			self.touchDown = True
		return super().on_touch_down(touch)

	def on_touch_up(self, touch):
		if self.inWidget(touch) and self.touchDown:
			self.toEditor()
		self.touchDown = False
		return super().on_touch_up(touch)

	def seppukuHandler(self, *args):
		self.touchDown = False
		popup = SurePopup(self.activity, self.portfolio.name, self.seppuku)
		popup.open()

	def seppuku(self):
		self.master.portfolios.remove(self.portfolio)
		self.master.updateLoader()

	def toEditor(self):
		self.activity.titleLabel.text = self.portfolio.name + "'s Stocks"
		self.activity.swap(PortfolioEditorLayout(self.portfolio, self.activity))


class PortfolioEditorLayout(GridLayout):
	def __init__(self, portfolio, activity):
		super().__init__(cols = 1, size_hint_y = None)
		self.bind(minimum_height=self.setter('height'))
		self.portfolio = portfolio
		self.activity = activity
		self.titleLayout = GridLayout(rows = 1, size_hint_y = None, height = Window.height * .1)
		self.backButton = IconButton(self.back, "back")
		self.titleLayout.add_widget(self.backButton)
		self.nameEntry = TextInput(text = self.portfolio.name, background_color = (0, 0, 0, 0),
			foreground_color = (1, 1, 1, 1), cursor_color = (0, 1, 0, 1), multiline = False, 
			font_size = "24sp", height = Window.height * .1, size_hint_y = None, width = Window.width * .75, 
			size_hint_x = None, padding = [6, (Window.height * .025)])
		self.nameEntry.bind(on_text_validate = self.changeName)
		self.nameEntry.bind(focus = self.changeNameFocus)
		self.titleLayout.add_widget(self.nameEntry)
		self.updateButton = IconButton(self.updateLoader, "sync")
		self.titleLayout.add_widget(self.updateButton)
		self.add_widget(self.titleLayout)
		self.sWidgets = []
		for stock in self.portfolio.stocks:
			sWidget = StockWidget(stock, self, self.activity.app)
			self.sWidgets.append(sWidget)
			self.add_widget(sWidget)
		self.centeringLayout = GridLayout(rows = 1, size_hint_y = None)
		self.centeringLabel = Label(text = "", size_hint_y = None, size_hint_x = None, 
			height = Window.height * .1, width = Window.width *.45)
		self.centeringLayout.add_widget(self.centeringLabel)
		self.addStockButton = IconButton(self.addStock, "add", (0, 1, 0, .6))
		self.centeringLayout.add_widget(self.addStockButton)
		self.add_widget(self.centeringLayout)
		pickle.dump(self.activity.portfolios, open("res/userPortfolios.p", 'wb'))
		self.bind(pos = self.manageConduit, size = self.manageConduit)

	def manageConduit(self, *args):
		self.activity.app.conduit = self

	def updateLoader(self, *args):
		self.loading = LoadingPopup()
		self.loading.open()
		Clock.schedule_once(self.update)

	def update(self, *args):
		# for stock in self.portfolio.stocks:
		# 	stock.update()
		self.portfolio.update()
		pickle.dump(self.activity.portfolios, open("res/userPortfolios.p", 'wb'))
		self.redraw()
		self.loading.dismiss()

	def addStock(self, *args):
		self.activity.titleLabel.text = "Add Stock to " + self.portfolio.name
		self.activity.swap(StockAdderWidget(self, self.activity))

	def redraw(self):
		self.clear_widgets()
		self.add_widget(self.titleLayout)
		self.sWidgets = []
		for stock in self.portfolio.stocks:
			sWidget = StockWidget(stock, self, self.activity.app)
			self.sWidgets.append(sWidget)
			self.add_widget(sWidget)
		self.add_widget(self.centeringLayout)

	def back(self, *args):
		self.activity.app.conduit = None
		self.activity.titleLabel.text = "Portfolios"
		self.activity.swap(PortfolioWidgetsLayout(self.activity.portfolios, self.activity))

	def changeNameFocus(self, *args):
		if not args[-1]:
			self.changeName(None)

	def changeName(self, *args):
		newName = self.nameEntry.text
		self.portfolio.name = newName
		self.activity.titleLabel.text = self.portfolio.name + "'s Stocks"
		self.nameEntry.focus = False 

class StockWidget(GridLayout):
	def __init__(self, stock, master, app):
		super().__init__(rows = 1, size_hint_y = None)
		fs = "12sp"
		self.bind(minimum_height=self.setter('height'))
		self.stock = stock
		self.master = master
		self.app = app
		self.seppukuButton = IconButton(self.seppukuHandler, "delete", (1, 69/255, 0, .7))
		self.add_widget(self.seppukuButton)
		stockDescriptor = stock.abbr+"\n"+stock.name
		if len(stockDescriptor) >= 30:
			stockDescriptor = stockDescriptor[:27] + "..."
		self.abbrLabel = Label(text = stockDescriptor, font_name = "res/Aldrich", font_hinting = "light", 
								font_size = fs, height = Window.height * .1, size_hint_y = None,
								width = Window.width * .18, size_hint_x = None, halign = "center", valign = "center")
		self.abbrLabel.text_size = [Window.width * .18, Window.height * .1]
		self.add_widget(self.abbrLabel)
		self.detailLayout = GridLayout(cols = 1, height = Window.height * .1, size_hint_y = None)
		self.valueLayout = GridLayout(rows = 1, height = Window.height * .05, size_hint_y = None)
		self.avgCostLabel = Label(text = "Initial Cost: ${0:.2f}".format(stock.purchasePrice), font_name = "res/Aldrich", font_hinting = "light",
								font_size = fs, height = Window.height * .05, size_hint_y = None,
								width = Window.width * .36, size_hint_x = None,
								halign = "center", valign = "center")
		self.avgCostLabel.text_size[0] = self.avgCostLabel.width
		self.valueLayout.add_widget(self.avgCostLabel)
		self.valueLabel = Label(text = "Current Value: ${0:.2f}".format(stock.currentPrice), font_name = "res/Aldrich", font_hinting = "light",
								font_size = fs, height = Window.height * .05, size_hint_y = None,
								width = Window.width * .36, size_hint_x = None,
								halign = "center", valign = "center")
		self.valueLabel.text_size[0] = self.valueLabel.width
		self.valueLayout.add_widget(self.valueLabel)
		self.detailLayout.add_widget(self.valueLayout)
		self.profitLayout = GridLayout(rows = 1, height = Window.height * .05, size_hint_y = None)
		self.flatLabel = Label(text = "Profit: ${0:.2f}".format(stock.flatProfit), font_name = "res/Aldrich", font_hinting = "light",
								font_size = fs, height = Window.height * .05, size_hint_y = None,
								width = Window.width * .36, size_hint_x = None,
								halign = "center", valign = "center")
		self.flatLabel.text_size[0] = self.flatLabel.width
		self.profitLayout.add_widget(self.flatLabel)
		self.percentLabel = Label(text = "Percent Change: {0:.2f}%".format(stock.percentProfit), font_name = "res/Aldrich", font_hinting = "light",
								font_size = fs, height = Window.height * .05, size_hint_y = None,
								width = Window.width * .36, size_hint_x = None,
								halign = "center", valign = "center")
		self.percentLabel.text_size[0] = self.percentLabel.width
		self.profitLayout.add_widget(self.percentLabel)
		self.detailLayout.add_widget(self.profitLayout)
		self.add_widget(self.detailLayout)
		with self.canvas:
			Color(100/255, 149/255, 237/255, .86)
			self.underLine = Line(points = [self.x + .1 * self.width, self.y, self.x + .9 * self.width, self.y], 
									width = .5, cap = 'round', joint = 'round', close = False)
		self.bind(pos = self.manageLine, size = self.manageLine)
		self.touchDown = False

	def manageLine(self, *args):
		self.canvas.remove(self.underLine)
		with self.canvas:
			Color(100/255, 149/255, 237/255, .86)
			self.underLine = Line(points = [self.x + .1 * self.width, self.y, self.x + .9 * self.width, self.y], 
									width = .5, cap = 'round', joint = 'round', close = False)

	def inWidget(self, touch):
		within = False
		if touch.x > self.x and touch.x < self.x + self.width:
			if touch.y > self.y and touch.y < self.y + self.height:
				within = True
		return within

	def on_touch_down(self, touch):
		if self.inWidget(touch):
			self.touchDown = True
		return super().on_touch_down(touch)

	def on_touch_up(self, touch):
		if self.inWidget(touch) and self.touchDown:
			self.toStock()
		self.touchDown = False
		return super().on_touch_up(touch)

	def seppukuHandler(self, *args):
		self.touchDown = False
		popup = SurePopup(self.master.activity, self.stock.name, self.seppuku)
		popup.open()

	def seppuku(self, *args):
		self.master.portfolio.removeStock(self.stock)
		self.master.updateLoader()

	def toStock(self):
		self.app.activities["search"].artificialUpdateGraph(self.stock.abbr)
		self.app.activitySelect.artificialClick("search")

class StockAdderWidget(GridLayout):
	def __init__(self, master, activity):
		super().__init__(cols = 1, size_hint_y = None)
		self.bind(minimum_height=self.setter('height'))
		self.activity = activity
		self.master = master
		self.searchLayout = GridLayout(rows = 1, size_hint_y = None, height = Window.height * .1)
		self.searchBar = SearchBar(self, self.activity, self.activity.searchDB)
		self.searchLayout.add_widget(self.searchBar)
		self.cancelButton = Button(text = "Cancel", font_name = "res/Aldrich", font_hinting = "light",
								height = Window.height * .1, size_hint_y = None,
								size_hint_x = .3)
		self.cancelButton.bind(on_press = self.back)
		self.searchLayout.add_widget(self.cancelButton)
		self.add_widget(self.searchLayout)
		self.searchRecLayout = GridLayout(cols = 1, 
				size_hint_y = None, height = Window.height * 1)
		self.add_widget(self.searchRecLayout)
		self.bind(pos = self.manageConduit, size = self.manageConduit)

	def manageConduit(self, *args):
		self.activity.app.conduit = self
			

	def back(self, *args):
		self.activity.app.conduit = None
		self.activity.titleLabel.text = self.master.portfolio.name + "'s Stocks"
		self.activity.swap(PortfolioEditorLayout(self.master.portfolio, self.activity))

class Portfolio:
	def __init__(self, name = "New Portfolio"):
		self.name = name
		self.stocks = []
		self.entryFees = []
		self.entryFee = 0
		self.currentPrice = 0
		self.flatProfit = 0
		self.percentProfit = 0
		self.avgPercentChange = 0

	def addStock(self, abbr, name):
		currentPrice = yf.Ticker(abbr).history("1d", "1m")["Low"].values[-1]
		self.entryFees.append(currentPrice)
		st = Stock(abbr, name, currentPrice)
		self.stocks.append(st)
		self.update()

	def removeStock(self, stock):
		i = self.stocks.index(stock)
		self.entryFees.pop(i)
		self.stocks.pop(i)
		self.update()

	def update(self):
		self.entryFee = sum(self.entryFees)
		self.currentPrice = 0
		avgPercentChange = []
		for st in self.stocks:
			currentPrice, percentProfit = st.update()
			self.currentPrice += currentPrice
			avgPercentChange.append(percentProfit)
		self.flatProfit = self.currentPrice - self.entryFee
		self.percentProfit = self.flatProfit
		if avgPercentChange:
			self.avgPercentChange = (sum(avgPercentChange) / len(avgPercentChange))
		else:
			self.avgPercentChange = 0


class Stock:
	def __init__(self, abbr, name, pp):
		self.abbr = abbr
		self.name = name
		self.purchasePrice = pp
		self.currentPrice = pp
		self.flatProfit = 0
		self.percentProfit = 0

	def update(self):
		currentPrice = yf.Ticker(self.abbr).history("1d", "1m")["Low"].values[-1]
		self.currentPrice = currentPrice
		self.flatProfit = currentPrice - self.purchasePrice
		percentProfit = 100 * (self.flatProfit / self.purchasePrice)
		self.percentProfit = percentProfit
		return currentPrice, percentProfit

class SearchBar(TextInput):
	def __init__(self, master, activity, searchDB = None):
		#db = (searchables, SearchTree)
		super().__init__(hint_text = "Company...", background_color = (0, 0, 0, 0),
			foreground_color = (1, 1, 1, 1), cursor_color = (0, 1, 0, 1),
			multiline = False, size_hint_y = None, size_hint_x = .7, 
			height = Window.height * .1)
		if not searchDB:
			searchables = pickle.load(open("res/searchables.p", 'rb'))
			self.crossRefs = pickle.load(open("res/crossMark6.p", 'rb'))
			self.searchRecs = SearchTree(searchables)
		else:
			self.crossRefs = searchDB[0]
			self.searchRecs = searchDB[1]
		self.activity = activity
		self.master = master
		self.scrollView = None
		self.searchRecLayout = None
		#self.bind(focus = self.updateAFBox)
		self.bind(text = self.autofill)

	def updateAFBox(self, *args):
		if args[-1]:
			self.searchRecLayout = GridLayout(cols = 1, 
				size_hint_y = None, height = Window.height * 1)
			if self.text:
				self.autofill(self.text)
			if self.master.searchRecLayout:
				self.master.remove_widget(self.master.searchRecLayout)
			self.master.add_widget(self.searchRecLayout)
			self.master.searchRecLayout = self.searchRecLayout
		# else:
		# 	self.activity.swap()

	def autofill(self, *args):
		if args[-1]:
			self.searchRecLayout = GridLayout(cols = 1, 
				size_hint_y = None, height = Window.height * 1)
			recommend = self.searchRecs.relateItem(args[-1].upper())
			txts = []
			for r in recommend:
				cross = ""
				if r in self.crossRefs:
					cross = self.crossRefs[r]
				abbr = cross
				name = r
				if len(r) < len(cross) or not cross:
					abbr = r
					name = cross
				elif len(r) == len(cross) and r < cross:
					abbr = r
					name = cross
				if "(the)" in name.lower(): name = "The " + name[0:-6]
				txt = abbr + ": " + name
				if txt in txts:
					continue
				txts.append(txt)
				b = Button(text = txt, height = Window.height * .1, halign = "center", font_name = "res/Aldrich", font_hinting = "light",
					size_hint_max_y = Window.height * .1, size_hint_min_y = Window.height * .1)
				b.text_size[0] = Window.width
				b.abbr = abbr
				b.name = name
				def useRec(itself):
					#self.text = itself.abbr
					self.master.master.portfolio.addStock(itself.abbr, itself.name)
					self.activity.titleLabel.text = self.master.master.portfolio.name + "'s Stocks"
					self.activity.swap(PortfolioEditorLayout(self.master.master.portfolio, self.activity))
				b.bind(on_press = useRec)
				self.searchRecLayout.add_widget(b)
			self.searchRecLayout.height = Window.height * .1 * len(recommend)
			if self.master.searchRecLayout:
				self.master.remove_widget(self.master.searchRecLayout)
			self.master.add_widget(self.searchRecLayout)
			self.master.searchRecLayout = self.searchRecLayout
			# self.alpha.swap(self.alpha.searchRecLayout)




class IconButton(Button):
	def __init__(self, func, src, color = None):
		super().__init__(text = "",background_color = (1,1,1,0), size_hint_y = None, size_hint_x = None,
			height = Window.height * .1, width = Window.width *.1)
		if color: 
			self.color = color
		else:
			self.color = (1,1,1,1)
		with self.canvas:
			self.image = Image(source = "res/" + src + ".png", color = self.color)
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


