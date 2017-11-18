from datetime import datetime

########################################################
# Log file configuration
########################################################

# If this file does not exist, it will not be created.
# You need to make sure this file exists yourself.
task_log_name = ".task_log"

# The datetime format used in the logfile.
time_format = "%Y-%m-%d %H:%M:%S.%f"


########################################################
# Task class
########################################################

class Task:
	def __init__(self, name, hours_spent, start_time, deadline, finish_time, finished):
		# Populate the Task's properties
		self.name = name
		self.hours_spent = hours_spent
		self.start_time = start_time
		self.deadline = deadline
		self.finish_time = finish_time
		self.finished = finished

	@staticmethod
	def make_task(name, deadline):
		# This is a new task, so clearly we haven't spent time on it
		hours_spent = 0;
	
		# We are starting this task now
		start_time = datetime.now()

		# For the moment the finish time is meaningless; use the deadline
		finish_time = deadline

		# We have not finished a task we have just started
		finished = False
		return Task(name, hours_spent, start_time, deadline, finish_time, finished)

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

########################################################
# Input times from the user
########################################################

def get_time(request):
	# Keep trying until we properly parse the input
	while True:
		try:
			# Get the time from the user
			time = str(input(request))

			# Return time if successfully parsed
			return datetime.strptime(time,"%Y-%m-%d %H:%M")
		except ValueError:
			# Report to the user that the string couldn't be parsed
			print("Sorry, that time you entered could not be interpreted as such. PLease use the format [Y-m-d H:M] and try again: ")

########################################################
# Read in a data file of tasks
########################################################

def read_tasks(file_name):
	# Try to read in the task file
	try:
		task_file = open(file_name, 'r')
	except IOError:
		raise IOError("The specified file could not be opened.")

	# We are going to store tasks in a list
	task_list = []

	# Each line in the file corresponds to a task
	for task_str in task_file:
		# Split each line using spaces into a list
		task_str_list = task_str.split(",")

		# Identify which elements in the list are which
		name = task_str_list[0]
		hours_spent = task_str_list[1]
		start_time = task_str_list[2]
		deadline = task_str_list[3]
		finish_time = task_str_list[4]
		finished = task_str_list[5]

		# Convert from strings to the correct formats
		try:
			hours_spent = int(hours_spent)
			start_time = datetime.strptime(start_time,time_format)
			deadline = datetime.strptime(deadline,time_format)
			finish_time = datetime.strptime(finish_time,time_format)
			finished = bool(hours_spent)
		except ValueError:
			raise ValueError("The opened file could not be parsed.")

		# Create the task for this line
		task = Task(name, hours_spent, start_time, deadline, finish_time, finished)

		# Append the task to our task list
		task_list.append(task)

	# Close the file
	task_file.close()

	# Return the list of tasks
	return task_list

########################################################
# Testing section
########################################################

try:
	task_list = read_tasks(task_log_name)
except:
	print("Could not read in the log file! It may be corrupted or missing. Exiting...")
	exit()

example_task = task_list[0]
print(example_task.deadline)
