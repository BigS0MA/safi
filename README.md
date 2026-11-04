# صافي

**برومبتات وسكيلز لشغلك بالعربي، من كاروسيلات motasem.ai. بكبسة نسخ أو تنزيل.**

الموقع: **https://motasem.ai/safi** · الرقم اللي بالكاروسيل هو نفسه الرابط: `motasem.ai/safi/1`

**النشر:** محتوى `site/` بينسخ لمجلد `safi/` بريبو موقع motasem.ai، وسطور `redirects_for_main_site.toml` بتنحط بآخر `netlify.toml` تبعه (عشان `/safi/1` يحوّل لـ `/safi/p/1/`). المسار بيتغيّر بـ `SAFI_BASE`.

## شو بالمكتبة

| # | العنصر | النوع |
|---|---|---|
| 01 | [ملف Word عربي ما بيتخربط](items/01-arabic-word) | سكيل + برومبت + تصليح يدوي |
| 02 | [8 اختصارات بالعربي](items/02-shortcuts) | بلوك إعدادات |
| 03 | [خليه يكتب بلهجتك](items/03-my-voice) | برومبت (خطوتين) |
| 04 | [خليه ينتقدك بجد](items/04-be-honest) | بلوك إعدادات |
| 05 | [عرض PowerPoint عربي ما بيتخربط](items/05-arabic-pptx) | سكيل + برومبت + تصليح يدوي |
| 06 | [الفويس الطويل ← 3 سطور ورد جاهز](items/06-voice-notes) | برومبت |
| 07 | [كتاب رسمي بالفصحى من حكيك العادي](items/07-official-letter) | سكيل + برومبت |
| 08 | [قرار الـ 20 دولار: مجاني ولا مدفوع؟](items/08-twenty-dollars) | دليل |

### سكربتات بتشتغل لحالها (بلا Claude)
```bash
pip install python-docx python-pptx
python3 items/01-arabic-word/skill/scripts/arabic_docx.py ملفك.docx          # تصليح Word عربي
python3 items/05-arabic-pptx/skill/scripts/arabic_pptx.py عرضك.pptx          # تصليح PowerPoint عربي
python3 items/07-official-letter/skill/scripts/kitab.py letter.json كتاب.docx  # كتاب رسمي
```
بيعدّلوا الاتجاه والخط والجداول، وما بيلمسوا النص.

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
