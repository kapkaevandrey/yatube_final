# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
# api_final

### _Описание проекта_

> ***Марк Туллий Цицерон***
>>Ничто так не сближает, как сходство характеров.
>>
Проект небольшой социальной сети. 
Позволяет публиковать собственные заметки и размещать к ним фото или любую другую картинку (желательно приличного содержания). Данный проект позволяет найти друзей, узнать что-нибудь новое и сделать это мир немного лучше.

### _Технологии_
 - _[Python 3.9.7](https://docs.python.org/3/)_
 - _[Django 2.2.16](https://docs.djangoproject.com/en/2.2/)_
 - _[Pillow 8.3.1](https://pillow.readthedocs.io/en/stable/)_


### _Как запустить проект_:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/kapkaevandrey/api_final_yatube.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
python3 pip install -r requirments.txt
```



### _Что могут делать пользователи_:

**Зарегистрированные :innocent:** пользователи могут:
1. Просматривать, публиковать, удалять и редактировать свои публикации;
2. Просматривать, информацию о сообществах;
3. Просматривать, публиковать комментарии от своего имени к публикациям других пользователей *(включая самого себя)*, удалять и редактировать **свои** комментарии;
4. Подписываться на других пользователей и просматривать **свои** подписки.
***Примечание***: Доступ ко всем операциям записи, обновления и удаления доступны только после аутентификации и получения токена.

**Анонимные :alien:** пользователи могут:
1. Просматривать, публикации;
2. Просматривать, информацию о сообществах;
3. Просматривать, комментарии;

### _Набор доступных эндпоинтов :point_down:_:
* ```posts/``` - отображение постов и публикаций (_GET, POST_).
* ```posts/{id}``` - Получение, изменение, удаление поста с соответствующим **id** (_GET, PUT, PATCH, DELETE_).
* ```posts/{post_id}/comments/``` - Получение комментариев к посту с соответствующим **post_id** и публикация новых комментариев(_GET, POST_).
* ```posts/{post_id}/comments/{id}``` - Получение, изменение, удаление комментария с соответствующим **id** к посту с соответствующим **post_id** (_GET, PUT, PATCH, DELETE_).
* ```posts/groups/``` - Получение описания зарегестрированных сообществ (_GET_).
* ```posts/groups/{id}/``` - Получение описания сообщества с соответствующим **id** (_GET_).
* ```posts/follow/``` - Получение информации о подписках текущего пользователя, создание новой подписки на пользователя (_GET, POST_).



#### Автор
Капкаев Андрей
>*Улыбайтесь - это всех раздражает :relaxed:.*
