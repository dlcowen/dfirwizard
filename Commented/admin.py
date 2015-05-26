#!/usr/bin/env python
# -*- coding: utf-8; more: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vim: fileencoding=utf-8 tabstop=4 expandtab shiftwidth=4

# (C) COPYRIGHT © Preston Landers 2010
# Released under the same license as Python 2.6.5
# modified for Part 5 of the series 

import sys, os, traceback, types

# Function isUserAdmin checks to see if OS is Windows and if the current thread has admin privileges
def isUserAdmin():

	# Using the name function in OS checking to see if this is a Windows NT system
	if os.name == 'nt':
		import ctypes
		# WARNING: requires Windows XP SP2 or higher
		try:
			return ctypes.windll.shell32.IsUserAnAdmin()
		except:
			traceback.print_exc()
			print "Admin check failed, assuming not an admin."
			return False
	elif os.name == 'posix':
		# Check for root on Posix (*nix?)
			return os.getuid() == 0
	else:
		raise RuntimeErrror, "Unsupported operating system for this module: %s" % (os.name,)
		
# End isUserAdmin -----------------------------------------------------------------------------------------------------------------

# Function runAsAdmin restarts the script with admin privileges, does not kill the already running script
def runAsAdmin(cmdLine=None, wait=True):
	# If the OS is not a Windows NT OS raise an error that this function will not run
	if os.name != 'nt':
		raise RuntimeError, "This function is only implemented on Windows"
		
	import win32api, win32con, win32event, win32process
	# Importing specific functions allow functions to be called without full package names
	from win32com.shell.shell import ShellExecuteEx
	from win32com.shell import shellcon
	
	# Store the path to the python interpreter in use
	python_exe = sys.executable
	
	if cmdLine is None:
		# sys.argv is the executable currently running, here we are making a tuple/list with interpreter and script being run
		cmdLine = [python_exe] + sys.argv
		# if cmdLine isn't a list or tuple it will not contain the info we need so we will raise an error
	elif type(cmdLine) not in (types.TupleType,types.ListType):
		raise ValueError, "cmdLine is not a sequence."
	# Pull out the first value in cmdLine and save it as a string giving the python interpreter path for later use
	cmd = '"%s"' % (cmdLine[0],)
	# XXX TODO: isn't there a function or something we can call to massage command line params
	# params stores the running script name as a string for later use, if multiple params passed in will be joined together
	params = " ".join(['"%s"' % (x,) for x in cmdLine[1:]])
	cmdDir = ''
	# This determines if we want to show command line or not, since not GUI we don't want to hide the window
	showCmd = win32con.SW_SHOWNORMAL
	#showCmd = win32con.SW_HIDE
	lpVerb = 'runas' # causes UAC elevation prompt
	
	# ShellExecute() doesn't seem to allow us to fetch the PID or handle
	# of the process so we can't get anything useful from it.  Therefore
	# the more complex ShellExecuteEx() must be used.
	
	# procHandle = win32api.ShellExecute(0, lpVerb, cmd, params, cmdDir, showCmd)
	
	procInfo = ShellExecuteEx(nShow=showCmd,
											# This prevents the parent process from exiting
											fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
											lpVerb=lpVerb,
											lpFile=cmd,
											lpParameters=params)
	
	# Waiting on the admin prompt to pop up before moving on if wait is set to true
	if wait:
		procHandle = procInfo['hProcess']
		obj = win32event.WaitForSingleObject(procHandle, win32event.INFINITE)
		rc = win32process.GetExitCodeProcess(procHandle)
		#print "Process handle %s returned code %s" % (procHandle, rc)
	else:
		rc = None
		
	return rc
# End of runAsAdmin function ---------------------------------------------------------------------------------------------
	
if __name__ == "__main__":
	sys.exit(test())