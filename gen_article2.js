const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel,
        BorderStyle, ExternalHyperlink } = require("docx");

const bodyText = (text, opts = {}) => new Paragraph({
  spacing: { before: 120, after: 120, line: 400 },
  alignment: AlignmentType.JUSTIFIED,
  ...opts,
  children: [new TextRun({ text, font: "Microsoft YaHei", size: 22 })]
});

const sectionTitle = (text) => new Paragraph({
  spacing: { before: 360, after: 180 },
  children: [new TextRun({ text, font: "Microsoft YaHei", size: 30, bold: true })]
});

const articleTitle = (text) => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 200, after: 400 },
  children: [new TextRun({ text, font: "Microsoft YaHei", size: 40, bold: true })]
});

const boldBody = (text) => new Paragraph({
  spacing: { before: 120, after: 120, line: 400 },
  alignment: AlignmentType.JUSTIFIED,
  children: [new TextRun({ text, font: "Microsoft YaHei", size: 22, bold: true })]
});

const linkPara = (text, url) => new Paragraph({
  spacing: { before: 120, after: 120 },
  children: [new ExternalHyperlink({
    children: [new TextRun({ text, font: "Microsoft YaHei", size: 22, style: "Hyperlink" })],
    link: url,
  })]
});

const divider = () => new Paragraph({
  spacing: { before: 240, after: 240 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC", space: 1 } },
  children: []
});

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Microsoft YaHei", size: 22 } } },
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      articleTitle("AI时代，承接房地产塌方的凭什么会是数据产业？"),

      bodyText("如果说有哪一个行业有资格对21世纪上半叶的中国进行定位，毫无疑问就是房地产。这个曾让中国真正腾飞的经济引擎，在把无数人的财富人生推向高位之后，又迅速裹挟着大众坠入了谷底。"),
      
      bodyText("站在中国经济新旧引擎交替的十字路口，普通打工人要怎么说服自己在一个前途未卜的AI新时代里，劳动者要怎么从AI和机器人手里抢到饭碗？"),

      divider(),

      sectionTitle("一、房地产：从引擎到拖累"),

      bodyText("过去二十年，房地产是中国经济最重要的发动机。截至2024年，房地产业和建筑业增加值合计占GDP比重仍达13%，直接带动就业超过7000万人，关联上下游近50个行业——钢铁、水泥、家电、金融。高峰时期，房地产对GDP的综合贡献曾接近30%。"),

      bodyText("但这部发动机正在熄火。"),

      bodyText("2022到2024年，房地产投资连续三年下降，在固定资产投资中的占比从27%跌到19%。2025年上半年又跌了11%。土地出让收入从2021年的8.71万亿降到2024年的4.87万亿，几乎腰斩。建筑业农民工累计减少了1300万人。2025年，房地产对经济增长的拖累幅度达到-2.3%。"),

      boldBody("不是房地产不重要了，是旧的发展模式已经走到尽头。"),

      bodyText("当一台年产8万亿增加值、养活7000万人的引擎开始反向拖累经济，中国必须找到新的增长极。问题是：替代者在哪里？"),

      divider(),

      sectionTitle("二、谁能接住这个盘子？"),

      bodyText("制造业是中国经济的压舱石——34.7万亿增加值，全球第一，不会动摇。但制造业正在智能化，用工量持续下降，它不能承接被房地产挤出的劳动力。"),

      bodyText("消费和服务业体量巨大，但增速温和，无法填补房地产留下的增长缺口。"),

      bodyText("新能源和碳经济是确定性的增量，但规模还在万亿级以下，至少需要五到十年才能长成支柱。"),

      bodyText("那数据产业呢？"),

      bodyText("2025年，信息传输、软件和信息技术服务业增加值达到8万亿——跟房地产业的8万亿平起平坐。但趋势完全相反：信息IT业以每年11%的速度增长，房地产投资则以17%的速度萎缩。"),

      bodyText("根据国家数据局统计，2024年全国数据企业超过40万家，数据产业规模达到5.86万亿元，年均增速超过15%。按这个速度，最迟2028年，数据产业的规模就会超过纯房地产业。"),

      boldBody("这是目前唯一一个体量相当、增速足够、且在加速扩张的产业。"),

      bodyText("但体量只是第一步。真正的问题是：它能消化多少劳动力？"),

      divider(),

      sectionTitle("三、数据产业能接住多少人"),

      bodyText("房地产业直接和间接带动了7000万人就业。数据产业目前远远不到这个数量级——七大数据标注基地的标注从业人员加起来刚过9.5万。光看这个数字，说\"替代\"是可笑的。"),

      bodyText("但数据产业跟房地产有一个根本性的不同：它不是盖完就结束了。"),

      bodyText("房地产的价值创造集中在建设期——房子盖完，产业链的就业高峰就过了。数据产业的价值创造是持续性的——一份医疗数据今天被标注、明天被调用、五年后还可能有新模型在用它。每一次调用都在产生新的治理、更新、校验需求。这不是一次性的基建工程，是长期的服务业。"),

      bodyText("更重要的是，数据产业消纳的不是\"体力劳动力\"，是\"认知劳动力\"。"),

      boldBody("每个行业都有属于自己的认知壁垒，这些壁垒在AI时代恰好变成了就业机会。"),

      bodyText("医生的一双眼睛能看懂CT片上的微小阴影——这个判断力，可以训练100个诊断模型。工程师的经验知道哪张老图纸上的标注有歧义——这个判断力，可以变成工业缺陷检测的标准数据集。法官的直觉能分辨两份相似判决文书背后的不同法律逻辑——这个判断力，可以成为智能法律检索的训练数据。"),

      bodyText("这些认知能力目前基本没有被当作经济资源来使用。一旦各行各业的海量非结构化数据开始苏醒——病历、图纸、判例、传感器日志——需要的不只是\"几分钱一条\"的初级标注，而是成千上万的领域判断者。"),

      bodyText("全国语言数据标注人才缺口已经超过100万。长沙一个城市就培育了2.2万名持证标注员。这不是终点——七个基地已经形成85PB标注规模、364家企业、183亿产值，离\"规模化\"还有很长的增长曲线。国家目标：到2027年，数据标注产业年均复合增长率超过20%。"),

      bodyText("数据产业不可能在五年内完全替代房地产的7000万就业。但它是最好的起步方向——因为它是唯一一个\"AI越强、需要的人越多\"的行业。其他行业是AI替人，这个行业是AI养人。"),

      divider(),

      sectionTitle("四、AI正在把这件事加速"),

      bodyText("有人会问：你刚说完数据标注需要大量人力，AI不是正在替代标注员吗？"),

      bodyText("恰好相反。三个技术拐点刚刚跨过，它们不是在消灭岗位，是在降低数据治理的成本——让以前标不起的海量数据现在能标了。"),

      bodyText("第一，大语言模型本身成了最好的结构化工具。以前把一份手写病历转成结构化字段，需要医学专家逐条标注，成本极高。现在可以喂给大模型，让它按schema输出——在很多场景准确率已经超过人工。人只需要做抽检。"),

      bodyText("第二，AI标注形成了正反馈闭环。人标注→训练模型→模型辅助标注→人只做抽检→单价持续下降。结果是：以前因为成本太高而被放弃的数据（老旧工厂图纸、地方档案馆文档、稀有农作物病虫害照片），现在可以被纳入产业化的轨道了。"),

      bodyText("第三，数据产品的定义正在标准化。以前\"卖数据\"是买卖裸数据，法律风险大、定价模糊。现在\"卖数据产品\"——比如一套医疗影像诊断训练包——是\"数据+标注+模型\"的封装方案，有清晰的产品形态和定价逻辑。有了产品，才有了产业链。"),

      boldBody("AI不是数据行业的替代者，是数据行业的放大器。它让每一份数据都能产生更多的价值，也让创造这些价值的人有机会分到更多。"),

      divider(),

      sectionTitle("五、产业做大了，然后呢"),

      bodyText("如果这篇文章停在这里，它是一篇行业科普。但你知道我要说什么。"),

      bodyText("互联网时代有一个教训：一个新兴产业从零发展到万亿级的过程中，分配规则不会自动变好。平台越做越大，产业链最末端的人越分越少。这不是任何人主观上的恶意，是分配机制设计的滞后——工业时代的计件工资规则，处理不了AI时代\"一份数据被一百个模型反复调用\"这种层积式价值创造。"),

      bodyText("数据产业正在以每年15%的速度膨胀，最迟2028年就会超过房地产。如果分配规则不跟上，结果就是：产业越大，不公平越大。一个年产183亿产值的标注产业如果还沿用\"几分钱一条\"的计件规则，那它在分配意义上的进步为零。"),

      bodyText("所以我们试着做了一个回答。不是空谈——有贡献值量化公式，有智能合约自动分润的设计，有从公共数据到企业数据的逐步推进路径。开源在 GitHub 上，欢迎来挑刺，也欢迎来一起把这一步推到下一步。"),

      bodyText("替代房地产，不是数据产业一家的事。但它是第一个具备\"体量相当、增速足够、且能消化大规模认知劳动力\"条件的产业。"),

      bodyText("规模的问题我们已经回答了。分配的问题，还没有人认真回答。"),

      linkPara("github.com/Willsgao/data-contribution-economy", "https://github.com/Willsgao/data-contribution-economy"),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("F:\\wills\\economy-structures\\文章\\第2篇_AI时代承接房地产塌方的凭什么会是数据产业.docx", buffer);
  console.log("Done: 第2篇_AI时代承接房地产塌方的凭什么会是数据产业.docx");
});
