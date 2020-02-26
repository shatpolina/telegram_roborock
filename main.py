import json

config = json.loads(open("config.json").read())

token = config["tg_token"]

import telebot
from telebot import types
import miio

bot = telebot.TeleBot(token)
#localhost:9150
telebot.apihelper.proxy = {'https': 'socks5://localhost:9050'}


tokenrobot = config["robot_token"]
iprobot = config["robot_ip"]

robot = miio.vacuum.Vacuum(iprobot, tokenrobot, start_id=0, debug=0)
keyboard_hider = types.ReplyKeyboardRemove()

class Button():
	def __init__(self, name):
		self.name = name
		self.children = []
		self.parent = None
		self.callback = None

	def add_child(self, child):
		child.parent = self
		self.children += [child]

	def button_action(self, sender):
		if self.callback != None:
			self.callback(sender)

buttons = []
current_btn = {}

def on_back(sender):
	current_btn[sender] = buttons.index(buttons[current_btn[sender]].parent)

def robot_start(speed):
	robot.set_fan_speed(speed)
	robot.start()

root_btn = Button("")
buttons += [root_btn]

btn_start = Button("Start")
btn_stop = Button("Stop")
btn_stop.callback = lambda x: robot.stop()
btn_home = Button("Go home")
btn_home.callback = lambda x: robot.home()

root_btn.add_child(btn_start)
root_btn.add_child(btn_stop)
root_btn.add_child(btn_home)
buttons += [btn_start, btn_stop, btn_home]

btn_wet = Button("Wet clean")
btn_wet.callback = lambda x: robot_start(105)
btn_dry = Button("Dry clean")
btn_dry.callback = lambda x: robot_start(60)
btn_other = Button("Other")
btn_back_1 = Button("Back")
btn_back_1.callback = on_back

btn_start.add_child(btn_wet)
btn_start.add_child(btn_dry)
btn_start.add_child(btn_other)
btn_start.add_child(btn_back_1)
buttons += [btn_wet, btn_dry, btn_other, btn_back_1]

btn_quiet = Button("Quiet")
btn_quiet.callback = lambda x: robot_start(32)
btn_turbo = Button("Turbo")
btn_turbo.callback = lambda x: robot_start(75)
btn_max = Button ("Max")
btn_max.callback = lambda x: robot_start(100)
btn_back_2 = Button("Back")
btn_back_2.callback = on_back

btn_other.add_child(btn_quiet)
btn_other.add_child(btn_turbo)
btn_other.add_child(btn_max)
btn_other.add_child(btn_back_2)
buttons += [btn_quiet, btn_turbo, btn_max, btn_back_2]

def read_db():
	global current_btn
	s = open("db.json").read()
	current_btn = json.loads(s)

def write_db():
	s = json.dumps(current_btn)
	open("db.json", "w").write(s)

def render_keyboard(root):
	markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
	for child in root.children:
		markup.add(types.KeyboardButton(child.name))
	return markup

@bot.message_handler(commands=['start']) 
def handle_start(message):
	sender = str(message.chat.id)
	current_btn[sender] = buttons.index(root_btn)
	markup = render_keyboard(buttons[current_btn[sender]])
	bot.send_message(sender, "Hello, UBLUDOK!\nChoose action for me:", reply_markup=markup)

@bot.message_handler(content_types = ["text"])
def process_btn(message):
	sender = str(message.chat.id)
	if not sender in current_btn:
		current_btn[sender] = buttons.index(root_btn)
	clicked_btn = None
	print(current_btn)
	for child in buttons[current_btn[sender]].children:
		if message.text == child.name:
			clicked_btn = child
			break
	if clicked_btn == None:
		bot.send_message(sender, "Invalid command! Press /start")
	else:
		clicked_btn.button_action(sender)
		if len(clicked_btn.children) > 0:
			current_btn[sender] = buttons.index(clicked_btn)
		markup = render_keyboard(buttons[current_btn[sender]])
		bot.send_message(sender, "Choose:", reply_markup=markup)

@bot.message_handler(commands = ["start_robot"])
def listener(message):
	robot.start()

if __name__ == "__main__":
	read_db()
	bot.infinity_polling()
	write_db()