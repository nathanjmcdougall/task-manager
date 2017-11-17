from datetime import datetime

class Task:
	def __init__(self, name, deadline):
		# Name of the task
		self.name = name
		# The task has been started now, as the initialising takes place
		self.start_time = datetime.now()
		# The task is not yet finished
		self.finished = False
		# The deadline as specified by the user
		self.deadline = deadline
		# We haven't yet spend any time on this task
		self.hours_spent = 0

	def time_remaining(self):
		# How much time remains for this task; or negative if we have exceeded the deadline
		return self.deadline - self.start_time

	def finish_task(self):
		# We have finished the task
		self.finished = True
		# We have finished it now
		self.finish_time = datetime.now()

	def spend_hour(self):
		# Increment the number of hours spent counter
		self.hours_spent += 1

def get_time(request):
	while True:
		try:
			time = str(input(request))
			return datetime.strptime(time,"%Y-%m-%d %H:%M")
		except ValueError:
			print("Sorry, that time you entered could not be interpreted as such. PLease use the format [Y-m-d H:M] and try again: ")

deadline = get_time("Please enter the deadline: ")
example_task = Task('Example task', deadline)
print(example_task.time_remaining())
