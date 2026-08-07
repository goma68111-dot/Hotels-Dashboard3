# -*- coding: utf-8 -*-
"""
Hotel Reviews Observatory — LUXE v4 (chat fix: suggestions are real buttons, no new tab)
Run:  streamlit run dashboard.py
"""

import re, os, json
from collections import Counter

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ═══════════════════════════════════════════════════════════════
# 0) CONFIG + STATE
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="Hotel Reviews Observatory ✨ | مرصد مراجعات الفنادق",
                   page_icon="🏨", layout="wide", initial_sidebar_state="expanded")
for _k, _v in {"lang": "en", "dark": True, "chat_open": True, "chat_history": [],
               "png_on": False}.items():
    st.session_state.setdefault(_k, _v)
L, DARK = st.session_state.lang, st.session_state.dark

# ═══════════════════════════════════════════════════════════════
# 1) i18n
# ═══════════════════════════════════════════════════════════════
STR = {
 "en": {
  "badge": "Luxe Edition", "mast_title": 'Hotel Reviews <span class="hl">Observatory</span>',
  "mast_tag": "30k+ guest voices across 1,100+ hotels — ratings, seasons, nationalities and sentiment in one live analytics surface.",
  "reviews": "reviews", "hotels": "hotels", "period": "period",
  "k_reviews": "Total Reviews", "k_score": "Average Score", "k_hotels": "Hotels",
  "k_nights": "Avg Nights", "k_quality": "Quality Score", "vs_prev": "vs prev month",
  "mom_na": "no prior month",
  "sb_quick": "Quick Stats", "sb_quality": "Review quality", "sb_suspicion": "Suspicion levels",
  "sb_top_nat": "Top nationality", "sb_period": "Date span", "sb_src_csv": "Source: Hotel_Reviews_ULTIMATE_CLEAN.csv",
  "sb_src_demo": "⚠️ CSV not found — running on generated demo data.", "sb_export": "Export",
  "sb_png": "Enable PNG export (slower)",
  "fb_title": "Filters", "sb_traveler": "Traveler Type", "sb_hotel": "Hotel",
  "sb_room": "Room Type", "sb_score": "Score Range", "sb_reset": "↺ Reset",
  "sb_matching": "matching", "sb_avg_after": "avg",
  "tb_ratings": "📊 Ratings", "tb_hotels": "🏨 Hotels & Rooms", "tb_nat": "🌍 Nationalities",
  "tb_season": "📅 Seasonality", "tb_trends": "📈 Trends", "tb_wc": "☁️ Word Cloud",
  "tb_ai": "🤖 AI Assistant", "tb_data": "📋 Data",
  "c_hist": "Score Distribution", "c_tt_bar": "Average Score by Traveler Type",
  "c_tt_box": "Score Spread by Traveler Type", "c_top10": "Top 10 Hotels by Rating",
  "c_bottom": "Bottom 5 Hotels", "c_decline": "Biggest Rating Declines",
  "c_room": "Average Score by Room Type", "c_tree": "Review Volume by Hotel",
  "c_nat_score": "Top 15 Nationalities by Rating", "c_nat_count": "Top 15 Nationalities by Volume",
  "c_nat_pie": "Nationality Share", "c_month": "Seasonal Rhythm (month-of-year)",
  "c_year": "Average Score by Year", "c_best_m": "Best Month", "c_worst_m": "Weakest Month",
  "c_trend": "Rating Trend Over Time — monthly + 3-mo moving average",
  "c_corr": "Correlation Matrix", "c_scatter": "Score vs Nights Stayed",
  "c_susp": "Suspicion Levels", "c_qlty": "Review Quality Distribution",
  "cap_minrev": "Ranked with a minimum of 20 reviews to keep averages honest.",
  "cap_tree": "Top 30 hotels by review volume, colored by average score.",
  "cap_pie": "Top 10 nationalities, remainder grouped as “Other”.",
  "cap_decline": "Hotels with ≥10 reviews in each half of the period; sorted by 2nd-half minus 1st-half.",
  "cap_corr": "Pearson correlation between score, length of stay and review quality.",
  "cap_scatter": "Each dot is a review, colored by traveler type (sampled for clarity).",
  "score": "Score", "avg_score": "Avg score", "count": "Reviews", "ma3": "3-mo avg",
  "wc_source": "Cloud source", "wc_pos": "Positive reviews", "wc_neg": "Negative reviews",
  "wc_all": "All reviews", "wc_max": "Max words", "wc_gen": "☁️ Generate Word Cloud",
  "wc_top": "Top 20 words", "wc_word": "Word", "wc_count": "Count",
  "wc_hint": "Pick a source and press generate — the cloud respects current filters.",
  "wc_font_note": "Arabic text needs a system font with Arabic glyphs (see FONT_PATHS in code).",
  "ai_title": "Ask the data", "ai_sub": "Rule-based assistant — answers are computed live from the filtered dataset, in your question’s language. No API needed.",
  "ai_note": "💡 Answers respect the top filters. Tap a suggestion — the reply appears right here, no page reload.",
  "ai_empty": "No conversation yet — tap a suggestion 👇", "ai_sug": "Suggested questions",
  "chat_title": "AI Assistant", "chat_ph": "Type your question… (AR/EN)",
  "chat_empty": "Chat is empty — ask me about hotels, months, nationalities…",
  "d_title": "Filtered Records", "d_showing": "Showing", "of": "of",
  "no_data": "⚠️ No reviews match the current filters — widen the score range or clear a filter.",
  "dl_png": "⬇ PNG", "dl_note": "Enable “PNG export” in the sidebar to download charts.",
  "foot": "Hotel Reviews Observatory · Luxe Edition · built with Streamlit & Plotly",
 },
 "ar": {
  "badge": "نسخة فاخرة", "mast_title": 'مرصد <span class="hl">مراجعات الفنادق</span>',
  "mast_tag": "أكثر من 30 ألف صوت ضيف عبر 1,100+ فندق — التقييمات والمواسم والجنسيات والمشاعر في لوحة تحليلات حيّة واحدة.",
  "reviews": "مراجعة", "hotels": "فندق", "period": "الفترة",
  "k_reviews": "إجمالي المراجعات", "k_score": "متوسط التقييم", "k_hotels": "عدد الفنادق",
  "k_nights": "متوسط الليالي", "k_quality": "جودة المراجعة", "vs_prev": "عن الشهر السابق",
  "mom_na": "لا شهر سابق",
  "sb_quick": "إحصائيات سريعة", "sb_quality": "جودة المراجعات", "sb_suspicion": "مستويات الاشتباه",
  "sb_top_nat": "أكثر جنسية", "sb_period": "النطاق الزمني", "sb_src_csv": "المصدر: Hotel_Reviews_ULTIMATE_CLEAN.csv",
  "sb_src_demo": "⚠️ لم يتم العثور على CSV — يعمل ببيانات تجريبية مولّدة.", "sb_export": "التصدير",
  "sb_png": "تفعيل تصدير PNG (أبطأ)",
  "fb_title": "الفلاتر", "sb_traveler": "نوع المسافر", "sb_hotel": "الفندق",
  "sb_room": "نوع الغرفة", "sb_score": "نطاق التقييم", "sb_reset": "↺ إعادة تعيين",
  "sb_matching": "مطابقة", "sb_avg_after": "المتوسط",
  "tb_ratings": "📊 التقييمات", "tb_hotels": "🏨 الفنادق والغرف", "tb_nat": "🌍 الجنسيات",
  "tb_season": "📅 الموسمية", "tb_trends": "📈 الاتجاهات", "tb_wc": "☁️ سحابة الكلمات",
  "tb_ai": "🤖 المساعد الذكي", "tb_data": "📋 البيانات",
  "c_hist": "توزيع التقييمات", "c_tt_bar": "متوسط التقييم حسب نوع المسافر",
  "c_tt_box": "تشتت التقييمات حسب نوع المسافر", "c_top10": "أفضل 10 فنادق بالتقييم",
  "c_bottom": "أقل 5 فنادق تقييمًا", "c_decline": "أكبر تراجعات في التقييم",
  "c_room": "متوسط التقييم حسب نوع الغرفة", "c_tree": "حجم المراجعات لكل فندق",
  "c_nat_score": "أفضل 15 جنسية بالتقييم", "c_nat_count": "أكثر 15 جنسية بالمراجعات",
  "c_nat_pie": "حصة الجنسيات", "c_month": "الإيقاع الموسمي (شهر السنة)",
  "c_year": "متوسط التقييم حسب السنة", "c_best_m": "أفضل شهر", "c_worst_m": "أضعف شهر",
  "c_trend": "اتجاه التقييم عبر الزمن — شهري + متوسط متحرك 3 أشهر",
  "c_corr": "مصفوفة الارتباط", "c_scatter": "التقييم مقابل ليالي الإقامة",
  "c_susp": "مستويات الاشتباه", "c_qlty": "توزيع جودة المراجعات",
  "cap_minrev": "الترتيب بحد أدنى 20 مراجعة لضمان موثوقية المتوسطات.",
  "cap_tree": "أفضل 30 فندقًا حسب عدد المراجعات، ملوّنة بمتوسط التقييم.",
  "cap_pie": "أكثر 10 جنسيات، والباقي مجمّع تحت «أخرى».",
  "cap_decline": "فنادق لها ≥10 مراجعات في كل نصف من الفترة؛ مرتبة حسب (النصف الثاني − الأول).",
  "cap_corr": "ارتباط بيرسون بين التقييم ومدة الإقامة وجودة المراجعة.",
  "cap_scatter": "كل نقطة مراجعة، ملوّنة حسب نوع المسافر (عيّنة للوضوح).",
  "score": "التقييم", "avg_score": "متوسط التقييم", "count": "المراجعات", "ma3": "متوسط 3 أشهر",
  "wc_source": "مصدر السحابة", "wc_pos": "المراجعات الإيجابية", "wc_neg": "المراجعات السلبية",
  "wc_all": "كل المراجعات", "wc_max": "أقصى عدد كلمات", "wc_gen": "☁️ توليد سحابة الكلمات",
  "wc_top": "أكثر 20 كلمة", "wc_word": "الكلمة", "wc_count": "التكرار",
  "wc_hint": "اختر المصدر ثم اضغط توليد — السحابة تحترم الفلاتر الحالية.",
  "wc_font_note": "النص العربي يتطلب خط نظام يدعم العربية (راجع FONT_PATHS في الكود).",
  "ai_title": "اسأل البيانات", "ai_sub": "مساعد مبرمج مسبقًا — تُحسب الإجابات مباشرة من البيانات المفلترة وبلغة سؤالك. بدون أي API.",
  "ai_note": "💡 الإجابات تحترم الفلاتر العلوية. اضغط اقتراحًا — يظهر الرد هنا فورًا دون إعادة تحميل.",
  "ai_empty": "لا محادثة بعد — اضغط اقتراحًا 👇", "ai_sug": "أسئلة مقترحة",
  "chat_title": "المساعد الذكي", "chat_ph": "اكتب سؤالك… (عربي/إنجليزي)",
  "chat_empty": "المحادثة فارغة — اسألني عن الفنادق أو الأشهر أو الجنسيات…",
  "d_title": "السجلات المفلترة", "d_showing": "عرض", "of": "من",
  "no_data": "⚠️ لا توجد مراجعات مطابقة للفلاتر — وسّع نطاق التقييم أو أزل فلترًا.",
  "dl_png": "⬇ PNG", "dl_note": "فعّل «تصدير PNG» من الشريط الجانبي لتنزيل الرسوم.",
  "foot": "مرصد مراجعات الفنادق · نسخة فاخرة · مبني بـ Streamlit و Plotly",
 },
}
TT_AR = {"Couple": "الأزواج", "Solo Traveler": "المسافر المنفرد", "Family": "العائلات",
         "Business": "رجال الأعمال", "Group": "المجموعات"}
