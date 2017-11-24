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
backup_task_log_name = ".task_log_backup"

# If this file does not exist, it will not be created.
# You need to make sure this file exists yourself
roster_log_name = ".roster_log"

# The name of the backup file
backup_roster_log_name = ".roster_log_backup"

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
	def schedule_task(name, start_time, deadline):		
		# This is a new task, so clearly we haven't spent time on it
		hours_spent = 0;

		# For the moment the finish time is meaningless; use the deadline
		finish_time = deadline

		# We have not finished a task we have just started
		finished = False

		# Give back the task
		return Task(name, hours_spent, start_time, deadline, finish_time, finished)

	@staticmethod
	def make_task():
		# Get the name from the user
		name = get_name("Please enter in the name for this task: ")

		# We are starting this task now
		start_time = dt.now()

		# Get the deadline from the user
		deadline = get_time("Please enter the deadline for the new task: ")

		# Give back the task
		return shedule_task(name, hours_spent, start_time, deadline, finish_time, finished)

	def time_remaining(self):
		# How many days remain for this task; or negative if we have exceeded the deadline
		time_rem = self.deadline - dt.now()
		return time_rem.days + time_rem.seconds*days_per_second

	def time_elapsed(self):
		# How many days has this task been around?
		time_el = dt.now() - self.start_time
		return time_el.days + time_el.seconds*days_per_second

	def finish_task(self):
		# We have finished the task
		self.finished = True

		# We have finished it now
		self.finish_time = dt.now()

	def spend_hour(self):
		# Increment the number of hours spent counter
		self.hours_spent += 1

########################################################
# Roster class
########################################################

class Roster:
	def __init__(self, name, next_start_time, duration, period):
		# Populate the Roster's properties
		self.name = name
		self.next_start_time = next_start_time
		self.duration = duration
		self.period = period

	@staticmethod
	def make_roster():
		# Get the name from the user
		name = get_name("Please enter in the name for this task roster: ")

		# Get the first start time from the user
		first_start_time = get_time("Please enter the first start time: ")

		# Get the period
		period = get_timedelta("Please enter the number of days between each task instance: ")

		# Get the duration from the user
		duration = get_timedelta("Please enter in the number of days allowed for each task: ")

		# Give back the task
		return Roster(name, first_start_time, duration, period)

	def check_roster(self):
		# If the task's start time has elapsed, schedule the task
		if self.next_start_time <= dt.now():
			# The deadline occurs a duration worth of time after the start
			deadline = self.next_start_time + self.duration
			
			# Schedule the task
			new_task = Task.schedule_task(self.name, self.next_start_time, deadline)

			# Prepare the enxt start time
			self.next_start_time += self.period

			# Report the new task
			return new_task
		else:
			return False

	@staticmethod
	def check_all_rosters(roster_list, task_list):
		for roster in roster_list:
			new_task = roster.check_roster()
			if new_task:
				task_list.append(new_task)
		
		return task_list
		
			

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
			print("Sorry, that time you entered could not be interpreted as such. Please use the format [YYYY-MM-DD HH:MM] and try again: ")

########################################################
# Input time intervals from the user
########################################################

def get_timedelta(request):
	# Keep trying until we properly parse the input
	while True:
		try:
			# Get the time interval in days from the user
			time_interval = float(input(request))

			# Check it is positive
			assert(time_interval > 0)				

			# Return the interval as a timedelta
			return td(time_interval)
		except ValueError:
			# Report to the user that the string couldn't be parsed
			print("Sorry, that number of days you entered could not be interpreted as such. Please ensure it is a valid positive number and try again: ")

########################################################
# Input names from the user
########################################################

def get_name(request):
	# Query the user
	name = input(request)	

	# We use comma spacing for the log file, so remove any from the name.
	return name.replace(",", "")
	

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
# Read in the data file of tasks
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
			raise ValueError("The task log could not be parsed.")

		# Create the task for this line
		task = Task(name, hours_spent, start_time, deadline, finish_time, finished)

		# Append the task to our task list
		task_list.append(task)

	# Close the file
	task_file.close()

	# Return the list of tasks
	return task_list

