from django.db import models

class Task(models.Model):
	pass

class Instruction(models.Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="instruction_set")
	order = models.IntegerField()
	description = models.TextField()

	class Meta:
		unique_together = (("task", "order"),) 

	def __eq__(self, other):
		if(self.order == other.order and self.description == other.description):
			return True
		return False

	def __str__(self):
		return f'description = {self.description}; order = {self.order}'

class Expression(models.Model):
	instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE, related_name="expression_set")
	description = models.TextField()
	order = models.IntegerField()

	class Meta:
		unique_together = (("instruction", "order"),) 

	def __eq__(self, other):
		if(self.order == other.order and self.description == other.description):
			return True
		return False

	def __str__(self):
		return f'description = {self.description}; order = {self.order}'