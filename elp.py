#!python3
# https://towardsdatascience.com/building-a-simple-voice-assistant-for-your-mac-in-python-62247543b626
# https://maithegeek.medium.com/having-fun-in-macos-with-say-command-d4a0d3319668
#
# brew install portaudio
# pip install pyaudio
#
# python3 -m venv venv
# source ./venv/bin/activate
#
# Compile:
# pip install --upgrade cx_Freeze
# cxfreeze -c elp.py --target-dir dist
# ./dist/elp -r 180 -p 2 -m 1 -s 0 -c 1
#
# Example:
# import subprocess
# def say(text):
#     subprocess.call(['say', text])
# say("yo what-up dog")

import sys
import subprocess
import time
import random
import string
import argparse

# '--voice=Daniel'
# voices:
# Karen
# Siri
# Rishi
# Moira
# Tessa
# Daniel
# Eloquence
# Fred
# Junior
# Kathy
# Nicky
# Novelty
# Ralph
# Samantha

call_sign = "A6KID"

voices = {
    "Pilot": "Daniel",
    "ATC0": "Kate",
    "ATC1": "Tessa",
    "ATC2": "Karen",
    "ATC3": "Samantha",
    "ATC4": "Karen",
    "ATC5": "Karen",
    "ATC6": "Karen",
    "ATC7": "Karen",
    "ATC8": "Serena"
}

alfabet = {
    'A': "alfa",
    'B': "bravo",
    'C': "charlie",
    'D': "delta",
    'E': "echo",
    'F': "foxtrot",
    'G': "golf",
    'H': "hotel",
    'I': "india",
    'J': "juliett",
    'K': "kilo",
    'L': "lima",
    'M': "mike",
    'N': "november",
    'O': "oscar",
    'P': "papa",
    'Q': "quebec",
    'R': "romeo",
    'S': "sierra",
    'T': "tango",
    'U': "uniform",
    'V': "victor",
    'W': "whiskey",
    'X': "xray",
    'Y': "yankee",
    'Z': "zulu",
    '1': "wun",
    '2': "too",
    '3': "tree",
    '4': "fower",
    '5': "five",
    '6': "six",
    '7': "seven",
    '8': "ait",
    '9': "niner",
    '0': "zero",
    '00': "hundred",
    '000': "thousand",
    '.': "decimal"
}

messages = {
    1: "*",  # flight level
    2: "^",  # heading
    3: "&",  # squawk
    4: "=",  # runway
    5: "@",  # 117.975 – 137.000 MHz (VHF Aeronautical communications)
    6: "!",  # QNH
    7: "$",  # altitude
    8: "-",  # wind
    9: "+"   # any message
}

LR = {
    0: "left",
    1: "right"
}

valid_messages = {"ANY", "ATIS"}

num_msg = 1  # Number of messages
voice = 'ATC8'  # Default voice
rate = 160  # Speech rate to be used, in words per minute.
pause = 3  # pause delay
comma = False


