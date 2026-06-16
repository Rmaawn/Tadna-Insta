// Live translation for analyzer insight codes (emitted by the backend as
// {code, text, params}). If a code is unknown we fall back to the English text.

import type { Lang } from "./i18n";

type Tri = { fa: string; ar: string; en: string };

const INSIGHTS: Record<string, Tri> = {
  // --- profile ---
  "profile.no_cta": {
    fa: "بایو هیچ فراخوان عمل (CTA) روشنی ندارد — بازدیدکننده نمی‌داند قدم بعدی چیست.",
    ar: "النبذة لا تحتوي دعوة واضحة لاتخاذ إجراء — الزائر لا يعرف الخطوة التالية.",
    en: "Bio has no clear call-to-action — visitors don't know what to do next.",
  },
  "profile.no_link": {
    fa: "هیچ لینکی در بایو نیست: داری فرصت تبدیل (کانورژن) را از دست می‌دهی.",
    ar: "لا يوجد رابط في النبذة: أنت تفقد فرص التحويل.",
    en: "No link in bio: you're leaving conversions on the table.",
  },
  "profile.bio_short": {
    fa: "بایو کوتاه‌تر از آن است که ارزش پیشنهادی‌ات را منتقل کند.",
    ar: "النبذة أقصر من أن تنقل قيمتك المقترحة.",
    en: "Bio is too short to communicate your value proposition.",
  },
  "profile.niche_unclear": {
    fa: "نیچ تو از روی بایو روشن نیست — جایگاه‌یابی عمومی به نظر می‌رسد.",
    ar: "مجالك غير واضح من النبذة — يبدو التموضع عامًا.",
    en: "Your niche is unclear from the bio — positioning feels generic.",
  },
  "profile.low_ratio": {
    fa: "فالویینگِ بسیار بیشتر از فالوور، نشانه‌ی اعتبار پایین است.",
    ar: "متابعتك لأعداد أكبر بكثير من متابعيك تشير إلى ضعف المصداقية.",
    en: "Following far more than your followers signals low authority.",
  },
  "profile.solid": {
    fa: "پایه‌های پروفایل محکم است؛ حالا روی محتوا و انسجام تمرکز کن.",
    ar: "أساسيات الملف متينة؛ ركّز الآن على المحتوى والاتساق.",
    en: "Profile fundamentals are solid; focus on content and consistency next.",
  },
  // --- content ---
  "content.captions_short": {
    fa: "کپشن‌ها کوتاه‌اند — از آن‌ها به‌عنوان ابزار روایت و سئو کم استفاده می‌کنی.",
    ar: "التعليقات قصيرة — أنت لا تستغلها كأداة سرد وتحسين ظهور.",
    en: "Captions are short — you're underusing them as a storytelling and SEO surface.",
  },
  "content.low_cta": {
    fa: "کمتر از یک‌سوم پست‌ها فراخوان عمل دارند.",
    ar: "أقل من ثلث المنشورات تحتوي على دعوة لاتخاذ إجراء.",
    en: "Fewer than a third of posts include a call-to-action.",
  },
  "content.no_carousels": {
    fa: "در پست‌های اخیر هیچ کاروسلی نیست — کاروسل معمولاً ریچ و سیو بیشتری می‌آورد.",
    ar: "لا توجد ألبومات في المنشورات الأخيرة — الألبومات عادةً تزيد الوصول والحفظ.",
    en: "No carousels in recent posts — carousels typically drive higher reach and saves.",
  },
  "content.slow_cadence": {
    fa: "ریتم انتشار کند است؛ الگوریتم به انسجام پاداش می‌دهد.",
    ar: "إيقاع النشر بطيء؛ الخوارزمية تكافئ الانتظام.",
    en: "Posting cadence is slow; the algorithm rewards consistency.",
  },
  "content.irregular": {
    fa: "برنامه‌ی انتشار نامنظم است — فاصله‌ی بین پست‌ها خیلی متغیر است.",
    ar: "جدول النشر غير منتظم — الفجوات بين المنشورات تتباين كثيرًا.",
    en: "Posting schedule is irregular — gaps between posts vary widely.",
  },
  "content.best_window": {
    fa: "قوی‌ترین بازه‌ی انتشار تو {slot} است.",
    ar: "أقوى نافذة نشر لديك هي {slot}.",
    en: "Your strongest publishing window is {slot}.",
  },
  "content.healthy": {
    fa: "ترکیب محتوا و ریتم انتشار سالم به نظر می‌رسد — همین روند را حفظ کن.",
    ar: "مزيج المحتوى وإيقاع النشر يبدوان جيدين — حافظ على الزخم.",
    en: "Content mix and cadence look healthy — keep the momentum.",
  },
  // --- engagement ---
  "engagement.above_benchmark": {
    fa: "تعامل ({er}%) بالاتر از بنچمارک سایز توست — مخاطبت فعال است.",
    ar: "التفاعل ({er}%) أعلى من معيار حجمك — جمهورك نشط.",
    en: "Engagement ({er}%) is above the benchmark for your size — your audience is active.",
  },
  "engagement.below_benchmark": {
    fa: "تعامل ({er}%) پایین‌تر از بنچمارک {benchmark}% برای سایز توست.",
    ar: "التفاعل ({er}%) أقل من معيار {benchmark}% لحجمك.",
    en: "Engagement ({er}%) is below the {benchmark}% benchmark for your size.",
  },
  "engagement.declining": {
    fa: "تعامل در پست‌های اخیر روند نزولی دارد.",
    ar: "التفاعل في اتجاه هابط عبر المنشورات الأخيرة.",
    en: "Engagement is trending downward across recent posts.",
  },
  "engagement.rising": {
    fa: "تعامل روند صعودی دارد — محتوای اخیر گرفته است.",
    ar: "التفاعل في اتجاه صاعد — المحتوى الأخير يلقى تجاوبًا.",
    en: "Engagement is trending upward — recent content is resonating.",
  },
  "engagement.inconsistent": {
    fa: "تعامل بسیار ناپایدار است — چند پست بیشترِ تعامل را به دوش می‌کشند.",
    ar: "التفاعل متذبذب جدًا — عدد قليل من المنشورات يحمل معظم التفاعل.",
    en: "Engagement is highly inconsistent — a few posts carry most of the interaction.",
  },
  "engagement.steady": {
    fa: "تعامل پایدار و متناسب با سایز مخاطب توست.",
    ar: "التفاعل ثابت ومتوافق مع حجم جمهورك.",
    en: "Engagement is steady and in line with expectations for your audience size.",
  },
  // --- visual ---
  "visual.scattered": {
    fa: "تصاویر هویت رنگی منسجمی ندارند — گرید پراکنده به نظر می‌رسد.",
    ar: "الصور تفتقر لهوية لونية متسقة — تبدو الشبكة مبعثرة.",
    en: "Thumbnails lack a consistent color identity — the grid looks scattered.",
  },
  "visual.strong_palette": {
    fa: "پالت رنگ قوی و منسجم — گریدت هویت قابل‌تشخیصی دارد.",
    ar: "لوحة ألوان قوية ومتسقة — شبكتك ذات هوية مميزة.",
    en: "Strong, consistent color palette — your grid has a recognizable identity.",
  },
  "visual.text_heavy": {
    fa: "بیشتر تصاویر متن‌محورند؛ تصاویر تمیزتر معمولاً در فید بهتر خوانده می‌شوند.",
    ar: "معظم الصور كثيفة النص؛ الصور الأنظف عادةً أوضح في الموجز.",
    en: "Most thumbnails are text-heavy; cleaner visuals usually read better in-feed.",
  },
  "visual.faces_common": {
    fa: "پست‌های دارای چهره زیادند — این‌ها معمولاً تعامل بهتری دارند.",
    ar: "المنشورات التي تظهر فيها وجوه شائعة — وهي عادةً تتفوق في التفاعل.",
    en: "Posts featuring faces are common — these tend to outperform on engagement.",
  },
  "visual.no_faces": {
    fa: "هیچ چهره‌ای در تصاویر شناسایی نشد؛ چهره‌ی انسانی معمولاً تعامل را بالا می‌برد.",
    ar: "لم يتم رصد وجوه في الصور؛ الوجوه البشرية عادةً ترفع التفاعل.",
    en: "No faces detected in thumbnails; human faces typically lift engagement.",
  },
  "visual.dark": {
    fa: "تصاویر به‌سمت تاریکی متمایل‌اند — تصاویر روشن‌تر و پرکنتراست‌تر را در نظر بگیر.",
    ar: "الصور تميل إلى الإظلام — فكّر في صور أكثر سطوعًا وتباينًا.",
    en: "Imagery skews dark — consider brighter, higher-contrast visuals.",
  },
  "visual.coherent": {
    fa: "هویت بصری منسجم است؛ پالت و ترکیب‌بندی را همین‌طور حفظ کن.",
    ar: "الهوية البصرية متماسكة؛ حافظ على اللوحة والتكوين كما هما.",
    en: "Visual identity is coherent; keep the palette and composition consistent.",
  },
  "visual.no_thumbnails": {
    fa: "هیچ تصویری برای تحلیل بصری دانلود نشد.",
    ar: "تعذّر تنزيل أي صورة للتحليل البصري.",
    en: "No thumbnails could be downloaded for visual analysis.",
  },
};

export interface RawInsight {
  code?: string;
  text?: string;
  tone?: "good" | "bad";
  params?: Record<string, string | number>;
}

/** Translate one insight (object or legacy string) into the active language. */
export function insightText(lang: Lang, item: RawInsight | string): string {
  if (typeof item === "string") return item; // legacy / AI-provided text
  const entry = item.code ? INSIGHTS[item.code] : undefined;
  let s = entry ? entry[lang] : item.text ?? "";
  if (item.params) {
    for (const [k, v] of Object.entries(item.params)) {
      s = s.replace(`{${k}}`, String(v));
    }
  }
  return s;
}
