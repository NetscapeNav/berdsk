from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import quote

from lxml import etree
from lxml import html as lhtml


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_import" / "article-word.htm"
TEMPLATE = ROOT / "templates" / "article.html"
OUTPUT = ROOT / "articles" / "budget-spendings" / "index.html"


TRANSLIT = str.maketrans({
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh","з":"z","и":"i","й":"y",
    "к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f",
    "х":"h","ц":"ts","ч":"ch","ш":"sh","щ":"sch","ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya"
})


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def slugify(value: str) -> str:
    value = value.lower().translate(TRANSLIT)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "section"


def inline_html(node) -> str:
    parts: list[str] = []

    def walk(current):
        if current.text:
            parts.append(html.escape(current.text))
        for child in current:
            tag = child.tag.lower() if isinstance(child.tag, str) else ""
            if tag == "br":
                parts.append("<br>")
            elif tag in {"b", "strong"}:
                parts.append("<strong>")
                walk(child)
                parts.append("</strong>")
            elif tag in {"i", "em"}:
                parts.append("<em>")
                walk(child)
                parts.append("</em>")
            elif tag == "a" and child.get("href"):
                href = html.escape(child.get("href"), quote=True)
                parts.append(f'<a href="{href}">')
                walk(child)
                parts.append("</a>")
            elif tag not in {"script", "style"} and "display:none" not in (child.get("style") or "").replace(" ", ""):
                walk(child)
            if child.tail:
                parts.append(html.escape(child.tail))

    walk(node)
    result = "".join(parts)
    result = re.sub(r"[\r\n\t ]+", " ", result)
    result = re.sub(r" ?<br> ?", "<br>", result)
    return result.strip()


def is_list_paragraph(node) -> bool:
    cls = node.get("class") or ""
    style = node.get("style") or ""
    return "MsoList" in cls or "font-family:Symbol" in etree.tostring(node, encoding="unicode") or "text-indent:-" in style