########################################################
# Read in the data file of rosters
########################################################

def read_rosters():
	# Try to read in the roster log file
	try:
		roster_file = open(roster_log_name, "r")
	except IOError:
		raise IOError("The roster log file could not be opened.")

	# We are going to store rosters in a list
	roster_list = []

	# Each line in the file corresponds to a task
	for roster_str in roster_file:
		# Split each line using spaces into a list
		roster_str_list = roster_str.split(",")

		# Identify which elements in the list are which
		name = roster_str_list[0]
		next_start_time = roster_str_list[1]
		duration = roster_str_list[2]
		period = roster_str_list[3]

		# Convert from strings to the correct formats
		try:
			next_start_time = dt.strptime(next_start_time,time_format)
			duration = td(float(duration))
			period = td(float(period))
		except ValueError:
			raise ValueError("The roster log could not be parsed.")

		# Create the roster for this line
		roster = Roster(name, next_start_time, duration, period)

		# Append the task to our task list
		roster_list.append(roster)

	# Close the file
	roster_file.close()

	# Return the list of tasks
	return roster_list

########################################################
# Write to the data files
########################################################

def update_logs(task_list, roster_list):
	# Back up the task log file
	copyfile(task_log_name, backup_task_log_name)

	# Blank out the file
	clear_file(task_log_name)

	# Open the file
	try:
		task_file = open(task_log_name, "a")
	except IOError:
		raise IOError("The task log file could not be opened.")

	for task in task_list:
		# Convert from strings to the correct formats
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

	# Back up the roster log file
	copyfile(roster_log_name, backup_roster_log_name)

	# Blank out the file
	clear_file(roster_log_name)

	# Open the file
	try:
		roster_file = open(roster_log_name, "a")
	except IOError:
		raise IOError("The roster log file could not be opened.")

	for roster in roster_list:
		# Convert from strings to the correct formats
		name = roster.name
		next_start_time = dt.strftime(roster.next_start_time,time_format)
		duration = str(roster.duration.days+roster.duration.seconds*days_per_second)
		period = str(roster.period.days+roster.period.seconds*days_per_second)

		# Create the list of each quantity and join into a single comma seperated string
		roster_str_list = [name, next_start_time, duration, period]
		roster_str = ",".join(roster_str_list)

		# Add the roster to the roster log file
		roster_file.write(roster_str+",\n")

	# Close the roster log file
	roster_file.close()

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
	
	# Convert the parameters to floating point
	param = list(map(float,param_str))

	# Close the configuration file
	config_file.close()

	# Initialise the totals to zero
	total_deadline_weight = total_frac_time = total_hours_spent = total_time_weight = total_time_elapsed = total_util_weight = 0

	# Find the next deadline
	next_deadline = task_list[0].time_remaining()
	next_task = task_list[0]
	for task in task_list:
		if task.time_remaining() < next_deadline:
			next_deadline = task.time_remaining()
			next_task = task

	# Find the deadline weight
	for task in task_list:
		task.deadline_weight = np.exp(-param[0]*abs(task.time_remaining()/next_deadline))
		total_deadline_weight += task.deadline_weight
	# Normalise the deadline weight
	for task in task_list:
		task.deadline_weight /= total_deadline_weight

	# Get the fraction of the time until the next deadline that ought to be spent on this task
	if next_deadline < 0:
		for task in task_list:
			task.frac_time = 0

		next_task.frac_time = 1
	else:
		for task in task_list:
			task.frac_time = next_deadline / task.time_remaining()
			total_frac_time += task.frac_time
		for task in task_list:
			task.frac_time /= total_frac_time

	# Find the fraction-time-spent weight:
	for task in task_list:
		total_hours_spent += task.hours_spent
	for task in task_list:
		task.time_weight = task.frac_time - (task.hours_spent+param[1])/(total_hours_spent+param[2])
		if task.time_weight < 0:
			task.time_weight = 0
		total_time_weight += task.time_weight
	for task in task_list:
		task.time_weight /= total_time_weight

	# Find the time utilisation weight:
	for task in task_list:
		task.util_weight = ( task.hours_spent + param[3] ) / ( hours_per_day*task.time_elapsed() )
		total_util_weight += task.util_weight
	for task in task_list:
		task.util_weight /= total_util_weight
		
	
	# Weight the weights
	for task in task_list:
		task.priority = task.deadline_weight*param[4] + task.time_weight*param[5] + task.util_weight*(1-param[4]-param[5])

	return sorted(task_list, key=operator.attrgetter('priority'), reverse = True)
		

