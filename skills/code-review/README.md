# Code Review

> 多语言代码审查技能 - 支持安全审计、性能优化、代码质量检查

## 功能

### 核心功能

- **代码审查** - 逻辑检查、改进建议、优化方案
- **安全审计** - 漏洞检测（SQL注入、XSS、CSRF 等）
- **性能优化** - 性能问题、瓶颈分析
- **多语言支持** - JS/TS/Python/Go/Java/Rust/C++/C#/Ruby/PHP

### 审查维度

#### 1. 代码质量
- 代码逻辑和正确性
- 可读性和可维护性
- 命名规范
- 代码结构
- 重复代码检测
- 注释质量

#### 2. 安全审计
- SQL 注入漏洞
- XSS 跨站脚本攻击
- CSRF 跨站请求伪造
- 认证授权问题
- 敏感数据泄露
- 命令注入
- 路径遍历

#### 3. 性能优化
- 时间复杂度分析
- 空间复杂度分析
- 数据库查询优化
- 缓存建议
- N+1 查询检测

#### 4. 最佳实践
- 语言特定最佳实践
- 框架约定
- 设计模式使用
- 错误处理
- 测试覆盖

## 使用方法

```bash
/spencergo:code-review
```

或直接描述审查需求：
- "帮我审查这段代码"
- "检查安全漏洞"
- "优化这个函数"

## 触发方式

- 直接调用：`/spencergo:code-review`
- 描述式："审查代码"、"检查安全问题"

## 支持的语言

| 语言 | 文件扩展名 |
|------|------------|
| JavaScript | .js, .mjs |
| TypeScript | .ts, .tsx |
| Python | .py |
| Go | .go |
| Java | .java |
| Rust | .rs |
| C++ | .cpp, .cc, .h |
| C# | .cs |
| Ruby | .rb |
| PHP | .php |

## 严重等级

- **CRITICAL** - 安全漏洞，可能导致数据丢失
- **HIGH** - 严重 bug，安全风险
- **MEDIUM** - 性能问题，可维护性问题
- **LOW** - 代码风格问题，轻微改进
- **INFO** - 建议、最佳实践

## 输出示例

```
## 代码审查摘要

| 类别 | 问题数 | 严重程度 |
|------|--------|----------|
| 安全 | 3 | 高 |
| 性能 | 2 | 中 |
| 代码质量 | 5 | 低 |
| 最佳实践 | 4 | 低 |

综合评分: 7/10
```

## 安装

This skill is part of spencergo-marketplace.

Installation:
```bash
/plugin marketplace add spencerkit/spencergo-marketplace
/plugin install spencergo@spencerkit/spencergo-marketplace
```

## License

MIT
