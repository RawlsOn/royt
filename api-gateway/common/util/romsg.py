from django.conf import settings
from django.utils import timezone
import json

# docker exec robasev2-api-gateway-1 ./manage.py test_romsg

VER='1a.'
def rp(text, msg_type='INFO', filename='romsg', raise_error=False):
    to_print = []
    to_print.append(settings.SERVER_IP)
    if settings.EC2_INSTANCE_ID.strip() != '':
        to_print.append(settings.EC2_INSTANCE_ID)
    if settings.EC2_AWS_REGION:
        to_print.append(settings.EC2_AWS_REGION)
    if settings.EC2_LAUNCH_TIME:
        to_print.append(settings.EC2_LAUNCH_TIME)

    to_print.append('[' + msg_type + ']')
    to_print.append(timezone.now().strftime('%Y-%m-%d_%H:%M:%S'))
    if type(text) is not str:
        text = json.dumps(text, ensure_ascii= False)
    to_print.append(VER + text)
    to_print.append('\n')
    to_print = ' '.join(to_print)


    if msg_type == 'WARNING' or msg_type == 'ERROR':
        send(to_print, raise_error= raise_error)

    if msg_type == 'NOTICE':
        send(to_print, raise_error= False)

    if msg_type == 'IMPORTANT_NOTICE':
        send('<@UPF39TN95> ' + to_print, raise_error= raise_error)

    with open('/usr/log/' + filename + '.log', 'a') as f:
        f.write(to_print)
        print(to_print)

def send(text, raise_error=False):
    # print('romsg send: ' + text + '\n\n\n')
    # if 'slack'.upper() in settings.MSG_TARGET:
    #     _send_slack(text)
    # print('settings.MSG_TARGET', settings.MSG_TARGET)
    if 'telegram'.upper() in settings.MSG_TARGET:
        _send_telegram(text)

    if raise_error:
        raise ValueError(text)

def _send_slack(text):
    import slack_sdk
    slackclient = slack_sdk.WebClient(token= settings.SLACK_BOT_TOKEN)
    slackclient.chat_postMessage(
        channel= settings.SLACK_CHANNEL_ID,
        text= text
    )

def _send_telegram(text):
    pass
    # print('send_telegram', text)
    # 봇과 채팅창에서 그룹 만들고 원하는 사람 초대하고
    # getUpdates 날리면 (https://api.telegram.org/bot6099697280:AAEVQEoBgYdFGrNZoxkuzyq12qQZLktJeec/getUpdates)
    # 그룹챗 id를 볼 수 있음. 그룹챗 id는 -로 시작함 eg) -870373605,
    # send_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_CODE}/sendMessage?chat_id={settings.TELEGRAM_CHAT_ID}&text={text}"
    # print('_send_teelgram', send_url)
    # result = requests.get(send_url)
    # print('result', result)


