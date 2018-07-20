class Instruction(object):
	description = ''
	expressions = []

	def __init__(self, description, expressions):
		self.description = description
		self.expressions = expressions

	def __eq__(self, other):
		return self.description == other.description and bool(set(self.expressions) == set(other.expressions))

	def __repr__(self):
		return f'Instruction(description={self.description}, expressions={self.expressions})'