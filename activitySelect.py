from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from rangeButton import RangeButton
from stockGraph import StockGraph
from popups import LoadingPopup
from statsActivity import StatsActivity
from trackActivity import TrackActivity
from rankActivity import RankActivity
from learnActivity import LearnActivity

class ActivitySelect(BoxLayout):
	def __init__(self, alpha):
		super().__init__(orientation = "horizontal", y = 0,
			size_hint = (1, None), height = Window.height*.1)
		self.spacing = (self.width * .2)/4
		self.alpha = alpha
		self.buttons = dict()
		srcs = ["search", "money", "chart", "rank", "learn"]
		acts = ["search", "track", "stats", "rank", "learn"]
		funcs = [self.toSearchActivity, self.toTrackActivity,
				self.toCompareActivity, self.toRankActivity,
				self.toLearnActivity]
		for i in range(len(srcs)):
			b = IconButton(self, funcs[i], srcs[i])
			self.buttons[acts[i]] = b
			self.add_widget(b)
		self.updateSelected(self.buttons["search"])

	def artificialClick(self, activity):
		button = self.buttons[activity]
		if activity == "search": self.toSearchActivity(button)
		elif activity == "track": self.toTrackActivity(button)
		elif activity == "stats": self.toCompareActivity(button)
		elif activity == "rank": self.toRankActivity(button)

	def invertScroll(self, *args):
		self.alpha.scrollView.do_scroll_y = not self.alpha.scrollView.do_scroll_y

	def toSearchActivity(self, itself):
		self.invertScroll()
		self.updateSelected(itself)
		self.alpha.scrollView.remove_widget(self.alpha.activity)
		self.alpha.activity = self.alpha.activities["search"]
		self.alpha.scrollView.add_widget(self.alpha.activity)
		Clock.schedule_once(self.invertScroll)
		
	def toTrackActivity(self, itself):
		self.invertScroll()
		self.updateSelected(itself)
		self.alpha.scrollView.remove_widget(self.alpha.activity)
		if "track" not in self.alpha.activities:
			self.loading = LoadingPopup()
			self.loading.open()
			self.invertScroll()
			Clock.schedule_once(self.makeTrackActivity)
		else:
			self.alpha.activity = self.alpha.activities["track"]
			self.alpha.scrollView.add_widget(self.alpha.activity)
			Clock.schedule_once(self.invertScroll)

	def makeTrackActivity(self, *args):
		self.alpha.activities["track"] = TrackActivity(self.alpha, self.alpha.searchDB)
		self.alpha.activity = self.alpha.activities["track"]
		self.alpha.scrollView.add_widget(self.alpha.activity)
		self.loading.dismiss()

	def toCompareActivity(self, itself):
		self.invertScroll()
		self.updateSelected(itself)
		self.alpha.scrollView.remove_widget(self.alpha.activity)
		if "stats" not in self.alpha.activities:
			self.loading = LoadingPopup()
			self.loading.open()
			self.invertScroll()
			Clock.schedule_once(self.makeCompareActivity)
		else:
			self.alpha.activity = self.alpha.activities["stats"]
			self.alpha.scrollView.add_widget(self.alpha.activity)
			Clock.schedule_once(self.invertScroll)
	
	def makeCompareActivityExceptImAHomelessManThatDoesntKnowHowToCode(self, abbr):
		self.alpha.activities["stats"] = StatsActivity(self.alpha, self.alpha.searchDB, abbr)

	def makeCompareActivity(self, *args):
		self.alpha.activities["stats"] = StatsActivity(self.alpha, self.alpha.searchDB)
		self.alpha.activity = self.alpha.activities["stats"]
		self.alpha.scrollView.add_widget(self.alpha.activity)
		self.loading.dismiss()

	def toRankActivity(self, itself):
		self.invertScroll()
		self.updateSelected(itself)
		self.alpha.scrollView.remove_widget(self.alpha.activity)
		if "rank" not in self.alpha.activities:
			self.loading = LoadingPopup()
			self.loading.open()
			self.invertScroll()
			Clock.schedule_once(self.makeRankActivity)
		else:
			self.alpha.activity = self.alpha.activities["rank"]
			self.alpha.scrollView.add_widget(self.alpha.activity)	
			Clock.schedule_once(self.invertScroll)	

	def makeRankActivity(self, *args):
		self.alpha.activities["rank"] = RankActivity(self.alpha)
		self.alpha.activity = self.alpha.activities["rank"]
		self.alpha.scrollView.add_widget(self.alpha.activity)
		self.loading.dismiss()

	def toLearnActivity(self, itself):
		self.invertScroll()
		self.updateSelected(itself)
		self.alpha.scrollView.remove_widget(self.alpha.activity)
		if "learn" not in self.alpha.activities:
			self.loading = LoadingPopup()
			self.loading.open()
			self.invertScroll()
			Clock.schedule_once(self.makeLearnActivity)
		else:
			self.alpha.activity = self.alpha.activities["learn"]
			self.alpha.scrollView.add_widget(self.alpha.activity)	
			Clock.schedule_once(self.invertScroll)	

	def makeLearnActivity(self, *args):
		self.alpha.activities["learn"] = LearnActivity(self.alpha)
		self.alpha.activity = self.alpha.activities["learn"]
		self.alpha.scrollView.add_widget(self.alpha.activity)
		self.loading.dismiss()

	def updateSelected(self, itself):
		for button in self.buttons.values():
			if button != itself:
				button.colorUnselected()
		itself.colorSelected()


class IconButton(Button):
	def __init__(self, layout, func, src):
		super().__init__(text = "",background_color = (1,1,1,0))
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
		