// 周易占卜核心逻辑
const fs = require("fs");
const path = require("path");

// 加载数据
const gua64Data = require("../data/64-gua.json");
const gua8Data = require("../data/8-gua.json");

// 模拟摇铜钱
function yaoGua() {
  const coins = Array(3)
    .fill(0)
    .map(() => (Math.random() > 0.5 ? 1 : 0));
  const heads = coins.reduce((a, b) => a + b, 0);

  if (heads === 3)
    return { type: "老阴", yinYang: "阴", change: true, value: 0 };
  if (heads === 0)
    return { type: "老阳", yinYang: "阳", change: true, value: 1 };
  if (heads === 2)
    return { type: "少阳", yinYang: "阳", change: false, value: 1 };
  return { type: "少阴", yinYang: "阴", change: false, value: 0 };
}

// 摇6次得到一卦
function yaoLiuCi() {
  const yaos = [];
  for (let i = 0; i < 6; i++) {
    yaos.push(yaoGua());
  }
  return yaos;
}

// 数字到八卦的映射
const numToGua = [null, "乾", "兑", "离", "震", "巽", "坎", "艮", "坤"];

// 八卦符号
const guaSymbols = {
  乾: "☰",
  兑: "☱",
  离: "☲",
  震: "☳",
  巽: "☴",
  坎: "☵",
  艮: "☶",
  坤: "☷",
};

// 爻位名称
const yaoPositions = ["初", "二", "三", "四", "五", "上"];

// 根据爻计算上卦和下卦 (先天八卦数)
// 震100=4, 巽101=5, 坎110=6, 坤000=0(8)
// 公式: num = binary === 0 ? 8 : 8 - binary
function calcGua(yaos) {
  const lower = yaos.slice(0, 3);
  let lowerNum = lower.reduce((sum, y, i) => sum + y.value * Math.pow(2, i), 0);
  lowerNum = lowerNum === 0 ? 8 : 8 - lowerNum;

  const upper = yaos.slice(3, 6);
  let upperNum = upper.reduce((sum, y, i) => sum + y.value * Math.pow(2, i), 0);
  upperNum = upperNum === 0 ? 8 : 8 - upperNum;

  return { upper: upperNum, lower: lowerNum };
}

// 获取卦象名称
function getGuaName(yaos) {
  const { upper, lower } = calcGua(yaos);
  return {
    upperName: numToGua[upper],
    lowerName: numToGua[lower],
    upperNum: upper,
    lowerNum: lower,
    fullName: numToGua[upper] + numToGua[lower],
    upperSymbol: guaSymbols[numToGua[upper]],
    lowerSymbol: guaSymbols[numToGua[lower]],
  };
}

// 获取主卦和变卦
function getZhuAndBianGua(yaos) {
  const mainGua = yaos.map((y) => y.value);
  const changedGua = yaos.map((y) => {
    if (y.change) return y.value === 1 ? 0 : 1;
    return y.value;
  });

  const dongYao = yaos
    .map((y, i) => (y.change ? i + 1 : null))
    .filter((x) => x !== null);

  // 计算变卦名称
  let bianName = null;
  if (dongYao.length > 0) {
    const changedYaoValues = changedGua.map((v, i) => ({ value: v, index: i }));
    const { upper, lower } = calcGua(changedYaoValues);
    bianName = numToGua[upper] + numToGua[lower];
  }

  return {
    mainGua,
    changedGua,
    dongYao,
    bianName,
  };
}

// 格式化爻字符串（ASCII版）
function formatYaoAscii(yao, index) {
  const symbol = yao.value === 1 ? "---" : "- -";
  let suffix = "";
  if (yao.change) {
    suffix = yao.type === "老阳" ? "(变阴)" : "(变阳)";
  }
  return `${yaoPositions[index]} ${symbol} ${yao.type}${suffix}`;
}

// 格式化爻字符串（符号版）
function formatYao(yao, index) {
  const symbol = yao.value === 1 ? "━━━" : "━ ━";
  let suffix = "";
  if (yao.change) {
    suffix = yao.type === "老阳" ? "（变阴）" : "（变阳）";
  }
  return `${yaoPositions[index]} ${symbol} ${yao.type}${suffix}`;
}

// 64卦查找表：先天八卦数 [上卦][下卦] -> 数据key
// 索引: 1=乾 2=兑 3=离 4=震 5=巽 6=坎 7=艮 8=坤
const gua64ByNums = [
  [], // 0占位
  ["", "乾", "履", "大有", "无妄", "姤", "讼", "遯", "否"], // 乾上
  ["", "夬", "兑", "革", "归妹", "大过", "困", "咸", "萃"], // 兑上
  ["", "大有", "睽", "离", "丰", "家人", "既济", "贲", "明夷"], // 离上
  ["", "大壮", "随", "噬嗑", "震", "恒", "解", "小过", "豫"], // 震上
  ["", "小畜", "中孚", "鼎", "益", "巽", "涣", "蛊", "观"], // 巽上
  ["", "需", "节", "既济", "屯", "井", "坎", "蹇", "比"], // 坎上
  ["", "大畜", "损", "贲", "小过", "渐", "蒙", "艮", "剥"], // 艮上
  ["", "泰", "临", "明夷", "复", "升", "师", "谦", "坤"], // 坤上
];

