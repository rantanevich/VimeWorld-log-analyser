import re
import os
import time
import pickle
import operator
import requests
from pathlib import Path
from datetime import datetime, timedelta


ALERT_THRESHOLD = timedelta(minutes=5)
UPDATE_TIMEOUT = 3 * 60
MINECRAFT_LOG_PATH = 'C:\\Users\\user\\AppData\\Roaming\\.vimeworld\\minigames\\logs\\latest.log'

DISCORD_WEBHOOK_ALERT = os.getenv('DISCORD_WEBHOOK_ALERT')
DISCORD_WEBHOOK_RESPAWN = os.getenv('DISCORD_WEBHOOK_RESPAWN')

BOSS_COOLDOWN = {
    'Королевский зомби':    timedelta(minutes=20),
    'Сточный слизень':      timedelta(minutes=45),
    'Матка':                timedelta(hours=1, minutes=30),
    'Левиафан':             timedelta(hours=2, minutes=30),
    'Коровка из Коровёнки': timedelta(hours=2, minutes=45),
    'Йети':                 timedelta(hours=3),
    'Хранитель':            timedelta(hours=5),
    'Небесный владыка':     timedelta(hours=6),
}


basedir = Path(__file__).parent
db_file = basedir / 'db.pkl'
data_file = Path(MINECRAFT_LOG_PATH)

events = re.compile('\[(\d{2}:\d{2}:\d{2})\].+ \[CHAT\] ((?:' + '|'.join(BOSS_COOLDOWN) + '))')
parts_of_time = re.compile('(\d{2}):(\d{2}):(\d{2})')

while True:
    current_time = datetime.now()
    today_midnight = current_time.replace(hour=0, minute=0,
                                          second=0, microsecond=0)
    try:
        respawn = pickle.loads(db_file.read_bytes())
    except FileNotFoundError:
        respawn = {
            'Сточный слизень':      today_midnight,
            'Матка':                today_midnight,
            'Левиафан':             today_midnight,
            'Коровка из Коровёнки': today_midnight,
            'Йети':                 today_midnight,
            'Хранитель':            today_midnight,
            'Небесный владыка':     today_midnight,
            'Королевский зомби':    today_midnight,
        }

    is_updated = False
    for kill_time, boss_name in events.findall(data_file.read_text(encoding='utf-8')):
        hour, minute, second = [int(i) for i in parts_of_time.findall(kill_time)[0]]
        kill_datetime = today_midnight + timedelta(hours=hour, minutes=minute,
                                                   seconds=second)
        next_respawn = kill_datetime + BOSS_COOLDOWN[boss_name]
        if next_respawn > respawn[boss_name]:
            is_updated = True
            respawn[boss_name] = next_respawn

    if is_updated:
        respawn_list = []
        for boss, respawn_time in sorted(respawn.items(), key=operator.itemgetter(1)):
            respawn_list.append(f'[{respawn_time.strftime("%T")}] {boss}')
        message = '\n'.join(respawn_list)
        requests.patch(DISCORD_WEBHOOK_RESPAWN, json={'content': message})

    db_file.write_bytes(pickle.dumps(respawn))

    threshold_datetime = current_time + ALERT_THRESHOLD
    for boss, respawn_datetime in respawn.items():
        respawn_time = respawn_datetime.strftime('%T')
        if threshold_datetime > respawn_datetime and respawn_time != '00:00:00':
            if current_time > respawn_datetime:
                print(f'boss: {boss}, current: {current_time}, respawn: {respawn_datetime}')
                continue

            time_left = respawn_datetime - current_time
            minutes_left = (time_left.seconds // 60) % 60
            seconds_left = time_left.seconds - (minutes_left * 60)

            message = (f'{boss} появится через '
                       f'{minutes_left:02}:{seconds_left:02} [{respawn_time}]')
            requests.post(DISCORD_WEBHOOK_ALERT, json={'content': message})
    time.sleep(UPDATE_TIMEOUT)
