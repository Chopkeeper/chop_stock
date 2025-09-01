import datetime
def generate_doc_number(prefix, last_number=0):
    today = datetime.datetime.now().strftime('%Y%m%d')
    number = f'{last_number+1:03d}'
    return f'{prefix}-{today}-{number}'
