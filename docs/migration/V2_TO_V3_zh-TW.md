# 遷移指南（v2 到 v3）

## 摘要

- V3 引入了細粒度的權限控制和機器人商店功能，需要對 DynamoDB 架構進行變更
- **在遷移前備份您的 DynamoDB 對話表**
- 將您的倉庫 URL 從 `bedrock-claude-chat` 更新為 `bedrock-chat`
- 運行遷移腳本以將數據轉換為新架構
- 您的所有機器人和對話將在新的權限模型下被保留
- **重要：在遷移過程中，應用程式將對所有用戶不可用，直到遷移完成。此過程通常需要約 60 分鐘，具體取決於數據量和開發環境的性能。**
- **重要：在遷移過程中，必須刪除所有已發布的 API。**
- **警告：遷移過程無法保證所有機器人的 100% 成功。請在遷移前記錄重要的機器人配置，以便在需要時可以手動重新創建。**

## 簡介

### V3 的新功能

V3 為 Bedrock Chat 引入了重大的增強功能：

1. **細粒度權限控制**：使用基於用戶組的權限來控制對機器人的存取
2. **機器人商店**：透過集中的市集分享和發現機器人
3. **管理功能**：管理 API、將機器人標記為必要，並分析機器人使用情況

這些新功能需要對 DynamoDB 架構進行變更，因此需要對現有用戶進行遷移流程。

### 為什麼需要此遷移

新的權限模型和機器人商店功能需要重新構建機器人資料的儲存和存取方式。遷移流程會將現有的機器人和對話轉換為新架構，同時保留所有資料。

> [!WARNING]
> 服務中斷通知：**在遷移過程中，應用程式將對所有用戶不可用。** 請在維護時段進行此遷移，當用戶不需要存取系統時。只有在遷移腳本成功完成並且所有資料已正確轉換為新架構後，應用程式才會再次可用。此過程通常需要約 60 分鐘，具體取決於資料量和開發環境的效能。

> [!IMPORTANT]
> 在開始遷移之前：**遷移流程無法保證所有機器人 100% 成功**，尤其是使用舊版本或自訂配置建立的機器人。請在開始遷移流程之前，記錄重要機器人的配置（指令、知識來源、設定），以便在需要時可以手動重新建立。

## 遷移流程

### 關於 V3 中機器人可見性的重要通知

在 V3 中，**所有啟用公開分享的 v2 機器人都將可在 Bot Store 中搜尋。** 如果您有包含敏感資訊且不希望被發現的機器人，請考慮在遷移至 V3 之前將其設為私有。

### 步驟 1：識別您的環境名稱

