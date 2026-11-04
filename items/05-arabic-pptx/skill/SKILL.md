---
name: arabic-pptx
description: Makes Arabic PowerPoint decks (.pptx) that open correctly — right-to-left paragraphs and bullets, correct word order around English words, Arabic in the right font, tables from the right. Use whenever you create or edit a .pptx that contains Arabic, or when the user uploads an Arabic deck that looks broken (bullets on the left, mixed-up sentences, tables left-to-right).
---

# عرض PowerPoint عربي ما بيتخربط

## ليش
العروض اللي بتنعمل بالكود (python-pptx أو pptxgenjs) ما بتعرف إنها عربية. النقاط بتطلع على الشمال، والجمل بتتخربط حوالين الكلمات الإنجليزي، و«%.» بيطلع على الطرف الغلط، والجدول بيبلش من الشمال.

## الطريقة
1. اعمل العرض عادي.
2. **آخر خطوة دايماً، قبل ما تسلّم الملف:**
   ```bash
   pip install python-pptx  # إذا مش موجودة
   python3 scripts/arabic_pptx.py deck.pptx deck.pptx
   ```
   السكربت بيعدّل الاتجاه والمحاذاة واللغة والخط بس، وما بيلمس النص.
3. **لعرض خربان رفعه المستخدم:** شغّل نفس السكربت عليه، وسلّمه الملف المصلّح بنفس الاسم + `_fixed`.

## قواعد وإنت بتعمل العرض
- بـ PowerPoint (عكس Word) المحاذاة ثابتة: «يمين» يعني يمين. السكربت بيحط `algn="r"` للفقرات العربية اللي ما إلها محاذاة.
- الجداول: اكتب الأعمدة بترتيب القراءة (أول عمود = اللي على اليمين). السكربت بيحط `rtl="1"` على الجدول، وبيخلي كل الخلايا على اليمين.
- اختار خط بيدعم العربي (مثلاً IBM Plex Sans Arabic، Noto Sans Arabic، Tajawal). السكربت بيستخدم نفس الخط للعربي.

## تأكد قبل التسليم
حوّل لـ PDF (LibreOffice إذا موجود) وشوف: النقاط على اليمين؟ «%» و«.» بآخر الجملة؟ الأرقام والكلمات الإنجليزي بمكانها؟

## حدود
- LibreOffice ما بيعرض اتجاه الجدول (`rtl` على الجدول)، بس PowerPoint بيعرضه. فإذا شفت الجدول من الشمال بـ LibreOffice، هاد طبيعي.
- الأشكال المجمّعة والـ SmartArt ما انجرّبوا.
