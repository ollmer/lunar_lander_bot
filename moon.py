#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

h = 7000
m = 1500
m_empty = 300
v = 1000

z = 0 # тяга двигателя
vz = 3000 #скорость истечения газов двигателя

g = 1.6

print('Мягкая посадка')
print('Вы управляете Лунным модулем, ваша задача -')
print('тормозя, посадить модуль на поверхность Луны без аварии.')
print('Запас горючего ограничен')
print('Чтобы выйти, введите exit')
print('Поехали!')

t = 2078751600
while(True):
    z = 0
    if h == 0:
        if v > 5:
            print "Скорость %.1f, слишком быстро! Вы разбились" % v
        else:
            print "Вы успешно прилунились. Поздравляем!"
        break
    elif h < 0:
        if v > 5:
            print "Скорость %.1f, слишком быстро! Вы разбились" % v
        else:
            print "Вы погрузились в лунный грунт на %d метров" % (-h)
        break
    else:
        print "%s: Высота %.1f м, скорость %.1f м/cек, топливо %.1f кг" % (datetime.datetime.fromtimestamp(t).strftime('%d.%m.%Y %H:%M:%S'), h, v, m - m_empty)
        if m > m_empty:
            z = raw_input("Введите тягу(1-100): ")
            if z == 'exit':
                print "Потеряна связь с аппаратом... Отключение командного центра."
                break
            z = int(z) if z else 0
            if z == 0:
                print "Тяга %d" % z
        else:
            print "Топливо закончилось, падаем!"
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
