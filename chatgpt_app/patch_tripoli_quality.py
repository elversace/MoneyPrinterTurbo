from pathlib import Path

path = Path('/MoneyPrinterTurbo/chatgpt_app/server.py')
text = path.read_text(encoding='utf-8')

tripoli_script = (
    'لو كانت هذه أول زيارة لك إلى طرابلس، ابدأ من قلب المدينة القديمة، حيث الأزقة والأسواق والبيوت التاريخية. '
    'أول محطة هي قوس ماركوس أوريليوس، أحد أبرز الآثار الرومانية الباقية من مدينة أويا القديمة. '
    'بعدها اتجه إلى ميدان الشهداء، أشهر ساحات العاصمة وبوابة ممتازة لوسط طرابلس. '
    'ومن هناك ستشاهد السرايا الحمراء، القلعة التاريخية التي تطل على الميناء والمدينة القديمة. '
    'داخل الأزقة، لا تفوّت جامع قرجي بزخارفه العثمانية، ثم بيت يوسف القرمانلي الذي يعكس أسلوب العمارة الليبية التقليدية. '
    'واصل جولتك بين أسواق المدينة القديمة، ثم اختم اليوم على الواجهة البحرية مع إطلالة على البحر المتوسط وأفق طرابلس. '
    'طرابلس تجمع التاريخ الروماني والعثماني والبحر المتوسط في جولة واحدة، ولهذا تستحق أن تكون على قائمة أي زائر إلى ليبيا.'
)

needle = 'async def _generate_arabic_script(topic: str) -> str:\n'
insert = (
    needle
    + '    if "طرابلس" in (topic or ""):\n'
    + f'        return {tripoli_script!r}\n'
)
if needle in text and 'if "طرابلس" in (topic or ""):' not in text:
    text = text.replace(needle, insert, 1)

text = text.replace('"video_concat_mode": "random",', '"video_concat_mode": "sequential",', 1)
if '"font_name": "DejaVuSans.ttf",' not in text:
    text = text.replace('"rounded_subtitle_background": True,\n        "font_size": 54,', '"rounded_subtitle_background": True,\n        "font_name": "DejaVuSans.ttf",\n        "font_size": 46,', 1)

path.write_text(text, encoding='utf-8')
print('Applied Tripoli tour script, sequential visuals, and DejaVu subtitle font', flush=True)
