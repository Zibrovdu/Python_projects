print("Добро пожаловать в простой калькулятор версии 1.1")
print("Калькулятор выполняет математические операции над двумя числами")
print("Доступны следующие операции: ", "Сложение (+);", "Вычитание (-);", "Умножение (*);", "Деление (/)",
      "Возведение в степень (**);", "Корень (^);", sep='\n')


def calc():
    """Функция выполняет математические операции над двумя числами
    Доступны следующие операции:
    Сложение (+)
    Вычитание (-)
    Умножение (*)
    Деление (/)
    Возведение в степень (**)
    """
    a = float(input("Введите первое число: "))
    y = input("Введите действие: ")
    b = float(input("Введите второе число: "))
    if y == '+':
        x = a + b
        print("Результат: " + str(x))
    elif y == '-':
        x = a - b
        print("Результат: " + str(x))
    elif y == '*':
        x = a * b
        print("Результат: " + str(x))
    elif y == '/':
        if b == 0:
            print("На 0 делить нельзя. Пожалуйста попробуйте снова.")
        else:
            x = a / b
            print("Результат: " + str(x))
    elif y == '**':
        x = a ** b
        print("Результат: " + str(x))
    elif y == '^':
        x = pow(a, 1 / b)
        print("Результат: " + str(x))
    else:
        print("Команда нераспознана. Попробуйте еще раз.")


calc()

while True:
    flag = input('Чтобы продолжить работу введите "Да". Для выхода из программы введите "Нет": ')

    if flag == 'да':
        calc()
    elif flag == 'Yes':
        calc()
    elif flag == 'Да':
        calc()
    elif flag == 'yes':
        calc() 
    else:
        break