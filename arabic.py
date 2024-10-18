from camel_tools.utils.normalize import normalize_unicode
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.disambig.mle import MLEDisambiguator
from bidi.algorithm import get_display
from arabic_reshaper import reshape
from PIL import Image, ImageDraw, ImageFont
import colorsys
import os
import unicodedata

# 初始化MLEDisambiguator
mle = MLEDisambiguator.pretrained()

# 读取输入文件
with open('input.txt', 'r', encoding='utf-8') as f:
    text = f.read().strip()

# 按行分割文本
lines = text.split('\n')

# 对每行文本进行处理
processed_lines = []
for line in lines:
    # 规范化文本
    normalized = normalize_unicode(line)
    
    # 分词
    tokens = simple_word_tokenize(normalized)
    
    # 对每个词进行消歧和元音化
    vocalized_tokens = []
    for token in tokens:
        disambig = mle.disambiguate([token])
        if disambig and disambig[0].analyses:
            vocalized = disambig[0].analyses[0].analysis.get('diac', token)
        else:
            vocalized = token
        vocalized_tokens.append(vocalized)
    
    processed_lines.append((tokens, vocalized_tokens))

print(f"原文: {text}")
print(f"元音化后: {' '.join([' '.join(line[1]) for line in processed_lines])}")

# 检查所需的字体文件是否存在
assert os.path.exists('Amiri-Regular.ttf') or os.path.exists('Rubik-Regular.ttf'), "缺少阿拉伯语字体文件。"
assert os.path.exists('CharisSIL-Regular.ttf'), "缺少国际音标字体文件。"

# 选择阿拉伯语字体
if os.path.exists('Amiri-Regular.ttf'):
    arabic_font_path = 'Amiri-Regular.ttf'
else:
    arabic_font_path = 'Rubik-Regular.ttf'

ipa_font_path = 'CharisSIL-Regular.ttf'

# 创建画布，增加分辨率
img_width = 6000
img_height = 2000 * len(lines)  # 根据行数调整高度
image = Image.new('RGB', (img_width, img_height), color='white')
draw = ImageDraw.Draw(image)

# 设置DPI（可以根据需要调整）
dpi = 460

# 加载字体
font_size = 240  # 阿拉伯语字体大小
arabic_font = ImageFont.truetype(arabic_font_path, font_size)
ipa_font = ImageFont.truetype(ipa_font_path, int(font_size * 0.1))  # IPA字体大小

# 定义颜色列表生成函数
def generate_colors(n):
    colors = []
    for i in range(n):
        hue = i / n
        lightness = 0.5
        saturation = 0.9
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        colors.append(tuple(int(c * 255) for c in rgb))
    return colors

# 获取所有基础字母，计算需要的颜色数量
all_letters = []
for words, _ in processed_lines:
    for word in words:
        for char in word:
            if not unicodedata.combining(char):
                all_letters.append(char)
unique_letters = list(set(all_letters))
colors = generate_colors(len(unique_letters))
letter_color_map = dict(zip(unique_letters, colors))

# 定义IPA映射表
ipa_mapping = {
    'ب': 'b', 'ت': 't', 'ث': 'θ', 'ج': 'd͡ʒ', 'ح': 'ħ', 'خ': 'x',
    'د': 'd', 'ذ': 'ð', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'ʃ', 'ص': 'sˤ',
    'ض': 'dˤ', 'ط': 'tˤ', 'ظ': 'ðˤ', 'ع': 'ʕ', 'غ': 'ɣ', 'ف': 'f', 'ق': 'q',
    'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h',
    'ا': 'aː', 'و': 'w', 'ي': 'j', 'ء': 'ʔ', 'أ': 'ʔa', 'إ': 'ʔi', 'آ': 'ʔaː', 'ؤ': 'ʔu', 'ئ': 'ʔi',
    'ى': 'aː', 'ة': 't', 'ڤ': 'v', 'پ': 'p', 'چ': 't͡ʃ', 'گ': 'ɡ', 'ژ': 'ʒ',
    'َ': 'a', 'ِ': 'i', 'ُ': 'u', 'َا': 'aː', 'ِي': 'iː', 'ُو': 'uː',
    'ً': 'an', 'ٍ': 'in', 'ٌ': 'un', 'ّ': 'ː', 'ْ': '', 'ٰ': 'aː', 'ٖ': 'iː', 'ٗ': 'uː',
    'ال': 'al', 'الله': 'aɫ.ɫaːh', 'الت': 'at.t', 'الث': 'aθ.θ', 'الد': 'ad.d',
    'لأ': 'laʔ', 'لإ': 'liʔ', 'لآ': 'laːʔ',
    '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4', '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
}


