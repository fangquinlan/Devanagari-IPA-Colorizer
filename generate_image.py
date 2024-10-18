import os
import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango, PangoCairo
import cairo
import colorsys

# 检查所需的字体文件是否存在
assert os.path.exists('Shobhika-Regular.otf'), "缺少印度语字体文件。"
assert os.path.exists('CharisSIL-Regular.ttf'), "缺少国际音标字体文件。"

hindi_font_family = "Shobhika"
ipa_font_family = "Charis SIL"

# 读取输入文件
with open('input.txt', 'r', encoding='utf-8') as f:
    hindi_text = f.read().strip()

# 将文本拆分为行和单词
lines = hindi_text.split('\n')
words_in_lines = [line.split() for line in lines]

# 创建画布，增加分辨率
img_width = 3200
img_height = 1800  # 增加高度以适应多行

# 定义颜色列表
def generate_colors(n):
    colors = []
    for i in range(n):
        hue = i / n
        lightness = 0.5
        saturation = 0.9
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        colors.append(tuple(int(c * 255) for c in rgb))
    return colors

# 获取所有字符，计算需要的颜色数量
all_chars = list(hindi_text.replace(" ", "").replace("\n", ""))
unique_chars = list(set(all_chars))
colors = generate_colors(len(unique_chars))
char_color_map = dict(zip(unique_chars, colors))


ipa_mapping = {
    'अ': 'ɐ', 'आ': 'äː', 'इ': 'ɪ', 'ई': 'iː', 'उ': 'ʊ', 'ऊ': 'uː', 'ऋ': 'ɾiː',
    'ए': 'eː', 'ऐ': 'ɛː', 'ओ': 'oː', 'औ': 'ɔː', 'अं': 'ã', 'अः': 'ɦ', 'अँ': 'ɐ̃',
    'क': 'k', 'ख': 'kʰ', 'ग': 'ɡ', 'घ': 'ɡʱ', 'ङ': 'ŋ',
    'च': 't͡ʃ', 'छ': 't͡ʃʰ', 'ज': 'd͡ʒ', 'झ': 'd͡ʒʱ', 'ञ': 'ɲ',
    'ट': 'ʈ', 'ठ': 'ʈʰ', 'ड': 'ɖ', 'ढ': 'ɖʱ', 'ण': 'ɳ',
    'त': 't̪', 'थ': 't̪ʰ', 'द': 'd̪', 'ध': 'd̪ʱ', 'न': 'n̪',
    'प': 'p', 'फ': 'pʰ', 'ब': 'b', 'भ': 'bʱ', 'म': 'm',
    'य': 'j', 'र': 'ɾ', 'ल': 'l', 'व': 'ʋ',
    'श': 'ʃ', 'ष': 'ʂ', 'स': 's', 'ह': 'ɦ',
    'त्र': 't̪ɾ', 'ज्ञ': 'ɡj', 'क्ष': 'kʂ', 'क़': 'q',
    'ख़': 'x', 'ग़': 'ɣ', 'ज़': 'z', 'झ़': 'ʒ',
    'ड़': 'ɽ', 'ढ़': 'ɽʱ', 'फ़': 'f',
    'ि': 'ɪ', 'ी': 'iː', 'ु': 'ʊ', 'ू': 'uː', 'ृ': 'r̥',  
    'े': 'eː', 'ै': 'ɛː', 'ो': 'oː', 'ौ': 'ɔː',
    'ं': '̃', 
    'ः': 'ɦ', 
    'ँ': '̃',
    'ा': 'äː',
    'ऑ': 'ɒ',
    'ॐ': 'oːm',
}

# 定义需要组合的符号
combining_chars = set('िीुूृॄेैोौंःँ ़ ा ॉ ो ् ॑ ॒ ॓ ॔ ꣠ ꣡ ꣢ ꣣ ꣤ ꣥ ꣦ ꣧ ꣨ ꣩ ꣪ ꣫ ꣬ ꣭ ꣮ ꣯')

def get_next_char_group(word, start_index):
    """获取下一个字符组（包括所有需要组合的符号）"""
    group = word[start_index]
    i = start_index + 1
    while i < len(word) and word[i] in combining_chars:
        group += word[i]
        i += 1
    return group, i - start_index

# 创建Cairo surface和context
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, img_width, img_height)
context = cairo.Context(surface)

# 设置背景为白色
context.set_source_rgb(1, 1, 1)
context.paint()

# 创建Pango布局
layout = PangoCairo.create_layout(context)
font_description = Pango.FontDescription(f"{hindi_font_family} 240")
layout.set_font_description(font_description)

# 设置IPA字体描述
ipa_font_description = Pango.FontDescription(f"{ipa_font_family} 36")

# 设置初始位置
x_offset = 100
y_offset = 200
line_spacing = 400  # 行间距

for line in words_in_lines:
    x_offset = 100  # 重置每行的x偏移
    
    for word in line:
        layout.set_text(word)
        word_extents = layout.get_pixel_extents()[1]
        word_width = word_extents.width
        word_height = word_extents.height
        
        context.save()
        context.translate(x_offset, y_offset)
        
        # 为每个字符组创建单独的布局并上色
        i = 0
        while i < len(word):
            char_group, group_length = get_next_char_group(word, i)
            i += group_length
            
            char_layout = PangoCairo.create_layout(context)
            char_layout.set_font_description(font_description)
            char_layout.set_text(char_group)
            char_extents = char_layout.get_pixel_extents()[1]
            
            # 使用第一个字符的颜色
            color = char_color_map.get(char_group[0], (0, 0, 0))
            context.set_source_rgb(color[0]/255, color[1]/255, color[2]/255)
            
            PangoCairo.show_layout(context, char_layout)
            
            # 添加IPA（只为主要字符添加）
            base_char = char_group[0]  # 基础字符是第一个字符
            ipa = ipa_mapping.get(base_char, '')
            if ipa:
                # 如果是组合符号，如元音前置，需要进行组合
                for char in char_group[1:]:
                    if char in ipa_mapping:
                        ipa += ipa_mapping[char]

                ipa_layout = PangoCairo.create_layout(context)
                ipa_layout.set_font_description(ipa_font_description)
                ipa_layout.set_text(ipa)
                ipa_extents = ipa_layout.get_pixel_extents()[1]
                
                # 计算IPA文本的位置，使其居中对齐
                ipa_x = (char_extents.width - ipa_extents.width) / 2
                ipa_y = (char_extents.height - ipa_extents.height) / 2
                
                context.save()
                context.set_source_rgb(1, 1, 1)  # 白色
                context.translate(ipa_x, ipa_y)

                # 扩大文本尺寸来模拟描边效果
                context.set_line_width(4)  # 描边的粗细
                PangoCairo.layout_path(context, ipa_layout)
                context.stroke()  # 先绘制路径的描边
                context.restore()

                # 绘制实际的IPA文本（黑色）
                context.save()
                context.set_source_rgb(0, 0, 0)  # 黑色
                context.translate(ipa_x, ipa_y)
                PangoCairo.show_layout(context, ipa_layout)  # 直接绘制文本
                context.restore()
            
            context.translate(char_extents.width, 0)
        
        context.restore()
        x_offset += word_width + 100  # 100是词间距
    
    y_offset += line_spacing  # 移动到下一行

# 保存图片
surface.write_to_png('output_highres.png')
print("图片已保存为 output_highres.png")
