from searchTree import SearchTree
import pickle
w = pickle.load(open("res/searchables.p", 'rb'))
d = pickle.load(open("res/crossMark4.p", 'rb'))
st = SearchTree(w)

##for child in st.root.children:
##  print(child)


'''
x = st.root.children
print(len(x))
y = x[20]
z = x[1]
4print(y, z)
a = y.children[0]
b = y.children[1]
print(a,b)

def depthFirst(node):
  currentNode = node
  nextNode = node[0]
  print(currentNode)
  while nextNode:
    print(nextNode)
    nextNode = nextNode[0]



test = ["A", "AA", "AAA", "B", "BB", "BBB"]
testTree = SearchTree([])
for i in test:
  testTree.addItem(i)
  print(testTree.root)
  #for child in testTree.root:
  #  print(child)
  #x = input()

#depthFirst(testTree.root)
'''