在此程序中，`{YOUR_ENV_PREFIX}` 用於識別 CloudFormation Stacks 的名稱。如果您正在使用[部署多個環境](../../README.md#deploying-multiple-environments)功能，請將其替換為要遷移的環境名稱。如果沒有，請替換為空字串。

### 步驟 2：更新儲存庫 URL（建議）

儲存庫已從 `bedrock-claude-chat` 重新命名為 `bedrock-chat`。更新您的本地儲存庫：

```bash
# 檢查您目前的遠端 URL
git remote -v

# 更新遠端 URL
git remote set-url origin https://github.com/aws-samples/bedrock-chat.git

# 驗證更改
git remote -v
```

### 步驟 3：確保您在最新的 V2 版本

> [!WARNING]
> 您必須在遷移到 V3 之前更新到 v2.10.0。**跳過此步驟可能導致遷移過程中的資料遺失。**

在開始遷移之前，請確保您正在運行 V2 的最新版本（**v2.10.0**）。這確保在升級到 V3 之前，您已擁有所有必要的錯誤修復和改進：

```bash
# 獲取最新的標籤
git fetch --tags

# 切換到最新的 V2 版本
git checkout v2.10.0

# 部署最新的 V2 版本
cd cdk
npm ci
npx cdk deploy --all
```

### 步驟 4：記錄您的 V2 DynamoDB 表格名稱

從 CloudFormation 輸出中獲取 V2 ConversationTable 名稱：

```bash
# 獲取 V2 ConversationTable 名稱
aws cloudformation describe-stacks \
  --output text \
  --query "Stacks[0].Outputs[?OutputKey=='ConversationTableName'].OutputValue" \
  --stack-name {YOUR_ENV_PREFIX}BedrockAIAssistantStack
```

請確保將此表格名稱安全地保存，因為您稍後需要用於遷移腳本。

### 步驟 5：備份您的 DynamoDB 表格

在繼續之前，使用您剛剛記錄的名稱創建 DynamoDB ConversationTable 的備份：

```bash
# 創建 V2 表格的備份
aws dynamodb create-backup \
  --no-cli-pager \
  --backup-name "BedrockAIAssistantV2Backup-$(date +%Y%m%d)" \
  --table-name YOUR_V2_CONVERSATION_TABLE_NAME

# 檢查備份狀態是否可用
aws dynamodb describe-backup \
  --no-cli-pager \
  --query BackupDescription.BackupDetails \
  --backup-arn YOUR_BACKUP_ARN
```

### 步驟 6：刪除所有已發布的 API

> [!IMPORTANT]
> 在部署 V3 之前，您必須刪除所有已發布的 API，以避免 Cloudformation 輸出值在升級過程中衝突。

1. 以管理員身份登入您的應用程式
2. 導航至管理員區段並選擇「API 管理」
3. 查看所有已發布 API 的清單
4. 通過點擊每個 API 旁邊的刪除按鈕來刪除每個已發布的 API

您可以在 [PUBLISH_API.md](../PUBLISH_API_zh-TW.md)、[ADMINISTRATOR.md](../ADMINISTRATOR_zh-TW.md) 文件中找到有關 API 發布和管理的更多資訊。

### 步驟 7：拉取 V3 並部署

拉取最新的 V3 程式碼並部署：

```bash
git fetch
git checkout v3
cd cdk
npm ci
npx cdk deploy --all
```

> [!IMPORTANT]
> 一旦您部署 V3，在遷移過程完成之前，應用程式將對所有使用者不可用。新的架構與舊的資料格式不相容，因此使用者將無法存取他們的機器人或對話，直到您完成下一步的遷移腳本。

### 步驟 8：記錄您的 V3 DynamoDB 表格名稱

部署 V3 後，您需要獲取新的 ConversationTable 和 BotTable 名稱：

```bash
# 獲取 V3 ConversationTable 名稱
aws cloudformation describe-stacks \
  --output text \
  --query "Stacks[0].Outputs[?OutputKey=='ConversationTableNameV3'].OutputValue" \
  --stack-name {YOUR_ENV_PREFIX}BedrockAIAssistantStack

# 獲取 V3 BotTable 名稱
aws cloudformation describe-stacks \
  --output text \
  --query "Stacks[0].Outputs[?OutputKey=='BotTableNameV3'].OutputValue" \
  --stack-name {YOUR_ENV_PREFIX}BedrockAIAssistantStack
```

> [!Important]
> 請確保將這些 V3 表格名稱與您之前保存的 V2 表格名稱一起保存，因為您將在遷移腳本中需要所有這些名稱。

### 步驟 9：運行遷移腳本

遷移腳本將把您的 V2 資料轉換為 V3 架構。首先，編輯遷移腳本 `docs/migration/migrate_v2_v3.py` 以設置您的表格名稱和區域：

```python
# DynamoDB 所在的區域
REGION = "ap-northeast-1" # 替換為您的區域

V2_CONVERSATION_TABLE = "BedrockAIAssistantStack-DatabaseConversationTableXXXX" # 替換為您在步驟 4 記錄的值
V3_CONVERSATION_TABLE = "BedrockAIAssistantStack-DatabaseConversationTableV3XXXX" # 替換為您在步驟 8 記錄的值
V3_BOT_TABLE = "BedrockAIAssistantStack-DatabaseBotTableV3XXXXX" # 替換為您在步驟 8 記錄的值
```

然後從後端目錄使用 Poetry 運行腳本：

> [!NOTE]
> Python 需求版本已更改為 3.13.0 或更高版本（可能在未來開發中更改。請參見 pyproject.toml）。如果您已使用不同的 Python 版本安裝 venv，您需要先將其刪除。

```bash
# 導航到後端目錄
cd backend

# 如果尚未安裝依賴項，請安裝
poetry install

# 首先運行乾運行，查看將遷移的內容
poetry run python ../docs/migration/migrate_v2_v3.py --dry-run

# 如果一切看起來正常，運行實際遷移
poetry run python ../docs/migration/migrate_v2_v3.py

# 驗證遷移是否成功
poetry run python ../docs/migration/migrate_v2_v3.py --verify-only
```

遷移腳本將在當前目錄生成一個報告文件，其中包含遷移過程的詳細資訊。檢查此文件，確保所有資料已正確遷移。

#### 處理大量資料

對於有大量使用者或大量資料的環境，請考慮以下方法：

1. **逐個遷移使用者**：對於資料量大的使用者，逐個遷移：

   ```bash
   poetry run python ../docs/migration/migrate_v2_v3.py --users user-id-1 user-id-2
   ```

2. **記憶體考慮**：遷移過程會將資料載入記憶體。如果遇到記憶體不足（OOM）錯誤，請嘗試：

   - 逐個遷移使用者
   - 在記憶體更大的機器上運行遷移
   - 將遷移分批進行

3. **監控遷移**：檢查生成的報告文件，確保所有資料（尤其是大型資料集）都已正確遷移。

### 步驟 10：驗證應用程式

遷移後，打開您的應用程式並驗證：

- 所有機器人都可用
- 對話已保留
- 新的權限控制正常運作

### 清理（可選）

在確認遷移成功且所有資料在 V3 中正確可存取後，您可以選擇性地刪除 V2 對話表格以節省成本：

```bash
# 刪除 V2 對話表格（僅在確認成功遷移後）
aws dynamodb delete-table --table-name YOUR_V2_CONVERSATION_TABLE_NAME
```

> [!IMPORTANT]
> 僅在徹底驗證所有重要資料已成功遷移到 V3 後才刪除 V2 表格。即使刪除原始表格，我們建議至少保留在步驟 2 中創建的備份幾週。

## V3 常見問題集

### 機器人存取和權限

**Q: 如果我正在使用的機器人被刪除或我的存取權限被移除會發生什麼事？**
A: 授權在聊天時被檢查，因此您將立即失去存取權限。

**Q: 如果使用者被刪除（例如，員工離職）會發生什麼事？**
A: 可以通過刪除 DynamoDB 中以使用者 ID 作為分割鍵（PK）的所有項目來完全移除其資料。

**Q: 我可以關閉重要公開機器人的共享功能嗎？**
A: 不可以，管理員必須先將機器人標記為非重要，然後才能關閉共享。

**Q: 我可以刪除重要的公開機器人嗎？**
A: 不可以，管理員必須先將機器人標記為非重要，然後才能刪除。

### 安全性和實作

**Q: 機器人表是否實作了資料列層級安全性（RLS）？**
A: 不，考慮到存取模式的多樣性。在存取機器人時執行授權，與對話歷史記錄相比，元資料洩露的風險被認為是最小的。

**Q: 發佈 API 的要求是什麼？**
A: 機器人必須是公開的。

**Q: 初始 V3 版本中是否會有所有私人機器人的管理畫面？**
A: 不會。但是，仍可以通過使用使用者 ID 查詢來刪除項目。

**Q: 是否會有機器人標記功能以改善搜尋使用者體驗？**
A: 在初始 V3 版本中不會，但未來更新可能會新增基於 LLM 的自動標記。

### 管理

**Q: 管理員可以做什麼？**
A: 管理員可以：

- 管理公開機器人（包括檢查高成本機器人）
- 管理 API
- 將公開機器人標記為重要

**Q: 我可以將部分共享的機器人標記為重要嗎？**
A: 不可以，僅支援公開機器人。

**Q: 我可以為置頂機器人設定優先順序嗎？**
A: 在初始版本中，不可以。

### 授權配置

**Q: 如何設定授權？**
A:

1. 開啟 Amazon Cognito 控制台，在 BrChat 使用者池中建立使用者群組
2. 根據需要將使用者新增到這些群組
3. 在 BrChat 中，配置機器人共享設定時，選擇要允許存取的使用者群組

注意：群組成員資格變更需要重新登入才能生效。變更在權杖重新整理時反映，但在 ID 權杖有效期間（V3 中預設為 30 分鐘，可在 `cdk.json` 或 `parameter.ts` 中透過 `tokenValidMinutes` 配置）內不會改變。

**Q: 系統是否每次存取機器人時都會檢查 Cognito？**
A: 不會，授權是使用 JWT 權杖檢查，以避免不必要的 I/O 作業。

### 搜尋功能

**Q: 機器人搜尋是否支援語義搜尋？**
A: 不，僅支援部分文字匹配。由於目前 OpenSearch Serverless 的限制（2025 年 3 月），不支援語義搜尋（例如，"automobile" → "car"、"EV"、"vehicle"）。