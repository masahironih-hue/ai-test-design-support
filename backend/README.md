## Backend ローカル起動手順

### 前提

- Python 3.13.x
- Windows PowerShell

### 仮想環境作成

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 依存関係インストール

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Backend起動

```powershell
python -m uvicorn app.main:app --reload
```

### ヘルスチェック

```powershell
curl http://127.0.0.1:8000/health
```

期待レスポンス:

```json
{
  "status": "ok",
  "service": "ai-test-design-support-backend"
}
```

### テスト実行

```powershell
python -m pytest
```