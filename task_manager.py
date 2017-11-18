from datetime import datetime as dt, timedelta as td
from shutil import copyfile
import numpy as np
import operator

seconds_per_minute = 60
minutes_per_hour = 60
hours_per_day = 24
days_per_second = 1/(seconds_per_minute*minutes_per_hour*hours_per_day)

########################################################
# File configuration
########################################################

# If this file does not exist, it will not be created.
# You need to make sure this file exists yourself.
task_log_name = ".task_log"

# The name of the backup file
backup_log_name = ".task_log_backup"

# The name of the configuration file
config_name = ".config"

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
	def make_task():
		# Get the name from the user
		name = input("Please enter in the name for this task: ")

		# We use comma spacing for the log file, so remove any from the name.
		name = name.replace(",", "")
		
		# This is a new task, so clearly we haven't spent time on it
		hours_spent = 0;
	
		# We are starting this task now
		start_time = dt.now()

		# Get the deadline from the user
		deadline = get_time("Please enter the deadline for the new task: ")

		# For the moment the finish time is meaningless; use the deadline
		finish_time = deadline

		# We have not finished a task we have just started
		finished = False
		return Task(name, hours_spent, start_time, deadline, finish_time, finished)

	def time_remaining(self):
		# How much time remains for this task; or negative if we have exceeded the deadline
		return self.deadline - dt.now()

	def finish_task(self):
		# We have finished the task
		self.finished = True

		# We have finished it now
		self.finish_time = dt.now()

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
			return dt.strptime(time,"%Y-%m-%d %H:%M")
		except ValueError:
			# Report to the user that the string couldn't be parsed
			print("Sorry, that time you entered could not be interpreted as such. Please use the format [Y-m-d H:M] and try again: ")

########################################################
# Blank out a file
########################################################

def clear_file(file_name):
	# Try to read in the given file
	try:
		f = open(file_name, "w")
	except IOError:
		raise IOError("The specified file could not be opened.")

	# Empty the existing contents of the file
	f.seek(0)
	f.truncate()
	
	# Close the file
	f.close()

	

########################################################
# Read in a data file of tasks
########################################################

def read_tasks():
	# Try to read in the task log file
	try:
		task_file = open(task_log_name, "r")
	except IOError:
		raise IOError("The task log file could not be opened.")

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
			start_time = dt.strptime(start_time,time_format)
			deadline = dt.strptime(deadline,time_format)
			finish_time = dt.strptime(finish_time,time_format)
			finished = (finished == "1")
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
# Write to the data file
########################################################

def log_tasks(task_list):
	# Back up the task log file
	copyfile(task_log_name, backup_log_name)

	# Blank out the file
	clear_file(task_log_name)

	# Open the file
	try:
		task_file = open(task_log_name, "a")
	except IOError:
		raise IOError("The task log file could not be opened.")

	for task in task_list:
		# Convert from strings to the correct ftd.dt.daysormats
		name = task.name
		hours_spent = str(task.hours_spent)
		start_time = dt.strftime(task.start_time,time_format)
		deadline = dt.strftime(task.deadline,time_format)
		finish_time = dt.strftime(task.finish_time,time_format)
		finished = str(int(task.finished))

		# Create the list of each quantity and join into a single comma seperated string
		task_str_list = [name,hours_spent, start_time, deadline, finish_time, finished]
		task_str = ",".join(task_str_list)
		
		# Add the task to the task log file
		task_file.write(task_str+",\n")

	# Close the task log file
	task_file.close()

########################################################
# Determining the recommended tasks
########################################################

def sort_by_priority(task_list):
	# Load in the configuration file
	try:
		config_file = open(config_name, "r")
	except IOError:
		raise IOError("The configuration file could not be opened.")

	# Read in the parameters
	param_str = config_file.read().split(",")
	param = list(map(float,param_str))

	# Convert the parameters to floating point

	# Close the configuration file
	config_file.close()

	# Initialise the totals to zero
	total_deadline_weight = 0
	total_hours_spent = 0
	total_time_weight = 0
	for task in task_list:
		# Get the weighting to account for the time until the deadline
		# This will be normalised by total_deadline_weight later
		task.deadline_weight = np.exp(-abs(task.time_remaining().days+task.time_remaining().seconds*days_per_second))
		print(task.deadline_weight)
		total_deadline_weight += task.deadline_weight
		
		# Add up the number of hours spent so far
		total_hours_spent += task.hours_spent

	for task in task_list:
		# Calculate the weight to account for time spent
		task.time_weight = 1 + abs((task.hours_spent+1)/(total_hours_spent+1)-param[0])

		# Get normalising factor
		total_time_weight += task.time_weight

	for task in task_list:
		# Normalise the deadline weight
		task.deadline_weight /= total_deadline_weight
	
		# Normalise the time weight
		task.time_weight /= total_time_weight
	
		# Weight the weights
		task.priority = task.deadline_weight*param[1] + task.time_weight*(1-param[1])
		

	return sorted(task_list, key=operator.attrgetter('priority'), reverse = True)
		

########################################################
# Actual interface
########################################################

# Read in the log file
try:
	task_list = read_tasks()
except:
	print("Could not read in the log file! It may be corrupted or missing. Exiting...")
	exit()

while True:
	# Query the user as to what they'd like to do:
	print("")
	print("TASK MANAGER:")	
	print("0:		Get the top 5 things to do right now")
	print("1:		Create a new task")
	print("2:		Complete a task")
	print("Anything else:	Exit")
	option = input("Please enter your choice: ")
	print("")

	# Mostly we'll only be interested in the unfinished tasks, so filter them out now
	unfinished_tasks = [task for task in task_list if not task.finished]

	# Priority report: top 5 tasks to do
	if option == "0":
		# Sort the tasks by priority
		unfinished_tasks = sort_by_priority(unfinished_tasks)
		# Print out the top 5
		print("Name			Priority	Time until deadline")
		for task in unfinished_tasks[:5]:
			print(task.name+":		"+str(round(100*task.priority))+"%		"+str(round(task.time_remaining().days+task.time_remaining().seconds*days_per_second,2))+" days")
	# Create a new task
	elif option == "1":
		new_task = Task.make_task()
		task_list.append(new_task)
		print("The task has been successfully created!")
	# Complete a task
	elif option == "2":
		# Display the unfinished tasks for the user to choose from
		print("These are the unfinished taks:")
		task_id = 0
		print("Name			Time until deadline	ID")
		for task in unfinished_tasks:
			print(task.name+":		"+str(round(task.time_remaining().days+task.time_remaining().seconds*days_per_second,2))+" days		"+str(task_id))
			task_id += 1
		# Get the user's choice and mark the task as complete
		while True:
			try:
				task_id = input("Please input the ID of the task you are completeing, or [N] to cancel: ")

				# Allow the option to cancel
				if task_id == "N":
					break

				task_id = int(task_id)
				assert(task_id >= 0 and task_id < len(unfinished_tasks))
				unfinished_tasks[task_id].finished = True
				break
			except:
				print("Sorry, that task ID is not valid. Please try again: ")

	else:
		break
                                                                     
# Write the log file
try:
	log_tasks(task_list)
except:
	print("Could not write to the log file! It may be missing or there may be permission issues. Exiting...")
	exit()
