import Queue
import datetime
import time
from classes import *

# Trying not to use magic numbers
ONE_MS = 1

class Event:
    """Events are enqueued into the Simulator priority queue by their time. Events
    have a type (PUT, SEND, RECEIVE, GENERATEACK, GENERATEPACK) describing what is
    done to the packet. Each type of event has an associated network handler
    (Link, Device, Flow, respectively).
    """

    def __init__(self, packet, EventHandler, EventType, EventTime, flow):
        """ This will initialize an event.

        :param packet: The packet associated with the event.
        :type packet: Packet/None (None for GENERATE...)

        :param EventHandler: Object associated with event request.
        :type EventHandler: Device, Link, or None

        :param EventType: The type of event that will be sent.
        :type EventType: str

        :param EventTime: The time of the particular event, in milliseconds.
        :type EventTime: int

        EventType               EventHandler        Packet
        PUT                     (Link, Device)
        SEND                    (Link, Device)      None
        RECEIVE                 Device
        GENERATEACK             None                None
        GENERATEPACK            None                None

        """

        self.packet = packet
        self.handler = EventHandler
        self.type = EventType
        self.time = EventTime

        self.flow = flow

    def __cmp__(self, other):
        """Ordering by time.

        :param other: The other event we're comparing with.
        :type other: Event
        """
        return cmp(self.time, other.time)


class Simulator:
    # TODO
    def __init__(self, network):
        """ This will initialize the simulation with a Priority Queue
        that sorts based on time.

        :param network: Network system parsed from json
        :type network : Network
        """
        self.q = Queue.PriorityQueue()
        self.network = network

        # file for logging
        self.linkRateLog = open('linkRateLog.txt', 'w')
        self.bufferLog = open('bufferLog.txt', 'w')
        self.packetLog = open('packetLog.txt', 'w')
        self.flowRateLog = open('flowRateLog.txt', 'w')
        self.windowLog = open('windowLog.txt', 'w')
        self.delayLog = open('delayLog.txt', 'w')

        self.counter = 0

    def insertEvent(self, event):
        """ This will insert an event into the Priority Queue.

        :param event: This is the event we're adding into the queue.
        :type event: Event
        """
        self.q.put(event)

    def done(self):
        self.linkRateLog.close()
        self.bufferLog.close()
        self.packetLog.close()
        self.flowRateLog.close()
        self.windowLog.close()
        self.delayLog.close()

    def processEvent(self):
        """Pops and processes event from queue."""

        if(self.q.empty()):
            print "No events in queue."
            return

        event = self.q.get()

        print "Popped event type: ", event.type
        if event.type == "PUT":
            # Tries to put packet into link buffer
            # This happens whenever a device receives a packet.

            assert(isinstance(event.handler[0], Link))
            assert(isinstance(event.handler[1], Device))
            link = event.handler[0]
            device = event.handler[1]

            if not link.rateFullWith(event.packet):
                device.sendToLink(link, event.packet)
                newEvent = Event(None, (link, device), "SEND", event.time, event.flow)
                self.insertEvent(newEvent)

        elif event.type == "SEND":
            # Processes a link to send.
            assert(isinstance(event.handler[0], Link))
            assert(isinstance(event.handler[1], Device))
            link = event.handler[0]
            device = event.handler[1]

            # If you can send the packet, we check what buffer is currently in action.
            # If dev1->dev2, then we pop from device 1.
            # Else, we pop from device 2.
            # If we can't pop, then we call another send event 1 ms later.

            packet = link.sendPacket(device)
            if packet:
                print packet.type
                if(device == link.device1):
                    newEvent = Event(packet, link.device2, "RECEIVE", event.time +
                                     link.delay, event.flow)
                    self.insertEvent(newEvent)
                else:
                    newEvent = Event(packet, link.device1, "RECEIVE", event.time +
                                     link.delay, event.flow)
                    self.insertEvent(newEvent)

                # log the link rate. Log these in seconds, and in Mbps
                # don't capture every single data point we generate:
                # otherwise our plot has too many data points
                self.linkRateLog.write(str(event.time / s_to_ms)
                        + " " + str(link.getLinkRate()) + "\n")

            else:
                newEvent = Event(None, (link, device), "SEND", event.time + ONE_MS, event.flow)
                self.insertEvent(newEvent)

        elif event.type == "RECEIVE":
            # Processes a host/router action that would receive things.
            assert(isinstance(event.handler, Device))

            # Router.
            if isinstance(event.handler, Router):
                router = event.handler
                newLink = router.transfer(event.packet)

                newEvent = Event(event.packet, (newLink, router), "PUT", event.time, event.flow)
                self.insertEvent(newEvent)

            # Host

            elif isinstance(event.handler, Host):
                if(event.packet.type == "DATA"):
                    host = event.handler
                    host.receive(event.packet)

                    newEvent = Event(event.packet, None, "GENERATEACK", event.time, event.flow)
                    self.insertEvent(newEvent)
                else:
                    ########################################
                    ####### TODO: Acknowledgement got ######
                    ########################################

                    host = event.handler
                    host.receive(event.packet)


                    # boolean: which tells us whether window is completed or not
                    sendMore = event.flow.receiveAcknowledgement(event.packet)

                    # IF SO,
                    #######################################
                    ##### Push in new GENERATEPACKS... ####
                    #######################################

                    if(sendMore):
                        for i in range(event.flow.window_size):
                            newEvent = Event(None, None, "GENERATEPACK", event.time, event.flow)
                            self.insertEvent(newEvent)


        elif event.type == "GENERATEACK":
            # Processes a flow to generate an ACK.

            # Generate the new Ack Packet
            ackPacket = event.flow.generateAckPacket(event.packet)
            host = ackPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(ackPacket, (link, host), "PUT", event.time + host.PUT_INTO_BUFFER_TIME, event.flow)
            self.insertEvent(newEvent)


        elif event.type == "GENERATEPACK":
            # Processes a flow to generate a regular data packet.

            # Generate the new packet.
            newPacket = event.flow.generateDataPacket()

            if(newPacket == None):
                return
            host = newPacket.src
            link = host.getLink()

            # Send the event to put this packet onto the link.
            newEvent = Event(newPacket, (link, host), "PUT", event.time + host.PUT_INTO_BUFFER_TIME, event.flow)
            self.insertEvent(newEvent)


