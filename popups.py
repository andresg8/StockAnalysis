from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window


class ErrorPopup(Popup):
	def __init__(self, errmsg = "An Unexpected Error Has Occured..."):
		super().__init__(size_hint_y = None, size_hint_x = None,
			width = Window.width * .6, height = Window.width * .6,
			title = "")
		self.contentLayout = GridLayout(cols = 1)
		self.errorLabel = Label(text = "Sorry!\n" + errmsg,
			font_name = "res/Aldrich", font_hinting = "light", bold = True,
			halign = "center", valign = "center", width = self.width)
		self.errorLabel.text_size[0] = self.errorLabel.width * .9
		self.contentLayout.add_widget(self.errorLabel)
		self.seppukuLayout = GridLayout(rows = 1)
		self.spacer = Label(text = "", size_hint_x = None, width = self.width*.2)
		self.seppukuLayout.add_widget(self.spacer)
		self.seppukuButton = Button(text = "Close", 
			font_name = "res/Aldrich", font_hinting = "light", bold = True,
			halign = "center", valign = "center", size_hint_x = None,
			width = self.width * .5, height = self.width * .5)
		self.seppukuButton.bind(on_press = self.seppuku)
		self.seppukuLayout.add_widget(self.seppukuButton)
		self.contentLayout.add_widget(self.seppukuLayout)
		self.content = self.contentLayout

	def seppuku(self, *args):
		self.dismiss()

class LoadingPopup(Popup):
	def __init__(self):
		super().__init__(size_hint_y = None, size_hint_x = None,
			width = Window.width * .6, height = Window.width * .6,
			title = "", auto_dismiss = False)
		# self.bind(minimum_height=self.setter('height'))
		self.contentLayout = GridLayout(cols = 1)
		self.loadingLabel = Label(text = "Loading...", font_size = 20,
			font_name = "res/Aldrich", font_hinting = "light", bold = True,
			halign = "center", valign = "center", width = self.width)
		self.contentLayout.add_widget(self.loadingLabel)
		self.content = self.contentLayout

class SurePopup(Popup):
	def __init__(self, activity, name, seppuku):
		super().__init__(size_hint_y = None, size_hint_x = None,
			width = Window.width * .6, height = Window.width * .6,
			title = "")
		# self.bind(minimum_height=self.setter('height'))
		self.activity = activity
		self.name = name
		self.seppuku = seppuku
		self.contentLayout = GridLayout(cols = 1)
		self.youSure = Label(text = "Are you sure you wish to remove " + name + "?",
			font_name = "res/Aldrich", font_hinting = "light", bold = True,
			halign = "center", valign = "center", width = self.width)
		self.youSure.text_size[0] = self.youSure.width
		self.contentLayout.add_widget(self.youSure)
		self.add_widget(self.contentLayout)
		self.buttonLayout = GridLayout(rows = 1)
		self.confirmed = False
		self.confirm = Button(text = "Yes", font_name = "res/Aldrich", font_hinting = "light", bold = True,
			halign = "center", valign = "center", background_color = (0,1,0,.7))
		self.confirm.bind(on_press = self.confirmFunc)
		self.reject = Button(text = "No", font_name = "res/Aldrich", font_hinting = "light", bold = True,
			halign = "center", valign = "center", background_color = (1,0,0,.7))
		self.reject.bind(on_press = self.rejectFunc)
		self.buttonLayout.add_widget(self.confirm)
		self.buttonLayout.add_widget(self.reject)
		self.contentLayout.add_widget(self.buttonLayout)
		self.content = self.contentLayout

	def confirmFunc(self, *args):
		self.dismiss()
		self.seppuku()

	def rejectFunc(self, *args):
		self.dismiss()