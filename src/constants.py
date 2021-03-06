
# Queue delay for sending a packet.
QUEUE_DELAY = 1

# Alpha constant used for TCP-FAST congestion control.
alpha = 20

# constant that tells when to update the window size
UPDATE_WINDOW_TIME = 20

# Instead of logging every event, just log once in a discrete time interval.
# Currently set to 100ms.
LOG_TIME_INTERVAL = 0.1

# EPSILON_DELAY: a small delay, so that the priority queue can sort events
# properly. This delay is used for the time it takes to generate a
# data packet and putting/sending into buffers
EPSILON_DELAY = 0.001

# TIME_DELAY: A small delay that occurs if there is a timeout, and we need to resend.
TIME_DELAY = 500

# four conversion constants:
#   KB_TO_B: converts kilobytes to bytes.
#   B_to_b: converts bytes to bits
#   MB_TO_KB: converts megabytes to kilobytes
#   s_to_ms: converts seconds to milliseconds
KB_TO_B = 1024
B_to_b = 8
MB_TO_KB = 1024
s_to_ms = float(1000)

# some static constants:
#   DATA_SIZE: the size of a data packet (1024B)
#   ACK_SIZE: the size of an acknowledgment packet (64B)
#   ROUTING_SZIE: the size of routing packet (8B) (chosen to be small to avoid potential congestion problems)
DATA_SIZE = 1024
ACK_SIZE = 64
ROUTING_SIZE = 8

# For use when calculating routing tables. Equivalent to 100s delay 
ROUTING_INF = 100000

# How often we use dynamic routing. Every 5 seconds
REROUT_TIME = 5000
