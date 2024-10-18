# Hindi-IPA-Color-Visualizer

This repository creates images of Hindi text with unique color coding for each character and IPA transcription for phonetic representation.

本仓库通过为每个字符提供独特的颜色编码和 IPA 转录，生成印地语文本的图像。

## Features / 功能特点
- Unique color-coding for each character in the Hindi text.
- IPA transcription for every Hindi character.

- 为每个印地语字符提供独特的颜色编码。
- 为每个印地语字符提供 IPA 转录。

---

## Installation / 安装步骤

### Dependencies / 依赖项

You will need the following libraries to run the project:

您需要安装以下库来运行此项目：

- **gi (PyGObject)**
- **cairo** for rendering the image
- **colorsys** for generating colors

For Windows users, it is recommended to install Pango and related components via `conda`.

Windows用户推荐通过 `conda` 安装Pango及其相关组件。

```bash
conda install -c conda-forge pygobject pycairo pango
```

---

## Usage / 使用方法

1. Place the required font files in the project directory:
   - `Shobhika-Regular.otf` (for Hindi text)
   - `CharisSIL-Regular.ttf` (for IPA transcription)

2. Prepare an input text file `input.txt` with Hindi text to be visualized.

3. Run the script to generate the image:

   将所需的字体文件放置到项目目录中：
   - `Shobhika-Regular.otf`（用于印地语文本）
   - `CharisSIL-Regular.ttf`（用于 IPA 转录）

   准备一个包含印地语文本的 `input.txt` 输入文件。

   运行脚本生成图像：

```bash
python generate_image.py
```

4. The output image `output_highres.png` will be saved in the project directory.

4. 输出图像 `output_highres.png` 将保存在项目目录中。

---

## Example Result / 示例结果

The script reads the Hindi text from `input.txt`, assigns each unique character a distinct color, and displays IPA transcription along with it. The generated high-resolution image will look like this:

脚本从 `input.txt` 读取印地语文本，为每个独特的字符分配一个不同的颜色，并同时显示 IPA 转录。生成的高分辨率图像效果如下：

![Example Output](output_highres.png)