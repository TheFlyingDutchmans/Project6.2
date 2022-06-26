#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Top Block
# GNU Radio version: 3.8.5.0

from ast import parse
from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import AISTX
import osmosdr
import time
from optparse import OptionParser


class top_block(gr.top_block):

    def __init__(self, payload):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2e6
        self.channel_select = channel_select = 2
        self.bit_rate = bit_rate = 9600

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(samp_rate)
        self.osmosdr_sink_0.set_center_freq(161975e3, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(20, 0)
        self.osmosdr_sink_0.set_if_gain(20, 0)
        self.osmosdr_sink_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.digital_gmsk_mod_0_0 = digital.gmsk_mod(
            samples_per_symbol=int(samp_rate / bit_rate),
            bt=0.4,
            verbose=False,
            log=False)
        self.digital_gmsk_mod_0 = digital.gmsk_mod(
            samples_per_symbol=int(samp_rate / bit_rate),
            bt=0.4,
            verbose=False,
            log=False)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_gr_complex * 1, channel_select, 0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0_1_0 = blocks.multiply_const_cc(0.9)
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_cc(0.9)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_cc(0.45)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(0.45)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_sig_source_x_0_0 = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, 25000, 1, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_SIN_WAVE, -25000, 1, 0, 0)
        self.AISTX_Build_Frame_1 = AISTX.Build_Frame(payload, True, True)
        self.AISTX_Build_Frame_0 = AISTX.Build_Frame(payload, True, True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.AISTX_Build_Frame_0, 0), (self.digital_gmsk_mod_0, 0))
        self.connect((self.AISTX_Build_Frame_1, 0), (self.digital_gmsk_mod_0_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.blocks_selector_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_1_0, 0), (self.blocks_selector_0, 2))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.blocks_multiply_const_vxx_0_1_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.digital_gmsk_mod_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.digital_gmsk_mod_0_0, 0), (self.blocks_multiply_xx_0_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)

    def get_channel_select(self):
        return self.channel_select

    def set_channel_select(self, channel_select):
        self.channel_select = channel_select
        self.blocks_selector_0.set_input_index(self.channel_select)

    def get_bit_rate(self):
        return self.bit_rate

    def set_bit_rate(self, bit_rate):
        self.bit_rate = bit_rate


if __name__ == '__main__':
    parser = OptionParser(usage="%prog: [options]")
    parser.add_option("-p", "--payload")
    (options, args) = parser.parse_args()

    if not options.payload:
        parser.error("Payload not specified")

    tb = top_block(payload=options.payload)


    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)


    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()
