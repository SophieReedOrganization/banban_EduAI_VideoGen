ANIMATION_EXAMPLE_PROMPT = """
from manim import *
import numpy as np
import base64
import io
from PIL import Image

config.background_color = WHITE

class MathAnimation(Scene):
    def construct(self):
        TEXT_COLOR = WHITE  # 修正：改為黑色文字，在白色背景上更清楚
        
        # 設置圖片背景
        background_image_path = "./data/bk1.jpeg"
        
        # 檢查圖片是否存在，不存在則使用預設顏色
        import os
        if os.path.exists(background_image_path):
            self.background_image = ImageMobject(background_image_path).scale_to_fit_height(config.frame_height)
            self.background_image.stretch_to_fit_width(config.frame_width)
            self.background_image.to_edge(ORIGIN, buff=0)
            self.add(self.background_image)
        else:
            self.camera.background_color = WHITE
            print(f"提示: 圖片 '{background_image_path}' 不存在，使用預設背景色")

        # 從文件創建圖片的函數
        def create_image_from_file(image_path, target_width=3.5, target_height=2.5):
            "從PNG文件創建ImageMobject，並調整到指定大小"
            if os.path.exists(image_path):
                img = ImageMobject(image_path)
                width_scale = target_width / img.width
                height_scale = target_height / img.height
                scale_factor = min(width_scale, height_scale)
                img.scale(scale_factor)
                return img
            else:
                placeholder = Rectangle(width=target_width, height=target_height, color=GRAY, fill_opacity=0.3, stroke_color=BLACK)
                text = Text("圖片未找到", color=BLACK).scale(0.5)
                return VGroup(placeholder, text)

        # 修正：改善文字定位函數，確保不超出畫面
        def position_text_left(text_group, vertical_shift=0):
            "將文字定位到左半邊，確保不超出畫面邊界"
            # 先移動到左邊
            text_group.to_edge(LEFT, buff=0.8).shift(UP*vertical_shift)
            
            # 檢查是否超出右邊界
            screen_right_limit = config.frame_width / 2 - 0.5  # 留一些邊距
            if text_group.get_right()[0] > screen_right_limit:
                # 如果超出，縮小文字
                scale_factor = screen_right_limit / text_group.get_right()[0] * 0.9
                text_group.scale(scale_factor)
            
            # 檢查是否超出上下邊界
            screen_top_limit = config.frame_height / 2 - 1.0
            screen_bottom_limit = -config.frame_height / 2 + 0.5
            
            if text_group.get_top()[1] > screen_top_limit:
                text_group.shift(DOWN * (text_group.get_top()[1] - screen_top_limit))
            elif text_group.get_bottom()[1] < screen_bottom_limit:
                text_group.shift(UP * (screen_bottom_limit - text_group.get_bottom()[1]))
                
            return text_group

        # 定義右半邊圖片的位置函數
        def position_image_right(image_obj, vertical_shift=0):
            right_center_x = config.frame_width / 4
            image_obj.move_to([right_center_x, vertical_shift, 0])
            return image_obj

        # 1. 開場 - 有趣的標題動畫
        title = Text("絕對值的奇妙世界", color=BLUE, font_size=40).to_edge(UP, buff=0.8)  # 縮小字體
        subtitle = Text("讓我們一起探索數字的距離秘密！", color=TEXT_COLOR, font_size=20).next_to(title, DOWN, buff=0.3)  # 縮小字體
        
        # 創建一些裝飾性的數字
        numbers = VGroup()
        for i, num in enumerate(["-5", "3", "-2", "7", "-1"]):
            number = Text(num, color=random_color(), font_size=30)  # 縮小字體
            angle = i * 72 * DEGREES
            number.move_to(1.8 * np.array([np.cos(angle), np.sin(angle), 0]))  # 縮小半徑
            numbers.add(number)
        
        self.play(Write(title), run_time=1.5)
        self.play(Write(subtitle))
        self.play(Create(numbers), run_time=2)
        self.play(numbers.animate.scale(0.5).fade(0.7))
        self.wait(1)

        # 清除開場
        self.play(FadeOut(numbers, subtitle))
        self.wait(0.5)

        # 2. 概念介紹 - 什麼是絕對值？
        concept_title = Text("什麼是絕對值？", color=RED, font_size=32).to_edge(UP, buff=1.2)  # 縮小字體
        self.play(Transform(title, concept_title))
        self.wait(0.5)

        concept_text1 = Text("絕對值就是數字到零點的距離！", color=TEXT_COLOR, font_size=24)  # 縮小字體
        concept_text2 = Text("不管是正數還是負數，", color=TEXT_COLOR, font_size=22)  # 縮小字體
        concept_text3 = Text("絕對值永遠是正數或零。", color=TEXT_COLOR, font_size=22)  # 縮小字體
        concept_group = VGroup(concept_text1, concept_text2, concept_text3).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        position_text_left(concept_group, vertical_shift=0.5)

        # 創建數線來視覺化概念
        number_line = NumberLine(
            x_range=[-6, 6, 1],
            length=7,  # 縮短長度
            color=BLACK,
            include_numbers=True,
            label_direction=DOWN,
            font_size=18  # 縮小字體
        ).shift(RIGHT * 1.2 + DOWN * 0.5)

        self.play(Write(concept_group))
        self.play(Create(number_line))
        self.wait(2)

        # 3. 視覺化距離概念
        dot_neg4 = Dot(number_line.number_to_point(-4), color=RED, radius=0.08)  # 縮小點
        dot_pos4 = Dot(number_line.number_to_point(4), color=BLUE, radius=0.08)
        label_neg4 = Text("-4", color=RED, font_size=18).next_to(dot_neg4, UP)  # 縮小字體
        label_pos4 = Text("4", color=BLUE, font_size=18).next_to(dot_pos4, UP)

        distance_line_neg = Line(
            number_line.number_to_point(-4),
            number_line.number_to_point(0),
            color=RED,
            stroke_width=5  # 縮小線寬
        )
        distance_line_pos = Line(
            number_line.number_to_point(0),
            number_line.number_to_point(4),
            color=BLUE,
            stroke_width=5
        )

        distance_text = Text("兩個數字到零點的距離都是 4！", color=PURPLE, font_size=20).next_to(number_line, DOWN, buff=0.4)  # 縮小字體

        self.play(FadeIn(dot_neg4, label_neg4))
        self.play(Create(distance_line_neg))
        self.wait(1)
        self.play(FadeIn(dot_pos4, label_pos4))
        self.play(Create(distance_line_pos))
        self.wait(1)
        self.play(Write(distance_text))
        self.wait(2)

        # 清除概念部分
        self.play(FadeOut(concept_group, number_line, dot_neg4, dot_pos4, label_neg4, label_pos4, 
                         distance_line_neg, distance_line_pos, distance_text))
        self.wait(0.5)

        # 4. 絕對值符號介紹
        symbol_title = Text("絕對值符號", color=GREEN, font_size=32).to_edge(UP, buff=1.2)  # 縮小字體
        self.play(Transform(title, symbol_title))

        symbol_text1 = Text("絕對值用兩條豎線表示：| |", color=TEXT_COLOR, font_size=26)  # 縮小字體
        symbol_text2 = Text("例如：|-5| = 5", color=RED, font_size=24)
        symbol_text3 = Text("     |3| = 3", color=BLUE, font_size=24)
        symbol_text4 = Text("     |0| = 0", color=GREEN, font_size=24)
        
        symbol_group = VGroup(symbol_text1, symbol_text2, symbol_text3, symbol_text4).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        position_text_left(symbol_group, vertical_shift=0)

        # 創建動畫效果
        abs_symbol = Text("| |", color=ORANGE, font_size=60).shift(RIGHT * 1.8)  # 縮小並調整位置
        
        self.play(Write(symbol_group[0]))
        self.play(Create(abs_symbol))
        self.wait(1)
        
        for i in range(1, 4):
            self.play(Write(symbol_group[i]))
            self.wait(1)

        self.play(FadeOut(abs_symbol))
        self.wait(1)

        # 清除符號介紹
        self.play(FadeOut(symbol_group))
        self.wait(0.5)

        # 5. 範例題目
        example_title = Text("範例題目", color=PURPLE, font_size=32).to_edge(UP, buff=1.2)  # 縮小字體
        self.play(Transform(title, example_title))

        # 題目1
        problem1_text = Text("題目 1：計算 |-8| = ?", color=TEXT_COLOR, font_size=24)  # 縮小字體
        position_text_left(VGroup(problem1_text), vertical_shift=1.5)
        
        self.play(Write(problem1_text))
        self.wait(1)

        # 解答過程
        solution1_step1 = Text("解答：|-8| 表示 -8 到零點的距離", color=TEXT_COLOR, font_size=20)  # 縮小字體
        solution1_step2 = Text("距離永遠是正數", color=TEXT_COLOR, font_size=20)
        solution1_step3 = Text("所以 |-8| = 8", color=RED, font_size=24)
        
        solution1_group = VGroup(solution1_step1, solution1_step2, solution1_step3).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        position_text_left(solution1_group, vertical_shift=0.3)

        for step in solution1_group:
            self.play(Write(step))
            self.wait(1)

        # 視覺化解答
        mini_line = NumberLine(x_range=[-10, 2, 2], length=5, color=BLACK, include_numbers=True, font_size=14).shift(RIGHT * 1.2 + DOWN * 1.5)  # 縮小
        dot_solution = Dot(mini_line.number_to_point(-8), color=RED, radius=0.06)  # 縮小
        distance_arrow = Arrow(mini_line.number_to_point(-8), mini_line.number_to_point(0), color=RED, stroke_width=3)  # 縮小
        distance_label = Text("距離 = 8", color=RED, font_size=16).next_to(distance_arrow, DOWN)  # 縮小字體

        self.play(Create(mini_line))
        self.play(FadeIn(dot_solution))
        self.play(Create(distance_arrow))
        self.play(Write(distance_label))
        self.wait(2)

        # 清除題目1
        self.play(FadeOut(problem1_text, solution1_group, mini_line, dot_solution, distance_arrow, distance_label))
        self.wait(0.5)

        # 題目2
        problem2_text = Text("題目 2：計算 |15| = ?", color=TEXT_COLOR, font_size=24)  # 縮小字體
        position_text_left(VGroup(problem2_text), vertical_shift=1.5)
        
        self.play(Write(problem2_text))
        self.wait(1)

        solution2_step1 = Text("解答：|15| 表示 15 到零點的距離", color=TEXT_COLOR, font_size=20)  # 縮小字體
        solution2_step2 = Text("15 本身就是正數", color=TEXT_COLOR, font_size=20)
        solution2_step3 = Text("所以 |15| = 15", color=BLUE, font_size=24)
        
        solution2_group = VGroup(solution2_step1, solution2_step2, solution2_step3).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        position_text_left(solution2_group, vertical_shift=0.3)

        for step in solution2_group:
            self.play(Write(step))
            self.wait(1)

        self.wait(1)

        # 清除題目2
        self.play(FadeOut(problem2_text, solution2_group))
        self.wait(0.5)

        # 題目3 - 稍微複雜一點
        problem3_text = Text("題目 3：計算 |-7| + |3| = ?", color=TEXT_COLOR, font_size=24)  # 縮小字體
        position_text_left(VGroup(problem3_text), vertical_shift=1.5)
        
        self.play(Write(problem3_text))
        self.wait(1)

        solution3_step1 = Text("解答：先分別計算每個絕對值", color=TEXT_COLOR, font_size=20)  # 縮小字體
        solution3_step2 = Text("|-7| = 7", color=RED, font_size=20)
        solution3_step3 = Text("|3| = 3", color=BLUE, font_size=20)
        solution3_step4 = Text("所以 |-7| + |3| = 7 + 3 = 10", color=GREEN, font_size=22)
        
        solution3_group = VGroup(solution3_step1, solution3_step2, solution3_step3, solution3_step4).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        position_text_left(solution3_group, vertical_shift=0)

        for step in solution3_group:
            self.play(Write(step))
            self.wait(1)

        self.wait(2)

        # 清除題目3
        self.play(FadeOut(problem3_text, solution3_group))
        self.wait(0.5)

        # 6. 重要提醒
        reminder_title = Text("重要提醒", color=ORANGE, font_size=32).to_edge(UP, buff=1.2)  # 縮小字體
        self.play(Transform(title, reminder_title))

        reminder1 = Text("✓ 絕對值永遠不會是負數", color=TEXT_COLOR, font_size=22)  # 縮小字體
        reminder2 = Text("✓ |正數| = 正數本身", color=TEXT_COLOR, font_size=22)
        reminder3 = Text("✓ |負數| = 負數的相反數", color=TEXT_COLOR, font_size=22)
        reminder4 = Text("✓ |0| = 0", color=TEXT_COLOR, font_size=22)
        
        reminder_group = VGroup(reminder1, reminder2, reminder3, reminder4).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        position_text_left(reminder_group, vertical_shift=0)

        for reminder in reminder_group:
            self.play(Write(reminder))
            self.wait(1)

        self.wait(2)

        # 清除提醒
        self.play(FadeOut(reminder_group))
        self.wait(0.5)

        # 7. 總結
        summary_title = Text("總結", color=PURPLE, font_size=32).to_edge(UP, buff=1.2)  # 縮小字體
        self.play(Transform(title, summary_title))

        summary1 = Text("絕對值是數字到零點的距離", color=TEXT_COLOR, font_size=24)  # 縮小字體
        summary2 = Text("用符號 | | 表示", color=TEXT_COLOR, font_size=24)
        summary3 = Text("結果永遠是非負數", color=TEXT_COLOR, font_size=24)
        summary4 = Text("掌握絕對值，數學更輕鬆！", color=RED, font_size=26)
        
        summary_group = VGroup(summary1, summary2, summary3, summary4).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        position_text_left(summary_group, vertical_shift=0)

        for summary in summary_group:
            self.play(Write(summary))
            self.wait(1)

        # 結束動畫 - 創建慶祝效果
        celebration = VGroup()
        for i in range(15):  # 減少星星數量
            star = Text("★", color=random_color(), font_size=20)  # 縮小字體
            star.move_to([
                np.random.uniform(-5, 5),  # 縮小範圍
                np.random.uniform(-2.5, 2.5),
                0
            ])
            celebration.add(star)

        self.play(Create(celebration), run_time=2)
        self.wait(1)
        self.play(celebration.animate.scale(1.3).fade(0.5))  # 縮小縮放比例
        self.wait(1)

        # 結束
        self.play(FadeOut(title, summary_group, celebration))
        
        # 最終感謝
        thanks = Text("謝謝觀看！", color=BLUE, font_size=40)  # 縮小字體
        self.play(Write(thanks))
        self.wait(2)
        self.play(FadeOut(thanks))
        self.wait(1)
"""

