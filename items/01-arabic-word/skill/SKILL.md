---
name: arabic-word
description: Makes Arabic Word files (.docx) that open correctly — right-to-left paragraphs, correct word order around English words, Arabic the same size as English, tables from the right. Use whenever you create or edit a .docx that contains Arabic, or when the user uploads an Arabic Word file that looks broken (mixed-up lines, text stuck to the left, Arabic smaller than English).
---

# ملف Word عربي ما بيتخربط

## ليش
ملفات Word اللي بتنعمل بالكود (python-docx أو docx-js) ما بتعرف إنها عربية. فالفقرات بتطلع من الشمال، والجمل بتتخربط حوالين الكلمات الإنجليزي، والنقطة و«%» بيطلعوا على الطرف الغلط. وWord بيعطي الخط العربي حجم لحاله، فالعربي بيطلع أصغر من الإنجليزي.

## الطريقة
1. اعمل الملف عادي، بالطريقة اللي بتعرفها.
2. **آخر خطوة دايماً، قبل ما تسلّم الملف:**
   ```bash
   pip install python-docx  # إذا مش موجودة
   python3 scripts/arabic_docx.py file.docx file.docx
   ```
   السكربت بيعدّل الاتجاه والخط بس، وما بيلمس النص.
3. **لملف خربان رفعه المستخدم:** شغّل نفس السكربت عليه، وسلّمه الملف المصلّح بنفس الاسم + `_fixed`.

## قواعد وإنت بتكتب الملف
- **لا تحط محاذاة يمين بالكود** (`alignment = RIGHT` أو `jc="right"`). بالفقرة العربية، «يمين» Word بيفهمها «آخر السطر»، فبتطلع على الشمال. السكربت بيشيلها، والفقرة بتمشي من اليمين لحالها.
- خلّي حجم الخط بالـ style (Normal) أو بكل run، والسكربت بيعطي العربي نفس الحجم.
- الجداول: اكتب الأعمدة بترتيب القراءة (أول عمود = اللي على اليمين). السكربت بيقلب الجدول من اليمين.
- الأرقام والكلمات الإنجليزي اكتبها عادي. ما بتحتاج علامات اتجاه.

## تأكد قبل التسليم
- إذا عندك LibreOffice: حوّل لـ PDF وشوف أول صفحة.
- الفقرات العربية على اليمين؟ «%» و«.» بآخر الجملة؟ القوائم نقاطها على اليمين؟ الجدول بيبلش من اليمين؟

## حدود
- السكربت ما بيلمس فقرات ما فيها ولا حرف عربي (مثلاً سطر كله أرقام بجدول).
- الصناديق النصية (text boxes) والأشكال ما بيصلّحها.
