# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

Демо-версия сайта доступна по адресу [https://lypavel.ru](https://lypavel.ru)

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

## Как запустить dev-версию сайта

Для запуска сайта используются Docker-контейнеры. Необходимо одновременно запустить контейнеры с фронтэндом, бекэндом и базой данных.

1. Установите [Docker](https://docs.docker.com/engine/install/), если это не было сделано ранее.
2. Скачайте код
    ```sh
    git clone https://github.com/devmanorg/star-burger.git
    ```
3. Создайте в корне директории с проектом файл `.env`, внесите в него необходимые данные:
    ```ini
    DEBUG=True  # дебаг-режим, обязательно True для dev-версии
    SECRET_KEY=секретный_ключ_джанго

    ALLOWED_HOSTS=список разрешённых хостов
    DEBUG_TOOLBAR_IP=список разрешённых хостов для отображения Django Debug Toolbar

    YANDEX_GEOCODER_KEY=api ключ yandex геокодера

    ROLLBAR_POST_SERVER_ITEM_TOKEN=api ключ сервиса логгирования Rollbar
    ROLLBAR_ENVIRONMENT='development'  # название среды для Rollbar

    POSTGRES_USER=имя пользователя базы данных
    POSTGRES_PASSWORD=пароль пользователя базы данных
    POSTGRES_DB=star_burger  # название базы данных

    POSTGRES_DB_URL='postgresql://user:password@host:port/name'  # url postgres БД для Django
    ```
4. Перейдите в директорию `dev/`:
    ```sh
    cd star-burger/dev/
    ```
5. Запустите скрипт сборки dev-версии
    ```sh
    ./build_dev.sh
    ```
6. Проверьте, что всё работает
    ```sh
    >>> docker-compose ps
            Name                      Command               State                    Ports
    --------------------------------------------------------------------------------------------------------
    star_burger_backend    python manage.py runserver ...   Up      0.0.0.0:8000->8000/tcp,:::8000->8000/tcp
    star_burger_frontend   docker-entrypoint.sh ./nod ...   Up
    star_burger_postgres   docker-entrypoint.sh postgres    Up      0.0.0.0:5432->5432/tcp,:::5432->5432/tcp
    ```

## Как запустить prod-версию сайта

1. Установите [Docker](https://docs.docker.com/engine/install/), если это не было сделано ранее.
2. Скачайте код
    ```sh
    git clone https://github.com/devmanorg/star-burger.git
    ```
3. Создайте в корне директории с проектом файл `.env`, внесите в него необходимые данные:
    ```ini
    DEBUG=False  # дебаг-режим, обязательно False для prod-версии
    SECRET_KEY=секретный_ключ_джанго

    ALLOWED_HOSTS=список разрешённых хостов
    DEBUG_TOOLBAR_IP=список разрешённых хостов для отображения Django Debug Toolbar

    YANDEX_GEOCODER_KEY=api ключ yandex геокодера

    ROLLBAR_POST_SERVER_ITEM_TOKEN=api ключ сервиса логгирования Rollbar
    ROLLBAR_ENVIRONMENT='production'  # название среды для Rollbar

    POSTGRES_USER=имя пользователя базы данных
    POSTGRES_PASSWORD=пароль пользователя базы данных
    POSTGRES_DB=star_burger  # название базы данных

    POSTGRES_DB_URL='postgresql://user:password@host:port/name'  # url postgres БД для Django
    ```
4. Перейдите в директорию `prod/`:
    ```sh
    cd star-burger/prod/
    ```
5. Запустите скрипт сборки prod-версии
    ```sh
    sudo ROLLBAR_SERVER_POST_TOKEN=rollbar_token ./deploy.sh
    ```
6. Проверьте, что всё работает
    ```sh
    >>> docker-compose ps
            Name                      Command               State                     Ports
    ---------------------------------------------------------------------------------------------------------
    star_burger_backend    gunicorn -w 5 -b 0.0.0.0:8 ...   Up       127.0.0.1:8000->8000/tcp
    star_burger_frontend   docker-entrypoint.sh ./nod ...   Exit 0
    star_burger_postgres   docker-entrypoint.sh postgres    Up       0.0.0.0:5432->5432/tcp,:::5432->5432/tcp
    ```

Файлы статики будут находиться в директории `staticfiles/` в корне проекта.
Медиа файлы будут находиться в директории `media/` в корне проекта.

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного курса Django](https://dvmn.org/modules/django/)
- Второй урок [учебного курса Docker](https://dvmn.org/modules/docker-v2/)
