import telebot
import random
import time
from datetime import datetime, timedelta

TOKEN = '7568921828:AAGOywdESYSCSraOzTDeBm3rBIXkmkjtMN0'
ADMIN_ID = 6651180345  # آیدی تلگرامی ادمین
bot = telebot.TeleBot(TOKEN)

# تیم‌ها و بازیکنان
teams = {}
players = []

# ساخت بازیکن با نام تصادفی و اورال بین 50 تا 60
def generate_player():
    player_name = f"بازیکن_{random.randint(1000, 9999)}"
    ability = random.randint(50, 60)
    price = random.randint(100, 200)
    return {"name": player_name, "ability": ability, "price": price}

# اضافه کردن بازیکن به تیم
def add_player_to_team(team_name, player):
    if team_name not in teams:
        teams[team_name] = []
    if len(teams[team_name]) < 20:
        teams[team_name].append(player)

# ارسال اخبار به کانال تلگرام
def send_to_channel(message):
    bot.send_message('@wontball', message)

# ثبت نقل و انتقالات
def transfer_player(team_name, player_name, new_team):
    transfer_info = f"{player_name} از تیم {team_name} به تیم {new_team} منتقل شد."
    transfers.append(transfer_info)

# مسابقات حذفی
def start_tournament():
    if len(teams) < 2:
        send_to_channel("برای شروع تورنمنت حداقل ۲ تیم لازم است.")
        return

    teams_list = list(teams.keys())
    matches = []
    while len(teams_list) > 1:
        team1 = teams_list.pop(random.randint(0, len(teams_list) - 1))
        team2 = teams_list.pop(random.randint(0, len(teams_list) - 1))
        match_result = penalty_shootout(team1, team2)
        matches.append(match_result)

    for match in matches:
        send_to_channel(match)

# پنالتی کشی
def penalty_shootout(team1, team2):
    directions = ['چپ', 'راست', 'وسط', 'بالا', 'پایین', 'وسط_چپ']
    team1_score = 0
    team2_score = 0

    for i in range(5):
        team1_direction = random.choice(directions)
        team2_direction = random.choice(directions)

        if team1_direction != team2_direction:
            team1_score += 1
        if team2_direction != team1_direction:
            team2_score += 1

    return f"نتیجه پنالتی کشی: {team1} {team1_score} - {team2} {team2_score}"

# ارسال اخبار نقل و انتقالات
def send_transfer_news():
    transfer_message = "آخرین اخبار نقل و انتقالات:\n"
    for transfer in transfers:
        transfer_message += f"{transfer}\n"
    send_to_channel(transfer_message)

# توپ طلا و کفش طلا
golden_boot = {}
golden_ball = {}

def update_awards(player_name, goals):
    if player_name not in golden_boot or golden_boot[player_name] < goals:
        golden_boot[player_name] = goals

    if goals > 10:
        golden_ball[player_name] = goals

def send_awards():
    boot_message = "کفش طلا (بیشترین گل‌زنی):\n"
    for player, goals in golden_boot.items():
        boot_message += f"{player}: {goals} گل\n"
    
    ball_message = "توپ طلا (بهترین بازیکن):\n"
    for player, goals in golden_ball.items():
        ball_message += f"{player}: {goals} گل\n"
    
    send_to_channel(boot_message)
    send_to_channel(ball_message)

# برنامه‌ریزی ارسال اخبار
def send_daily_news():
    while True:
        current_time = datetime.now()
        target_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        time.sleep((target_time - current_time).seconds)

        send_transfer_news()
        send_awards()
        start_tournament()

# اجرای ربات
bot.polling()
