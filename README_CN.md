# 美国 K-12 教师在职证明信 Pro：HTML → PDF

这是一套用于学校授权行政人员、人力资源部门或校长办公室签发英文 `Employment Verification Letter` 的正式模板。**编辑器界面为简体中文**（按钮、分区、状态与校验提示）；**信件正文与证明字段内容保持英文**，以符合美国正式文件习惯。页面按美国 `Letter` 纸张设计（8.5 × 11 英寸），可直接在浏览器中逐字段修改，也可用 JSON 和 Python 批量/自动生成 PDF。

示例数据使用演示电话和保留域名，PDF 带有 `SAMPLE - NOT VALID` 水印。正式输出检查会阻止这些演示信息被误当成真实文件。

## 下载后保留的目录结构

```text
k12_employment_verification_pro_package/
├── k12_employment_verification_pro_editor.html
├── k12_employment_verification_pro_editor_singlefile.html
├── generate_pdf.py
├── requirements.txt
├── README_CN.md
├── FIELD_REFERENCE_CN.md
├── THIRD_PARTY_NOTICES.txt
├── vendor/
│   └── qrcode-generator.bundle.js
├── examples/
│   ├── blank_letter.json
│   └── sample_letter.json
└── output/
    ├── sample_employment_verification_pro_draft.pdf
    └── sample_employment_verification_pro_draft.pdf.manifest.json
```

## 模板已经支持的编辑能力

- 学校法定名称、显示名称、学校简称、部门、地址、电话、传真、邮箱、网站、NCES ID、州学校编号。
- 教师姓名、Employee ID、职位、学部、校区、任教学段和学科、在职状态、入职日期、结束日期、FTE、工时、合同学年、主管、教师资质和薪资。
- 签发日期、Letter ID、文件标题、副标题、主题、称呼、收件人和收件地址。
- 任意增加、删除、排序正文段落。
- 任意增加、删除、排序证明字段；每个字段的标签、值和半栏/整栏宽度都可修改。
- 正文可以使用 `{{employee.name}}`、`{{school.displayName}}` 等变量，修改基础字段后自动同步。
- 学校 Logo、学校自有信头背景、授权签字图片上传。
- 主色、强调色、正文和标题字体、字号、版式风格及排版密度。
- 核验网址、电话、邮箱、核验说明、可扫描 QR 码和记录指纹。
- 浏览器草稿保存、JSON 导入导出、完整 JSON 高级编辑。
- 预览区点击直接编辑可见文字。
- 一页溢出检测和自动压缩排版。

## 方法一：浏览器直接编辑并保存 PDF

### 推荐文件

直接打开：

```text
k12_employment_verification_pro_editor_singlefile.html
```

这是自包含版本，不依赖网络，也不需要额外的 JavaScript 文件。模块化版本 `k12_employment_verification_pro_editor.html` 也可以使用，但必须保留同目录下的 `vendor` 文件夹。

### 操作步骤

1. 使用 Chrome 或 Microsoft Edge 打开 HTML。
2. 在左侧逐项修改学校、教师、签字人和核验信息。
3. 需要完全自由调整时：
   - 打开“Letter Body Paragraphs”增加或删除正文；
   - 打开“Employment Detail Rows”增加、删除或移动证明字段；
   - 打开“Advanced JSON Editor”编辑完整数据；
   - 开启 `Click-to-edit preview`，直接点击右侧信件文字修改。
4. 上传学校正式 Logo；需要时上传授权签字人的透明 PNG 签名。
5. 审核稿点击 `Print / Save Draft PDF`，会保留草稿水印。
6. 正式稿点击 `Validate & Print Final`。模板会检查必填项、演示数据和页面溢出。
7. 浏览器打印窗口设置：
   - Destination：`Save as PDF`
   - Paper size：`Letter`
   - Scale：`100%`
   - Margins：`None`
   - Headers and footers：关闭
   - Background graphics：开启

