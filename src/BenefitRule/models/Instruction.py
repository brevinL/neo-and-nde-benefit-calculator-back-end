from django.db import models

class Task(models.Model):
	pass

class Instruction(models.Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="instruction_set")
	order = models.IntegerField()
	description = models.TextField()

class Expression(models.Model):
	instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE, related_name="expression_set")
	description = models.TextField()
	order = models.IntegerField()