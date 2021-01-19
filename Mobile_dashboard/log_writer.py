import datetime
import os


def log_writer(log_msg):
    current_date = datetime.datetime.now()
    write_date = current_date.strftime('%d-%m-%Y %H:%M:%S')

    filename_date = current_date.strftime('%d-%m-%Y')
    filepath = 'logs\\'

    if os.path.exists(filepath):
        f = open(f'{filepath + filename_date}.log', 'a')
        f.write(''.join([write_date, ': ', log_msg, '\n']))
        f.close()
    else:
        os.mkdir(filepath)
        f = open(f'{filepath + filename_date}.log', 'a')
        f.write(''.join([write_date, ': ', log_msg, '\n']))
        f.close()
