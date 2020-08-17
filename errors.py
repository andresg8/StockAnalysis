class BadTickerException(Exception):
	def __init__(self, ticker):
		super().__init__()
		self.ticker = ticker