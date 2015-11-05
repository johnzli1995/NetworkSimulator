#TODO: Add some stuff to the classes...
import Queue

# four conversion constants:
#   KB_TO_B: converts kilobytes to bytes.
#   B_to_b: converts bytes to bits
#   MB_TO_KB: converts megabytes to kilobytes
#   s_to_ms: converts seconds to milliseconds
KB_TO_B = 1024
B_to_b = 8
MB_TO_KB = 1024
s_to_ms = 1000

# some static constants:
#   DATA_SIZE: the size of a data packet (1024B)
#   ACK_SIZE: the size of an acknowledgment packet (64B)
DATA_SIZE = 1024
ACK_SIZE = 64

class bufferQueue:
    def __init__(self):
        self.items = []

    def empty(self):
        return self.items == []

    def put(self, item):
        self.items.insert(0,item)

    def get(self):
        if self.empty():
            raise BufferError("Tried to get element from empty bufferQueue")
        return self.items.pop()

    def size(self):
        return len(self.items)

    def peek(self):
        if self.empty():
            raise BufferError("Tried to peek element from empty bufferQueue")
        return self.items[len(self.items) - 1]

    def get_most_recent(self):
        return 0

    def qsize(self):
        return len(self.items)


class Device:

    """ Instantiating the Device.
     
    :param deviceID: Unique name by which the device is identified.
    :type deviceID: str
    :param queue: a Queue data structure which keeps track of received packets for host, and moving packets for routers.
    :type queue: Queue.Queue()
    :param links: Stores all attached links to the device
    :type links: Array of links
    :returns: void
    """
    def __init__(self, deviceID):
        self.deviceID = deviceID
        self.links = []
        self.queue = Queue.Queue()

    # attach a link
    def attachLink(self, link):
        # should be a for loop
        self.links.append(link)

    # we can think of this as a "queue" of packets currently being sent
    # enqueue a packet, send from
    # a particular link, into the device's 'receive queue', so that it
    # can process packets as they arrive
    def sending(self, link, packet):
        self.queue.put(packet)
        link.incrRate(packet)

    # the actual processing of the sent packets
    # we have to return the packet, so that we can update the total
    # amount of data sent
    def receiving(self, link):
        packet = self.queue.get()
        print "Received data of type: " + packet.type
        link.decrRate(packet)
        return packet


class Router(Device):

    # This will set a created routing table into the router's table.
    # The table will be decided using Bellman Ford.
    def createTable(self, table):
        self.table = table

    # Since I made the links hold the actual devices, instead of just
    # host numbers, the devices will be made separately first,
    # then the links, then the devices will attach the links.

class Host(Device):

    def getLink(self):
        return self.links[0]

    # logs sending packet
    # def logSend

    #processes the receiving packet
    def receiving(self):
        packet = Device.receiving(self, self.getLink())
        if packet.type == "acknowledgment":
            # do nothing
            # decrease the current link rate
            pass
        elif packet.type == "data":
            # send an acknowledgment packet
            # TODO
            pass
        return packet

class Flow:
    """ Instantiating a Flow
    :param flowID: ID to identify flow
    :type flowID: string
    :param src: Address to source of the flow.
    :type src: Host
    :param dest: Address to destination of flow.
    :type dest: Host
    """
    def __init__(self, flowID, src, dest, data_amt, flow_start):
        self.flowID = flowID
        self.src = src
        self.dest = dest
        self.data_amt = data_amt
        self.flow_start = flow_start
        # self.sendTime = sendTime

    # This method will generate data packets for the flow.
    def generateDataPacket(self):
        packet = Packet(self.src, self.dest, DATA_SIZE, "data")
        return packet

    # This method will generate acknowledgment packets for the flow.
    def generateAckPacket(self):
        packet = Packet(self.src, self.dest, ACK_SIZE, "acknowlegment")
        return packet

class Link:

    """ Instantiating a Link
    
    :param linkID: Indicates what link we're referencing
    :type linkID: string
    :param rate: Indicates how fast packets are being sent
    :type rate: Integer
    :param delay: How much delay there is for packet to arrive to destination
    :type delay: Integer
    :param buffer_size: Size of buffer. We crate the buffer from the Python queue library.
    :type buffer_size: Integer
    :param device1: One device connected to the link
    :type device1: Device
    :param device2: The other device connected to the link
    :type device2: Device
    """

    def __init__(self, linkID, rate, delay, buffer_size, device1, device2):
        self.linkID = linkID
        self.rate = rate
        self.delay = delay
        self.buffer_size = buffer_size

        # initially, the queue has no packets in it.
        self.current_buffer = 0

        #initially, the link isn't sending any packets
        self.current_rate = 0

        self.linkBuffer = bufferQueue()
        self.device1 = device1
        self.device1.attachLink(self)
        self.device2 = device2
        self.device2.attachLink(self)

    # the rate is given in Mbps. We have to convert that to bytes per sec
    # so we know many packets (given in bytes) can fit into that rate
    def rateInBytes(self, rate):
        return self.rate * MB_TO_KB * KB_TO_B / B_to_b;

    # since the buffer_size is in KB, and packets are in bytes,
    # just convert buffer_size into bytes as well
    def bufferInBytes(self, buffer_size):
        return buffer_size * KB_TO_B;

    # is the buffer full, if we add the new packet?
    # we just check if the current data in the buffer and the to-be-added
    # packet will exceed the buffer capacity
    def isFullWith(self, added_packet):
        return (self.bufferInBytes(self.buffer_size) <
            self.current_buffer + added_packet.data_size)

    # is the link rate at capacity, if we add the new packet?
    def rateFullWith(self, added_packet):
        return (self.rateInBytes(self.rate) <
                self.current_rate + added_packet.data_size)

    # sends the packet off to the destination
    def sendPacket(self, packet):
        if not self.rateFullWith(packet):
            print "sending..."
            packet.dest.sending(self, packet)

            # have to dequeue this packet now
            self.popFromBuffer()
            return True
        return False

    # this packet has been successfully sent, so the link
    # should have more capacity
    def decrRate(self, packet):
        self.current_rate -= packet.data_size

    # this packet is currently sending, taking up capacity
    # in the link rate
    def incrRate(self, packet):
        self.current_rate += packet.data_size

    def bufferEmpty(self):
        return self.linkBuffer.empty()

    def peekFromBuffer(self):
        return self.linkBuffer.peek()

    # This will pop off a packet from the linked buffer. I will then return
    # it so that it could be sent.
    def popFromBuffer(self):
        print "popped off buffer!"
        popped_elem = self.linkBuffer.get()
        self.current_buffer -= popped_elem.data_size
        return popped_elem

    # This will put in a packet into the queue.
    def putIntoBuffer(self, packet):
        if not self.isFullWith(packet):
            print "putting into buffer..."
            self.linkBuffer.put(packet)
            self.current_buffer += packet.data_size
            return True
        print "unable to put in buffer"
        return False

    # Method to calculate round trip time
    # (TBH, links themselves manage delay? I thought that was something
    #  we calculate...)
    def roundTripTime(self,rate, delay):
        #TODO
        pass

class Packet:

    """ Instantiating a Packet
    :param src: Indicates the source of the sending
    :type src: string(?)
    :param dest: Indicates the destination of the sending
    :type dest: string(?)
    :param type: Either an actual data packet, or an acknowledgment packet. We shouldn't really care about what is actually is in the data
    :type type: Packet(?)
    :param data_size: data in BYTES.
    :type data_size: Integer
    """
    def __init__(self, src, dest, data_size, type):
        self.src = src
        self.dest = dest
        self.data_size = data_size
        self.type = type

