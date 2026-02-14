import pydivert
import keyboard  # у этой либы инпут нормальный в идеале че помощнее. 
import mouse

import sys
import threading
import time
from queue import Queue

from collections import Counter
import ipaddress

# глобалка для дропа
dropper_active = False  

def on_event(event, target_key, switch_type):

    global dropper_active
    
    # Проверка на нажатие или отпускание клавиши
    if event.event_type == 'down' and event.scan_code == target_key:
        if switch_type == "hold":
            dropper_active = True  # Пока клавиша зажата, активируем dropper
        elif switch_type == "press":
            if not dropper_active:  # Активируем dropper при первом нажатии
                dropper_active = True
    elif event.event_type == 'up' and event.scan_code == target_key:
        if switch_type == "hold":
            dropper_active = False  # Деактивируем, как только клавиша отпускается
        elif switch_type == "press":
            dropper_active = False  # Деактивируем на отпускание клавиши

def ip_sniff(size=100,filter_local_ips=True):
    """
    `size` - сколько пакетов ждем до статистики

    `filter_local_ips` - НЕ учитываем локальные и приватные IP? True - не учитываем.

    Если запустить скан без интернет трафика он тупо повистнет, мне похуй 😎👍
    """
    #print("Sniffer started. Scanning...",flush=True)

    in_packets = []
    processed_count  = 0

    with pydivert.WinDivert("inbound", 
                             priority=0,
                            flags=pydivert.Flag.SNIFF) as w:
        
        for i,packet in enumerate(w):

            if filter_local_ips:
                ip_obj = ipaddress.ip_address(packet.src_addr)
                if ip_obj.is_private or ip_obj.is_loopback:
                      continue

            in_packets.append(packet.src_addr)
            processed_count+=1

            if processed_count == size :
                break

        stat_list = Counter(in_packets).most_common()
        popular_ip = stat_list[0][0]
        
        # вывожу сразу с процентамми 
        for i,elem in enumerate(stat_list):
            percent = (elem[1]/size)* 100
            stat_list[i] = (elem[0],f"{percent :.2f}%")

        #local_trafic_percent = (1 - (processed_count/i))*100
        #print(f"local trafic: {local_trafic_percent :.2f}%")  # можем себе позвоилить

        print(stat_list,flush=True) # этот print нужен чтобы интерфейс увидел инфу через  stdout
        #print(popular_ip,flush=True)
        
        return popular_ip,stat_list  # return нужен если запускать без интерфейсаю что-то типо супер изи варианта, но не для очередняр, смотри ниже в (main) как я запускаю


def packet_control(target_ip:str,
                   inbound:bool,outbound:bool,
                   tcp:bool,udp:bool,
                   key:str,switch_type:str):
    """
    `packet_control` - сейчас эта функция дропает все пакеты которые ты указал.
    ----------------------
    `target_ip` - какой ip нам дропать

    `inbound`/`outbound` - какой трафик дропаем (исходящий\входящий), можно весь

    `tcp`/`udp` - какой протокол дропаем, можно оба

    `key` - какая клавиша активирует дроп

    `switch_type` - вид переключателся `press` или `hold`

    """

    global dropper_active

    if  not (inbound or outbound):
        return 
    if  not (tcp or udp):
        return
    
    try:
        target_key = keyboard.key_to_scan_codes(key)[0]     
        keyboard.hook(lambda e: on_event(e, target_key, switch_type))
    except Exception as e:
        return
    
    if outbound and inbound:
        FILTER = f"(ip.DstAddr == {target_ip} or ip.SrcAddr == {target_ip})" 
    elif (not inbound) and outbound:
        FILTER = f"(ip.DstAddr == {target_ip})"
    else:
        FILTER = f"(ip.SrcAddr == {target_ip})"
    
    if tcp and udp:
        pass 
    elif (not tcp) and udp:
        FILTER += " and udp"
    else:
        FILTER += " and tcp"

    print(FILTER)

    with pydivert.WinDivert(FILTER,priority=1) as w:
        for packet in w:
            if not dropper_active: 
                w.send(packet)


if __name__ == "__main__":
    #  Это версия без интерфеса, сам ручками вбивай че надо
    popular_ip, stat_list = ip_sniff()

    target_ip:str = popular_ip
    inbound:bool = False
    outbound:bool = True
    tcp:bool = True
    udp:bool = True
    key:str = "x"
    switch_type:str = "hold"
    
    # сейчас настроено на ДРОП ВСЕХ ИСХОДЯЩИХ пакетов
    packet_control(target_ip,inbound,outbound,tcp,udp,key,switch_type)
