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
    "lastRejectedReason": null
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
    "currentRevisionGate": "awaiting_revision_plan_approval",
    "awaitingUserApproval": true
  },
  "blockingIssues": [
    "Waiting for user approval on current polishing round"
  ]
}
```