## 方法二：通过 JSON 自动生成 PDF

### 安装依赖

```bash
python -m pip install -r requirements.txt
playwright install chromium
```

如果系统已经安装 Chrome 或 Chromium，脚本会优先尝试使用现有浏览器。

### 生成审核稿

```bash
python generate_pdf.py \
  --data examples/sample_letter.json \
  --output output/teacher_letter_draft.pdf \
  --manifest
```

### 建立真实数据文件

```bash
cp examples/blank_letter.json teacher_jordan_lee.json
```

用文本编辑器、代码编辑器或网页编辑器把所有占位内容换成学校已核实的信息。

### 生成正式稿

```bash
python generate_pdf.py \
  --data teacher_jordan_lee.json \
  --output output/Jordan_Lee_employment_verification.pdf \
  --final \
  --manifest
```

`--final` 会：

- 移除草稿水印；
- 检查学校、教师、签字人和核验必填字段；
- 阻止方括号占位符、演示电话、保留域名、`sample` 或 `draft` 等测试内容；
- 检查薪资开关与薪资内容是否一致；
- 检查内容是否超过一页；
- 写入 PDF 标题、作者、主题和 Letter ID 元数据。

`--manifest` 会在 PDF 旁边生成 JSON 清单，其中包含 PDF 文件的 SHA-256 摘要。`--force` 只用于受控版面测试，不应作为正式签发流程。

## 变量 / Token 用法

正文和证明字段的值可以引用完整 JSON 路径。例如：

```text
{{employee.name}}
{{employee.jobTitle}}
{{employee.startDate}}
{{school.legalName}}
{{school.officeName}}
{{document.issueDate}}
{{document.id}}
{{verification.phone}}
{{verification.email}}
```

示例：

```text
This letter confirms that {{employee.name}} is currently employed by
{{school.legalName}} as a {{employee.jobTitle}}.
```

完整路径见 `FIELD_REFERENCE_CN.md`。

## QR 码、记录指纹与清单

- QR 码由 HTML 在本地离线生成，内容为 `verification.url`。
- 页面中的 `Record fingerprint` 是基于信件数据计算的 SHA-256 截断值，用于内部记录比对。
- `--manifest` 生成的 `pdfSha256` 是最终 PDF 文件的完整 SHA-256 摘要。
- 这些机制有助于核验和审计，但不等同于由受信任证书机构签发的数字签名。学校需要真正的加密签名时，应在最终 PDF 上使用本校获批的电子签名平台。

## 正式签发建议

1. 只允许学校授权的 HR、校长办公室或行政人员签发。
2. 使用学校法定名称、官方域名邮箱、官网和可由第三方独立回拨的电话。
3. 每封信分配唯一 Letter ID，并在学校内部保存对应 JSON、PDF 和签发记录。
4. 核验网址应使用 HTTPS，并由学校实际控制。
5. 薪资、教师证号、住址等敏感信息只在得到教师授权且确有必要时提供。
6. 正式 PDF 应使用学校真实 Logo 和经授权的签名方式。
7. 不要加入学校并不具备的认证、政府许可、第三方徽标、印章、公证标记或资质声明。
8. 第三方来电核验时，应通过学校官网公开渠道确认联系人，不应只依赖 PDF 中自行填写的联系方式。

## 版面过长时

编辑器顶部会显示 `Content exceeds one page`。处理顺序：

1. 点击 `Auto-fit One Page`；
2. 将 Density 改为 `Compact` 或 `Tight`；
3. 适度降低 Base font size；
4. 删除不必要的自定义行；
5. 缩短正文或收件地址。

脚本生成 PDF 时发现溢出会停止输出，不会静默裁切内容。

## PDF 是否可直接改字段

最终 PDF 是适合发送给教师或核验方的扁平化正式文件，不保留可修改表单域。需要修改时，应编辑 HTML 或 JSON 后重新生成 PDF。这样可以减少 PDF 被收件人直接改写的风险。