def get_frequency():
    fq_msg = ["departure",
              "berlin tower",
              "apron",
              "dubai information",
              "munich approach",
              "munich tower",
              "ground",
              "fujairah information"]
    x = random.randint(117975, 137000)
    x = (x // 5) * 5
    s_fq = "{:03d}.{:03d}".format(x // 1000, x % 1000)
    s_fq = s_fq.rstrip('0')  # remove zeroes at the end of string
    s_fq = s_fq.rstrip('.')  # remove '.' at the end of string
    return "contact " + fq_msg[random.randint(0, len(fq_msg) - 1)] + " " + s_fq


def get_rw():
    return "runway {:02d} {}".format(random.randint(10, 360) // 10, LR[random.randint(0, 1)])


def get_wind():
    return "wind {:03d} degree {:d} knots".format((random.randint(10, 360) // 10) * 10, random.randint(1, 50))


def get_squawk():
    squawk_tmp = random.randint(2000, 9999)
    while squawk_tmp in [7500, 7600, 7700]:
        squawk_tmp = random.randint(2000, 9999)
    return "squawk {:04d}".format(squawk_tmp)


def get_fl():
    x = random.randint(60, 420)
    x = (x // 5) * 5
    return "flight level " + str(x)


def get_altitude():
    hundreds = 0
    thousands = 0
    x = random.randint(500, 42000)
    x = (x // 100) * 100
    if x > 1000:
        thousands = (x // 1000)
    if x > 1000 and (x - (thousands * 1000)) > 0:
        hundreds = (x - (thousands * 1000)) // 100
    #print("DEBUG: x={}, thousands={}, hundreds={}".format(x, thousands, hundreds))
    alt_msg = "altitude"
    if thousands > 0:
        alt_msg = alt_msg + " " + str(thousands) + " " + alfabet['000']
    if hundreds > 0:
        alt_msg = alt_msg + " " + str(hundreds) + " " + alfabet['00']
    return alt_msg + " feet"
    #return "altitude !" + str(x) + " feet"


def get_heading():
    x = random.randint(10, 360)
    x = (x // 10) * 10
    return "heading {:03d}".format(x)


def get_qnh(imperial=True):
    qnh = "qnh "
    if imperial is False or random.randint(0, 1) == 0:
        x = random.randint(931, 1066)
        qnh = qnh + str(x) + " hectopascal"
    else:
        x = random.randint(2750, 3150)
        x = x / 100
        qnh = qnh + str(x) + " inches"
    return qnh


def get_temperature():
    temperature = random.randint(-30, 50)
    dew_point = random.randint(temperature - 15, temperature)
    minus_temp = ""
    minus_dp = ""
    if temperature < 0:
        minus_temp = "minus"
        temperature = 0 - temperature
    if dew_point < 0:
        minus_dp = "minus"
        dew_point = 0 - dew_point

    return "temperature {} {} dew point {} {}".format(minus_temp, temperature, minus_dp, dew_point)


def get_random_msg():
    any_msg = [
        "engine start-up approved",
        "cleared to munich via T1B departure",
        "cleared to lyon via M2F departure",
        "hold short =, taxi via LFM"
    ]
    any_tmp = ""
    found = ""
    for _symbol in any_msg[random.randint(0, len(any_msg) - 1)]:
        if _symbol in alfabet:
            if _symbol != 'T' and _symbol not in string.digits:
                _symbol = random.choice(string.ascii_uppercase)
                while _symbol in found:
                    _symbol = random.choice(string.ascii_uppercase)
                found = found + _symbol
            any_tmp = any_tmp + alfabet[_symbol] + " "
        else:
            if _symbol == '=':
                any_tmp = any_tmp + get_rw()
            else:
                any_tmp = any_tmp + _symbol
    any_tmp = any_tmp.replace('  ', ' ')

    return any_tmp


def get_atis_message():
    airports = ['schiphol', 'dubai', 'new york', 'detroit', 'abu dhabi', 'warsaw', 'berlin', 'al bateen']
    info_no = random.choice(string.ascii_uppercase)
    atis_h1 = "this is {} arrival information {}".format(airports[random.randint(0, len(airports)-1)], info_no)
    atis_h2 = "main landing " + get_rw()
    atis_h3 = "transition level " + str((random.randint(50, 100) // 10) * 10)
    atis_h4 = "{:03d} degree {:d} knots".format((random.randint(10, 360) // 10) * 10, random.randint(1, 50))
    atis_h5 = "visibility !{} metres".format((random.randint(100, 10000) // 100) * 100)
    atis_h6 = "few !{}, scattered !{}, broken !{}".format((random.randint(1000, 2500) // 100) * 100,
                                                          (random.randint(2500, 3500) // 100) * 100,
                                                          (random.randint(3500, 10000) // 100) * 100)
    atis_h7 = get_temperature()
    atis_h8 = get_qnh(False)
    atis_h9 = "no significant change"
    atis_h10 = "end of information " + info_no

    atis_msg = ", ".join([atis_h1, atis_h2, atis_h3, atis_h4, atis_h5,
                          atis_h6, atis_h7, atis_h8, atis_h9, atis_h10])
    return atis_msg


def get_any_message():
    tmp_msg = call_sign + ", "
    a = [0] * len(messages)
    idx = 0
    while True:
        x = random.randint(1, int(len(a)))
        if x in a:
            continue
        a[idx] = x
        idx = idx + 1
        if idx >= len(a):
            break
    for n in range(0, len(a), 1):
        ss = ""
        for sym in messages[a[n]]:
            if '=' in sym:
                ss = ss + get_rw()
            elif '*' in sym:
                ss = ss + get_fl()
            elif '!' in sym:
                ss = ss + get_qnh()
            elif '$' in sym:
                ss = ss + get_altitude()
            elif '@' in sym:
                ss = ss + get_frequency()
            elif '^' in sym:
                ss = ss + get_heading()
            elif '&' in sym:
                ss = ss + get_squawk()
            elif '-' in sym:
                ss = ss + get_wind()
            elif '+' in sym:
                ss = ss + get_random_msg()
            else:
                ss = ss + sym
        tmp_msg = tmp_msg + ss
        if n < (len(a) - 1):
            tmp_msg = tmp_msg + ", "

    return tmp_msg


def get_message(type_of_msg):
    tmp_msg = "Unknown type of the message!"

    if type_of_msg in valid_messages:
        if type_of_msg == "ANY":
            tmp_msg = get_any_message()
        elif type_of_msg == "ATIS":
            tmp_msg = get_atis_message()

    return tmp_msg


def be_ready(val):
    for j in range(pause, -1, -1):
        print('\rBe ready in %d seconds' % j, end="")
        time.sleep(val)
    print("\r", end="")


def say(text, flag, comma_pause):
    global voice

    # check voice, if defined then set voice and exit
    for key, value in voices.items():
        if text.find(key) == 0:
            voice = key
            print("{} ({}):".format(voice, voices[voice]))
            return

    # delay if "Pause" found
    if text.find("!Pause") == 0:
        time.sleep(pause)
        return

    if comma_pause is True:
        for tmp_say in text.split(','):
            tmp_say = tmp_say.strip(' ')
            # print and say message
            if flag is True:
                print("{}".format(tmp_say))
            subprocess.call(['say',
                             "--voice={}".format(voices[voice]),
                             "--rate={}".format(rate), tmp_say])
            time.sleep(0.5)
    else:
        # print and say message
        if flag is True:
            print("{}".format(text))
        subprocess.call(['say',
                         "--voice={}".format(voices[voice]),
                         "--rate={}".format(rate), text])
    return True


print("{} -m [messages] -r [rate] -p [delay] -c [comma pause[True[1]:False[0]]]\n".format(sys.argv[0]))
print("Default voice: {}\nDefault rate: {} words per minute\nDefault number of messages: {}\n"
      .format(voices[voice], rate, num_msg))

parser = argparse.ArgumentParser(
    prog="elp.py",
    description='ELP training tool for pilots',
    epilog='')

parser.add_argument('-t', '--type', choices=valid_messages, default='any', help="Message type",
                    type=lambda s: s.upper())
parser.add_argument('-m', '--count', default=1, help='Message count')
parser.add_argument('-r', '--rate', default=180, help='Words per minute')
parser.add_argument('-p', '--pause', default=5, help='Pause between messages')
parser.add_argument('-c', '--comma', default=0, help='Pause between blocks')
parser.add_argument('-s', '--sayagain', default=0, help='Repeat each message 2 times')

args = parser.parse_args()

num_msg = int(args.count)
rate = int(args.rate)
pause = int(args.pause)
comma = bool(args.comma)
msg_type = args.type
sayagain = int(args.sayagain)

print("Messages:{} Type:{} Count:{} Rate:{} Pause:{} Comma:{} Sayagain:{}\n".format(num_msg, msg_type, num_msg, rate, pause, comma, sayagain))

sayagain_cnt = 0
msg = ""
if sayagain == True:
    num_msg = num_msg * 2

for i in range(0, num_msg, 1):
    tmp = ""
    be_ready(1)

    if sayagain == False or (sayagain == True and sayagain_cnt in [0,2]):
        msg = get_message(msg_type)
        voice = "ATC{}".format(random.randint(0, 8))

    if sayagain == True and sayagain_cnt == 2:
        sayagain_cnt = 0

    print(msg)
    skip = False

    for symbol in msg:
        if symbol == '!':
            skip = True
        elif symbol == ' ' or symbol == ',':
            tmp = tmp + symbol
            skip = False
        elif symbol in alfabet and skip is False:
            tmp = tmp + alfabet[symbol] + " "
        else:
            tmp = tmp + symbol
    tmp = tmp.replace('  ', ' ')

    say(tmp, False, comma)

    sayagain_cnt = sayagain_cnt + 1
