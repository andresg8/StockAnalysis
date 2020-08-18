from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import *
import pickle

'''
Current best idea = txt files for each stat / description loaded 
individually at runtime to save on init load times

'''
class LearnActivity(GridLayout):
	def __init__(self, app):
		super().__init__(cols = 1, size_hint_y = None)
		self.bind(minimum_height=self.setter('height'))
		self.app = app
		self.titleLabel = Label(text = "Learn!", font_name = "res/Aldrich", 
			font_hinting = "light", bold = True, italic = True, font_size = "24sp",
			halign = "left", height = Window.height * .1, size_hint_y = None)
		self.add_widget(self.titleLabel)
		# List of buttons that redirect to a datalayout for the txt file contents
		# need swap paradigm from other activities
		self.libraryLayout = GridLayout(cols = 1, size_hint_y = None)
		self.libraryLayout.bind(minimum_height=self.libraryLayout.setter('height'))
		
		# How do I use?
		self.howLabel = Label(text = "How do I use...", font_name = "res/Aldrich", 
			font_hinting = "light", bold = True, italic = True, font_size = "24sp",
			halign = "left", valign = "center", height = Window.height * .1, 
			size_hint_y = None)
		self.howLabel.bind(size = self.howLabel.setter("text_size"))
		self.libraryLayout.add_widget(self.howLabel)
		books = []
		with open("res/how.txt") as file:
			for line in file:
				bookLayout = BookLayout()
				txt = ""
				icon = ""
				if "[" in line:
					txt = line.split("[")[0]
					icon = line.split("[")[1].replace("]", "").strip()
				if icon:
					bookIcon = IconButton(icon, self.spin)
					bookLayout.add_widget(bookIcon)
				bookTitle = Button(text = txt, font_name = "res/Aldrich", 
					font_hinting = "light", bold = True, italic = True, font_size = "18sp",
					halign = "left", valign = "center", height = Window.height * .1, 
					size_hint_y = None, background_color = (1, 1, 1, 0))
				bookTitle.bind(size = bookTitle.setter("text_size"), on_press = self.openPage)
				bookLayout.add_widget(bookTitle)
				books.append(bookLayout)
				self.libraryLayout.add_widget(bookLayout)
		# What is?
		self.whatLabel = Label(text = "What is...", font_name = "res/Aldrich", 
			font_hinting = "light", bold = True, italic = True, font_size = "24sp",
			halign = "left", valign = "center", height = Window.height * .1, 
			size_hint_y = None)
		self.whatLabel.bind(size = self.whatLabel.setter("text_size"))
		self.libraryLayout.add_widget(self.whatLabel)
		with open("res/what.txt") as file:
			for line in file:
				bookLayout = BookLayout()
				txt = line.strip()
				icon = ""
				if "[" in line:
					txt = line.split("[")[0].strip()
					icon = line.split("[")[1].replace("]", "").strip()
				if icon:
					bookIcon = IconButton(icon, self.spin)
					bookLayout.add_widget(bookIcon)
				else: 
					bookLayout.padding = [Window.width * .05, 0]
				bookTitle = Button(text = txt, font_name = "res/Aldrich", 
					font_hinting = "light", bold = True, italic = True, font_size = "18sp",
					halign = "left", valign = "center", height = Window.height * .1, 
					size_hint_y = None, background_color = (1, 1, 1, 0))
				bookTitle.bind(size = bookTitle.setter("text_size"), on_press = self.openPage)
				bookLayout.add_widget(bookTitle)
				books.append(bookLayout)
				self.libraryLayout.add_widget(bookLayout)
		self.focusLayout = self.libraryLayout
		self.add_widget(self.focusLayout)

	def spin(self, *args):
		pass

	def openPage(self, itself):
		self.newPage = BookPage(itself.text.strip(), self)
		self.swap(self.newPage)


	def swap(self, new = None):
		if not new:
			new = self.libraryLayout
		self.remove_widget(self.focusLayout)
		self.focusLayout = new
		self.add_widget(self.focusLayout)

class BookPage(GridLayout):
	def __init__(self, src, master):
		super().__init__(cols = 1, size_hint_y = None)
		self.bind(minimum_height=self.setter('height'))
		self.src = src
		self.master = master
		self.bar = GridLayout(rows = 1, size_hint_y = None, height = Window.height * .1,
			spacing = [Window.width * .05, 0])
		self.backButton = IconButton("back", self.back)
		self.bar.add_widget(self.backButton)
		self.titleLabel = Label(text = src, font_name = "res/Aldrich", 
					font_hinting = "light", bold = True, italic = True, font_size = "24sp",
					halign = "left", valign = "center", height = Window.height * .1, 
					size_hint_y = None)
		self.titleLabel.bind(size = self.titleLabel.setter("text_size"))
		self.bar.add_widget(self.titleLabel)
		self.add_widget(self.bar)
		self.contentLayout = GridLayout(cols = 1, size_hint_y = None, padding = [Window.width * .05, 0])
		self.contentLayout.bind(minimum_height=self.contentLayout.setter('height'))
		self.content = ""
		with open("res/" + src + ".txt", "r") as file:
			lines = file.readlines()
			self.content = "".join([line.strip() + " " if line.strip() else "\n\n" for line in lines])
		self.contentLabel = Label(text = self.content, font_name = "res/Aldrich", 
					font_hinting = "light", bold = True, italic = True, font_size = "15sp",
					halign = "justify", valign = "top", width = Window.width * .9, 
					size_hint_y = None, line_height = 1.5)
		# self.contentLabel.bind(size = self.contentLabel.setter("text_size"),
		# 	texture_size = self.contentLabel.setter("height"))
		self.bind(size = self.continuousHeight, pos = self.continuousHeight)
		self.contentLayout.add_widget(self.contentLabel)
		self.add_widget(self.contentLayout)

	def continuousHeight(self, *args):
		self.contentLabel.text_size[0] = Window.width * .9
		self.contentLabel.height = self.contentLabel.texture_size[1]

	def back(self, *args):
		self.master.swap(self.master.libraryLayout)

class BookLayout(GridLayout):
	def __init__(self):
		super().__init__(rows = 1, size_hint_y = None, height = Window.height * .1,
					spacing = [Window.width * .05, 0])
		with self.canvas:
			Color(128/255, 128/255, 128/255, 1)
			self.underLine = Line(points = [self.x + .1 * self.width, self.y, self.x + .9 * self.width, self.y], 
									width = .5, cap = 'round', joint = 'round', close = False)
		self.draw()
		self.bind(pos = self.draw, size = self.draw)

	def draw(self, *args):
		self.canvas.remove(self.underLine)
		with self.canvas:
			Color(128/255, 128/255, 128/255, 1)
			self.underLine = Line(points = [self.x + .1 * self.width, self.y, self.x + .9 * self.width, self.y], 
									width = .5, cap = 'round', joint = 'round', close = False)

class IconButton(Button):
	def __init__(self, src, func):
		super().__init__(text = "",background_color = (1,1,1,0), size_hint_y = None, size_hint_x = None,
			height = Window.height * .1, width = Window.height * .1)
		with self.canvas:
			self.image = Image(source = "res/" + src + ".png", color = (255/255,255/255,255/255,1))
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