# Бердск — Кученков Степан

Статический сайт цикла аналитических статей Степана Кученкова о бюджете и устройстве власти Бердска.

Опубликованные материалы:

- «Бердский бюджет. Как тратят деньги?»
- «Бердский бюджет. Откуда приходят деньги?»

## Локальный просмотр

Откройте папку через любой статический веб-сервер. Для пересборки первой статьи нужен исходный HTML в `_import/article-word.htm`:

```powershell
C:\Users\Netscape\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\build_article.py
```

Вторая статья собирается из `_import/budget-revenues.docx`:

```powershell
C:\Users\Netscape\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe scripts\build_revenue_article.py
```

## Публикация

Сайт рассчитан на GitHub Pages из корня ветки `main`. Предполагаемый адрес:

`https://netscapenav.github.io/berdsk/`

Внешние библиотеки, рекламные блоки, аналитика и cookie не используются.
