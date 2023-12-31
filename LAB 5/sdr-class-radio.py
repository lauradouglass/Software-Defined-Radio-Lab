# Copyright 2018-2022 Drexel University
# Author: Geoffrey Mainland <mainland@drexel.edu>

import asyncio
from concurrent.futures import CancelledError
import logging
import random
import time

import numpy as np

import dragonradio
import dragonradio.radio

class MyRadio(dragonradio.radio.Radio):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def configureSimpleMACSchedule(self):
        """Set a simple static MAC schedule."""
        nchannels = len(self.channels)
        nodes = sorted(list(self.radionet.nodes))

        sched = self.pureTDMASchedule(nodes)

        logging.debug("TDMA schedule: %s", sched)

        self.installMACSchedule(sched)

    def pureTDMASchedule(self, nodes):
        """Create a pure TDMA schedule that gives each node a single slot.

        Args:
            nodes: The nodes

        Returns:
            A schedule consisting of a 1 X nslots array of node IDs.
        """
        nslots = len(nodes)
        sched = np.zeros((1, nslots), dtype=int)

        for i in range(0, len(nodes)):
            sched[0][i] = nodes[i]

        return sched

    async def frequencyHop(self):
        try:
            while True:
                # Uncomment to set frequency to 1.31 GHz every second. Please do
                # something more intelligent!
                self.frequency = 1.31e9
                # Sleep for 1 second
                await asyncio.sleep(1)
        except CancelledError:
            pass

def main():
    # Create configuration and set defaults
    config = dragonradio.radio.Config()

    # Default options
    config.mac = 'tdma'
    config.num_nodes = 2

    # Default options specific to SDR class
    config.tx_antenna = 'TX/RX'
    config.rx_antenna = 'RX2'
    config.tx_gain = 25
    config.rx_gain = 25
    config.auto_soft_tx_gain = 100
    config.channel_bandwidth = 500e3
    config.bandwidth = 500e3
    config.aloha_prob = 1/10
    config.slot_size = 0.050

    # Create command-line argument parser
    parser = config.parser()

    # Parse arguments
    try:
        parser.parse_args(namespace=config)
    except SystemExit as err:
        return err.code

    # Set up logging
    logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
                        level=config.loglevel)

    # If a log directory is set, log packets and events
    if config.log_directory:
        config.log_sources += ['log_recv_packets', 'log_sent_packets', 'log_events']

    # Create the radio
    radio = MyRadio(config, config.mac)

    # Start frequency hopping task
    radio.createTask(radio.frequencyHop(),
                     name='frequency hop')

    # Run the radio
    return radio.start()

if __name__ == '__main__':
    main()