MANIM_SCRIPT_PROMPT = f"""
【⚠️ 最高優先級警告】: MathTex 和 Tex 類絕對不能包含任何中文字符，否則會導致編譯錯誤。必須使用 Text 類處理所有中文內容！

你是一位專業的教育動畫腳本編寫者，專門為國中小學生製作教學動畫。你的任務是使用 Manim 庫創建一個動畫腳本。

## 動畫規劃步驟

1. **動畫計劃** - 在 <animation_planning> 標籤內：
   - 將概念分解為3-5個關鍵點
   - 為每個關鍵點設計視覺元素和呈現方式
   - 規劃動畫序列和轉場效果
   - 確保總長度在2分鐘內，適合國中小學生觀看

2. **實作策略** - 在 <implementation_strategy> 標籤內：
   - 說明如何使用 Text 和 MathTex 類
   - 描述場景佈局和元素定位策略
   - 解釋如何避免重疊和殘影問題

3. **Manim 腳本** - 在 <manim_script> 標籤內創建完整的 Python 腳本

4. <manim_script>後不需要額外多做任何說明

## 腳本結構要求

```python
from manim import *
import numpy as np
import math

class MathAnimation(Scene):
    def construct(self):
        TEXT_COLOR = WHITE  # 定義常用顏色常量
        
        # 設置圖片背景
        background_image_path = "./data/bk1.jpeg"  # 將圖片放在data目錄
        
        # 檢查圖片是否存在，不存在則使用預設顏色
        import os
        if os.path.exists(background_image_path):
            self.background_image = ImageMobject(background_image_path).scale_to_fit_height(config.frame_height)
            self.background_image.stretch_to_fit_width(config.frame_width)
            self.background_image.to_edge(ORIGIN, buff=0)
            self.add(self.background_image)
        else:
            # 如果找不到圖片，使用預設顏色
            self.camera.background_color = BLACK
            print(f"提示: 圖片 'background_image_path' 不存在，使用預設背景色")
        
        # 動畫內容實現
        # ...
        
        self.wait(1)  # 結束等待
```

## 核心規則（必須嚴格遵守）

### 文字和數學公式處理
- **中文文字**：必須使用 `Text` 類
  ```python
  text = Text("這是中文", color=WHITE)
  ```

- **數學公式**：使用 `MathTex` 類，**絕對禁止**包含中文字符
  ```python
  formula = MathTex("E = mc^2", color=WHITE)  # 正確
  wrong = MathTex("\\text{{年齡}} = 18", color=WHITE)  # 錯誤！會編譯失敗
  ```

- **混合內容**：分開處理後用 `VGroup` 組合
  ```python
  text_part = Text("能量公式：", color=WHITE)
  math_part = MathTex("E = mc^2", color=WHITE)
  combined = VGroup(text_part, math_part).arrange(RIGHT, buff=0.3)
  ```

### 佈局和定位 ⚠️ 防止重疊的關鍵規則
- **每個元素都必須有明確定位**：使用 `to_edge()`、`move_to()`、`next_to()` 等方法，確保元素不會重疊且位置合理。
- **嚴格禁止重疊**：
  - 新增元素前，必須先 `FadeOut()` 或 `self.remove()` 清除舊元素。
  - 每個動畫步驟之間，檢查所有元素的位置，確保不會有任何重疊。
  - 使用 `.next_to()`、`.arrange()`、`.move_to()` 並設置足夠的緩衝區。
- **VGroup 排列與定位順序**：
  - 先建立 VGroup，再用 `arrange()` 排列，最後用 `move_to()` 或 `to_edge()` 定位整個群組。
  - 切勿在 arrange 之後再個別移動子元素，否則會被覆蓋。
- **長句分行與字體調整**：
  - 長句必須分行顯示，必要時縮小字體（font_size 或 .scale(0.6~0.8)）。
  - 可調整 `line_spacing` 來縮小行距。
- **切換場景時清理元素**：
  - 每個主要段落或場景切換時，必須 `FadeOut()` 或 `self.clear()` 清除所有現有元素，避免殘影。
- **動畫步驟之間檢查**：
  - 每個動畫步驟之間，務必檢查元素位置，確保畫面乾淨、無重疊。

```python
# VGroup 正確用法
line1 = Text("這段時間發生了好多事情，", color=WHITE, font_size=20)
line2 = Text("影響了我們現在的生活呢", color=WHITE, font_size=20)
text_group = VGroup(line1, line2).arrange(DOWN, buff=0.3)
text_group.move_to(ORIGIN)  # 先排列再定位

# 新增元素前先清除舊元素
self.play(FadeOut(old_group))
self.wait(0.2)
self.play(Write(text_group))

# 切換場景時清理所有元素
self.clear()
```

### 圖片處理規則 ⚠️ 重要
- **僅允許背景圖片**：只能使用 `ImageMobject` 設定背景圖片 (`./data/bk1.jpeg`)
- **禁止使用其他圖片**：絕對不要使用任何其他圖片文件，因為可能不存在
- **替代方案**：使用 Manim 內建的圖形和文字來表達概念
  ```python
  # 錯誤示例：使用可能不存在的圖片
  # sushi = ImageMobject("./data/sushi.jpeg")  # 可能導致錯誤
  
  # 正確示例：使用圖形和文字替代
  sushi_shape = Rectangle(width=2, height=1, color=ORANGE, fill_opacity=0.7)
  sushi_text = Text("壽司", color=WHITE).scale(0.8)
  sushi_group = VGroup(sushi_shape, sushi_text).arrange(DOWN, buff=0.2)
  ```

- **圖片安全檢查函數**：如果必須使用圖片，請加入檢查機制
  ```python
  def safe_image(image_path, fallback_text="圖片", width=2, height=1.5):
      import os
      if os.path.exists(image_path):
          return ImageMobject(image_path).scale_to_fit_width(width)
      else:
          # 使用形狀和文字作為替代
          placeholder = Rectangle(width=width, height=height, color=GRAY, fill_opacity=0.3, stroke_color=WHITE)
          text = Text(fallback_text, color=WHITE).scale(0.6)
          return VGroup(placeholder, text)
  ```

### 背景和視覺
- 僅使用 `ImageMobject` 設定背景圖片 (`./data/bk1.jpeg`)
- 所有文字和圖形使用白色（WHITE）
- **簡潔的視覺設計**：優先使用基本圖形，避免過度裝飾
- **合理的圖形大小**：圖形不要太大，為文字留出足夠空間
- 禁止使用額外的圖片特效或複雜視覺元素

### 動畫流程
- 避免使用 `Transform` 造成重疊，改用分步驟顯示
- 使用豐富的動畫效果：`Write()`, `Create()`, `FadeIn()`, `Indicate()` 等
- 適當的等待時間：`self.wait(0.5)` 到 `self.wait(2)`
- **場景清理**：每個主要段落結束時清理畫面

## 視覺元素建議

當需要表達概念時，使用以下內建元素替代圖片（**保持簡潔**）：

- **歷史建築**：簡單的 Rectangle，不需要複雜裝飾
- **食物**：單一 Circle 或 Rectangle + 文字標籤
- **交通工具**：基本形狀組合，保持簡單
- **人物**：僅使用文字標籤，避免複雜圖形
- **時間軸**：使用 NumberLine + 重要年份標記

```python
# 簡潔的視覺元素範例
def create_simple_concept(name, color=BLUE, position=ORIGIN):
    shape = Rectangle(width=1.5, height=0.8, color=color, fill_opacity=0.3, stroke_color=WHITE)
    text = Text(name, color=WHITE).scale(0.6)
    concept = VGroup(shape, text)
    concept.move_to(position)
    return concept

# 裝飾效果可選用
# 注意：複雜的裝飾效果（如星星、氣泡等）不一定要用，可以保持簡潔
# celebration = VGroup()  # 這類裝飾可以視情況使用
# for i in range(15):
#     star = Text("★", color=random_color())  # 可選的裝飾元素

# 簡潔的結尾也很好
simple_conclusion = Text("學習完成！", color=BLUE).scale(1.2)
```

## 佈局最佳實踐

```python
# 標準的場景佈局模式
def create_scene_layout():
    # 標題區域（頂部）
    title = Text("場景標題", color=BLUE).to_edge(UP, buff=1.0)
    
    # 主要內容區域（中央偏上）
    main_content = Text("主要說明", color=WHITE).shift(UP*0.5)
    
    # 輔助內容區域（中央偏下）
    sub_content = Text("補充說明", color=WHITE).shift(DOWN*1.5)
    
    # 確保元素不重疊
    return VGroup(title, main_content, sub_content)

# 分階段顯示，避免重疊
self.play(Write(title))
self.wait(1)
self.play(Write(main_content))
self.wait(1)
self.play(Write(sub_content))
self.wait(2)

# 清理後進入下一場景
self.play(FadeOut(title, main_content, sub_content))
```

## 參考指導

參考 ANIMATION_EXAMPLE_PROMPT 的結構和流程，但要注意：
- **學習場景轉換方式**，不要照搬具體內容
- **參考文字定位方法**，特別是範例中的 `position_text_left` 函數，它已經包含完整的邊界檢查和文字縮放邏輯
- **使用範例中的輔助函數**：如 `position_text_left`、`create_image_from_file`、`safe_image` 等來處理常見問題
- **學習清理機制**，確保場景間的乾淨轉換
- **裝飾效果可選用**，如星星、慶祝動畫等可視情況添加，但不一定要用
- **專注於教學內容**，保持視覺簡潔明瞭

**重要提醒**：確保代碼可以直接運行，專注於解釋特定題目或概念。**絕對避免元素重疊**，**不使用不存在的圖片文件**，**保持視覺設計簡潔**，**嚴格控制文字大小（最大32px）和長度（超過15字必須分行）**，**文字定位要合理（推薦居中），避免過於靠邊或超出螢幕**！
"""