function getGua64Key(upperNum, lowerNum) {
  if (upperNum >= 1 && upperNum <= 8 && lowerNum >= 1 && lowerNum <= 8) {
    return gua64ByNums[upperNum][lowerNum];
  }
  return null;
}

// 获取64卦数据
function getGuaData(guaInfo) {
  // guaInfo包含 upper, lower 数字
  const key = getGua64Key(guaInfo.upper, guaInfo.lower);
  if (key && gua64Data[key]) {
    return gua64Data[key];
  }

  // 尝试直接查找
  if (gua64Data[guaInfo.fullName]) {
    return gua64Data[guaInfo.fullName];
  }

  return null;
}

// 生成完整占卜结果
function performDivination(question) {
  const yaos = yaoLiuCi();
  const guaInfo = getGuaName(yaos);
  const zhuBian = getZhuAndBianGua(yaos);
  const guaData = getGuaData({
    upper: guaInfo.upperNum,
    lower: guaInfo.lowerNum,
    fullName: guaInfo.fullName,
  });

  // 生成起卦过程描述
  const processLines = [];
  yaos.forEach((yao, i) => {
    const coinResults = [];
    // 模拟铜钱结果
    if (yao.type === "老阳") coinResults.push("○○○");
    else if (yao.type === "老阴") coinResults.push("●●●");
    else if (yao.type === "少阳") coinResults.push("○○●");
    else coinResults.push("●●○");

    processLines.push({
      times: i + 1,
      coins: coinResults[0],
      result: yao.yinYang + "爻",
      detail: yao.type,
      change: yao.change,
    });
  });

  return {
    question,
    yaos,
    guaInfo,
    zhuBian,
    guaData,
    processLines,
  };
}

// 格式化输出
function formatOutput(divinationResult) {
  const { question, guaInfo, zhuBian, guaData, processLines } =
    divinationResult;

  let output = "";
  output += "═══════════════════════════════════════\n";
  output += "         周 易 占 卜\n";
  output += "═══════════════════════════════════════\n\n";

  output += `【占卜问题】\n"${question}"\n\n`;

  output += "【起卦过程】\n";
  processLines.forEach((p) => {
    let line = `第${p.times}次: ${p.coins} → ${p.result}（${p.detail}）`;
    if (p.change) line += " ✦ 动爻";
    output += line + "\n";
  });
  output += "\n";

  output += "【得卦】\n";
  output += `主卦: ${guaInfo.fullName}卦 ${guaInfo.upperSymbol}${guaInfo.lowerSymbol}\n`;

  if (zhuBian.bianName) {
    output += `变卦: ${zhuBian.bianName}卦\n`;
    output += `动爻: ${zhuBian.dongYao.map((i) => yaoPositions[i - 1]).join("、")}\n`;
  }
  output += "\n";

  output += "【上卦】\n";
  output += `${guaInfo.upperName}（${gua8Data[guaInfo.upperName]?.nature || "未知"}）${guaInfo.upperSymbol}\n\n`;

  output += "【下卦】\n";
  output += `${guaInfo.lowerName}（${gua8Data[guaInfo.lowerName]?.nature || "未知"}）${guaInfo.lowerSymbol}\n\n`;

  if (guaData) {
    output += "【解卦】\n";
    output += `【卦辞】${guaData.guaCi}\n`;
    output += `【卦义】${guaData.xiang}\n`;

    if (guaData.yaoCi && guaData.yaoCi.length > 0) {
      output += "\n【爻辞摘要】\n";
      guaData.yaoCi.forEach((yc, i) => {
        output += `${yaoPositions[i]}: ${yc}\n`;
      });
    }
  }

  output += "\n═══════════════════════════════════════\n";

  return output;
}

// 生成AI解读提示
function generateAIPrompt(question, divinationResult) {
  const { guaInfo, zhuBian, guaData } = divinationResult;

  let prompt = `你是周易大师，请根据以下卦象为用户解读。\n\n`;
  prompt += `用户问题是：${question}\n\n`;
  prompt += `得到的卦象是：${guaInfo.fullName}卦\n`;

  if (guaData) {
    prompt += `卦辞：${guaData.guaCi}\n`;
    prompt += `象征意义：${guaData.xiang}\n`;
  }

  if (zhuBian.bianName) {
    prompt += `\n出现动爻：${zhuBian.dongYao.map((i) => yaoPositions[i - 1]).join("、")}（变为${zhuBian.bianName}卦）\n`;
    prompt += `变卦代表事物发展的最终结果。\n`;
  } else {
    prompt += `\n本卦无动爻，为静卦，表示当前状态稳定。\n`;
  }

  prompt += `\n请用文言文风格但现代人易懂的方式回答：\n`;
  prompt += `1. 这个卦象的总体含义是什么？\n`;
  prompt += `2. 针对用户的问题"${question}"，吉凶如何？\n`;
  prompt += `3. 有什么建议？\n`;
  prompt += `4. （如有变卦）变卦意味着什么？\n`;

  return prompt;
}

module.exports = {
  yaoGua,
  yaoLiuCi,
  calcGua,
  getGuaName,
  getZhuAndBianGua,
  formatYao,
  formatYaoAscii,
  guaSymbols,
  numToGua,
  getGuaData,
  performDivination,
  formatOutput,
  generateAIPrompt,
};