def table_html(node) -> tuple[str, list[str]]:
    rows = node.xpath(".//tr")
    parsed: list[list[str]] = []
    for row in rows:
        cells = row.xpath("./th|./td")
        parsed.append([normalize_space(" ".join(cell.itertext())) for cell in cells])
    parsed = [row for row in parsed if any(row)]
    if not parsed:
        return "", []

    header = parsed[0]
    out = ['<div class="table-wrap" tabindex="0" role="region" aria-label="Таблица с бюджетными данными"><table>']
    out.append("<thead><tr>" + "".join(f"<th scope=\"col\">{html.escape(cell)}</th>" for cell in header) + "</tr></thead><tbody>")
    for row in parsed[1:]:
        out.append("<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out), header


def donut_chart() -> str:
    items = [
        ("#176e66", "Образование", "54,5%"), ("#3f928a", "ЖКХ", "17,4%"),
        ("#c48a2c", "Национальная экономика", "9,4%"), ("#b6542c", "Культура", "5,2%"),
        ("#6e7080", "Общегосударственные вопросы", "4,8%"), ("#a26f87", "Социальная политика", "4,1%"),
        ("#779052", "Физкультура и спорт", "4,0%"), ("#b9b4a9", "Другое", "0,6%")
    ]
    legend = "".join(f'<div class="legend-item"><span class="swatch" style="background:{color}"></span><span>{label}</span><b>{value}</b></div>' for color,label,value in items)
    return f'''<figure class="chart-card" aria-labelledby="spending-2025-title"><figcaption id="spending-2025-title"><strong>Расходы Бердска в 2025 году</strong><span>Фактическое исполнение, доля от 5,924 млрд рублей</span></figcaption><div class="donut-grid"><div class="donut" role="img" aria-label="Образование 54,5 процента, ЖКХ 17,4 процента, национальная экономика 9,4 процента, остальные разделы 18,7 процента"></div><div class="legend">{legend}</div></div></figure>'''


def city_bars() -> str:
    rows = [("Бердск",92.7),("Юрга",95.0),("Рубцовск",96.5),("Северск",98.8)]
    bars = "".join(f'<div class="bar-row"><span>{name}</span><div class="bar-track"><div class="bar-fill" style="width:{value}%"></div></div><b>{str(value).replace(".",",")}%</b></div>' for name,value in rows)
    return f'''<figure class="chart-card" aria-labelledby="cities-title"><figcaption id="cities-title"><strong>Исполнение уточнённого плана расходов за 2025 год</strong><span>Бердск исполнил план хуже трёх городов сравнения</span></figcaption><div class="bar-list">{bars}</div><p class="chart-note">Северск — ЗАТО и не является полностью сопоставимым по структуре финансирования; здесь он используется как контрольная точка исполнения плана.</p></figure>'''


def trend_chart() -> str:
    return '''<figure class="chart-card" aria-labelledby="trend-title"><figcaption id="trend-title"><strong>Расходы Бердска: факт 2021–2025 и план 2026–2028</strong><span>Млрд рублей. План будущих лет ещё может меняться решениями Совета депутатов.</span></figcaption><svg class="chart-svg" data-budget-trend role="img" aria-label="Расходы выросли с 3,7 миллиарда рублей в 2021 году до плановых 9,1 миллиарда в 2028 году" viewBox="0 0 760 350"></svg></figure>'''


def sources() -> str:
    return '''<section class="source-box" id="sources"><h2>Документы и источники</h2><ul>
      <li>Решения Совета депутатов Бердска № 69, 157, 245, 377 и 454 — исполнение бюджетов 2021–2025 годов.</li>
      <li>Решения № 31, 134, 208, 315 и 408 — первоначальные бюджеты 2022–2026 годов.</li>
      <li>Решения № 386, 394, 400, 409, 431, 443 и 455 — поправки к бюджетам 2025–2028 годов.</li>
      <li>Протоколы 4-й, 14-й, 23-й, 32-й, 41–45-й, 47-й, 49-й и 50-й сессий Совета депутатов Бердска.</li>
      <li><a href="https://openbudget.mfnso.ru/index.php">Открытый бюджет Новосибирской области</a>.</li>
      <li><a href="https://berdsk-online.ru/wp-content/uploads/2026/05/byudzhet-berdska-za-2025g.pdf">Материалы отчёта об исполнении бюджета Бердска за 2025 год</a>.</li>
      <li><a href="https://rosstat.gov.ru/statistics/price">Росстат: статистика цен и инфляции</a> и <a href="https://www.rosstat.gov.ru/storage/mediabank/120_12-08-2026.html">индекс потребительских цен в июле 2026 года</a>.</li>
      <li><a href="https://www.yurga.org/upload/files/deyatelnost/ekonomika/finansy-i-kredit/budget-dlya-grajdan/IBudgGr_2025-2027_reshenie.pdf">Официальный отчёт Юрги за 2025 год</a>, <a href="https://rubtsovsk.org/index.php/node/1401">отчёт Рубцовска</a>, <a href="https://duma-seversk.ru/normativnye-dokumenty/resheniya-dumy-i-snp/15564/">отчёт Северска</a>.</li>
      <li><a href="https://docs.superhuman.com/@berdsk-kuchenkov/budget-spendings/-13">Исходная версия статьи в Superhuman Docs</a>.</li>
    </ul><p>Все суммы округлены. Плановые показатели отделены от фактических.</p></section>'''


def build_body() -> str:
    if not SOURCE.exists():
        raise SystemExit(f"Не найден исходник: {SOURCE}")
    doc = lhtml.parse(str(SOURCE))
    section = doc.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," WordSection1 ")]')
    if not section:
        raise SystemExit("В экспортированном HTML не найден WordSection1")

    blocks: list[str] = []
    list_items: list[str] = []
    list_tag = "ul"
    chart_title_seen = False
    inserted_city_bars = False
    inserted_trend = False

    def flush_list():
        nonlocal list_items
        if list_items:
            blocks.append(f"<{list_tag}>" + "".join(f"<li>{item}</li>" for item in list_items) + f"</{list_tag}>")
            list_items = []

    for child in section[0]:
        tag = child.tag.lower() if isinstance(child.tag, str) else ""
        if tag in {"h2", "h3"}:
            flush_list()
            text = normalize_space(" ".join(child.itertext()))
            if not text:
                continue
            level = tag
            blocks.append(f'<{level} id="{slugify(text)}">{html.escape(text)}</{level}>')
        elif tag == "p":
            raw_text = normalize_space(" ".join(child.itertext()))
            if not raw_text:
                continue
            content = inline_html(child)
            if is_list_paragraph(child):
                content = re.sub(r"^(?:·|•|\u00b7)\s*", "", content)
                list_items.append(content)
            else:
                flush_list()
                css = ' class="compact-lines"' if content.count("<br>") >= 2 else ""
                blocks.append(f"<p{css}>{content}</p>")
        elif tag == "table":
            flush_list()
            table, header = table_html(child)
            text = normalize_space(" ".join(child.itertext()))
            if len(header) == 1 and "Расходы Бердска в 2025" in text:
                chart_title_seen = True
                blocks.append(donut_chart())
                continue
            if table:
                blocks.append(table)
            joined = " ".join(header)
            if not inserted_city_bars and "Город" in joined and "Исполнение" in joined:
                blocks.append(city_bars())
                inserted_city_bars = True
            if not inserted_trend and "2026" in joined and "2027" in joined and "2028" in joined:
                blocks.append(trend_chart())
                inserted_trend = True
    flush_list()
    if not chart_title_seen:
        blocks.insert(4, donut_chart())
    blocks.append(sources())
    return "\n".join(blocks)


def main() -> None:
    body = build_body()
    template = TEMPLATE.read_text(encoding="utf-8")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(template.replace("{{ARTICLE_BODY}}", body), encoding="utf-8")
    print(f"Собрано: {OUTPUT}")


if __name__ == "__main__":
    main()

