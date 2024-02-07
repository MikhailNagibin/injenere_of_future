import threading
import time

print((~18 | (132 >> 2)) & (86 << 1))
def print_numbers():
    for i in range(5):
        time.sleep(1)
        print(f"Number: {i}")

def print_letters():
    for letter in 'ABCDE':
        time.sleep(1)
        print(f"Letter: {letter}")

# Create two threads
threads = []
threads.append(threading.Thread(target=print_numbers))
threads.append(threading.Thread(target=print_letters))

# Start the threads
threads[0].start()
threads[1].start()

time.sleep(2)
del threads[0]

# Wait for both threads to finish
threads[0].join()
# threads[1].join()

print("Main program finished.")
