from random import randint
try:
    number = int(input("Введите число от 1 до 10: "))
    if number not in range(1,11):
        raise ValueError("НЕ В НАШЕМ ДИАПАЗОНЕ")
except ValueError:
    print("Ошибка: Неправильный формат ввода!")

while True:

    maybe_number = randint(1,10)
    try:
        unswer = int(input(f"""Ваше число равняется {maybe_number}
            1. ДА
            2. НЕТ
        """))
        if unswer!=1 and unswer!=2: raise ValueError()

    except ValueError:
        print("Неправильно ввели ответ!")
        continue
    
    if unswer == 1:
       print("Ура!")
       break

