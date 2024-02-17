import enum

class Commands(enum.Enum):
    HI = 0           # args: user_name
    ECHO = 1         # args: text_to_return
    QUIT = 2         # args: no
    TIME = 3         # args: no
    UPLOAD = 4       # args: file_name file_size(скрытый)
    DOWNLOAD = 5     # args: file_name
    LIST = 6         # args: no
    NOTCOMMAND = 7

class ResponseCodes(enum.Enum):
    SUCCESS = 200
    UNFINISHED_UP = 201   # нужны доп. действия
    UNFINISHED_DOWN = 202
    ERROR = 400


"""
    Пример взаимодействия
    - ECHO текст текст -> разделить и отправить
    - клиент ждет ответ (набор байт, что преобразуются в строку)
    - 200&текст текст&аргум2

    
    UPLOAD
        UPLOAD cat.jpg (UPLOAD cat.jpg размер_файла(строкой))- разбить на команду-обьект класса, лист строк
        отправить
        клиент получает "200" -> клиент шлет по 64кб -> ввод пользователя
                        "400" -> вывод ошибки

    
"""
    