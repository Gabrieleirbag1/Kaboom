import subprocess
import shlex
import time

my_log = "my.log"

commands = (
    # Open a new tab and display time and message
    "gnome-terminal --tab -- bash -c \"date 2>&1 | tee " + my_log +
    "; echo foo 2>&1 | tee -a " + my_log + "; exec bash\"",
    # Open a new tab and display time and an error message
    "gnome-terminal --tab -- bash -c \"date 2>&1 | tee -a " + my_log +
    "; whatami 2>&1 | tee -a " + my_log + "; exec bash\"",
    # Open a new tab and display time and the current user
    "gnome-terminal --tab -- bash -c \"date 2>&1 | tee -a " + my_log +
    "; whoami 2>&1 | tee -a " + my_log + "; exec bash\"",
    # Display command results from log
    "cat my.log")

for c in commands:
    subprocess.run(shlex.split(c))
    time.sleep(0.5)