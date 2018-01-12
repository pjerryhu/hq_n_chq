from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import solver
import time

class ExampleHandler(FileSystemEventHandler):
    def on_created(self, event): # when file is created
        # do something, eg. call your function to process the image
        # print "Got event for file %s" % event.src_path 
        # print event.src_path
        solver.run_solver(event.src_path)

observer = Observer()
event_handler = ExampleHandler() # create event handler
# set observer to use created handler in directory
observer.schedule(event_handler, path='/Users/fanxu/Desktop/Screenshots')
observer.start()

# sleep until keyboard interrupt, then stop + rejoin the observer
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
