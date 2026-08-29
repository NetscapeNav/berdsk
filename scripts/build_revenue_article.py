from __future__ import annotations

import html
import re
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_import" / "budget-revenues.docx"
OUTPUT = ROOT / "articles" / "budget-revenues" / "index.html"


def iter_blocks(document):
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, document)
        elif child.tag.endswith("}tbl"):
            yield Table(child, document)


def clean_text(value: str) -> str:
    exact = {
        "Согласно федеральному законодательству, 15% от НДФЛ уходит в бюджет муниципалитета.": "Для основной части НДФЛ Бюджетный кодекс устанавливает базовый норматив зачисления в бюджет городского округа — 15%.",
        "Таким образом, получается упрощённо около 42 рублей из каждых 100 рублей НДФЛ уходит в казну бюджета города Бердска.": "Таким образом, упрощённо около 42 рублей из каждых 100 рублей основной части НДФЛ поступают в бюджет Бердска.",
        "За 2025 год земельным налогом было набрано 86,2 миллионов рублей, а налогом на имущество физических лиц — 91,1 миллионов рублей. Вместе эти два налога дали Бердску 177,3 млн рублей — менее 3% всех доходов бюджета.": "В 2025 году земельный налог принёс 86,2 млн рублей, а налог на имущество физических лиц — 91,1 млн рублей. Вместе эти два налога дали Бердску 177,3 млн рублей — менее 3% всех доходов бюджета.",
        "В том же 2025 году в федеральном законодательстве появлся новый налог— туристический. Совет депутатов ввёл его на территории Бердска решением № 310 от 21 ноября 2024 года.. Его платят владельцы гостиниц, санаториев и других средств размещения, включённых в соответствующий реестр. Все собранные средства полностью уходят в бюджет муниципалитета.": "С 1 января 2025 года появился новый местный налог — туристический. Совет депутатов ввёл его на территории Бердска решением № 310 от 21 ноября 2024 года. Его платят владельцы гостиниц, санаториев и других средств размещения, включённых в соответствующий реестр. Все собранные средства полностью поступают в бюджет муниципалитета.",
        "Таким образом налогами Бердск смог получить налогами 1,79 миллиарда рублей. Полученная сумма — лишь часть от того, что уплатили бердчане.": "Таким образом, в 2025 году Бердск получил 1,79 млрд рублей налоговых доходов. Это лишь часть налогов, уплаченных жителями и организациями на территории города.",
        "Для сравнения возьмём 2024 год — последний завершённый период. Возьмём для сравнения Бердск, Юрга, Рубцовск и Северск как группа похожих городов с населением от 100 до 200 тысяч человек.": "Для сравнения возьмём завершённый 2025 год и группу городов с населением примерно от 100 до 200 тысяч человек: Бердск, Юргу, Рубцовск и Северск. При этом Северск имеет статус ЗАТО и особую систему финансирования.",
        "В предыдущей статье мы видели, что планируемый бюджет Бердска растёт с нынешних 5,9 млрд до 9,1 млрд рублей к 2028 году. Значит ли это, что город разбогатеет и сможет проводить более самостоятельную политику? Нет, как раз наоборот, почти весь рост обеспечивается не собственными доходами, а трансфертами.": "В предыдущей статье мы видели, что доходы бюджета Бердска должны вырасти с фактических 5,971 млрд рублей в 2025 году до 9,134 млрд к 2028-му. Значит ли это, что город разбогатеет и сможет проводить более самостоятельную политику? Нет: почти весь запланированный рост обеспечивается не собственными доходами, а трансфертами.",
        "Что это значит для города? Увеличение зависимости от региона ставит власти города в зависимое положение. Плохие результаты власти на выборах, отказ от исполнения требований федеральной или региональной власти, протесты депутатов, как на голосовании по выставлению “неуда” мэру, могут с лёгкостью привести к пересмотру бюджета Новосибирской области и отказу от финансирования инфрастуктурных проблем города. А отсутствие у городских властей публичной стратегии роста собственных доходов лишь подкрепляет эти опасения.": "Финансовая зависимость не означает, что область вправе произвольно лишить город денег за неугодное голосование: опубликованные документы такого механизма не подтверждают. Она проявляется практичнее — город зависит от региональных сроков, перечней объектов и условий программ и вынужден подстраивать свои проекты под внешнее финансирование. Поэтому критиковать следует не предполагаемый политический шантаж, а отсутствие у городских властей публичной стратегии роста собственной доходной базы.",
    }
    value = exact.get(value, value)
    value = value.replace("налог на доход физических лиц", "налог на доходы физических лиц")
    value = value.replace("инфрастуктурных", "инфраструктурных")
    value = value.replace("поступилия", "поступления")
    value = value.replace("налогооблажения", "налогообложения")
    value = value.replace("То есть, 169 миллионов", "То есть 169 миллионов")
    value = value.replace("в 2026 норматив составит", "в 2026 году норматив составляет")
    value = value.replace("в 2023-м — 5,8%", "в 2023-м — 5,9%")
    value = value.replace("конкурс сорван целевые", "конкурс сорван, целевые")
    value = value.replace("“", "«").replace("”", "»")
    return value.strip()


