#!/usr/bin/python3

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

	def button_action(self):
		if self.callback != None:
			self.callback()

current_btn = None

def on_back():
	global current_btn
	current_btn = current_btn.parent

def robot_start(speed):
	robot.set_fan_speed(speed)
	robot.start()

root_btn = Button("")

btn_start = Button("Start")
btn_stop = Button("Stop")
btn_stop.callback = lambda: robot.stop()
btn_home = Button("Go home")
btn_home.callback = lambda: robot.home()

root_btn.add_child(btn_start)
root_btn.add_child(btn_stop)
root_btn.add_child(btn_home)

btn_wet = Button("Wet clean")
btn_wet.callback = lambda: robot_start(105)
btn_dry = Button("Dry clean")
btn_dry.callback = lambda: robot_start(60)
btn_other = Button("Other")
btn_back_1 = Button("Back")
btn_back_1.callback = on_back

btn_start.add_child(btn_wet)
btn_start.add_child(btn_dry)
btn_start.add_child(btn_other)
btn_start.add_child(btn_back_1)

btn_quiet = Button("Quiet")
btn_quiet.callback = lambda: robot_start(32)
btn_turbo = Button("Turbo")
btn_turbo.callback = lambda: robot_start(75)
btn_max = Button ("Max")
btn_max.callback = lambda: robot_start(100)
btn_back_2 = Button("Back")
btn_back_2.callback = on_back

btn_other.add_child(btn_quiet)
btn_other.add_child(btn_turbo)
btn_other.add_child(btn_max)
btn_other.add_child(btn_back_2)


def render_keyboard(root):
	markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
	for child in root.children:
		markup.add(types.KeyboardButton(child.name))
	return markup


@bot.message_handler(commands=['start']) 
def handle_start(message):
	global current_btn
	current_btn = root_btn
	markup = render_keyboard(current_btn)
	bot.send_message(message.chat.id, "Hello, UBLUDOK!\nChoose action for me:", reply_markup=markup)

@bot.message_handler(content_types = ["text"])
def process_btn(message):
	global current_btn
	if current_btn == None:
		current_btn = root_btn
	clicked_btn = None
	for child in current_btn.children:
		if message.text == child.name:
			clicked_btn = child
			break
	if clicked_btn == None:
		bot.send_message(message.chat.id, "Invalid command! Press /start")
	else:
		clicked_btn.button_action()
		if len(clicked_btn.children) > 0:
			current_btn = clicked_btn
		markup = render_keyboard(current_btn)
		bot.send_message(message.chat.id, "Choose:", reply_markup=markup)

@bot.message_handler(commands = ["start_robot"])
def listener(message):
	robot.start()

if __name__ == "__main__":
	bot.infinity_polling()
