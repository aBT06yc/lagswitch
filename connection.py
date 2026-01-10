import pydivert
import keyboard  # у этой либы инпут нормальный в идеале че помощнее. 
import mouse

import sys
import threading
import time
from queue import Queue

def port_search():
    in_packets = []

    with pydivert.WinDivert("udp and inbound", 
                             priority=0,
                            flags=pydivert.Flag.SNIFF) as w:
        
        for packet in w:

            in_packets.append(packet)
            w.send(packet)

            if len(in_packets) == 50:
                break
        
        max_count = 0
        popular_dst_port = -1
        ip_dict ={}
        
        for packet in in_packets:
            src_addr = packet.src_addr
            if src_addr not in list(ip_dict.keys()):
                ip_dict[src_addr] = {"dst_port":packet.dst_port,"packet_count":1}    #packet.src_port
            else:
                ip_dict[src_addr]["packet_count"]+=1
                if ip_dict[src_addr]["packet_count"] > max_count:
                    max_count = ip_dict[src_addr]["packet_count"]
                    popular_dst_port = ip_dict[src_addr]["dst_port"]

        udp_port = popular_dst_port
        print(ip_dict)
        #print(popular_dst_port)

def lagswitch(udp_port:int,inbound:bool,outbound:int):
    global key_is_pressed

    if  not inbound and not outbound:
        return 
    
    if outbound and outbound:
        FILTER = f"udp.SrcPort == {udp_port} or udp.DstPort == {udp_port}" 
    elif (not outbound) and outbound:
        FILTER = f"udp.SrcPort == {udp_port}"
    else:
        FILTER = f"udp.DstPort == {udp_port}"
    
    print(FILTER)

    with pydivert.WinDivert(FILTER,priority=1) as w:
        for packet in w:
            if not key_is_pressed: 
                w.send(packet)

def parse_kwargs(argv):
    kwargs = {}
    for arg in argv:
        if "=" in arg:
            key, value = arg.split("=", 1)
            kwargs[key] = value
    return kwargs

def on_event(event):
    global key_is_pressed
    if event.event_type == 'down' and event.scan_code == TARGET_VK_CODE:
        key_is_pressed = True
    elif event.event_type == 'up' and event.scan_code == TARGET_VK_CODE:
        key_is_pressed = False


key_is_pressed = False  

if __name__ == "__main__":

    func_name,kwargs  = sys.argv[1],parse_kwargs(sys.argv[2:])
    #print(func_name,kwargs)
    if func_name == "port_search":
        port_search()


    if func_name == "lagswitch":
        udp_port,inbound,outbound,key = int(kwargs["udp_port"]),eval(kwargs["inbound"]),eval(kwargs["outbound"]),kwargs["key"]
        TARGET_VK_CODE = keyboard.key_to_scan_codes(key)[0]              

        keyboard.hook(on_event)
        #mouse.hook(on_mouse_event)
        lagswitch(udp_port,inbound,outbound)

        #py main.py lagswitch udp_port=1111 inbound=False outbound=True key=x


