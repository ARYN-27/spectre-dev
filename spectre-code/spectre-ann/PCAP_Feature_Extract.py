import os
import statistics
from scapy.all import *


class FeaturesCalc:

    malware_label = 1.0
    legitimate_label = 0.0

    def __init__(self, flow_type, min_window_size=2):
        self.flow_type = flow_type
        self.min_window_size = int(min_window_size)
        assert (
            self.flow_type == "malware" or self.flow_type == "legitimate"
        ), "Invalid flow_type. Valid values are malware or legitimate."
        assert (
            self.min_window_size > 0
        ), "Invalid value for min_windows_size. Must be greater than 0."
        self.label = None
        if self.flow_type == "malware":
            self.label = self.malware_label
        else:
            self.label = self.legitimate_label

        self.features_name = [
            "Avg_syn_flag",
            "Avg_urg_flag",
            "Avg_fin_flag",
            "Avg_ack_flag",
            "Avg_psh_flag",
            "Avg_rst_flag",
            "Avg_DNS_pkt",
            "Avg_TCP_pkt",
            "Avg_UDP_pkt",
            "Avg_ICMP_pkt",
            "Duration_window_flow",
            "Avg_delta_time",
            "Min_delta_time",
            "Max_delta_time",
            "StDev_delta_time",
            "Avg_pkts_lenght",
            "Min_pkts_lenght",
            "Max_pkts_lenght",
            "StDev_pkts_lenght",
            "Avg_small_payload_pkt",
            "Avg_payload",
            "Min_payload",
            "Max_payload",
            "StDev_payload",
            "Avg_DNS_over_TCP",
            "Label",
        ]

        self.total_packets = 0
        self.nb_samples = 0

    def compute_features(self, packets_list):
        def increment_sample_nb(nb):
            self.nb_samples += nb

        def update_received_pkts(nb):
            self.total_packets += nb

        def compute_avg(list_of_values):
            if len(list_of_values) == 0:
                return 0.0
            else:
                return float(sum(list_of_values) / self.get_min_window_size())

        def compute_min(list_of_values):
            if len(list_of_values) == 0:
                return 0.0
            else:
                return float(min(list_of_values))

        def compute_max(list_of_values):
            if len(list_of_values) == 0:
                return 0.0
            else:
                return float(max(list_of_values))

        def compute_stDev(list_of_values):
            if len(list_of_values) == 0 or len(list_of_values) == 1:
                return 0.0
            else:
                try:
                    stat = statistics.stdev(list_of_values)
                    return float(stat)
                except:
                    return 0.0

        # Given a list of pkts it returns a list of the same size with the ratio (DNS/PKT5Layer) in the first position
        # If there are no DNS packets or no non-DNS level 5 packets, return as the first item in list 0
        def DNS_over_TCP_ratio(packets_list):
            total_DNS = float(sum(compute_DNS_packets(packets_list)))
            ratio_list = []
            total_packet_high_level_list = (
                []
            )  # list of 1s and 0s where 1 occurs if the package is level 5 and 0 in all other cases
            list_of_pkt_with_TCP = compute_TCP_packets(
                packets_list
            )  # Compared to the list I have 1.0 where there is tcp and 0.0 where there is none
            list_of_paylod_lenght = compute_packet_TCP_payload_size(
                packets_list, count_packet_without_payload=True
            )  # Compared to the list I have len(payload) where there is tcp with load, 0.0 where there is tcp without load, and None where there is no tcp
            # Calculate how many lvl 5 packets I have in the window that are not DNS
            if len(packets_list) == len(list_of_pkt_with_TCP) and len(
                packets_list
            ) == len(list_of_paylod_lenght):
                for i in range(0, len(packets_list) - 1):
                    # Check if the Pkt has TCP
                    if list_of_pkt_with_TCP[i] == 1.0:
                        # Check if the pkt has a payload as it means it is level 5
                        if list_of_paylod_lenght[i] > 0:
                            # Verify that the pkt that has the tcp with a payload is not DNS
                            if not packets_list[i].haslayer("DNS"):
                                total_packet_high_level_list.append(1.0)
                            else:
                                total_packet_high_level_list.append(0.0)
                        # If pkt has no payload
                        else:
                            total_packet_high_level_list.append(0.0)
                    # The pkt has no tcp
                    else:
                        total_packet_high_level_list.append(0.0)
            else:
                print("Unexpected error in dnsOverTCPRatio()")
            total_packet_high_level = float(sum(total_packet_high_level_list))
            if total_packet_high_level != 0:
                ratio_list.append(float(total_DNS / total_packet_high_level))
            else:
                ratio_list.append(0.0)
            i = 1
            # add as many 0s as 1s to len(pktList) - 1
            while i <= len(packets_list) - 1:
                ratio_list.append(0.0)
                i += 1
            return ratio_list

        # Calculate packet stream duration.
        def compute_duration_flow(packets_list):
            return packets_list[len(packets_list) - 1].time - packets_list[0].time

        # Calculate the byte size of each package in a package list
        def packets_bytes_lenght(packets_list):
            pkt_lenght_list = []
            for pkt in packets_list:
                pkt_lenght_list.append(float(len(pkt)))
            return pkt_lenght_list

        # Calculate the number of DNS packets
        def compute_DNS_packets(packets_list):
            dns_counter = []
            for pkt in packets_list:
                if pkt.haslayer("DNS"):
                    dns_counter.append(1.0)
                else:
                    dns_counter.append(0.0)
            return dns_counter

        # Calculate the number of TCP packets
        def compute_TCP_packets(packets_list):
            tcp_counter = []
            for pkt in packets_list:
                if pkt.haslayer("TCP"):
                    tcp_counter.append(1.0)
                else:
                    tcp_counter.append(0.0)
            return tcp_counter

        # Calculate the number of UDP packets
        def compute_UDP_packets(ackets_list):
            udp_counter = []
            for pkt in packets_list:
                if pkt.haslayer("UDP"):
                    udp_counter.append(1.0)
                else:
                    udp_counter.append(0.0)
            return udp_counter

        # Calculate the number of ICMP packets
        def compute_ICMP_packets(packets_list):
            icmp_counter = []
            for pkt in packets_list:
                if pkt.haslayer("ICMP") is True:
                    icmp_counter.append(1.0)
                else:
                    icmp_counter.append(0.0)
            return icmp_counter

        # Count the number of packets with the tcp layer that have little or no payload
        def compute_packet_with_small_TCP_payload(
            packets_list, count_packet_without_payload=False
        ):
            packets_small_payload_count = []
            pktPayloadList = compute_packet_TCP_payload_size(
                packets_list, count_packet_without_payload=count_packet_without_payload
            )
            for payload in pktPayloadList:
                if (
                    payload <= 32
                ):  # 32 was chosen based on the bonesi framework which simulates a botnet and defaults the paylaod to 32
                    packets_small_payload_count.append(1.0)
                elif payload > 32:
                    packets_small_payload_count.append(0.0)
                elif payload is None:
                    # If it has the tcp layer and doesn't respect the standards, increase the counter. If it doesn't have the tcp layer it doesn't increment the counter.
                    # So even if a window is 10 pkt, this parameter will be weighted against the number of pkts that have the TCP layer
                    if count_packet_without_payload:
                        packets_small_payload_count.append(0.0)
                    else:
                        pass
            return packets_small_payload_count

        # Calculate payload size of a TCP packet
        def compute_packet_TCP_payload_size(
            packets_list, count_packet_without_payload=False
        ):
            payload_size_list = []
            for pkt in packets_list:
                if pkt.haslayer("TCP"):
                    if (
                        pkt["TCP"].payload is None
                    ):  # The packet is TCP but has no payload. It's probably a three way
                        payload_size_list.append(0.0)
                    else:
                        payload_size_list.append(float(len(pkt["TCP"].payload)))
                else:
                    if count_packet_without_payload:
                        payload_size_list.append(None)
                    else:
                        pass
            return payload_size_list

        def compute_delta_time(packets_list):
            i = 1
            delta_time_list = []
            while i <= (len(packets_list) - 1):
                delta_time_list.append(packets_list[i].time - packets_list[i - 1].time)
                i += 1
            return delta_time_list

        # Calculate active TCP flags in a packet. The array contains 1 if the flag
        # is active, 0 if not or the pkt is not TCP
        def compute_tcp_flags(packets_list):
            syn_counter = []
            fin_counter = []
            ack_counter = []
            psh_counter = []
            urg_counter = []
            rst_counter = []
            FIN = 0x01
            SYN = 0x02
            RST = 0x04
            PSH = 0x08
            ACK = 0x10
            URG = 0x20
            for pkt in packets_list:
                if pkt.haslayer("TCP"):
                    F = pkt["TCP"].flags
                    if F & FIN:
                        fin_counter.append(1.0)
                        syn_counter.append(0.0)
                        ack_counter.append(0.0)
                        psh_counter.append(0.0)
                        urg_counter.append(0.0)
                        rst_counter.append(0.0)
                    elif F & SYN:
                        fin_counter.append(0.0)
                        syn_counter.append(1.0)
                        ack_counter.append(0.0)
                        psh_counter.append(0.0)
                        urg_counter.append(0.0)
                        rst_counter.append(0.0)
                    elif F & RST:
                        fin_counter.append(0.0)
                        syn_counter.append(0.0)
                        ack_counter.append(0.0)
                        psh_counter.append(0.0)
                        urg_counter.append(0.0)
                        rst_counter.append(1.0)
                    elif F & PSH:
                        fin_counter.append(0.0)
                        syn_counter.append(0.0)
                        ack_counter.append(0.0)
                        psh_counter.append(1.0)
                        urg_counter.append(0.0)
                        rst_counter.append(0.0)
                    elif F & ACK:
                        fin_counter.append(0.0)
                        syn_counter.append(0.0)
                        ack_counter.append(1.0)
                        psh_counter.append(0.0)
                        urg_counter.append(0.0)
                        rst_counter.append(0.0)
                    elif F & URG:
                        fin_counter.append(0.0)
                        syn_counter.append(0.0)
                        ack_counter.append(0.0)
                        psh_counter.append(0.0)
                        urg_counter.append(1.0)
                        rst_counter.append(0.0)
                    else:
                        pass
                else:
                    fin_counter.append(0.0)
                    syn_counter.append(0.0)
                    ack_counter.append(0.0)
                    psh_counter.append(0.0)
                    urg_counter.append(0.0)
                    rst_counter.append(0.0)
            return (
                syn_counter,
                fin_counter,
                ack_counter,
                psh_counter,
                urg_counter,
                rst_counter,
            )

        if len(packets_list) < self.get_min_window_size():
            print("\nNumber of packets too low\n")
            return None
        else:
            syn_lst, fin_lst, ack_lst, psh_lst, urg_lst, rst_lst = compute_tcp_flags(
                packets_list
            )
            syn_avg = compute_avg(syn_lst)
            fin_avg = compute_avg(fin_lst)
            ack_avg = compute_avg(ack_lst)
            psh_avg = compute_avg(psh_lst)
            urg_avg = compute_avg(urg_lst)
            rst_avg = compute_avg(rst_lst)

            durationFlow = compute_duration_flow(packets_list)
            avgTimeFlow = compute_avg(compute_delta_time(packets_list))
            minTimeFlow = compute_min(compute_delta_time(packets_list))
            maxTimeFlow = compute_max(compute_delta_time(packets_list))
            stdevTimeFlow = compute_stDev(compute_delta_time(packets_list))
            dns_pkt = compute_avg(compute_DNS_packets(packets_list))
            tcp_pkt = compute_avg(compute_TCP_packets(packets_list))
            udp_pkt = compute_avg(compute_UDP_packets(packets_list))
            icmp_pkt = compute_avg(compute_ICMP_packets(packets_list))
            pktLenghtAvg = compute_avg(packets_bytes_lenght(packets_list))
            pktLenghtMin = compute_min(packets_bytes_lenght(packets_list))
            pktLenghtMax = compute_max(packets_bytes_lenght(packets_list))
            pktLenghtStDev = compute_stDev(packets_bytes_lenght(packets_list))
            smallPktPayloadAvg = compute_avg(
                compute_packet_with_small_TCP_payload(packets_list, False)
            )
            avgPayload = compute_avg(
                compute_packet_TCP_payload_size(packets_list, False)
            )
            minPayload = compute_min(
                compute_packet_TCP_payload_size(packets_list, False)
            )
            maxPayload = compute_max(
                compute_packet_TCP_payload_size(packets_list, False)
            )
            stDevPayload = compute_stDev(
                compute_packet_TCP_payload_size(packets_list, False)
            )
            dnsOverTcpRatioNormalized = compute_avg(DNS_over_TCP_ratio(packets_list))

            row = [
                syn_avg,
                urg_avg,
                fin_avg,
                ack_avg,
                psh_avg,
                rst_avg,
                dns_pkt,
                tcp_pkt,
                udp_pkt,
                icmp_pkt,
                durationFlow,
                avgTimeFlow,
                minTimeFlow,
                maxTimeFlow,
                stdevTimeFlow,
                pktLenghtAvg,
                pktLenghtMin,
                pktLenghtMax,
                pktLenghtStDev,
                smallPktPayloadAvg,
                avgPayload,
                minPayload,
                maxPayload,
                stDevPayload,
                dnsOverTcpRatioNormalized,
                self.label,
            ]
            increment_sample_nb(1)
            update_received_pkts(len(packets_list))
            return row

    def get_total_pkts(self):
        return self.total_packets

    def get_total_sample(self):
        return self.nb_samples

    def reset_sample_counter(self):
        self.nb_samples = 0

    def reset_total_pkts_counter(self):
        self.total_packets = 0

    def set_min_window_size(self, val):
        self.min_window_size = val

    def get_min_window_size(self):
        return self.min_window_size

    def set_flow_type(self, flow_type):
        assert (
            self.flow_type == "malware" or self.flow_type == "legitimate"
        ), "Flow_type non valido. Valori validi sono malware o legitimate."
        self.flow_type = flow_type
        if self.flow_type == "malware":
            self.label = self.malware_label
        else:
            self.label = self.legitimate_label

    def get_flow_type(self):
        return self.flow_type

    def get_features_name(self):
        return self.features_name
