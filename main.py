from kivy.app import App 
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from searchActivity import SearchActivity
from activitySelect import ActivitySelect
from searchTree import SearchTree
import pickle
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

#TODO: Bind(esc)

class StockAnalysis(App):
	def build(self):
		searchables = pickle.load(open("res/searchables.p", 'rb'))
		self.crossRefs = pickle.load(open("res/crossMark6.p", 'rb'))
		self.searchRecs = SearchTree(searchables)
		self.searchDB = (self.crossRefs, self.searchRecs)
		self.activities = {"search": SearchActivity(self, self.searchDB)}
		self.root = GridLayout(cols = 1)
		self.activity = self.activities["search"]
		#######################################
		############# Scroll View #############
		#######################################
		self.scrollView = ScrollView(size_hint = (1, None), do_scroll_x = False,
			do_scroll_y = True, size = (Window.width, Window.height*.9), scroll_timeout = 250,
			y = Window.height*.1)
		def scrollViewScale(*args):
			self.scrollView.size = (Window.width, Window.height*.9)
			self.scrollView.y = Window.height*.1
		self.scrollView.bind(size = scrollViewScale)
		self.scrollView.add_widget(self.activity)
		self.root.add_widget(self.scrollView)
		self.activitySelect = ActivitySelect(self)
		def activitySelectScale(*args):
			self.activitySelect.size = (Window.width, Window.height*.1)
			self.activitySelect.y = 0
		self.activitySelect.bind(size = activitySelectScale)
		self.root.add_widget(self.activitySelect)
		self.currentConduitLabel = ""
		self.conduit = None
		Window.bind(on_keyboard = self.androidBack)
		return self.root

	def androidBack(self, window, key1, key2, *args):
		# print(self.conduit)
		if key1 in [27, 1001]:
			if self.conduit:
				self.conduit.back()
			return True
		return False

if __name__ == "__main__":
	app = StockAnalysis()
	app.run()