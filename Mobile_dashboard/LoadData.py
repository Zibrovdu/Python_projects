import pandas as pd
from datetime import timedelta


def LoadEtspData():
    df = pd.read_excel('assets/Выгрузка.xlsx')
    df['Дата решения'].fillna('2020-12-01 00:00:00', inplace=True)
    df['Дата решения'] = pd.to_datetime(df['Дата решения'])
    df['timedelta'] = df['Дата решения'] - df['Дата регистрации']

    empl_df = pd.read_excel('assets/employes.xlsx', usecols='B,C')
    df = df.merge(empl_df, how='left', left_on=['Затронутый пользователь'], right_on=['фио'])
    df.drop('фио', axis=1, inplace=True)

    df['month_open'] = df['Дата регистрации'].dt.month
    df['month_solved'] = df['Дата решения'].dt.month
    df['count_task'] = 1
    df['start_date'] = df['Дата регистрации'].dt.date.apply(lambda x: str(x))
    df['finish_date'] = df['Дата решения'].dt.date.apply(lambda x: str(x))

    return df


def LoadSueData():
    df = pd.read_excel('assets/exportSD.xlsx', usecols='K,M,R,V,X,AK')
    df['Фактическое время выполнения'].fillna('2020-12-01 00:00:00', inplace=True)
    df['Описание'].fillna(' ', inplace=True)
    df['Фактическое время выполнения'] = pd.to_datetime(df['Фактическое время выполнения'])
    df['timedelta'] = df['Фактическое время выполнения'] - df['Дата/время регистрации']

    empl_df = pd.read_excel('assets/employes.xlsx', usecols='B,C')
    df = df.merge(empl_df, how='left', left_on=['Получатель услуг'], right_on=['фио'])
    df.drop('фио', axis=1, inplace=True)

    df['month_open'] = df['Дата/время регистрации'].dt.month
    df['month_solved'] = df['Фактическое время выполнения'].dt.month
    df['count_task'] = 1
    df['start_date'] = df['Дата/время регистрации'].dt.date.apply(lambda x: str(x))
    df['finish_date'] = df['Фактическое время выполнения'].dt.date.apply(lambda x: str(x))

    return df


def GetTimeData(df):
    delta_4h, delta_8h, delta_24h, delta_5d = timedelta(hours=4), timedelta(hours=8), timedelta(hours=24), timedelta(
        days=5)

    time_dict = {'до 4-х часов': df[df['timedelta'] <= delta_4h].count_task.sum(),
                 'от 4-х до 8-ми часов': df[(df.timedelta <= delta_8h) & (df.timedelta > delta_4h)].count_task.sum(),
                 'от 8-ми до 24-х часов': df[(df.timedelta <= delta_24h) & (df.timedelta > delta_8h)].count_task.sum(),
                 'от 1-го до 5-ти дней': df[(df.timedelta <= delta_5d) & (df.timedelta > delta_24h)].count_task.sum(),
                 'свыше 5-ти дней': df[df.timedelta > delta_5d].count_task.sum()}
    df1 = pd.DataFrame.from_dict(time_dict, orient='index')

    list_mean_time = [df[df.timedelta <= delta_4h].timedelta.mean(),
                      df[(df.timedelta <= delta_8h) & (df.timedelta > delta_4h)].timedelta.mean(),
                      df[(df.timedelta <= delta_24h) & (df.timedelta > delta_8h)].timedelta.mean(),
                      df[(df.timedelta <= delta_5d) & (df.timedelta > delta_24h)].timedelta.mean(),
                      df[df.timedelta > delta_5d].timedelta.mean()]
    df1.reset_index(inplace=True)
    df1.rename(columns={'index': 'time_task', 0: 'count_task'}, inplace=True)

    df1['persent_task'] = 0
    df1['mean_time'] = 0
    for num in range(len(df1)):
        df1.loc[num, ['persent_task']] = df1.loc[num, ['count_task']].iloc[0] / df1['count_task'].sum()
        df1.loc[num, ['mean_time']] = list_mean_time[num]

    return df1


