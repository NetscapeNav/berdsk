import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { marked } from "file:///C:/Users/Netscape/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/marked/lib/marked.esm.js";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "..");
const source = path.resolve(root, "..", "Бердский бюджет. Как тратят деньги.md");
const output = path.join(root, "articles", "budget-spendings-plain", "index.html");

if (!fs.existsSync(source)) {
  throw new Error(`Не найден Markdown-файл: ${source}`);
}

const markdown = fs.readFileSync(source, "utf8");
let article = marked.parse(markdown, { gfm: true, breaks: false });
article = article
  .replaceAll("<table>", '<div class="table-scroll" tabindex="0" role="region" aria-label="Таблица"><table>')
  .replaceAll("</table>", "</table></div>");

const document = `<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Бердский бюджет. Как тратят деньги?</title>
  <meta name="description" content="Разбор расходов бюджета Бердска за 2021–2028 годы.">
  <meta name="author" content="Степан Кученков">
  <meta name="theme-color" content="#ffffff">
  <meta property="og:type" content="article">
  <meta property="og:title" content="Бердский бюджет. Как тратят деньги?">
  <meta property="og:description" content="Разбор расходов бюджета Бердска за 2021–2028 годы.">
  <meta property="og:url" content="https://netscapenav.github.io/berdsk/articles/budget-spendings-plain/">
  <link rel="canonical" href="https://netscapenav.github.io/berdsk/articles/budget-spendings-plain/">
  <style>
    * { box-sizing: border-box; }
    html { background: #fff; }
    body {
      margin: 0;
      color: #222;
      background: #fff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 18px;
      line-height: 1.58;
      text-rendering: optimizeLegibility;
    }
    main { width: min(100% - 40px, 720px); margin: 0 auto; padding: 54px 0 90px; }
    h1, h2, h3 { color: #111; line-height: 1.16; letter-spacing: -.025em; }
    h1 { margin: 0 0 30px; font-size: 38px; font-weight: 750; }
    h2 { margin: 54px 0 20px; font-size: 29px; font-weight: 720; }
    h3 { margin: 38px 0 16px; font-size: 23px; font-weight: 700; }
    p { margin: 0 0 24px; }
    strong { color: #111; font-weight: 700; }
    a { color: #168acd; text-decoration: none; }
    a:hover { text-decoration: underline; }
    ul, ol { margin: 0 0 24px; padding-left: 1.4em; }
    li { margin: 7px 0; }
    blockquote { margin: 30px 0; padding-left: 20px; border-left: 3px solid #222; color: #555; }
    .table-scroll {
      width: calc(100% + 40px);
      margin: 30px -20px;
      overflow-x: auto;
      border-top: 1px solid #e1e1e1;
      border-bottom: 1px solid #e1e1e1;
    }
    table { width: 100%; min-width: 620px; border-collapse: collapse; font-size: 14px; line-height: 1.42; }
    th, td { padding: 11px 12px; text-align: left; vertical-align: top; border-bottom: 1px solid #e7e7e7; }
    th { color: #111; background: #f5f5f5; font-weight: 650; }
    tr:last-child td { border-bottom: 0; }
    @media (max-width: 600px) {
      body { font-size: 17px; }
      main { width: min(100% - 32px, 720px); padding-top: 34px; }
      h1 { font-size: 32px; }
      h2 { margin-top: 45px; font-size: 26px; }
      h3 { font-size: 22px; }
      .table-scroll { width: calc(100% + 32px); margin-right: -16px; margin-left: -16px; }
    }
    @media print {
      body { color: #000; font-size: 11pt; }
      main { width: auto; padding: 0; }
      .table-scroll { width: auto; margin: 20px 0; overflow: visible; }
      table { min-width: 0; font-size: 8pt; }
    }
  </style>
</head>
<body>
  <main>
    <article>${article}</article>
  </main>
</body>
</html>
`;

fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, document, "utf8");
console.log(`Собрано: ${output}`);
