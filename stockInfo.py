from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import *


class StockInfo(GridLayout):
	def __init__(self, ticker):
		super().__init__(cols = 1, size_hint_y = None, padding = [Window.width * .05, 0])
		self.ticker = ticker
		self.nameLabel = Label(text = "", font_name = "res/Aldrich", font_size = "24sp",
			font_hinting = "light", bold = True, halign = "left", valign = "center")
		self.add_widget(self.nameLabel)
		self.addressLabel = Label(text = "Address:", font_name = "res/Aldrich", 
			font_size = "15sp", font_hinting = "light", halign = "left", valign = "bottom")
		self.add_widget(self.addressLabel)
		self.phoneLabel = Label(text = "Phone:", font_name = "res/Aldrich", 
			font_size = "15sp", font_hinting = "light", halign = "left", valign = "center")
		self.add_widget(self.phoneLabel)
		self.websiteLabel = Label(text = "Website:", font_name = "res/Aldrich", 
			font_size = "15sp", font_hinting = "light", halign = "left", valign = "center")
		self.add_widget(self.websiteLabel)
		self.detailLabel = Label(text = "Details:", font_name = "res/Aldrich", 
			font_size = "15sp", font_hinting = "light", halign = "justify", valign = "top",
			line_height = 1.5)
		self.getInfo()
		self.add_widget(self.detailLabel)
		self.nameLabel.size_hint_y = None
		self.nameLabel.height = Window.height * .1
		self.addressLabel.size_hint_y = None
		self.addressLabel.height = Window.height * .15
		self.phoneLabel.size_hint_y = None
		self.phoneLabel.height = Window.height * .05
		self.websiteLabel.size_hint_y = None
		self.websiteLabel.height = Window.height * .06
		self.detailLabel.size_hint_y = None
		self.detailLabel.height = Window.height * .4
		self.continuousHeight()
		self.bind(size = self.scale)
		Clock.schedule_once(self.continuousHeight, 0)

	def scale(self, *args):
		Clock.schedule_once(self.continuousHeight, 0)

	def continuousHeight(self, *args):
		self.nameLabel.text_size[0] = Window.width * .9
		self.nameLabel.height = self.nameLabel.texture_size[1]
		self.addressLabel.text_size[0] = Window.width * .9
		self.phoneLabel.text_size[0] = Window.width * .9
		self.websiteLabel.text_size[0] = Window.width * .9
		self.detailLabel.text_size[0] = Window.width * .9
		self.detailLabel.height = self.detailLabel.texture_size[1]
		self.height = (self.nameLabel.height + self.addressLabel.height + 
			self.phoneLabel.height + self.websiteLabel.height + self.detailLabel.height)

	def updateTicker(self, ticker):
		self.ticker = ticker
		self.getInfo()


	def getInfo(self):
		try: info = self.ticker.info
		except: info = dict()
		name = ""
		a1 = ""
		a2 = ""
		city = ""
		state = ""
		z = ""
		phone = ""
		website = ""
		details = ""
		country = ""
		try:name = info["longName"] + " "
		except:pass 
		try:a1 = info["address1"] + " "
		except:
			a1 = "Sorry! There was a problem downloading this information, check back soon..."
		try:a2 = info["address2"] + " "
		except:pass
		try:city = info["city"] + ", "
		except:pass
		try:state = info["state"] + " "
		except:pass
		try:country = info["country"] + " "
		except:pass
		try:z = info["zip"] + " "
		except:pass
		try:phone = info["phone"] + " "
		except:pass
		try:website = info["website"] + " "
		except:pass
		try:details = info["longBusinessSummary"] + " "
		except:pass
		self.nameLabel.text = name
		self.addressLabel.text = "Address: " + a1 + a2 + "\n              " + city + state + z + "\n              " + country
		self.phoneLabel.text = "Phone: " + phone
		self.websiteLabel.text = "Website: " + website
		self.detailLabel.text = "Details: " + details.replace("&#39;", "'")
		# self.detailLabel.height = self.detailLabel.texture_size[1]
		# self.height = (self.nameLabel.height + self.addressLabel.height + 
		# 	self.phoneLabel.height + self.websiteLabel.height + self.detailLabel.height)
		# self.nameLabel.height = self.nameLabel.texture_size[1]
		# self.addressLabel.height = self.addressLabel.texture_size[1]
		# self.phoneLabel.height = self.phoneLabel.texture_size[1]
		# self.websiteLabel.height = self.websiteLabel.texture_size[1]
		# self.detailLabel.height = self.detailLabel.texture_size[1]