def GetIntent(df):
    pd.options.mode.chained_assignment = None

    df['Описание'] = df['Описание'].fillna('missed value')
    df['Описание'] = df['Описание'].apply(lambda x: str(x).lower())

    temp_df = pd.DataFrame(columns=['num', 'text', 'intent'])
    for i in range(len(df)):
        temp_df.loc[i] = i, df['Описание'].loc[i], ''

    conf = {
        'intents': {
            "1С ЭБ": ['эб', 'элбюджету', 'элбюджета', 'эб', 'элбюджета', ' 1с ', ' 1c ', 'базу 1с ', ' систему 1с ',
                      ' 1c ', 'электронным бюджетом', 'не заходит в 1с', '1с,', 'в 1с, ', '1с:предприятие', '1с:п',
                      '1 c ', '1с-облако', 'электронный бюджет', '-1с', 'эл.бюджет', '1с.', 'в 1с.', '1с в', ' с 1с',
                      'эл.бюджет', ' работает 1 с ', 'базе 1 с', 'бюджету', 'электронный', 'бюджет'],
            'ЛанДокс': ['lan docs', 'ландокс', 'лан докс', 'landocs', 'лаандокс'],
            'ЗКВС': ['звкс', 'зквс', 'vdi', 'getmobit', ' закрытый контур', 'контур'],
            'Электронная почта': ['почта ', 'аутлук', 'сбросить', 'пароль от почты', 'пароль от пя', ' входом почту',
                                  'сменить пароль', 'пароля от уз', 'действия пароля', ' востановить пароль',
                                  'изменить пароль', 'обновить пароль', 'нового правила', 'настроить почту',
                                  'почта работает', 'работает почт', 'outlook', 'почтой', 'правила почты',
                                  'правило почты', 'аутлук', 'настройка почты', 'подключение почты ', 'почты',
                                  'работает аутлук', 'почтовый ящик', 'почтового ящика', 'оутлук', 'настройка почты ',
                                  'отправляется письмо ', 'сменить пароль'],
            'настройка ЭП': [' эп ', 'эцп', 'эцпп', 'эцп', 'эцп', 'эцпп', 'эцп ', 'новую эп', 'настроить криптопро',
                             'криптопро', ' лицензию крипто', 'криптоарм', 'крипто арм ', 'эцпп'],
            'не работают базы (ПУиОТ)': ['пуиот', 'пу и от'],
            'установка 1С «Тонкий Клиент»': ['тонкий', 'клиент', 'тонкие', 'клиенты', 'tionix', 'thinclient',
                                             ' тонкий клиент', 'документы печать'],
            'установка банк-клиент': ['банк-клиент'],
            'не работает СУЭ ФК': ['суэ фк', 'суэ'],
            'Доступ': ['доступ ', 'доступа ', 'могу войти', 'войти', 'зайти на диск', 'не могу зайти',
                       'ошибки при входе', 'не дает зацти', 'получается зайти', 'не дает зайти',
                       'предоставить логин и пароль', 'сетевых', 'папок', 'диске', 'ресурсу', 'ресурс', 'сетевой',
                       'папке', 'папку', 'общий', 'диск', 'сетевую папку', 'сетевая папка', 'сетевым папкам',
                       'работает интернет', 'интернетом', ' доступ сайт', 'wi fi', 'настройка доступа',
                       'доступа интернет', ' доступ сайту', 'wifi', 'нету интернета', 'доступ порталу', 'работает сайт',
                       'подключения интернету', ' портала'],
            'Органайзер': ['органайзер', 'БГУ ', ' ЗКГУ ', 'модуль бухгалтерия', 'ошибка крипто провайдера ',
                           'не установлено расширение'],
            'ПУР': ['пур', 'п у р'],
            'ПУИО': ['пуио', 'пу и о'],
            'ПУОТ': ['пуот', 'пу о т '],
            'не подписывается документ': ['не может подписать', 'подписью', 'возможности подписать',
                                          'ошибка при подписании', 'документ не удается', 'подписать документ',
                                          'подписывает документ', 'подписать документы', 'jinn', 'client', 'стороннее',
                                          ' cisco ', ' jinn ', ' справкибк', ' справки бк', ' впн клиента ', ' cisco ',
                                          ' jinn ', ' справкибк', ' справки бк', ' впн клиента '],
            'Настройка печати': ['пинкод ', ' pin ', 'инкод ', ' пин ', 'код доступа', 'пин-код', 'печаль',
                                 'пикод печати', 'код использования', 'принтеры', 'настройка печати', 'печатается файл',
                                 'доступ принтеру', 'настроить печать', 'документов печать', 'подключить принтер',
                                 'печати ', 'печатью ', 'пароль печати'],
            'Замена РМ': ['тонер', 'мало', 'картридж', 'картриджа', 'пурпурный', 'замяло бумагу', 'зажевывает',
                          'зажевал'],
            'Работа с техникой': ['вкл пк', ' монитор ', ' спящего ', ' режима ', ' включается ', 'завис пк',
                                  ' сломался', 'мышки', 'клавиатура ', ' мышь ', ' kvm ', ' свитч ', ' переключатель ',
                                  'switch', ' nd телефон '],
            'Перемещение рабочих мест': ['переноса', 'переноса рабоч', 'перенос мест', 'перенести рабочее',
                                         'переместить с', 'переместить сотрудника', 'перенос ', ' пересадить '],
            'скуд': ['скуд', 'замок'],
            'консультант +': ['консультант +', 'консультантплюс', 'консультант+', ' консультант', 'консультанте плюс '],
            'Новый сотрудник': ['полная', 'первичная', 'сотруднику', 'организовать', 'рабочее', 'полная', 'организация',
                                'нового', 'организация рабоч', 'создать учетную запись'],
        }
    }

    for item, value in conf['intents'].items():
        for i in value:
            mask = temp_df['text'].str.contains(i)
            temp_df.loc[mask, 'intent'] = item

    total_df = pd.DataFrame(columns=['num', 'text', 'intent'])

    df3 = temp_df[temp_df.loc[:, 'intent'] == '1С ЭБ']
    mask = df3['text'].str.contains('работает')
    df3.loc[mask, 'intent'] = 'не работает (1С ЭБ)'

    df4 = temp_df[temp_df['intent'] == 'ЛанДокс']
    mask = df4['text'].str.contains('настроить ')
    df4.loc[mask, 'intent'] = 'настроить ЛанДокс'

    df5 = temp_df[temp_df['intent'] == 'ЗКВС']
    mask = df5['text'].str.contains('работает', 'установка')
    df5.loc[mask, 'intent'] = 'установка (не работает) ЗКВС'

    total_df = df3.append(df5[df5.intent == 'установка (не работает) ЗКВС'])

    df5 = df5[df5.intent == 'ЗКВС']

    df6 = df5.append(df4)

    mask = df6['text'].str.contains('настроить ')
    df6.loc[mask, 'intent'] = 'настроить (ЛанДокс, ЗКВС)'

    total_df = total_df.append(df6[df6.intent == 'настроить (ЛанДокс, ЗКВС)'])
    total_df = total_df.append(df6[df6.intent == 'ЛанДокс'])

    df7 = df6[df6.intent == 'ЗКВС'].append(temp_df[temp_df['intent'] == 'Электронная почта'])

    mask = df7['text'].str.contains('сброс', 'парол')
    df7.loc[mask, 'intent'] = 'сброс пароля (почта, ЗКВС)'

    total_df = total_df.append(df7)

    total_df = total_df.append(temp_df[temp_df['intent'] == 'ПУИО'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'ПУР'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'ПУОТ'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Органайзер'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Доступ'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'не работает СУЭ ФК'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'настройка ЭП'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'не работают базы (ПУиОТ)'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'не подписывается документ'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'установка 1С «Тонкий Клиент»'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'консультант +'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Новый сотрудник'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Настройка печати'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Работа с техникой'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Замена РМ'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'скуд'])

    total_df = total_df.append(temp_df[temp_df['intent'] == 'Перемещение рабочих мест'])

    temp_df1 = temp_df.drop(list(total_df.num), axis=0)
    temp_df1.intent = 'Прочие обращения'
    total_df = total_df.append(temp_df1)

    df.reset_index(inplace=True)
    df.rename(columns={'index': 'num'}, inplace=True)
    merged_df = pd.DataFrame()
    merged_df = df.merge(total_df[['num', 'intent']], on='num', how='left')
    merged_df.drop('num', axis=1, inplace=True)
    df.drop('num', axis=1, inplace=True)

    temp_df, df3, df4, df5, df6, df7, total_df, temp_df1 = 0, 0, 0, 0, 0, 0, 0, 0

    return merged_df