def slugify(value: str) -> str:
    letters = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    latin = ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "c", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya"]
    translit = str.maketrans(dict(zip(letters, latin)))
    value = value.lower().translate(translit)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "section"


def paragraph_html(paragraph: Paragraph) -> str:
    text = clean_text(paragraph.text)
    if not text:
        return ""
    escaped = html.escape(text)
    if paragraph.style.name == "Heading 2":
        return f'<h2 id="{slugify(text)}">{escaped}</h2>'
    if paragraph.style.name == "Heading 3":
        return f'<h3 id="{slugify(text)}">{escaped}</h3>'
    return f"<p>{escaped}</p>"


def normalized_table(table_index: int, table: Table):
    rows = [[clean_text(cell.text) for cell in row.cells] for row in table.rows]

    if table_index == 0:
        rows[-1][1] = "1 790,0"
        rows[8][2] = "0,15875% регионального пула (1,5875% муниципальной доли)"
    elif table_index == 1:
        rows[10][5] = "11,7"
        rows[11][0] = "ЕНВД прошлых лет и ЕСХН"
        rows[11][3] = "−0,7"
        rows[-1][5] = "1 790,0"
    elif table_index == 2:
        rows[0] = ["Структура неналоговых доходов Бердска за 2025 год"] * len(rows[0])
    elif table_index == 5:
        rows[0][2] = "Фактические поступления, млн руб."
    elif table_index == 6:
        rows[0] = [
            "Город",
            "Все доходы, млрд руб.",
            "Собственные доходы, млрд руб.",
            "Внешние поступления, млрд руб.",
            "Доля собственных доходов",
            "Доля внешних поступлений",
        ]
    elif table_index == 7:
        rows[0] = ["Прогноз доходов Бердска на 2026–2028 годы"] * len(rows[0])

    for row in rows:
        if row and re.fullmatch(r"2[\s\u202f]0\d{2}", row[0]):
            row[0] = row[0].replace(" ", "").replace("\u202f", "")
    return rows


