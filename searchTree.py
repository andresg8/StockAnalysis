class Node():
	def __init__(self, content, visible, children = None):
		self.content = content
		self.visible = visible
		if children:
			self.children = children
		else:
			self.children = []

	def addChild(self, child):
		self.children.append(child)

	def __str__(self):
		return self.content

	def __contains__(self, item):
		contents = []
		for child in self.children:
			contents.append(child.content)
		return item in contents

	def __getitem__(self, index):
		return self.children[index]

	def __iter__(self):
		return iter(self.children)


class SearchTree():
	def __init__(self, l):
		self.items = sorted(l, key = lambda x: x.upper())
		self.root = Node("", False)
		alpha = []
		for item in self.items:
			self.addItem(item)

	def searchItem(self, item):
		current = self.root
		depth = 1
		while current.children and depth < len(item)+1:
			found = False
			for child in current:
				if item[:depth].upper() == child.content.upper():
					found = True
					current = child
					break
			if not found:
				return current
			depth += 1
		return current

	def addItem(self, item):
		parent = self.searchItem(item)
		if len(parent.content) +1 < len(item):
			for i in range(len(parent.content)+1, len(item)):
				newNode = Node(item[:i], False)
				parent.addChild(newNode)
				parent = newNode
		newNode = Node(item, True)
		parent.addChild(newNode)

	def relateItem(self, item, depth = 10):
		parent = self.searchItem(item)
		related = []
		if parent.visible:
			related.append(parent.content)
		current = parent
		nextNodes = []
		n = 0
		loop = 0
		done = False
		while current and not done:
			for child in current:
				nextNodes.append(child)
				if child.visible:
					related.append(child.content)
					n += 1
				if n > depth:
					done = True
					break
			if loop < len(nextNodes):
				current = nextNodes[loop]
				loop += 1
			else:
				current = None
		return related