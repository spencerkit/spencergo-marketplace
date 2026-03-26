# State Fields Template

Use this as a quick reference for important `.novel-state.json` fields.

```json
{
  "workflow": {
    "currentStage": "drafting",
    "currentSubstage": "batch-plan-review",
    "lastCompletedStage": "character-system",
    "nextStage": "drafting",
    "status": "awaiting_user_approval"
  },
  "approvals": {
    "discoveryApproved": true,
    "planningApproved": true,
    "characterApproved": true,
    "draftingApproved": false,
    "polishingApproved": false,
    "proofreadingApproved": false,
    "finalApproved": false,
    "titleConfirmed": true,
    "workingTitleApproved": false
  },
  "artifacts": {
    "hotSearchScan": true,
    "userPreference": true,
    "topicReport": true,
    "ideaDoc": true,
    "outlineDoc": true,
    "characterSummary": true,
    "chapterSkeleton": true,
    "recapDoc": true,
    "characterFiles": true,
    "manuscriptFiles": true,
    "feishuSynced": false
  },
  "batch": {
    "active": true,
    "chapterRange": "第1章-第3章",
    "chapterCount": 3,
    "scopeConfirmed": true,
    "chapterPlanExists": true,
    "chapterPlanApproved": true,
    "draftComplete": true,
    "polishingComplete": false,
    "proofreadingComplete": false,
    "recapUpdated": false,
    "awaitingNextBatchDecision": false,
    "focus": "开篇立钩子 + 主角气质建立",
    "attractionPoints": ["隐藏实力", "打脸前奏"],
    "climaxTarget": "第3章结尾反转"
  },
  "review": {
    "currentGate": "waiting_polishing_feedback",
    "lastUserFeedbackSummary": "语气还不够稳，主角魅力不足",
    "lastRevisionFocus": "加强主角吸引点和场景语气统一",
    "lastRejectedReason": null,
    "finalDecision": "conditional pass",
    "finalDeliveryReady": false,
    "finalBlockingIssues": [
      "第12章收束仍偏弱，需要补强终局情绪"
    ],
    "finalReviewSummary": "整体可读性稳定，但仍有阻塞项，暂不建议交付"
  },
  "revision": {
    "active": true,
    "feedbackType": "plot_feedback",
    "feedbackSummary": "加强前三章羞辱感和翻盘钩子",
    "affectedStages": ["drafting", "polishing"],
    "affectedFiles": [
      "05_本轮章节规划.md",
      "manuscript/第1章_你配不上我.md"
    ],
    "overrideMode": "add_on",
    "scopeSummary": "回改本轮章节规划和第1章开篇节奏",
    "conflictSummary": "不覆盖既定主线，只加强开篇吸引力",
    "revisionPlanSummary": "先改规划，再改正文，再复核润色结论",
    "resultSummary": null,
    "currentRevisionGate": "awaiting_revision_plan_approval",
    "awaitingUserApproval": true,
    "lastClosedRevision": null
  },
  "blockingIssues": [
    "Formal revision active: awaiting_revision_plan_approval"
  ]
}
```
