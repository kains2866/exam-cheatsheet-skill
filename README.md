# Exam Cheatsheet Skill

把学习大纲、课件、批注、习题与旧小抄整理成 **一张 A4 双面、最多两页的可编辑 Word Cheatsheet**。

English: An agent skill for source-grounded, page-limited exam reference sheets, with plain headings, source coverage, visual annotation review and space for important tables/images.

## 能做什么

- 逐份考虑用户提供的文件，对照大纲与 Learning Objectives 检查覆盖。
- 检查 Important、荧光笔、圈画、箭头、手写批注等视觉重点；说明无法辨认之处。
- 制作前集中询问尚未明确的考试范围、薄弱板块、具体问题与图表需求。
- 保留精确定义、关键区别、公式条件、代表例题及解题理由。
- 使用纯文字标题，可加粗、斜体或编号；默认不使用填色标题条。
- 先安排重要表格、图片和后续贴图留白，再分配正文篇幅。
- 渲染最终 Word，检查最多两页 A4，并逐页检查实际清晰度。

这是一套供支持 Agent Skills 的助手执行的工作流程。模型仍需文档读取、视觉与 Word→PDF 渲染能力；随附脚本不自动理解课程内容、不识别手写、不重绘图片，也不自动保证排版完成。

## 安装

下载 [Release](https://github.com/kains2866/exam-cheatsheet-skill/releases/latest) 的 `.skill` 或 `.zip`。两者均为 ZIP 格式，内容相同；`.skill` 只供支持该导入格式的客户端使用。也可克隆仓库：

```sh
git clone https://github.com/kains2866/exam-cheatsheet-skill.git
```

将 `skills/build-exam-cheatsheet/` 整个文件夹放入所用客户端的 Skill 发现目录。例如使用 `~/.agents/skills/` 的环境：

```sh
mkdir -p ~/.agents/skills
cp -R exam-cheatsheet-skill/skills/build-exam-cheatsheet ~/.agents/skills/
```

已有同名 Skill 时先比较内容，避免覆盖本地修改。按客户端要求重新加载 Skill。

## 使用示例

> 使用 build-exam-cheatsheet，根据这些课件、学习大纲、批注和习题制作英文 Word 小抄。一张 A4 双面，最多两页；重点解释 free float 和 total float。保留指定表格，在第二页底部留出 50mm，之后贴图。

准备材料时说明考试范围与格式规则、需要加强的问题、必须保留的图表，以及贴图空间。已说明的信息会沿用，不重复提问。材料覆盖报告单独交付，不占用小抄两页。

## 默认版式

A4 纵向，主体三栏，栏距约 1.23mm，上下边距 4mm、左右 5mm；Arial Narrow 正文 6pt、标题 7pt，中文宋体，正文固定行距 6.7pt。重要宽表可使用通栏。默认第二页底部预留全宽 45mm，用户可调整；这是工具预设，不是通用标准。实际可读性和考试要求优先，字体替换后需要重验。

## 工具与验证

Python 3.10+，工具依赖 `python-docx` 与 `pypdf`；渲染需另备 LibreOffice 或可用的 Word/PDF 工具。

```sh
python -m pip install -r requirements.txt
python skills/build-exam-cheatsheet/scripts/make_template.py sheet.docx --reserve-mm 45
# 在 Word 中替换模板样例并填入内容，然后导出到全新目录
soffice --headless --convert-to pdf --outdir preview sheet.docx
python skills/build-exam-cheatsheet/scripts/check_pdf.py preview/sheet.pdf
python -m unittest discover -s tests -v
```

`make_template.py` 拒绝覆盖现有文件。它通过增大第二页下边距预留空白带；日后填入该区时先相应减小该页下边距，再插入内容并重新验页。

`check_pdf.py` 的退出码：0=物理页数/尺寸通过，1=不符合限制，2=读取错误。输出中的 `visual_review: required` 表示仍须检查每一页；通过不代表字体、图表或内容已经合格。未能渲染时只能交付未验证草稿。

## 测试边界

`tests/test_tools.py` 检查两页限制、A4/CropBox/旋转、异常输出和模板样式/留白。`evals/scenarios.json` 与原创素材用于独立 Agent 行为测试，不是自动评分器。实际模型行为依赖执行环境，不承诺固定命中率或改进幅度。

随附 Python 工具在本地运行且不主动联网；资料如何传输取决于所用 Agent、模型和文档工具的配置。仓库中的示例为原创，不附课程原件。MIT 许可证不涵盖用户提供的课件、字体或其他第三方素材。