########################################################
# Actual interface
########################################################

# Read in the log files
try:
	task_list = read_tasks()
	roster_list = read_rosters()
except:
	print("Could not read in one of the log files! Either may be corrupted or missing. Exiting...")
	exit()

while True:
	# Check if any rostered tasks need scheduling
	task_list = Roster.check_all_rosters(roster_list, task_list)

	# Query the user as to what they'd like to do:
	print("")
	print("TASK MANAGER:")	
	print("0:		Get the top 5 things to do right now")
	print("1:		Create a new task")
	print("2:		Complete a task")
	print("3:		Create a new task roster")
	print("4:		Record an hour of a task")
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
			print(task.name+":		"+str(round(100*task.priority))+"%		"+str(round(task.time_remaining(),2))+" days")
	# Create a new task
	elif option == "1":
		new_task = Task.make_task()
		task_list.append(new_task)
		print("The task has been successfully created!")
	# Complete a task
	elif option == "2":
		# Display the unfinished tasks for the user to choose from
		print("These are the unfinished tasks:")
		task_id = 0
		print("Name			Time until deadline	ID")
		for task in unfinished_tasks:
			print(task.name+":		"+str(round(task.time_remaining(),2))+" days		"+str(task_id))
			task_id += 1
		# Get the user's choice and mark the task as complete
		while True:
			try:
				task_id = input("Please input the ID of the task you are completeing, or [N] to cancel: ")

				# Allow the option to cancel
				if task_id == "N":
					break

				# Otherwise check the ID is valid and if so mark the task as finished
				task_id = int(task_id)
				assert(task_id >= 0 and task_id < len(unfinished_tasks))
				unfinished_tasks[task_id].finished = True
				break
			except:
				print("Sorry, that task ID is not valid. Please try again: ")
	# Create a new task roster
	elif option == "3":
		new_roster = Roster.make_roster()
		roster_list.append(new_roster)
		print("The task roster has been successfully created!")
	# Complete an hour of a task
	# Complete a task
	elif option == "4":
		# Display the unfinished tasks for the user to choose from
		print("These are the unfinished tasks:")
		task_id = 0
		print("Name			Time until deadline	ID")
		for task in unfinished_tasks:
			print(task.name+":		"+str(round(task.time_remaining(),2))+" days		"+str(task_id))
			task_id += 1
		# Get the user's choice and increment the hours-worked counter
		while True:
			try:
				task_id = input("Please input the ID of the task you are working an hour on, or [N] to cancel: ")

				# Allow the option to cancel
				if task_id == "N":
					break

				# Otherwise check the ID is valid and if so mark the task as finished
				task_id = int(task_id)
				assert(task_id >= 0 and task_id < len(unfinished_tasks))
				unfinished_tasks[task_id].hours_spent += 1
				break
			except:
				print("Sorry, that task ID is not valid. Please try again: ")
	else:
		break
                                                                     
# Write the log file
try:
	update_logs(task_list, roster_list)
except:
	print("Could not write to the log files! Either may be missing or there may be permission issues. Exiting...")
	exit()