def table_html(table_index: int, table: Table) -> str:
    rows = normalized_table(table_index, table)
    caption = None
    if len(rows[0]) > 1 and len(set(rows[0])) == 1:
        caption = rows.pop(0)[0]

    head = rows.pop(0)
    parts = ['<div class="table-block">']
    if caption:
        parts.append(f'<p class="table-caption">{html.escape(caption)}</p>')
    parts.append('<div class="table-wrap" tabindex="0" role="region" aria-label="Таблица с бюджетными данными"><table>')
    parts.append("<thead><tr>" + "".join(f'<th scope="col">{html.escape(cell)}</th>' for cell in head) + "</tr></thead>")
    parts.append("<tbody>")
    for row in rows:
        parts.append("<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row) + "</tr>")
    parts.append("</tbody></table></div></div>")
    if table_index == 1:
        parts.append('<p class="table-note">Отрицательная сумма за 2023 год относится не к туристическому налогу. По ЕНВД прошлых лет было отражено −737,7 тыс. рублей, по ЕСХН — +50,8 тыс.; вместе это −686,9 тыс. рублей, или −0,7 млн после округления.</p>')
    return "".join(parts)


def source_box() -> str:
    return """<section class="source-box" id="sources"><h2>Документы и источники</h2><ul>
      <li>Решения Совета депутатов Бердска № 69, 157, 245, 377 и 454 — исполнение бюджетов 2021–2025 годов.</li>
      <li>Решения № 278, 281, 310, 315, 386, 394, 400, 409 и 454; протоколы 28-й, 31-й, 32-й, 42–45-й, 49-й и 50-й сессий Совета депутатов Бердска.</li>
      <li><a href="https://berdsk-online.ru/wp-content/uploads/2026/05/byudzhet-berdska-za-2025g.pdf">Отчёт об исполнении бюджета Бердска за 2025 год</a>.</li>
      <li><a href="https://www.consultant.ru/document/cons_doc_LAW_19702/5a28766b76334b2eccf42fc690e981887d8c856c/">Бюджетный кодекс РФ, статья 61.2</a>; <a href="https://www.consultant.ru/document/cons_doc_LAW_19702/1e231e90031b99643b29b6eb4579016c2a06533f/">статья 58</a>; <a href="https://www.consultant.ru/document/cons_doc_LAW_19702/958d77bbceed0d6b2ee32ddbb1a6fb2572b4ab9f/">статья 138</a>.</li>
      <li><a href="https://base.garant.ru/7106602/">Закон Новосибирской области № 132-ОЗ</a>; законы об областном бюджете <a href="http://publication.pravo.gov.ru/document/5400202412200002">№ 546-ОЗ</a> и <a href="http://publication.pravo.gov.ru/document/5400202512220001">№ 37-ОЗ</a>.</li>
      <li><a href="https://asdg.ru/about/struct/sobr/XLII/6_Analis_byudzh_2022_2024_plan_2025.pdf">Сравнительный анализ бюджетов городов АСДГ</a>.</li>
      <li><a href="https://www.yurga.org/upload/files/deyatelnost/ekonomika/finansy-i-kredit/budget-dlya-grajdan/IBudgGr_2025-2027_reshenie.pdf">Официальный отчёт Юрги за 2025 год</a>, <a href="https://rubtsovsk.org/node/byudzhet-rubcovska-za-2025-god-ispolnen-dokhody-prevysili-raskhody">отчёт Рубцовска</a> и <a href="https://xn--80appbun8c.xn----7sbhlbh0a1awgee.xn--p1ai/uploads/ckfinder/userfiles/files/%D0%91%D1%8E%D0%B4%D0%B6%D0%B5%D1%82%20%D0%B4%D0%BB%D1%8F%20%D0%B3%D1%80%D0%B0%D0%B6%D0%B4%D0%B0%D0%BD%202025%20%D0%9E%D0%A2%D0%A7%D0%95%D0%A2_%D1%81%D0%B0%D0%B9%D1%82.pdf">отчёт Северска</a>.</li>
    </ul><p>Все суммы округлены. Плановые показатели отделены от фактических.</p></section>"""


def build():
    document = Document(SOURCE)
    body = []
    table_index = 0
    list_prefixes = (
        "33,9 млн рублей аренды земельных участков",
        "7 млн рублей аренды имущества",
        "4,6 млн рублей аренды имущества",
        "6,4 млн рублей платы",
        "4,7 млн рублей платы",
        "около 5,3 млн рублей других имущественных",
        "2,176 млрд рублей на выполнение",
        "724,7 млн рублей прочих",
        "162,2 млн рублей на капитальные",
        "84,1 млн рублей на дорожную",
        "69,4 млн рублей на бесплатное",
        "56 млн рублей на модернизацию",
        "53,2 млн рублей на выплаты",
        "44,9 млн рублей на формирование",
        "15 млн рублей на создание",
        "2,8 млн рублей на поддержку",
    )
    list_open = False
    for block in iter_blocks(document):
        if isinstance(block, Paragraph):
            cleaned = clean_text(block.text)
            is_list_item = any(cleaned.startswith(prefix) for prefix in list_prefixes)
            if is_list_item:
                if not list_open:
                    body.append('<ul class="compact-list">')
                    list_open = True
                rendered = f"<li>{html.escape(cleaned)}</li>"
            else:
                if list_open:
                    body.append("</ul>")
                    list_open = False
                rendered = paragraph_html(block)
        else:
            if list_open:
                body.append("</ul>")
                list_open = False
            rendered = table_html(table_index, block)
            table_index += 1
        if rendered:
            body.append(rendered)
    if list_open:
        body.append("</ul>")
    body.append(source_box())
    article_body = "\n".join(body)

    page = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Бердский бюджет. Откуда приходят деньги? — Степан Кученков</title>
  <meta name="description" content="Разбор собственных доходов, налогов и трансфертов Бердска, сравнение с другими городами и анализ работы Совета депутатов.">
  <meta name="author" content="Степан Кученков">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#111311" media="(prefers-color-scheme: dark)">
  <meta property="og:type" content="article">
  <meta property="og:title" content="Бердский бюджет. Откуда приходят деньги?">
  <meta property="og:description" content="Какая часть налогов остаётся в Бердске и почему большой бюджет не означает финансовую самостоятельность города.">
  <meta property="og:image" content="https://netscapenav.github.io/berdsk/assets/og-budget-revenues.svg">
  <meta property="og:url" content="https://netscapenav.github.io/berdsk/articles/budget-revenues/">
  <link rel="canonical" href="https://netscapenav.github.io/berdsk/articles/budget-revenues/">
  <link rel="icon" href="../../assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../../assets/site.css?v=20260829-1">
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article","headline":"Бердский бюджет. Откуда приходят деньги?","datePublished":"2026-08-29","dateModified":"2026-08-29","inLanguage":"ru","author":{{"@type":"Person","name":"Степан Кученков"}},"publisher":{{"@type":"Person","name":"Степан Кученков"}}}}</script>
</head>
<body>
  <a class="skip-link" href="#article">К статье</a>
  <div class="progress" data-progress aria-hidden="true"></div>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="../../">Бердск <span>·</span> Кученков Степан</a>
      <button class="nav-toggle" data-nav-toggle aria-expanded="false" aria-label="Открыть меню">Меню</button>
      <nav class="site-nav" data-site-nav aria-label="Основная навигация">
        <a href="../../">Главная</a>
        <a href="https://berdsk2026.ru/">Бердск 2026 <span aria-hidden="true">↗</span></a>
      </nav>
    </div>
  </header>

  <main>
    <header class="article-hero">
      <div class="article-hero-inner">
        <p class="eyebrow">Авторская аналитика · городской бюджет</p>
        <h1>Бердский бюджет. Откуда приходят деньги?</h1>
        <p class="article-deck">Какая часть налогов остаётся в Бердске, откуда приходят остальные средства и почему большой бюджет ещё не означает самостоятельный город.</p>
        <div class="author-card">
          <span class="author-mark" aria-hidden="true">СК</span>
          <span class="author-details"><small>Автор статьи</small><strong>Кученков Степан</strong><span>кандидат в Совет депутатов города Бердска</span></span>
          <time datetime="2026-08-29">29 августа 2026 года</time>
        </div>
      </div>
    </header>

    <div class="stat-strip" aria-label="Ключевые показатели">
      <div class="stats">
        <div class="stat"><b>5,971 млрд</b><span>все доходы Бердска в 2025 году</span></div>
        <div class="stat"><b>1,923 млрд</b><span>собственные доходы города</span></div>
        <div class="stat"><b>67,8%</b><span>доля внешних поступлений</span></div>
        <div class="stat"><b>42,15%</b><span>норматив основной части НДФЛ в 2025 году</span></div>
      </div>
    </div>

    <div class="article-layout">
      <aside class="toc" aria-label="Содержание статьи"><p class="toc-title">Содержание</p><ol data-toc></ol></aside>
      <article class="article-body" id="article">
{article_body}
        <div class="article-actions"><button class="copy-button" type="button" data-copy-link>Скопировать ссылку</button><button class="copy-button" type="button" onclick="window.print()">Версия для печати</button></div>
      </article>
    </div>
  </main>

  <footer class="site-footer"><div class="footer-inner"><p>Аналитическая статья Кученкова Степана, кандидата в Совет депутатов города Бердска</p></div></footer>
  <script src="../../assets/site.js?v=20260829-1" defer></script>
</body>
</html>
"""

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"Собрано: {OUTPUT}")


if __name__ == "__main__":
    build()
