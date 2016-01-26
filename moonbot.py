#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json
import time
import datetime
import requests
import telegram
import redis

m_empty = 700
z = 0 # тяга двигателя
vz = 3000 #скорость истечения газов двигателя
g = 1.6

LAST_UPDATE_ID = 0

db = redis.StrictRedis(host='localhost')
db.ping()

bot = telegram.Bot("148502399:AAG7WPZazwl4EeAtfSRSWtp9Btm_8qvZuB0")

def loop():
    global LAST_UPDATE_ID
    while True:
        try:
            updates = bot.getUpdates(LAST_UPDATE_ID+1)
            print 'got'
            for update in updates:
                if LAST_UPDATE_ID < update.update_id:
                    handleUpdate(update)
                    LAST_UPDATE_ID = update.update_id
        except Exception as e:
            print e
            break
        time.sleep(0.2)

def handler(data):
    update = telegram.Update.de_json(json.loads(data))
    handleUpdate(update)

def handleUpdate(update):
    response = ""
    keyboard = [["20", "50", "100"],["2", "5", "10"],["Выход", "0", "1"]]

    uid = update.message.from_user.id
    chat_id = update.message.chat.id
    if update.message.text == 'выход' or update.message.text == "Выход":
        bot.sendPhoto(photo=open("luna_lost.jpg", "rb"), chat_id=chat_id)
        response =  "Потеряна связь с аппаратом..."
        keyboard = [["Заново"]]
        bot.sendMessage(chat_id=chat_id, text=response, reply_markup=telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return db.delete("moon%d" % uid)
    data = db.get("moon%d" % uid)
    if data:
        h, m, v, t = json.loads(data)
    else:
        h = 7000
        m = 1500
        v = 1000
        t = 0
        db.set("moon%d" % uid, json.dumps([h, m, v, t]))
        response = """Добро пожаловать в Центр управления полетом, командир!
Вы управляете лунным модулем, ваша задача - тормозя двигателем, посадить модуль на поверхность Луны без аварии. Запас горючего ограничен."""
        bot.sendPhoto(photo=open("luna_start.jpg", "rb"), chat_id=chat_id)
        keyboard = [["Поехали!"]]
        bot.sendMessage(chat_id=chat_id, text=response, reply_markup=telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return
    z = 0
    if m > m_empty and t:
        z = update.message.text
        if z == 'выход' or z == 'Выход':
            bot.sendPhoto(photo=open("luna_lost.jpg", "rb"), chat_id=chat_id)
            response =  "Потеряна связь с аппаратом..."
            keyboard = [["Заново"]]
            bot.sendMessage(chat_id=chat_id, text=response, reply_markup=telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            return db.delete("moon%d" % uid)
        try:
            z = int(z) if z else 0
        except:
            z = 0
            response += "Ввод не распознан, тяга 0\n"
        if z > m - m_empty:
            z = m - m_empty
            response += "Недостаточно топлива, тяга %d\n" % z
        if z < 0:
            z = 0
            response += "Ввод не распознан, тяга 0\n"
        if z > 100:
            z = 100
            response += "Установлена максимальная тяга 100\n"
    elif t:
        keyboard = [["Выход","Дальше"]]
    dt = 1
    p = m * v
    dp = z * vz
    m = m - z
    dv = dp/m
    dv_fall = g * dt
    v = v - dv + dv_fall
    dh = v * dt
    h = h - dh
    t += dt
    db.set("moon%d" % uid, json.dumps([h, m, v, t]))
    response +=  "%d. Высота %.1f м    \nСкорость %.1f м/cек\nТопливо %.0f кг" % (t, h, v, m - m_empty)
    if m <= m_empty and z:
        response +=  "\nТопливо закончилось. Скорее всего, это конец..\n"
        keyboard = [["Выход","Дальше"]]
    if t<2:
        response += "\n--\nВведите тягу (0-100)"
    if h > 25000:
        bot.sendPhoto(photo=open("luna_far.jpg", "rb"), chat_id=chat_id)
        response =  "Аппарат ушел слишком далеко в космос, мы теряем с ним связь. Это конец..."
        keyboard = [["Заново"]]
        bot.sendMessage(chat_id=chat_id, text=response, reply_markup=telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return db.delete("moon%d" % uid)
    if h < 2:
        if v > 5:
            bot.sendPhoto(photo=open("luna_crash.jpg", "rb"), chat_id=chat_id)
            response =  "Бах! Скорость %.1f м/c была слишком велика! Аппарат разрушился от удара о поверхность Луны" % v
            if v > 15:
                response =  "Бадуум! Аппарат врезался в поверхность Луны на скорости %.1f м/c и разлетелся на осколки. Всё кончено..." % v
        else:
            bot.sendPhoto(photo=open("luna_success.jpg", "rb"), chat_id=chat_id)
            response =  "Аппарат выпустил шасси и мягко коснулся поверхности Луны. Вы успешно провели эту нелегкую миссию за %d секунд. Мои поздравления, командир!" % t
        keyboard = [["Заново"]]
        bot.sendMessage(chat_id=chat_id, text=response, reply_markup=telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return db.delete("moon%d" % uid)

    if keyboard:
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    else:
        reply_markup = telegram.ReplyKeyboardHide()

    bot.sendMessage(chat_id=chat_id, text=response, reply_markup=reply_markup)



if __name__ == '__main__':
    print('Bot started')
    loop()
