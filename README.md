# vkpdevtools
Инструменты для работы с **кабинетом разработчика** VK Play.

# achtool.py

Импортирует достижения из Steamworks Stats VDF файла в кабинет VK Play.

У VK Play есть кнопка "Импорт из файла"... только вот она не работает.

![image](https://github.com/nkrapivin/vkpdevtools/assets/33228822/1734025a-a29b-40ce-9185-0bfc2f740f21)

Короче девиз вк плея - "Хочешь что-то сделать, делай это сам!" Спасибо, я то сделаю, мне не сложно, а другие что?

```
.\achtool.py -h
usage: achtool.py [-h] [--game_id GAME_ID] [--vdf VDF] [--csrf CSRF] [--csrf_jwt CSRF_JWT] [--cookies COOKIES]

A tool to autoimport Stats from Steamworks into VK Play

options:
  -h, --help           show this help message and exit
  --game_id GAME_ID    Internal game id on VK dashboard
  --vdf VDF            Path to the Stats VDF file from Steamworks
  --csrf CSRF          CSRF token
  --csrf_jwt CSRF_JWT  CSRF JWT token from multipart
  --cookies COOKIES    Cookie string from Headers
```

"game_id" это `ID Игры (GMRID)` из системных свойств, он как правило отличается от GC ID и ID Эмуляции Steam.

"vdf" это текст из Steamworks Settings -> View Raw Settings -> Stats, скопировать полностью и сохранить в .vdf файл.

"csrf" это CSRF токен из заголовков к апи запросам, узнать можно из Chrome DevTools.

"csrf_jwt" узнать сложнее, нужно сделать какой-нибудь запрос делающий multipart post реквест и внутри него в мультипарте будет он.

"cookies" это просто строка кукисов из тех же заголовков девтулза, та что `a=aaa; b=bbb; c=ccc`.