ROOM_AR = {"Double Room": "غرفة مزدوجة", "Twin Room": "غرفة بسريرين", "Single Room": "غرفة مفردة",
           "Suite": "جناح", "Deluxe Room": "غرفة ديلوكس", "Family Room": "غرفة عائلية",
           "Standard Room": "غرفة قياسية", "Triple Room": "غرفة ثلاثية", "Executive Suite": "جناح تنفيذي"}
SUS_AR = {"Low": "منخفض", "Medium": "متوسط", "High": "مرتفع"}
MONTHS = {"en": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
          "ar": ["يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]}
def t(k):         return STR[L][k]
def tt_name(v):   return TT_AR.get(v, v) if L == "ar" else v
def room_name(v): return ROOM_AR.get(v, v) if L == "ar" else v
def sus_name(v):  return SUS_AR.get(str(v), v) if L == "ar" else v
def month_name(m):return MONTHS[L][int(m) - 1]

# ═══════════════════════════════════════════════════════════════
# 2) LUXE THEME + CSS
# ═══════════════════════════════════════════════════════════════
FONT_BODY = "Inter, Almarai, system-ui, sans-serif"
FONT_SUB  = "Montserrat, Almarai, sans-serif"
FONT_DISP = "'Playfair Display', Amiri, serif"
FONT_NUM  = "'Space Grotesk', monospace"
TH = {
 "dark": dict(bg="#0a0e1a", card="#141c2c", card2="#182238", text="#e8e6e3", muted="#96a0b5",
   navy="#4a6fa5", gold="#c9a84c", gold_b="#e6c877", orange="#e07a5f", sand="#d4a373",
   goldtx="#e6c877", vlg1="#8fb3ec", vlg2="#e6c877", hlg1="#c9a84c", hlg2="#f5d77b",
   border="rgba(201,168,76,0.25)", border_soft="rgba(201,168,76,0.14)", grid="rgba(201,168,76,0.09)",
   glass="rgba(255,255,255,0.05)", glass2="rgba(255,255,255,0.02)", tag="rgba(26,42,108,0.45)",
   o1="rgba(26,42,108,0.55)", o2="rgba(201,168,76,0.15)", o3="rgba(224,122,95,0.13)",
   dot="rgba(201,168,76,0.10)", tpl="plotly_dark"),
 "light": dict(bg="#f8f4ed", card="#ffffff", card2="#fdfaf3", text="#1e2a3a", muted="#5c6678",
   navy="#1a2a6c", gold="#c9a84c", gold_b="#c9a84c", orange="#d5694b", sand="#c99a6b",
   goldtx="#8f6b1c", vlg1="#1a2a6c", vlg2="#a8842a", hlg1="#9a7520", hlg2="#c9a84c",
   border="rgba(201,168,76,0.35)", border_soft="rgba(26,42,108,0.12)", grid="rgba(26,42,108,0.10)",
   glass="rgba(255,255,255,0.60)", glass2="rgba(255,255,255,0.25)", tag="rgba(26,42,108,0.10)",
   o1="rgba(26,42,108,0.16)", o2="rgba(201,168,76,0.22)", o3="rgba(224,122,95,0.12)",
   dot="rgba(26,42,108,0.08)", tpl="plotly_white"),
}
C = TH["dark" if DARK else "light"]
PALETTE = (["#6b8fd4", "#c9a84c", "#e07a5f", "#4a6fa5", "#d4a373", "#9db4d8"] if DARK
           else ["#1a2a6c", "#c9a84c", "#e07a5f", "#4a6fa5", "#d4a373", "#2d4059"])
NAVY_GOLD = [[0, C["navy"]], [1, C["gold_b"]]]
LUX_SCALE = [[0, C["orange"]], [0.55, C["sand"]], [1, C["gold_b"]]]
CORR_SCALE = [[0, C["orange"]], [0.5, C["card2"]], [1, C["gold_b"]]]

CSS_TPL = r"""
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Montserrat:wght@500;600;700&family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&family=Amiri:wght@400;700&family=Almarai:wght@300;400;700;800&display=swap');

.stApp{
  --bg:__BG__; --card:__CARD__; --card2:__CARD2__; --text:__TEXT__; --muted:__MUTED__; --gold:__GOLDTX__; --border:__BORDER__;
  --background-color:__BG__; --secondary-background-color:__CARD__; --text-color:__TEXT__;
  --primary-color:#c9a84c; --border-color:__BORDER__;
  background:var(--bg); color:var(--text); font-family:__BODY__;
}
html,body{background:var(--bg) !important}
[data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], [data-testid="stVerticalBlock"]{background:transparent}
.stApp::before{content:"";position:fixed;top:0;left:0;right:0;height:4px;z-index:1200;
  background:linear-gradient(90deg,#1a2a6c,#c9a84c 55%,#e07a5f)}
.stApp::after{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:radial-gradient(__DOT__ 1px, transparent 1px);background-size:26px 26px;
  -webkit-mask-image:linear-gradient(180deg,rgba(0,0,0,.6),transparent 65%);
  mask-image:linear-gradient(180deg,rgba(0,0,0,.6),transparent 65%)}
.ambient{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.orb{position:absolute;border-radius:50%;filter:blur(95px)}
.o1{width:540px;height:540px;background:__O1__;top:-170px;right:-130px;animation:drift1 22s ease-in-out infinite alternate}
.o2{width:430px;height:430px;background:__O2__;bottom:-150px;left:-110px;animation:drift2 27s ease-in-out infinite alternate}
.o3{width:300px;height:300px;background:__O3__;top:42%;left:56%;animation:drift3 31s ease-in-out infinite alternate}
@keyframes drift1{to{transform:translate(-70px,55px) scale(1.1)}}
@keyframes drift2{to{transform:translate(75px,-45px) scale(1.14)}}
@keyframes drift3{to{transform:translate(-55px,-65px)}}
section.main, section[data-testid="stSidebar"]{position:relative;z-index:1}
#MainMenu,footer{visibility:hidden}
header[data-testid="stHeader"]{background:transparent;backdrop-filter:none}
.block-container{padding-top:2.2rem !important;padding-bottom:1rem !important}
::selection{background:#c9a84c;color:#1a2a6c}
::-webkit-scrollbar{width:9px;height:9px}::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:linear-gradient(180deg,#1a2a6c,#c9a84c);border-radius:8px}

.mast{padding:14px 4px 0}
.masttop{display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.logo{width:60px;height:60px;border-radius:16px;display:flex;align-items:center;justify-content:center;
  font-size:28px;background:linear-gradient(135deg,#1a2a6c,#2d4059);border:1px solid rgba(201,168,76,.5);flex:none;
  box-shadow:0 10px 28px rgba(26,42,108,.45), inset 0 1px 0 rgba(255,255,255,.18);animation:rise .6s both}
.mast .eyebrow{display:flex;gap:10px;align-items:center;color:var(--muted);font-family:__SUB__;
  font-size:11.5px;font-weight:600;letter-spacing:1.6px;text-transform:uppercase;flex-wrap:wrap}
.pulse{width:9px;height:9px;border-radius:50%;background:#c9a84c;flex:none;
  box-shadow:0 0 0 0 rgba(201,168,76,.6);animation:pulse 2.2s infinite}
@keyframes pulse{70%{box-shadow:0 0 0 11px rgba(201,168,76,0)}100%{box-shadow:0 0 0 0 rgba(201,168,76,0)}}
.badge{font-size:9.5px;font-weight:700;letter-spacing:1.6px;color:var(--gold);
  border:1px solid rgba(201,168,76,.45);border-radius:999px;padding:3px 11px;background:rgba(201,168,76,.08)}
.mast h1{font-family:__DISP__;font-size:clamp(32px,4.5vw,56px);font-weight:800;margin:4px 0 0;
  line-height:1.12;letter-spacing:-.5px;animation:rise .6s .08s both}
.mast .hl{background:linear-gradient(135deg,__HLG1__,__HLG2__);-webkit-background-clip:text;
  background-clip:text;-webkit-text-fill-color:transparent}
.mast .tag{color:var(--muted);font-size:15px;max-width:780px;line-height:1.75;margin-top:8px;animation:rise .6s .16s both}
.skyline{color:#c9a84c;opacity:.28;margin:10px 0 -6px;animation:rise .8s .2s both}
.skyline svg{display:block;width:100%;height:52px}

.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin:16px 0 18px}
.kpi{background:linear-gradient(145deg,__GLASS__,__GLASS2__);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  border:1px solid __BORDER__;border-radius:20px;padding:16px 18px 14px;position:relative;overflow:hidden;
  transition:all .4s ease;animation:rise .55s both}
.kpi::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#1a2a6c,#c9a84c,#e07a5f)}
.kpi:hover{border-color:#c9a84c;box-shadow:0 10px 40px rgba(201,168,76,.15);transform:translateY(-5px)}
.kpi .row1{display:flex;align-items:center;justify-content:space-between}
.kpi .ic{width:42px;height:42px;display:flex;align-items:center;justify-content:center;font-size:20px;
  border-radius:13px;background:linear-gradient(135deg,rgba(26,42,108,.35),rgba(201,168,76,.22));border:1px solid __BORDER__}
.spark{width:88px;height:28px;display:block}
.kpi .lb{font-family:__SUB__;text-transform:uppercase;letter-spacing:1.3px;font-size:10px;color:var(--muted);margin-top:9px;font-weight:600}
.kpi .vl{font-family:__NUM__;font-size:31px;font-weight:700;line-height:1.15;margin-top:2px;
  background:linear-gradient(135deg,__VLG1__,__VLG2__);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.kpi .dl{font-family:__NUM__;font-size:10.5px;margin-top:7px;display:inline-block;padding:3px 10px;border-radius:999px;font-weight:600}
.up{background:rgba(201,168,76,.16);color:var(--gold);border:1px solid rgba(201,168,76,.3)}
.dn{background:rgba(224,122,95,.14);color:#e07a5f;border:1px solid rgba(224,122,95,.3)}
.nt{background:rgba(74,111,165,.14);color:__NAVYTX__;border:1px solid rgba(74,111,165,.3)}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
.kpi:nth-child(2){animation-delay:.06s}.kpi:nth-child(3){animation-delay:.12s}
.kpi:nth-child(4){animation-delay:.18s}.kpi:nth-child(5){animation-delay:.24s}
@media(max-width:1100px){.kpis{grid-template-columns:repeat(2,1fr)}}

.fbar-head{display:flex;align-items:center;gap:12px;margin:4px 0 8px}
.fbar-head .bar{width:10px;height:10px;border-radius:2.5px;transform:rotate(45deg);
  background:linear-gradient(135deg,#c9a84c,#e07a5f);box-shadow:0 0 12px rgba(201,168,76,.55)}
.fbar-head h3{font-family:__DISP__;font-size:19px;font-weight:700;margin:0}
[data-testid="stVerticalBlockBorderWrapper"]{background:linear-gradient(145deg,__GLASS__,__GLASS2__) !important;
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid __BORDER__ !important;
  border-radius:20px !important;box-shadow:0 10px 30px rgba(0,0,0,.18)}
[data-testid="stVerticalBlockBorderWrapper"]:hover{border-color:rgba(201,168,76,.45) !important}

.sec{display:flex;align-items:center;gap:12px;margin:2px 0 6px}
.sec .bar{width:10px;height:10px;flex:none;border-radius:2.5px;transform:rotate(45deg);
  background:linear-gradient(135deg,#c9a84c,#e07a5f);box-shadow:0 0 12px rgba(201,168,76,.55)}
.sec h3{font-family:__DISP__;font-size:20px;font-weight:700;margin:0;letter-spacing:.2px}
.cap{color:var(--muted);font-size:12.5px;margin:-2px 0 6px}

.stButton>button{background:linear-gradient(135deg,#1a2a6c,#c9a84c);color:#fff;border:none;
  border-radius:50px;padding:9px 22px;font-weight:600;font-family:__SUB__;letter-spacing:.3px;width:100%;
  box-shadow:0 4px 15px rgba(26,42,108,.35);transition:all .3s ease;text-shadow:0 1px 2px rgba(0,0,0,.25)}
.stButton>button p{color:#fff;font-weight:600}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(201,168,76,.4);color:#fff}
/* أزرار الاقتراحات: مظهر outline ذهبي يميّزها عن أزرار الأفعال */
.sugbtn button{background:linear-gradient(145deg,__GLASS__,__GLASS2__) !important;color:var(--text) !important;
  border:1px solid __BORDER__ !important;border-radius:14px !important;text-align:start !important;
  justify-content:flex-start !important;height:auto !important;white-space:normal !important;
  line-height:1.45 !important;font-size:12.5px !important;padding:11px 14px !important;
  text-shadow:none !important;box-shadow:none !important}
.sugbtn button p{color:var(--text) !important;font-weight:600 !important;text-align:start !important}
.sugbtn button:hover{background:linear-gradient(135deg,rgba(26,42,108,.32),rgba(201,168,76,.14)) !important;
  border-color:#c9a84c !important;color:var(--gold) !important;transform:translateY(-2px);
  box-shadow:0 8px 22px rgba(201,168,76,.16) !important}
.sugbtn button:hover p{color:var(--gold) !important}
.stDownloadButton>button{background:transparent;border:1px solid __BORDER__;color:var(--gold);
  border-radius:50px;padding:8px 18px;font-weight:600;font-family:__SUB__;font-size:12.5px;width:100%;transition:all .3s ease}
.stDownloadButton>button p{color:var(--gold);font-weight:600}
.stDownloadButton>button:hover{background:rgba(201,168,76,.12);transform:translateY(-2px);border-color:#c9a84c}

.stTabs [data-baseweb="tab-list"]{gap:8px;border-bottom:1px solid __BORDERSOFT__;padding:4px 2px;flex-wrap:wrap}
.stTabs [data-baseweb="tab"]{position:relative;border-radius:30px;padding:10px 20px;font-weight:600;
  font-family:__SUB__;font-size:13px;color:var(--muted);border:1px solid transparent;transition:all .3s ease}
.stTabs [data-baseweb="tab"]:hover{color:var(--gold);background:rgba(201,168,76,.08)}
.stTabs [data-baseweb="tab"][aria-selected="true"]{background:linear-gradient(135deg,rgba(26,42,108,.32),rgba(201,168,76,.20));
  color:var(--gold);border:1px solid rgba(201,168,76,.35);box-shadow:0 4px 18px rgba(201,168,76,.14)}
.stTabs [data-baseweb="tab"]::after{content:"";position:absolute;left:20px;right:20px;bottom:5px;height:2px;
  border-radius:2px;background:linear-gradient(90deg,#c9a84c,#e07a5f);transform:scaleX(0);transform-origin:center;transition:transform .35s ease}
.stTabs [data-baseweb="tab"][aria-selected="true"]::after{transform:scaleX(1)}

section[data-testid="stSidebar"]{background:linear-gradient(180deg,__BG__,__CARD__);border-inline-end:1px solid rgba(201,168,76,.15)}
section[data-testid="stSidebar"] .block-container{padding-top:2.2rem}
.fbox{background:linear-gradient(145deg,__GLASS__,__GLASS2__);backdrop-filter:blur(10px);border:1px solid __BORDER__;
  border-radius:14px;padding:12px 14px;font-size:13px;margin:8px 0 16px;transition:border-color .3s, box-shadow .3s}
.fbox:hover{border-color:#c9a84c;box-shadow:0 8px 24px rgba(201,168,76,.12)}
.fbox b{font-family:__NUM__;color:var(--gold);font-size:15.5px}
[data-baseweb="select"]>div:first-of-type{background:__GLASS__;border:1px solid __BORDER__;border-radius:12px;
  color:var(--text);transition:border-color .25s, box-shadow .25s}
[data-baseweb="select"]:hover>div:first-of-type{border-color:#c9a84c;box-shadow:0 0 0 3px rgba(201,168,76,.12)}
[data-baseweb="tag"]{background:__TAG__;border:1px solid rgba(201,168,76,.3);border-radius:20px}
[data-baseweb="popover"]{background:var(--card2);border:1px solid __BORDER__;box-shadow:0 18px 44px rgba(0,0,0,.35)}
[data-baseweb="popover"] li{color:var(--text)}
[data-baseweb="popover"] li:hover,[data-baseweb="popover"] li[aria-selected="true"]{background:rgba(201,168,76,.14)}
[data-baseweb="slider"] div[role="slider"]{background:linear-gradient(135deg,#1a2a6c,#c9a84c);border:none;box-shadow:0 2px 12px rgba(201,168,76,.45)}
div[role="progressbar"]{background:linear-gradient(90deg,#1a2a6c,#c9a84c)!important;border-radius:8px}
label{color:var(--text);font-family:__SUB__;font-weight:600;font-size:13px}
[data-testid="stDataFrame"]{border:1px solid __BORDER__;border-radius:14px;overflow:hidden}

[data-testid="stBottom"], [data-testid="stChatInputContainer"]{background:transparent !important;backdrop-filter:none !important}
[data-testid="stBottom"]::before, [data-testid="stChatInputContainer"]::before{display:none !important}
[data-testid="stBottom"] > div{background:transparent !important}
[data-testid="stChatInput"]{background:linear-gradient(145deg,__GLASS__,__GLASS2__) !important;
  backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid __BORDER__ !important;
  border-radius:18px !important;box-shadow:0 8px 30px rgba(0,0,0,.28) !important;transition:all .3s}
[data-testid="stChatInput"]:focus-within{border-color:#c9a84c !important;box-shadow:0 0 0 3px rgba(201,168,76,.18),0 8px 30px rgba(0,0,0,.3) !important}
[data-testid="stChatInput"] textarea{background:transparent !important;color:var(--text) !important}
[data-testid="stChatInput"] svg{color:var(--gold) !important}

.chatpanel{position:fixed;bottom:96px;right:18px;width:min(360px,88vw);z-index:1100;font-family:__BODY__}
.chatpanel details{background:linear-gradient(165deg,__GLASS__,__GLASS2__);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border:1px solid __BORDER__;border-radius:22px;box-shadow:0 22px 50px rgba(0,0,0,.35);overflow:hidden;animation:rise .4s both}
.chatpanel summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:9px;padding:13px 16px;
  font-weight:700;font-size:14px;font-family:__SUB__;user-select:none;color:var(--gold)}
.chatpanel summary::-webkit-details-marker{display:none}
.dotlive{width:8px;height:8px;border-radius:50%;background:#e07a5f;margin-inline-start:auto;animation:pulse 2.4s infinite}
.chatpanel .body{max-height:46vh;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:9px}
.bub{max-width:88%;padding:10px 14px;font-size:13.5px;line-height:1.65;animation:rise .3s both;box-shadow:0 4px 14px rgba(0,0,0,.18)}
.bub.u{align-self:flex-end;background:linear-gradient(135deg,#1a2a6c,#2a3a7c);color:#fff;border-radius:20px 20px 4px 20px}
.bub.b{align-self:flex-start;color:var(--text);background:linear-gradient(135deg,rgba(201,168,76,.16),rgba(201,168,76,.05));
  border:1px solid rgba(201,168,76,.25);border-radius:20px 20px 20px 4px}
.chatrtl .bub.u{align-self:flex-start}.chatrtl .bub.b{align-self:flex-end}.chatrtl .bub{text-align:right}
.chatpanel .empty{color:var(--muted);font-size:12.5px;text-align:center;padding:12px 6px}

.statcard{background:linear-gradient(145deg,__GLASS__,__GLASS2__);backdrop-filter:blur(12px);border:1px solid __BORDER__;
  border-radius:20px;padding:18px 20px;position:relative;overflow:hidden;transition:all .35s ease}
.statcard:hover{transform:translateY(-4px);border-color:#c9a84c;box-shadow:0 12px 34px rgba(201,168,76,.16)}
.statcard .lb{font-family:__SUB__;text-transform:uppercase;letter-spacing:1.3px;font-size:10px;color:var(--muted);font-weight:600}
.statcard .big{font-family:__DISP__;font-size:27px;font-weight:800;margin-top:5px}
.statcard .sub{font-family:__NUM__;color:var(--muted);font-size:13px;margin-top:5px}
.statcard .em{position:absolute;top:12px;inset-inline-end:16px;font-size:27px;opacity:.9}
[data-testid="stChatMessage"]{background:transparent;padding:6px 0}
.foot{text-align:center;color:var(--muted);font-family:__SUB__;font-size:11.5px;letter-spacing:.6px;
  padding:28px 0 10px;border-top:1px solid __BORDERSOFT__;margin-top:28px}
.foot b{color:var(--gold)}
__RTL__
"""
RTL_CSS = """
section.main .block-container{direction:rtl;text-align:right}
section[data-testid="stSidebar"]{direction:rtl}
section[data-testid="stSidebar"] *{text-align:right}
.stTabs [data-baseweb="tab-list"]{direction:rtl}
.sugbtn button, .sugbtn button p{text-align:right !important;justify-content:flex-end !important}
"""
_css = (CSS_TPL
  .replace("__BG__", C["bg"]).replace("__CARD__", C["card"]).replace("__CARD2__", C["card2"])
  .replace("__TEXT__", C["text"]).replace("__MUTED__", C["muted"]).replace("__GOLDTX__", C["goldtx"])
  .replace("__BORDER__", C["border"]).replace("__BORDERSOFT__", C["border_soft"])
  .replace("__GLASS__", C["glass"]).replace("__GLASS2__", C["glass2"]).replace("__TAG__", C["tag"])
  .replace("__VLG1__", C["vlg1"]).replace("__VLG2__", C["vlg2"]).replace("__HLG1__", C["hlg1"]).replace("__HLG2__", C["hlg2"])
  .replace("__O1__", C["o1"]).replace("__O2__", C["o2"]).replace("__O3__", C["o3"]).replace("__DOT__", C["dot"])
  .replace("__NAVYTX__", "#8fb3ec" if DARK else "#1a2a6c")
  .replace("__BODY__", FONT_BODY).replace("__SUB__", FONT_SUB).replace("__DISP__", FONT_DISP)
  .replace("__NUM__", FONT_NUM).replace("__RTL__", RTL_CSS if L == "ar" else ""))
st.markdown(f"<style>{_css}</style>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 3) DATA
# ═══════════════════════════════════════════════════════════════
def make_demo_data():
    rng = np.random.default_rng(7); n = 8000
    brands = ["Grand","Royal","Azure","Pearl","Oasis","Marina","Sultan","Mirage","Cedar","Lotus","Ivory","Falcon","Palmyra","Coral","Velvet"]
    kinds = ["Palace","Plaza","Resort","Suites"]
    cities = ["Dubai","Istanbul","Cairo","Paris","London","Rome","Madrid","Vienna","Prague","Lisbon","Doha","Marrakech"]
    hotels = [f"{b} {k} {c}" for b in brands for k in kinds for c in cities][:180]
    tt = rng.choice(["Couple","Solo Traveler","Family","Business","Group"], n, p=[.38,.22,.20,.12,.08])
    room = rng.choice(["Double Room","Twin Room","Deluxe Room","Suite","Family Room","Single Room","Standard Room"], n,
                      p=[.28,.18,.16,.14,.10,.08,.06])
    nats = ["United Kingdom","United States of America","France","Germany","Spain","Italy","Netherlands","Australia",
            "Canada","Japan","Brazil","India","United Arab Emirates","Egypt","Saudi Arabia","Turkey"]
    nat = rng.choice(nats, n, p=[.14,.12,.09,.08,.07,.07,.06,.06,.05,.05,.05,.04,.04,.03,.03,.02])
    dates = pd.to_datetime("2018-01-01") + pd.to_timedelta(rng.integers(0, 2900, n), unit="D")
    score = np.clip(np.round(rng.beta(5, 2, n) * 10, 1), 2.5, 10)
    nights = rng.choice(range(1, 13), n, p=np.array([18,16,14,12,10,8,7,5,4,3,2,1])/100)
    quality = np.clip(score * 9 + rng.normal(0, 8, n) + 8, 20, 100).round(1)
    susp = rng.choice(["Low","Medium","High"], n, p=[.90,.07,.03])
    pos = ["Great location","Friendly staff","Clean rooms","Amazing breakfast","Comfortable bed","موقع ممتاز","طاقم ودود","غرف نظيفة","إفطار رائع","تجربة مميزة","Beautiful view","Will come back"]
    neg = ["Noisy street","Slow wifi","Small room","Old furniture","Weak AC","ضجيج في الشارع","واي فاي بطيء","غرفة صغيرة","أثاث قديم","تكييف ضعيف","Pricey parking"]
    P = [f"{rng.choice(pos)} {rng.choice(pos)}".strip() for _ in range(n)]
    N = [f"{rng.choice(neg)}".strip() if rng.random() < .7 else "No Negative" for _ in range(n)]
    return pd.DataFrame({"Hotel_Name": rng.choice(hotels, n), "Reviewer_Score_Fixed": score, "Traveler_Type": tt,
        "Room_Type": room, "Reviewer_Nationality": nat, "Review_Date_Fixed": dates,
        "Negative_Review_Cleaned": N, "Positive_Review_Cleaned": P,
        "Review_Consistency": rng.choice(["Consistent","Mixed"], n, p=[.85,.15]),
        "Review_Quality_Score": quality, "Nights_Stayed": nights, "Suspicion_Level": susp})

@st.cache_data(show_spinner=False)
def load_data():
    try:
        df = pd.read_csv("Hotel_Reviews_ULTIMATE_CLEAN.csv"); demo = False
    except Exception:
        df, demo = make_demo_data(), True
    for col in ("Reviewer_Score_Fixed", "Nights_Stayed", "Review_Quality_Score"):
        if col in df: df[col] = pd.to_numeric(df[col], errors="coerce")
    if "Review_Date_Fixed" in df:
        df["Review_Date_Fixed"] = pd.to_datetime(df["Review_Date_Fixed"], errors="coerce")
        df["month"] = df["Review_Date_Fixed"].dt.month
        df["year"] = df["Review_Date_Fixed"].dt.year
    return df.dropna(subset=["Reviewer_Score_Fixed"]), demo

df, IS_DEMO = load_data()

# ═══════════════════════════════════════════════════════════════
# 4) SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    cA, cB = st.columns(2)
    if cA.button("🇸🇦 العربية" if L == "en" else "🇬🇧 English", key="sb_lang"):
        st.session_state.lang = "ar" if L == "en" else "en"
    if cB.button("☀️" if DARK else "🌙", key="sb_theme"):
        st.session_state.dark = not DARK
    st.markdown(f'<div class="sec"><span class="bar"></span><h3>{t("sb_export")}</h3></div>', unsafe_allow_html=True)
    st.toggle(t("sb_png"), value=st.session_state.png_on, key="png_on")
    st.caption(t("dl_note") if not st.session_state.png_on else "✅ PNG ready per chart.")
    st.markdown(f'<div class="sec"><span class="bar"></span><h3>{t("sb_quick")}</h3></div>', unsafe_allow_html=True)
    st.caption(t("sb_src_demo") if IS_DEMO else t("sb_src_csv"))

# ═══════════════════════════════════════════════════════════════
# 5) CHART HELPERS
# ═══════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def _fig_png(spec_json: str):
    return go.Figure(json.loads(spec_json)).to_image(format="png", scale=2, width=1200, height=640)

def style(fig, title=None, h=430):
    fig.update_layout(template=C["tpl"], paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_SUB, size=12.5, color=C["text"]), colorway=PALETTE,
        margin=dict(l=16, r=16, t=50, b=16), height=h,
        title=dict(text=title or "", font=dict(family=FONT_DISP, size=18, color=C["text"])),
        hoverlabel=dict(bgcolor=C["card2"], font_size=13, font_family=FONT_SUB, bordercolor=C["gold"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1))
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(color=C["muted"]))
    fig.update_yaxes(gridcolor=C["grid"], tickfont=dict(color=C["muted"]))
    return fig

def chart_sec(title, fig, key, caption=None):
    a, b = st.columns([7, 1])
    a.markdown(f'<div class="sec"><span class="bar"></span><h3>{title}</h3></div>', unsafe_allow_html=True)
    if st.session_state.png_on:
        try:
            b.download_button(t("dl_png"), _fig_png(fig.to_json()), file_name=f"{key}.png",
                              mime="image/png", key=f"dl_{key}")
        except Exception:
            b.caption("kaleido?")
    if caption: st.caption(caption)
    st.plotly_chart(fig, use_container_width=True, key=f"pc_{key}",
                    config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})

# ═══════════════════════════════════════════════════════════════
# 6) MASTHEAD
# ═══════════════════════════════════════════════════════════════
SKYLINE = '<svg viewBox="0 0 1200 80" preserveAspectRatio="none"><path fill="currentColor" d="M0 80 0 55 40 55 40 38 62 38 62 50 90 50 90 24 96 24 96 12 100 4 104 12 104 24 110 24 110 50 140 50 140 34 170 34 170 55 210 55 210 42 240 42 240 58 280 58 280 30 300 30 300 20 306 20 306 30 320 30 320 58 360 58 360 44 400 44 400 52 440 52 440 26 448 26 448 14 452 6 456 14 456 26 464 26 464 52 500 52 500 40 540 40 540 56 580 56 580 36 610 36 610 48 650 48 650 22 658 22 658 10 662 2 666 10 666 22 674 22 674 48 710 48 710 42 750 42 750 54 790 54 790 32 820 32 820 50 860 50 860 40 900 40 900 56 940 56 940 28 948 28 948 16 952 8 956 16 956 28 964 28 964 56 1000 56 1000 44 1040 44 1040 52 1080 52 1080 34 1120 34 1120 58 1160 58 1160 46 1200 46 1200 80 Z"/></svg>'
dmin, dmax = df["Review_Date_Fixed"].min(), df["Review_Date_Fixed"].max()
span = f"{dmin:%Y}–{dmax:%Y}" if pd.notna(dmin) else "—"
st.markdown(
    f'''<div class="ambient"><span class="orb o1"></span><span class="orb o2"></span><span class="orb o3"></span></div>
    <div class="mast"><div class="masttop"><div class="logo">🏨</div>
      <div style="flex:1;min-width:280px">
        <div class="eyebrow"><span class="pulse"></span>
          <span>{len(df):,} {t("reviews")} · {df["Hotel_Name"].nunique():,} {t("hotels")} · {t("period")}: {span}</span>
          <span class="badge">✨ {t("badge")}</span></div>
        <h1>{t("mast_title")}</h1></div></div>
      <div class="tag">{t("mast_tag")}</div><div class="skyline">{SKYLINE}</div></div>''',
    unsafe_allow_html=True)

h1, h2, h3, _ = st.columns([1, 1, 1, 5])
if h1.button("🇸🇦 العربية" if L == "en" else "🇬🇧 English", key="hd_lang"):
    st.session_state.lang = "ar" if L == "en" else "en"
if h2.button("☀️ Light" if DARK else "🌙 Dark", key="hd_theme"):
    st.session_state.dark = not DARK
if h3.button("💬 ✕" if st.session_state.chat_open else "💬", key="hd_chat"):
    st.session_state.chat_open = not st.session_state.chat_open

# ═══════════════════════════════════════════════════════════════
# 7) SPARKLINE HELPER
# ═══════════════════════════════════════════════════════════════
def spark(vals, up):
    if not vals or len(vals) < 2: return ""
    mn, mx = min(vals), max(vals); rng = (mx - mn) or 1; w, h, n = 88, 28, len(vals)
    pts = [(i/(n-1)*w, h-((v-mn)/rng)*(h-5)-2.5) for i, v in enumerate(vals)]
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    col = "#c9a84c" if up else "#e07a5f"
    area = f"{d} L {w:.1f},{h} L 0,{h} Z"
    return (f'<svg class="spark" viewBox="0 0 {w} {h}" preserveAspectRatio="none">'
            f'<path d="{area}" fill="{col}" opacity=".13"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="2.5" fill="{col}"/></svg>')

def mom_pct(s):
    if s is None or len(s) < 2: return None
    a, b = s.iloc[-2], s.iloc[-1]
    return ((b - a) / a * 100) if a else None

def delta_html(v):
    if v is None: return f'<span class="dl nt">— {t("mom_na")}</span>', False
    up = v >= 0
    return f'<span class="dl {"up" if up else "dn"}">{"▲" if up else "▼"} {abs(v):.1f}% {t("vs_prev")}</span>', up

# ═══════════════════════════════════════════════════════════════
# 8) TOP FILTER BAR
# ═══════════════════════════════════════════════════════════════
tt_opts = sorted(df["Traveler_Type"].dropna().unique().tolist())
hotel_opts = sorted(df["Hotel_Name"].dropna().unique().tolist())
room_opts = sorted(df["Room_Type"].dropna().unique().tolist())

st.markdown(f'<div class="fbar-head"><span class="bar"></span><h3>{t("fb_title")}</h3></div>', unsafe_allow_html=True)
with st.container(border=True):
    fc1, fc2, fc3, fc4, fc5 = st.columns([2, 2, 2, 2, 1])
    with fc1:
        sel_tt = st.multiselect(t("sb_traveler"), tt_opts, default=tt_opts, format_func=tt_name, key="f_tt")
    with fc2:
        sel_ht = st.multiselect(t("sb_hotel"), hotel_opts, default=hotel_opts, key="f_ht")
    with fc3:
        sel_rm = st.multiselect(t("sb_room"), room_opts, default=room_opts, format_func=room_name, key="f_rm")
    with fc4:
        lo, hi = st.slider(t("sb_score"), 0.0, 10.0, (0.0, 10.0), 0.5, key="f_score")
    with fc5:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        if st.button(t("sb_reset"), key="reset_btn"):
            for k in ("f_tt", "f_ht", "f_rm"): st.session_state.pop(k, None)
            st.session_state["f_score"] = (0.0, 10.0)

fdf = df[df["Traveler_Type"].isin(sel_tt) & df["Hotel_Name"].isin(sel_ht) &
         df["Room_Type"].isin(sel_rm) & df["Reviewer_Score_Fixed"].between(lo, hi)]
favg = fdf["Reviewer_Score_Fixed"].mean() if len(fdf) else 0.0
st.markdown(f'<div class="fbox" style="margin-top:10px">🧾 <b>{len(fdf):,}</b> {t("sb_matching")} '
            f'&nbsp;·&nbsp; ⭐ <b>{favg:.2f}</b> {t("sb_avg_after")}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 9) KPIs + MoM + SPARKLINES
# ═══════════════════════════════════════════════════════════════
md = fdf.dropna(subset=["Review_Date_Fixed"]).copy()
if len(md):
    md["ym"] = md["Review_Date_Fixed"].dt.to_period("M")
    g = md.groupby("ym")
    s_rev, s_score, s_hot = g.size(), g["Reviewer_Score_Fixed"].mean(), g["Hotel_Name"].nunique()
    s_night = g["Nights_Stayed"].mean() if "Nights_Stayed" in fdf else None
    s_qual = g["Review_Quality_Score"].mean() if "Review_Quality_Score" in fdf else None
else:
    s_rev = s_score = s_hot = s_night = s_qual = pd.Series(dtype=float)

n_all, n_f = len(df), len(fdf)
avg_f = favg
nights_f = fdf["Nights_Stayed"].mean() if n_f and "Nights_Stayed" in fdf else 0.0
qual_f = fdf["Review_Quality_Score"].mean() if n_f and "Review_Quality_Score" in fdf else 0.0

def kpi(icon, label, value, d_html, sp, delay):
    return (f'<div class="kpi" style="animation-delay:{delay}s"><div class="row1">{icon}{sp}</div>'
            f'<div class="lb">{label}</div><div class="vl">{value}</div>{d_html}</div>')

ic = lambda e: f'<div class="ic">{e}</div>'
d_rev, up = delta_html(mom_pct(s_rev))
d_score, up2 = delta_html(mom_pct(s_score))
d_hot, up3 = delta_html(mom_pct(s_hot))
d_night, up4 = delta_html(mom_pct(s_night))
d_qual, up5 = delta_html(mom_pct(s_qual))

kpis = (
    kpi(ic("🧾"), t("k_reviews"), f"{n_f:,}", d_rev, spark(list(s_rev), up), 0) +
    kpi(ic("⭐"), t("k_score"), f"{avg_f:.2f}", d_score, spark(list(s_score), up2), .06) +
    kpi(ic("🏨"), t("k_hotels"), f"{fdf['Hotel_Name'].nunique() if n_f else 0:,}", d_hot, spark(list(s_hot), up3), .12) +
    kpi(ic("🌙"), t("k_nights"), f"{nights_f:.1f}", d_night, spark(list(s_night) if s_night is not None else [], up4), .18) +
    kpi(ic("✅"), t("k_quality"), f"{qual_f:.0f}", d_qual, spark(list(s_qual) if s_qual is not None else [], up5), .24))
st.markdown(f'<div class="kpis">{kpis}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 10) AI ENGINE
# ═══════════════════════════════════════════════════════════════
MIN_REV = 20
def detect_language(text): return "ar" if re.search(r"[\u0600-\u06FF]", text or "") else "en"
def _ranked(data, col, ascending=False):
    g = data.groupby(col)["Reviewer_Score_Fixed"]; means, counts = g.mean(), g.size()
    el = means[counts >= MIN_REV]; used = not el.empty
    if not used: el = means
    return el.sort_values(ascending=ascending), counts, used

TT_KW = {"Couple": (["couple"], ["أزواج","زوجين","الازواج","ثنائي"]),
         "Solo Traveler": (["solo","alone","single traveler"], ["منفرد","فردي","سولو"]),
         "Family": (["family","families","kids"], ["عائل","عائلات","أسر","اسر","أطفال","اطفال"]),
         "Business": (["business"], ["أعمال","اعمال","رحلة عمل"]),
         "Group": (["group","friends"], ["مجموع","أصدقاء","اصدقاء","جماع"])}

def get_ai_response(question, data):
    q = (question or "").lower(); ar = detect_language(question) == "ar"
    if data is None or data.empty:
        return ("⚠️ لا توجد بيانات مطابقة للفلاتر الحالية." if ar else "⚠️ No data matches the current filters.")
    has = lambda *ks: any(k in q for k in ks); S = data["Reviewer_Score_Fixed"]
    if has("top 5","top five","top5") or has("أفضل 5","افضل 5","أفضل خمس","افضل خمس"):
        el, counts, _ = _ranked(data, "Hotel_Name")
        lines = "\n".join(f"{i+1}. **{h}** — {s:.2f} ({counts[h]:,})" for i,(h,s) in enumerate(el.head(5).items()))
        return (f"🏆 **أفضل 5 فنادق:**\n{lines}" if ar else f"🏆 **Top 5 hotels:**\n{lines}")
    if (has("best hotel","highest rating","highest rated","top hotel") and not has("nationality")) or has("أفضل فندق","افضل فندق","أعلى تقييم","اعلى تقييم"):
        el, counts, mn = _ranked(data, "Hotel_Name"); h, s = el.index[0], el.iloc[0]
        note = " _(≥20 مراجعة)_" if mn else ""
        return (f"🏆 أفضل فندق من حيث التقييم هو **{h}** بمتوسط **{s:.2f}** ({counts[h]:,} مراجعة).{note}" if ar
                else f"🏆 The highest rated hotel is **{h}** with a score of **{s:.2f}** ({counts[h]:,} reviews).{note}")
    if has("worst hotel","lowest rating") or has("أسوأ فندق","اسوا فندق","أدنى تقييم","ادنى تقييم"):
        el, counts, _ = _ranked(data, "Hotel_Name", ascending=True); h, s = el.index[0], el.iloc[0]
        return (f"📉 أدنى فندق تقييمًا هو **{h}** بمتوسط **{s:.2f}** ({counts[h]:,} مراجعة)." if ar
                else f"📉 The lowest rated hotel is **{h}** with a score of **{s:.2f}** ({counts[h]:,} reviews).")
    if has("how many","total reviews","number of reviews") or has("كم عدد","عدد المراجعات","كم مراجعة"):
        return (f"🧾 يوجد **{len(data):,}** مراجعة عبر **{data['Hotel_Name'].nunique():,}** فندقًا (وفق الفلاتر الحالية)." if ar
                else f"🧾 There are **{len(data):,}** reviews across **{data['Hotel_Name'].nunique():,}** hotels (current filters).")
    if has("best month") or has("أفضل شهر","افضل شهر") or has("month") or has("شهر"):
        m = data.dropna(subset=["month"]).groupby("month")["Reviewer_Score_Fixed"].mean()
        if m.empty: return "📅 لا توجد تواريخ صالحة." if ar else "📅 No valid dates available."
        bm = m.idxmax()
        return (f"📅 أفضل شهر للسفر هو **{MONTHS['ar'][bm-1]}** بمتوسط تقييم **{m.max():.2f}**." if ar
                else f"📅 The best month for reviews is **{MONTHS['en'][bm-1]}** with an average score of **{m.max():.2f}**.")
    if has("which nationality","nationality") or has("أي جنسية","اي جنسية","جنسية"):
        el, counts, mn = _ranked(data, "Reviewer_Nationality"); nt, v = el.index[0], el.iloc[0]
        note = " _(≥20 مراجعة)_" if mn else ""
        return (f"🌍 أعلى الجنسيات تقييمًا هي **{nt}** بمتوسط **{v:.2f}** ({counts[nt]:,} مراجعة).{note}" if ar
                else f"🌍 The highest-rating nationality is **{nt}** with an average of **{v:.2f}** ({counts[nt]:,} reviews).{note}")
    if has("room type","most common room","rooms") or has("نوع الغرفة","الغرفة","الغرف"):
        rc = data["Room_Type"].value_counts(); rm, c = rc.index[0], rc.iloc[0]
        return (f"🛏️ نوع الغرفة الأكثر شيوعًا هو **{room_name(rm)}** بعدد **{c:,}** مراجعة ({c/len(data)*100:.1f}%)." if ar
                else f"🛏️ The most common room type is **{rm}** with **{c:,}** reviews ({c/len(data)*100:.1f}%).")
    if has("nights","length of stay") or has("ليالي","ليال","مدة الإقامة","مدة الاقامة"):
        v = data["Nights_Stayed"].mean()
        return (f"🌙 متوسط عدد ليالي الإقامة هو **{v:.1f}** ليلة." if ar else f"🌙 The average number of nights stayed is **{v:.1f}**.")
    for tt,(en_kw,ar_kw) in TT_KW.items():
        if has(*en_kw) or has(*ar_kw):
            sub = data[data["Traveler_Type"] == tt]
            if sub.empty: return f"⚠️ لا توجد بيانات لفئة {TT_AR[tt]}." if ar else f"⚠️ No data for {tt}."
            v = sub["Reviewer_Score_Fixed"].mean(); name = TT_AR[tt] if ar else tt
            return (f"📊 متوسط تقييم **{name}** هو **{v:.2f}** من 10 ({len(sub):,} مراجعة)." if ar
                    else f"📊 The average score for **{name}** is **{v:.2f}** out of 10 ({len(sub):,} reviews).")
    if has("average","score","rating") or has("متوسط","تقييم"):
        return (f"📊 المتوسط العام للتقييم هو **{S.mean():.2f}** / 10 عبر **{len(data):,}** مراجعة." if ar
                else f"📊 The overall average score is **{S.mean():.2f}** / 10 across **{len(data):,}** reviews.")
    if has("quality") or has("جودة"):
        return (f"✅ متوسط جودة المراجعات هو **{data['Review_Quality_Score'].mean():.1f} / 100**." if ar
                else f"✅ Average review quality score is **{data['Review_Quality_Score'].mean():.1f} / 100**.")
    if has("suspicious","suspicion","fake") or has("مريب","اشتباه","شك","مزيف"):
        parts = " · ".join(f"{sus_name(k)} **{v:.0%}**" for k,v in data["Suspicion_Level"].value_counts(normalize=True).items())
        return f"🕵️ توزيع الاشتباه: {parts}" if ar else f"🕵️ Suspicion breakdown: {parts}"
    return ("❌ عذرًا، لم أفهم سؤالك. الرجاء استخدام أحد الأسئلة المقترحة." if ar
            else "❌ Sorry, I didn't understand your question. Please use one of the suggested questions.")

SUG = {"en": ["What is the average score for Couples?","Which hotel has the highest rating?",
        "What is the best month to travel?","Which nationality gives the highest ratings?",
        "What is the most common room type?","What are the top 5 hotels?",
        "How many reviews do we have?","What is the average number of nights stayed?"],
       "ar": ["ما هو متوسط تقييم الأزواج؟","أي فندق حصل على أعلى تقييم؟","ما هو أفضل شهر للسفر؟",
        "أي جنسية تعطي أعلى التقييمات؟","ما هو نوع الغرفة الأكثر شيوعاً؟","ما هي أفضل 5 فنادق؟",
        "كم عدد المراجعات الموجودة؟","ما هو متوسط عدد ليالي الإقامة؟"]}

def ask(question):
    st.session_state.chat_history.append({"r": "u", "t": question.strip()})
    st.session_state.chat_history.append({"r": "b", "t": get_ai_response(question, fdf)})
    st.session_state.chat_history = st.session_state.chat_history[-30:]

# ═══════════════════════════════════════════════════════════════
# 11) TABS
# ═══════════════════════════════════════════════════════════════
if fdf.empty:
    st.warning(t("no_data"))
else:
    tabs = st.tabs([t("tb_ratings"), t("tb_hotels"), t("tb_nat"), t("tb_season"),
                    t("tb_trends"), t("tb_wc"), t("tb_ai"), t("tb_data")])
    tmp = fdf.copy(); tmp["tt"] = tmp["Traveler_Type"].map(tt_name); tmp["room"] = tmp["Room_Type"].map(room_name)

    with tabs[0]:
        fig = go.Figure(go.Histogram(x=fdf["Reviewer_Score_Fixed"], xbins=dict(start=0, end=10, size=0.5),
            marker_color=C["gold"], marker_line_color=C["navy"], marker_line_width=1,
            hovertemplate="%{x} ★ : %{y} " + t("reviews") + "<extra></extra>"))
        mu = fdf["Reviewer_Score_Fixed"].mean()
        fig.add_vline(x=mu, line_dash="dash", line_color=C["orange"], line_width=2,
                      annotation_text=f"μ = {mu:.2f}", annotation_font_color=C["orange"])
        chart_sec(t("c_hist"), style(fig, t("c_hist")), "hist")
        m = tmp.groupby("tt")["Reviewer_Score_Fixed"].mean().sort_values(ascending=False)
        fig = go.Figure(go.Bar(x=m.index, y=m.values, marker_color=m.values, marker_colorscale=NAVY_GOLD,
            text=[f"{v:.2f}" for v in m.values], textposition="outside", textfont=dict(family=FONT_NUM)))
        chart_sec(t("c_tt_bar"), style(fig, t("c_tt_bar")), "tt_bar")
        fig = px.box(tmp, x="tt", y="Reviewer_Score_Fixed", points="outliers", color="tt", color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False)
        chart_sec(t("c_tt_box"), style(fig, t("c_tt_box")), "tt_box")

    with tabs[1]:
        el, counts, _ = _ranked(fdf, "Hotel_Name")
        top10 = el.head(10)[::-1]
        fig = go.Figure(go.Bar(y=top10.index, x=top10.values, orientation="h", marker_color=top10.values,
            marker_colorscale=LUX_SCALE, text=[f"{v:.2f}" for v in top10.values], textposition="outside",
            textfont=dict(family=FONT_NUM), customdata=[counts[h] for h in top10.index],
            hovertemplate="%{y}<br>%{x:.2f} ★ · %{customdata:,} " + t("reviews") + "<extra></extra>"))
        chart_sec(t("c_top10"), style(fig, t("c_top10"), h=480), "top10", t("cap_minrev"))
        bot5 = el.tail(5)
        fig = go.Figure(go.Bar(y=bot5.index, x=bot5.values, orientation="h", marker_color=C["orange"],
            text=[f"{v:.2f}" for v in bot5.values], textposition="outside", textfont=dict(family=FONT_NUM),
            customdata=[counts[h] for h in bot5.index],
            hovertemplate="%{y}<br>%{x:.2f} ★ · %{customdata:,} " + t("reviews") + "<extra></extra>"))
        chart_sec(t("c_bottom"), style(fig, t("c_bottom"), h=320), "bottom5", t("cap_minrev"))
        if "Review_Date_Fixed" in fdf and len(fdf) >= 40:
            mdf = fdf.dropna(subset=["Review_Date_Fixed"]).copy(); mid = mdf["Review_Date_Fixed"].median()
            mdf["half"] = np.where(mdf["Review_Date_Fixed"] <= mid, 1, 2)
            pv = mdf.pivot_table(index="Hotel_Name", columns="half", values="Reviewer_Score_Fixed", aggfunc=["mean", "count"])
            try:
                m1, c1 = pv[("mean", 1)], pv[("count", 1)]; m2, c2 = pv[("mean", 2)], pv[("count", 2)]
                ok = (c1 >= 10) & (c2 >= 10); delta = (m2 - m1)[ok].dropna().sort_values().head(5)
                if not delta.empty:
                    fig = go.Figure(go.Bar(y=delta.index, x=delta.values, orientation="h",
                        marker_color=delta.values, marker_colorscale=[[0, C["orange"]], [1, C["sand"]]],
                        text=[f"{v:+.2f}" for v in delta.values], textposition="outside", textfont=dict(family=FONT_NUM)))
                    fig.update_xaxes(zeroline=True, zerolinecolor=C["grid"])
                    chart_sec(t("c_decline"), style(fig, t("c_decline"), h=320), "decline", t("cap_decline"))
            except Exception: pass
        rm = tmp.groupby("room")["Reviewer_Score_Fixed"].mean().sort_values(ascending=False)
        fig = go.Figure(go.Bar(x=rm.index, y=rm.values, marker_color=rm.values, marker_colorscale=NAVY_GOLD,
            text=[f"{v:.2f}" for v in rm.values], textposition="outside", textfont=dict(family=FONT_NUM)))
        chart_sec(t("c_room"), style(fig, t("c_room")), "room_bar")
        vc = fdf["Hotel_Name"].value_counts().head(30); means = fdf.groupby("Hotel_Name")["Reviewer_Score_Fixed"].mean()
        fig = px.treemap(names=vc.index, parents=[""]*len(vc), values=vc.values, color=[means[h] for h in vc.index],
                         color_continuous_scale=LUX_SCALE, range_color=[5, 10])
        fig.update_traces(hovertemplate="<b>%{label}</b><br>%{value:,} " + t("reviews") + "<br>%{color:.2f} ★<extra></extra>")
        chart_sec(t("c_tree"), style(fig, t("c_tree"), h=520), "treemap", t("cap_tree"))

    with tabs[2]:
        el, counts, _ = _ranked(fdf, "Reviewer_Nationality"); top = el.head(15)[::-1]
        fig = go.Figure(go.Bar(y=top.index, x=top.values, orientation="h", marker_color=top.values, marker_colorscale=LUX_SCALE,
            text=[f"{v:.2f}" for v in top.values], textposition="outside", textfont=dict(family=FONT_NUM),
            customdata=[counts[n] for n in top.index],
            hovertemplate="%{y}<br>%{x:.2f} ★ · %{customdata:,} " + t("reviews") + "<extra></extra>"))
        chart_sec(t("c_nat_score"), style(fig, t("c_nat_score"), h=500), "nat_score", t("cap_minrev"))
        nc = fdf["Reviewer_Nationality"].value_counts().head(15)[::-1]
        fig = go.Figure(go.Bar(y=nc.index, x=nc.values, orientation="h", marker_color=nc.values, marker_colorscale=NAVY_GOLD,
            text=[f"{v:,}" for v in nc.values], textposition="outside", textfont=dict(family=FONT_NUM)))
        chart_sec(t("c_nat_count"), style(fig, t("c_nat_count"), h=500), "nat_count")
        pc = fdf["Reviewer_Nationality"].value_counts()
        names = list(pc.head(10).index) + (["Other" if L == "en" else "أخرى"] if len(pc) > 10 else [])
        vals = list(pc.head(10).values) + ([pc.iloc[10:].sum()] if len(pc) > 10 else [])
        fig = px.pie(names=names, values=vals, hole=.42, color_discrete_sequence=PALETTE)
        fig.update_traces(hovertemplate="%{label}<br>%{value:,} (%{percent})<extra></extra>")
        chart_sec(t("c_nat_pie"), style(fig, t("c_nat_pie")), "nat_pie", t("cap_pie"))

    with tabs[3]:
        sd = fdf.dropna(subset=["month"]); mm = sd.groupby("month")["Reviewer_Score_Fixed"].mean(); mc = sd.groupby("month").size()
        lbl = [month_name(m) for m in mm.index]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=lbl, y=[mc.get(m, 0) for m in mm.index], name=t("count"), marker_color=C["navy"], opacity=.5, yaxis="y2"))
        fig.add_trace(go.Scatter(x=lbl, y=mm.values, mode="lines+markers", name=t("avg_score"),
            line=dict(color=C["gold"], width=3), marker=dict(size=9, color=C["gold_b"]), fill="tozeroy", fillcolor="rgba(201,168,76,.10)"))
        bm = mm.idxmax()
        fig.add_annotation(x=month_name(bm), y=mm.max(), text="⭐", showarrow=True, arrowcolor=C["orange"], font=dict(size=16, color=C["orange"]))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, tickfont=dict(color=C["muted"])))
        chart_sec(t("c_month"), style(fig, t("c_month")), "month_line")
        ym = sd.groupby("year")["Reviewer_Score_Fixed"].mean().sort_index()
        fig = go.Figure(go.Bar(x=[str(int(y)) for y in ym.index], y=ym.values, marker_color=ym.values, marker_colorscale=NAVY_GOLD,
            text=[f"{v:.2f}" for v in ym.values], textposition="outside", textfont=dict(family=FONT_NUM)))
        chart_sec(t("c_year"), style(fig, t("c_year"), h=380), "year_bar")
        best_m, worst_m = mm.idxmax(), mm.idxmin(); a, b = st.columns(2)
        a.markdown(f'''<div class="statcard"><span class="em">🌟</span><div class="lb">{t("c_best_m")}</div>
            <div class="big" style="color:var(--gold)">{month_name(best_m)}</div>
            <div class="sub">⭐ {mm.max():.2f} · 🧾 {mc.get(best_m,0):,} {t("reviews")}</div></div>''', unsafe_allow_html=True)
        b.markdown(f'''<div class="statcard"><span class="em">🌧️</span><div class="lb">{t("c_worst_m")}</div>
            <div class="big" style="color:#e07a5f">{month_name(worst_m)}</div>
            <div class="sub">⭐ {mm.min():.2f} · 🧾 {mc.get(worst_m,0):,} {t("reviews")}</div></div>''', unsafe_allow_html=True)

    with tabs[4]:
        td = fdf.dropna(subset=["Review_Date_Fixed"]).copy()
        if len(td):
            td["ym"] = td["Review_Date_Fixed"].dt.to_period("M")
            tg = td.groupby("ym"); tmean = tg["Reviewer_Score_Fixed"].mean(); tcnt = tg.size()
            xs = [str(p) for p in tmean.index]; ma3 = tmean.rolling(3, min_periods=1).mean()
            fig = go.Figure()
            fig.add_trace(go.Bar(x=xs, y=tcnt.values, name=t("count"), marker_color=C["navy"], opacity=.4, yaxis="y2"))
            fig.add_trace(go.Scatter(x=xs, y=tmean.values, mode="lines+markers", name=t("avg_score"),
                line=dict(color=C["gold"], width=2.5), marker=dict(size=5), fill="tozeroy", fillcolor="rgba(201,168,76,.08)"))
            fig.add_trace(go.Scatter(x=xs, y=ma3.values, mode="lines", name=t("ma3"),
                line=dict(color=C["orange"], width=3, dash="dot")))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right", showgrid=False, tickfont=dict(color=C["muted"])))
            chart_sec(t("c_trend"), style(fig, t("c_trend"), h=440), "trend_line")
        else:
            st.info(t("no_data"))
        corr_cols = [c for c in ["Reviewer_Score_Fixed", "Nights_Stayed", "Review_Quality_Score"] if c in fdf.columns]
        if len(corr_cols) >= 2:
            corr = fdf[corr_cols].corr()
            labels = [t("k_score") if c == "Reviewer_Score_Fixed" else t("k_nights") if c == "Nights_Stayed" else t("k_quality") for c in corr_cols]
            fig = px.imshow(corr.values, x=labels, y=labels, text_auto=".2f", color_continuous_scale=CORR_SCALE, zmin=-1, zmax=1)
            fig.update_layout(coloraxis_showscale=False)
            chart_sec(t("c_corr"), style(fig, t("c_corr"), h=380), "corr", t("cap_corr"))
        samp = fdf.sample(min(2500, len(fdf)), random_state=3) if len(fdf) else fdf
        if "Nights_Stayed" in samp.columns:
            fig = px.scatter(samp, x="Nights_Stayed", y="Reviewer_Score_Fixed", color="Traveler_Type",
                             color_discrete_sequence=PALETTE, opacity=.55,
                             labels={"Nights_Stayed": t("k_nights"), "Reviewer_Score_Fixed": t("score"), "Traveler_Type": t("sb_traveler")})
            fig.update_traces(marker=dict(size=6, line=dict(width=0)))
            chart_sec(t("c_scatter"), style(fig, t("c_scatter"), h=420), "scatter", t("cap_scatter"))

    with tabs[5]:
        STOP = set("""the and for with was were this that hotel room stay stayed very but not are our all had have been would there their they from night nights just get got one two also staff location""".split()) | \
               set("في من على إلى ان إن كان هذا هذه ذلك التي الذي مع لكن لم لن هو هي نحن كانت فندق الغرفة غرفة إقامة كان لا ما هل قد".split())
        def tokenize(series):
            text = " ".join(series.dropna().astype(str)); toks = re.findall(r"[\w\u0600-\u06FF']{3,}", text.lower())
            return [w for w in toks if w not in STOP and not w.isdigit()]
        def build_wc(src, max_words):
            from wordcloud import WordCloud
            col = {"pos": "Positive_Review_Cleaned", "neg": "Negative_Review_Cleaned", "all": None}[src]
            series = (pd.concat([fdf.get("Positive_Review_Cleaned", pd.Series(dtype=str)), fdf.get("Negative_Review_Cleaned", pd.Series(dtype=str))])
                      if col is None else fdf[col])
            freq = Counter(tokenize(series)); has_ar = any(re.search(r"[\u0600-\u06FF]", w) for w in freq); freq_disp = freq
            if has_ar:
                try:
                    import arabic_reshaper
                    from bidi.algorithm import get_display
                    freq_disp = Counter({get_display(arabic_reshaper.reshape(w)): c for w, c in freq.items()})
                except ImportError: pass
            font = None
            if has_ar:
                for fp in ["C:/Windows/Fonts/arial.ttf","C:/Windows/Fonts/seguisb.ttf","/System/Library/Fonts/Geeza Pro.ttc",
                           "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"]:
                    if os.path.exists(fp): font = fp; break
            wc = WordCloud(width=1400, height=620, background_color=None, mode="RGBA", max_words=max_words,
                           colormap="viridis", font_path=font, prefer_horizontal=.92, relative_scaling=.5)
            wc.generate_from_frequencies(freq_disp); return wc.to_image(), freq
        w1, w2, w3 = st.columns([2, 2, 1])
        src = w1.selectbox(t("wc_source"), ["pos","neg","all"], format_func=lambda k: {"pos": t("wc_pos"),"neg": t("wc_neg"),"all": t("wc_all")}[k])
        mx = w2.slider(t("wc_max"), 50, 300, 150, 10); w3.markdown("<br>", unsafe_allow_html=True)
        regen = w3.button(t("wc_gen"), use_container_width=True)
        if "wc_img" not in st.session_state or regen:
            try: st.session_state.wc_img, st.session_state.wc_freq = build_wc(src, mx)
            except ImportError: st.error("pip install wordcloud")
        if "wc_img" in st.session_state:
            st.image(st.session_state.wc_img, use_container_width=True)
            st.markdown(f'<div class="sec"><span class="bar"></span><h3>{t("wc_top")}</h3></div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(st.session_state.wc_freq.most_common(20), columns=[t("wc_word"), t("wc_count")]),
                         hide_index=True, use_container_width=True, height=420)
        else: st.info(t("wc_hint"))
        st.caption(t("wc_font_note"))

    # ── AI Assistant: الاقتراحات = أزرار Streamlit حقيقية (لا روابط → لا تبويب جديد) ──
    with tabs[6]:
        st.markdown(f'<div class="sec"><span class="bar"></span><h3>🤖 {t("ai_title")}</h3></div>'
                    f'<div class="cap">{t("ai_sub")}</div>', unsafe_allow_html=True)
        st.caption(t("ai_note"))
        st.markdown(f"**{t('ai_sug')}**")
        # شبكة 2×4 من الأزرار الحقيقية — كل زر بمفتاح فريد ثابت
        for row in range(2):
            cols = st.columns(4)
            for i in range(4):
                idx = row * 4 + i
                qq = SUG[L][idx]
                with cols[i]:
                    with st.container():
                        st.markdown('<div class="sugbtn">', unsafe_allow_html=True)
                        if st.button(qq, key=f"sug_{idx}", use_container_width=True):
                            ask(qq)            # الرد يُضاف للسجل ويظهر فورًا في نفس الشات
                        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        hist = st.session_state.chat_history[-12:]
        if not hist:
            st.markdown(f"<div class='chatpanel' style='position:static'><details open><summary>💬 {t('chat_title')}</summary>"
                        f"<div class='body'><div class='empty'>{t('ai_empty')}</div></div></details></div>", unsafe_allow_html=True)
        for m in hist:
            st.chat_message("user" if m["r"] == "u" else "assistant", avatar="👤" if m["r"] == "u" else "🤖").markdown(m["t"])

    with tabs[7]:
        st.markdown(f'<div class="sec"><span class="bar"></span><h3>{t("d_title")}</h3></div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            if "Suspicion_Level" in fdf:
                sv = fdf["Suspicion_Level"].value_counts()
                fig = px.pie(names=[sus_name(k) for k in sv.index], values=sv.values, hole=.5,
                             color_discrete_sequence=[C["navy"], C["gold"], C["orange"]])
                chart_sec(t("c_susp"), style(fig, t("c_susp"), h=340), "susp")
        with d2:
            if "Review_Quality_Score" in fdf:
                fig = go.Figure(go.Histogram(x=fdf["Review_Quality_Score"], nbinsx=30, marker_color=C["gold"]))
                chart_sec(t("c_qlty"), style(fig, t("c_qlty"), h=340), "qual")
        show_cols = [c for c in ["Hotel_Name","Reviewer_Score_Fixed","Traveler_Type","Room_Type","Reviewer_Nationality",
                     "Review_Date_Fixed","Nights_Stayed","Review_Quality_Score","Suspicion_Level",
                     "Positive_Review_Cleaned","Negative_Review_Cleaned"] if c in fdf.columns]
        cfg = {"Hotel_Name": st.column_config.TextColumn(t("sb_hotel")),
               "Reviewer_Score_Fixed": st.column_config.NumberColumn(t("k_score"), format="%.1f"),
               "Traveler_Type": st.column_config.TextColumn(t("sb_traveler")),
               "Room_Type": st.column_config.TextColumn(t("sb_room")),
               "Reviewer_Nationality": st.column_config.TextColumn("الجنسية" if L == "ar" else "Nationality"),
               "Review_Date_Fixed": st.column_config.DateColumn(t("sb_period")),
               "Nights_Stayed": st.column_config.NumberColumn(t("k_nights")),
               "Review_Quality_Score": st.column_config.ProgressColumn(t("k_quality"), min_value=0, max_value=100),
               "Suspicion_Level": st.column_config.TextColumn(t("sb_suspicion"))}
        view = fdf[show_cols].head(1500)
        st.dataframe(view, column_config=cfg, hide_index=True, use_container_width=True, height=460)
        st.caption(f"{t('d_showing')} {len(view):,} {t('of')} {len(fdf):,}")

# ═══════════════════════════════════════════════════════════════
# 12) CHAT — الإدخال السفلي + اللوحة العائمة (سجل فقط) — بلا query_params
# ═══════════════════════════════════════════════════════════════
if st.session_state.chat_open:
    prompt = st.chat_input(t("chat_ph"), key="chat_in")
    if prompt:
        ask(prompt)

def md2html(s):
    s = str(s).replace("&", "&amp;").replace("<", "&lt;"); s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s.replace("\n", "<br>")

if st.session_state.chat_open:
    msgs = st.session_state.chat_history[-10:]; rtlc = " chatrtl" if L == "ar" else ""
    bubbles = "".join(f'<div class="bub {"u" if m["r"]=="u" else "b"}">{md2html(m["t"])}</div>' for m in msgs) \
              or f'<div class="empty">{t("chat_empty")}</div>'
    st.markdown(f'''<div class="chatpanel"><details open>
        <summary>💬 {t("chat_title")}<span class="dotlive"></span></summary>
        <div class="body{rtlc}">{bubbles}</div></details></div>''', unsafe_allow_html=True)

st.markdown(f'<div class="foot">✨ <b>{t("foot")}</b> · {pd.Timestamp.now():%Y-%m-%d %H:%M}</div>', unsafe_allow_html=True)