# 改进的配对函数
def pair_letters_with_diacritics(original_word, vocalized_word):
    paired = []
    base_letters = []
    i = 0
    while i < len(original_word):
        if original_word[i] in 'آأإؤئ':
            base_letters.extend(['ا', 'ء'])
            i += 1
        elif original_word[i] == 'ل' and i + 1 < len(original_word) and original_word[i+1] in 'اآأإ':
            base_letters.append(original_word[i:i+2])
            i += 2
        else:
            base_letters.append(original_word[i])
            i += 1
    
    vocalized_chars = list(vocalized_word)
    
    i = 0
    j = 0
    while i < len(vocalized_chars):
        char = vocalized_chars[i]
        if unicodedata.combining(char):
            if paired:
                paired[-1][1] += char
            i += 1
        else:
            if j < len(base_letters):
                paired.append([base_letters[j], ''])
                j += 1
            else:
                paired.append([char, ''])
            i += 1
    
    return paired

# 定义描边函数
def draw_text_with_stroke(draw, position, text, font, fill_color, stroke_color, stroke_width):
    x, y = position
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    draw.text(position, text, font=font, fill=fill_color)

# 设置初始y偏移
y_offset = 200

# 遍历每一行
for line_index, (words, vocalized_words) in enumerate(processed_lines):
    word_widths = []
    for word in vocalized_words:
        reshaped_word = reshape(word)
        bidi_word = get_display(reshaped_word)
        word_size = arabic_font.getbbox(bidi_word)
        word_width = word_size[2] - word_size[0]
        word_widths.append(word_width)

    spacing = 100
    total_width = sum(word_widths) + spacing * (len(vocalized_words) - 1)
    if total_width > (img_width - 200):
        raise ValueError(f"第 {line_index + 1} 行文本过长，无法在指定的画布宽度内显示。请增加画布宽度或减少文本长度。")

    x_offset = img_width - 100

    for word_index, word in enumerate(vocalized_words):
        word_width = word_widths[word_index]
        x_offset -= word_width

        original_word = words[word_index]
        vocalized_word = word

        paired_letters = pair_letters_with_diacritics(original_word, vocalized_word)

        reshaped_word = reshape(vocalized_word)
        bidi_word = get_display(reshaped_word)

        display_letters = list(bidi_word)
        if len(paired_letters) != len(display_letters):
            while len(paired_letters) < len(display_letters):
                paired_letters.append(['', ''])
            while len(paired_letters) > len(display_letters):
                paired_letters.pop()

        letter_positions = []
        current_x = x_offset
        for display_letter in display_letters:
            bbox = arabic_font.getbbox(display_letter)
            letter_width = bbox[2] - bbox[0]
            letter_positions.append((current_x, y_offset))
            current_x += letter_width

        ipa_list = []
        for base_letter, diac in paired_letters:
            ipa = ipa_mapping.get(base_letter, '')
            ipa_vowels = [ipa_mapping.get(d, '') for d in diac if d in ipa_mapping]
            combined_ipa = ipa + ''.join(ipa_vowels)
            ipa_list.append(combined_ipa)

        ipa_list.reverse()

        for idx, display_letter in enumerate(display_letters):
            base_letter, diac = paired_letters[idx] if idx < len(paired_letters) else ('', '')
            
            color = letter_color_map.get(base_letter[0] if base_letter else '', (0, 0, 0))
            position = letter_positions[idx]

            draw.text(position, display_letter, font=arabic_font, fill=color)

            combined_ipa = ipa_list[idx] if idx < len(ipa_list) else ''
            if combined_ipa:
                ipa_bbox = ipa_font.getbbox(combined_ipa)
                ipa_width = ipa_bbox[2] - ipa_bbox[0]
                ipa_position = (position[0] + (arabic_font.getbbox(display_letter)[2] - arabic_font.getbbox(display_letter)[0]) / 2 - ipa_width / 2, position[1] + font_size + 10)
                draw_text_with_stroke(draw, ipa_position, combined_ipa, ipa_font, fill_color='black', stroke_color='white', stroke_width=2)

        x_offset -= spacing

    y_offset += font_size * 2

# 保存图片
image.save('output_highres.png', dpi=(dpi, dpi))
print(f"图片已保存为 output_highres.png，DPI设置为 {dpi}")