def EtspCountMeanTime(etsp_filtered_df):
    etsp_duration = etsp_filtered_df['timedelta'].mean()
    etsp_count_tasks = etsp_filtered_df['count_task'].sum()

    # преобразование в дни, часы, минуты и секунды
    days, seconds = etsp_duration.days, etsp_duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    avg_time_etsp = days, hours, minutes, seconds

    if etsp_count_tasks == 0:
        etsp_avg_time = 'Данные отсутствуют'
    elif avg_time_etsp[0] == 0:
        etsp_avg_time = f'{avg_time_etsp[1]} час. {avg_time_etsp[2]} мин.'
    else:
        etsp_avg_time = f'{avg_time_etsp[0]} дн. {avg_time_etsp[1]} час. {avg_time_etsp[2]} мин.'

    return etsp_avg_time


def SueCountMeanTime(sue_filtered_df):
    sue_duration = sue_filtered_df['timedelta'].mean()
    sue_count_tasks = sue_filtered_df['count_task'].sum()

    # преобразование в дни, часы, минуты и секунды
    days, seconds = sue_duration.days, sue_duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    avg_time_sue = days, hours, minutes, seconds

    if sue_count_tasks == 0:
        sue_avg_time = 'Данные отсутствуют'
    elif avg_time_sue[0] == 0:
        sue_avg_time = f'{avg_time_sue[1]} час. {avg_time_sue[2]} мин.'
    else:
        sue_avg_time = f'{avg_time_sue[0]} дн. {avg_time_sue[1]} час. {avg_time_sue[2]} мин.'

    return sue_avg_time


def LoadInfSystemsData():
    df = pd.read_excel('data.xlsx', sheet_name='Работа в ИС', usecols='A,D:O')
    df.dropna(axis=0, inplace=True)
    df['Unnamed: 0'] = df['Unnamed: 0'].astype(int)
    df = df.T
    new_header = df.iloc[0]  # grab the first row for the header
    df = df[1:]  # take the data less the header row
    df.columns = new_header  # set the header row as the df header

    return df
