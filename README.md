# صافي

**برومبتات وسكيلز لشغلك بالعربي، من كاروسيلات motasem.ai. بكبسة نسخ أو تنزيل.**

الموقع: **https://safi.motasem.ai** · الرقم اللي بالكاروسيل هو نفسه الرابط: `safi.motasem.ai/1`

## شو بالمكتبة

| # | العنصر | النوع |
|---|---|---|
| 01 | [ملف Word عربي ما بيتخربط](items/01-arabic-word) | سكيل لـ Claude + برومبت لـ ChatGPT + تصليح يدوي |
| 02 | [بطّل تكتب برومبتات طويلة: 8 اختصارات بالعربي](items/02-shortcuts) | بلوك إعدادات |

### سكربت تصليح ملفات Word العربية (بلا Claude)
```bash
pip install python-docx
python3 items/01-arabic-word/skill/scripts/arabic_docx.py ملفك.docx
```
بيعدّل اتجاه الفقرات وحجم الخط العربي والجداول، وما بيلمس النص.

## البنية
```
items/<NN>-<slug>/
  item.json   العنوان، الوصف، الخطوات، الأقسام، النصيحة
  prompt.md   النص اللي بينسخ
  skill/      (للسكيلز) SKILL.md + scripts/، بينضغط zip وقت البناء
  TEST.md     ملاحظات التجربة الداخلية (ما بتنعرض بالموقع)
  tests/      ملفات التجربة
build.py      بيبني site/ من items/ (بلا مكتبات خارجية)
site/         الموقع (Netlify بيبنيه وبينشره)
RUBRIC.md     كيف بنجرّب كل عنصر قبل ما ينحط
```

## إضافة عنصر
1. انسخ مجلد عنصر موجود وغيّر الرقم.
2. جرّبه حسب `RUBRIC.md` واكتب `TEST.md`.
3. `python3 build.py`، وشوفه بسيرفر محلي: `python3 -m http.server -d site`.

## الترخيص
البرومبتات والسكيلز والسكربتات: استخدمها بشغلك بحرية. الخطوط: IBM Plex (SIL Open Font License 1.1).
