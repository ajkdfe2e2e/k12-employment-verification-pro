# 字段和 Token 参考

HTML 编辑器支持完整 JSON 导入导出。正文与证明字段可以通过 `{{路径}}` 引用数据。

## `document`

| 路径 | 用途 |
|---|---|
| `document.issueDate` | 签发日期，可使用学校习惯的英文日期格式 |
| `document.id` | 唯一 Letter ID / Document ID |
| `document.title` | 右上角主标题 |
| `document.subtitle` | 右上角副标题 |
| `document.subject` | 主题行，可使用 Token |
| `document.greeting` | 称呼 |
| `document.draftWatermark` | 是否显示草稿水印 |
| `document.watermarkText` | 水印文字 |
| `document.statusLabel` | 正式文件状态标签 |
| `document.labels.date` | 日期标签 |
| `document.labels.id` | ID 标签 |
| `document.labels.subjectPrefix` | 主题前缀，如 `RE:` |

## `school`

| 路径 | 用途 |
|---|---|
| `school.legalName` | 学校法定名称 |
| `school.displayName` | 信头显示名称 |
| `school.initials` | 无 Logo 时的字母标识 |
| `school.officeName` | 签发部门 |
| `school.secondaryLine` | 学区、学校类型、年级范围等 |
| `school.addressLine1` | 街道地址 |
| `school.cityStateZip` | 城市、州、ZIP |
| `school.phone` | 官方电话 |
| `school.fax` | 传真，可留空 |
| `school.email` | 官方邮箱 |
| `school.website` | 官方网站 |
| `school.ncesId` | NCES ID，可留空 |
| `school.stateSchoolId` | 州学校编号，可留空 |
| `school.logoDataUrl` | Logo 图片 Data URL，由网页上传自动生成 |
| `school.letterheadDataUrl` | 学校自有信头背景图片 Data URL |

## `recipient`

| 路径 | 用途 |
|---|---|
| `recipient.enabled` | 是否显示收件人块 |
| `recipient.name` | 收件人姓名 |
| `recipient.title` | 收件人职务 |
| `recipient.organization` | 收件机构 |
| `recipient.address` | 多行地址 |

## `employee`

| 路径 | 用途 |
|---|---|
| `employee.name` | 教师/员工姓名 |
| `employee.id` | Employee ID |
| `employee.jobTitle` | 职位 |
| `employee.department` | 学部或部门 |
| `employee.campus` | 校区或工作地点 |
| `employee.gradeSubject` | 任教年级、学段和学科 |
| `employee.status` | 在职状态 |
| `employee.startDate` | 入职日期 |
| `employee.endDate` | 结束日期，可留空 |
| `employee.scheduleFte` | FTE、每周工时或工作安排 |
| `employee.contractTerm` | 合同期限或学年 |
| `employee.supervisor` | 主管，可留空 |
| `employee.license` | 教师证或执业信息，可留空 |
| `employee.includeCompensation` | 是否把薪资加入证明表格 |
| `employee.compensation` | 薪资数值 |
| `employee.compensationBasis` | 年薪、时薪等口径 |
| `employee.note` | 表格下方的突出说明 |

## `letter`

| 路径 | 用途 |
|---|---|
| `letter.bodyParagraphs` | 正文段落数组，可增加、删除和排序 |
| `letter.closingParagraph` | 核验联系段落 |
| `letter.disclaimer` | 非合同、非持续雇佣保证等说明 |
| `letter.complimentaryClose` | `Sincerely,` 等结语 |
| `letter.footerText` | 页脚保密或使用说明 |
| `letter.footerRight` | 页脚右侧状态文字 |

## `detailRows`

每一项结构：

```json
{
  "label": "Employment Status",
  "value": "{{employee.status}}",
  "width": "half",
  "enabled": true
}
```

- `label`：字段标题，完全可改。
- `value`：字段内容，可使用 Token。
- `width`：`half` 为半栏，`full` 为整栏。
- `enabled`：JSON 中设为 `false` 时不显示。

## `signatory`

| 路径 | 用途 |
|---|---|
| `signatory.name` | 授权签字人姓名 |
| `signatory.credentials` | 学位或资质后缀 |
| `signatory.title` | 职务 |
| `signatory.department` | 部门 |
| `signatory.phone` | 核验电话 |
| `signatory.email` | 官方邮箱 |
| `signatory.typedSignature` | 没有图片时显示的签名字样 |
| `signatory.showTypedSignature` | 是否显示签名字样 |
| `signatory.signatureDataUrl` | 签名图片 Data URL |

## `verification`

| 路径 | 用途 |
|---|---|
| `verification.enabled` | 是否显示核验面板 |
| `verification.showQr` | 是否生成二维码 |
| `verification.title` | 面板标题 |
| `verification.url` | 二维码和在线核验网址 |
| `verification.phone` | 核验电话 |
| `verification.email` | 核验邮箱 |
| `verification.instructions` | 核验说明 |
| `verification.fingerprintLabel` | 记录指纹标签 |
| `verification.recordFingerprint` | 自动生成；也可由受控系统覆盖 |
| `verification.qrDataUrl` | 可选自定义二维码图片；通常留空由 HTML 自动生成 |

## `theme`

| 路径 | 可用值 / 用途 |
|---|---|
| `theme.style` | `classic`、`modern`、`minimal` |
| `theme.density` | `comfortable`、`compact`、`tight` |
| `theme.bodyFont` | CSS 字体栈 |
| `theme.headingFont` | CSS 字体栈 |
| `theme.primaryColor` | 六位十六进制颜色，如 `#17324d` |
| `theme.accentColor` | 六位十六进制颜色 |
| `theme.baseFontSize` | 正文字号，建议 8.5-12 pt |

## 常用 Token 示例

```text
{{employee.name}}
{{employee.id}}
{{employee.jobTitle}}
{{employee.department}}
{{employee.gradeSubject}}
{{employee.status}}
{{employee.startDate}}
{{employee.scheduleFte}}
{{employee.contractTerm}}
{{school.legalName}}
{{school.displayName}}
{{school.officeName}}
{{school.phone}}
{{school.email}}
{{document.issueDate}}
{{document.id}}
{{verification.phone}}
{{verification.email}}
```

引用不存在的路径时，预览中会显示为空。Token 只替换文字，不执行代码。
