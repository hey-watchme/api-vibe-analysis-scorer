# GitHub Actions CI/CD Setup

## 概要
このディレクトリにはGitHub Actionsを使用したCI/CDパイプラインの設定が含まれています。

## デプロイフロー

1. **トリガー**: 
   - mainブランチへのpush
   - 手動実行（GitHub Actions UI）

2. **ビルド**:
   - Dockerfile.prodを使用してDockerイメージをビルド
   - ECRにプッシュ（latest + commit SHAタグ）

3. **デプロイ**:
   - EC2にSSH接続
   - 最新イメージをプル
   - systemdサービスを再起動

4. **検証**:
   - ヘルスチェックエンドポイントで確認

## 必要なGitHub Secrets

以下のシークレットをGitHubリポジトリに設定する必要があります：

### AWS認証情報
- `AWS_ACCESS_KEY_ID`: AWS アクセスキーID
- `AWS_SECRET_ACCESS_KEY`: AWS シークレットアクセスキー

### EC2 SSH
- `EC2_SSH_KEY`: EC2インスタンスへのSSH秘密鍵

## シークレットの設定方法

1. GitHubリポジトリページで「Settings」タブを選択
2. 左メニューの「Secrets and variables」→「Actions」を選択
3. 「New repository secret」をクリック
4. 各シークレットを追加

### EC2_SSH_KEYの設定
```bash
# ローカルの秘密鍵を確認
cat ~/watchme-key.pem

# 内容をコピーして、GitHub Secretsに貼り付け
# -----BEGIN RSA PRIVATE KEY----- から
# -----END RSA PRIVATE KEY----- まで全て含める
```

### AWS認証情報の取得
```bash
# AWS CLIで確認（既に設定済みの場合）
cat ~/.aws/credentials

# または、AWS IAMコンソールで確認
```

## 手動デプロイ

CI/CDが設定されていない場合や、手動でデプロイしたい場合：

```bash
# プロジェクトディレクトリで実行
./deploy-ecr.sh

# EC2でサービス再起動
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82 "sudo systemctl restart api-gpt-v1"
```

## トラブルシューティング

### デプロイが失敗する場合
1. GitHub Secretsが正しく設定されているか確認
2. AWS認証情報の権限を確認（ECR push権限が必要）
3. EC2のセキュリティグループでGitHub ActionsのIPが許可されているか確認

### ローカルでテスト
```bash
# Dockerイメージのビルドテスト
docker build -f Dockerfile.prod -t test-api .

# ローカル実行
docker run -p 8002:8002 --env-file .env test-api
```

## 関連ファイル
- `deploy-ecr.yml`: GitHub Actionsワークフロー
- `../../Dockerfile.prod`: 本番用Dockerファイル
- `../../deploy-ecr.sh`: 手動デプロイスクリプト