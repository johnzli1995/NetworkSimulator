
# Trying not to use magic numbers
ONE_MS = 1

# EPSILON_DELAY: a small delay, so that the priority queue can sort events
# properly. This delay is used for the time it takes to generate a
# data packet, or the time it takes to process a packet/put it in a buffer
EPSILON_DELAY = 0.001

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
DATA_SIZE = 1024
ACK_SIZE = 64
ROUTING_SIZE = 8