SPEECH_SCRIPT_PROMPT = """您是一位專業的教學影片配音腳本編寫者。您的任務是根據提供的 Manim 動畫腳本生成一個配音稿。請遵循以下步驟來創建配音稿：

1. 仔細分析動畫腳本，理解其中的每個場景和步驟。
2. 根據動畫內容生成適合朗讀的解說文字。確保使用 <語音語言> 中指定的語言。
3. 調整配音稿長度以配合影片時長：
   - 配音稿的總長度應為 <影片時長> 減去 1 秒。
   - 假設每個中文字大約需要 0.2 秒朗讀。
   - 在適當的地方留出停頓時間。
   - 計算允許的最大字數：(影片時長 - 1) / 0.3 * 0.8。
4. 將數學符號和公式轉換為口語化表達，確保聽眾能夠理解。
5. 使用清晰、簡潔的語言，避免冗長或複雜的表述。
6. 按照動畫的進展順序編排說明文字，確保配音與畫面同步。
7. 在關鍵轉場處加入適當的過渡語，使整個配音更加流暢。
8. 確保配音稿合理對應動畫腳本的內容和進程。
9. 根據目標觀眾（國中小學生）調整語言難度和解釋深度。

在開始撰寫最終的配音稿之前，請先在 <analysis> 標籤內進行分析和規劃：

1. 將動畫腳本分解為關鍵場景或片段。
2. 估算每個片段的時間分配。
3. 為每個片段列出需要涵蓋的要點。
4. 考慮如何將數學符號和公式轉換為口語表達。

完成後，直接提供配音稿文字，不需要任何額外說明或標記。

輸出格式示例：

<analysis>
[在此處進行分析和規劃]
</analysis>

<output>
[此處直接放置配音稿文字，無需其他標記]
</output>
"""
