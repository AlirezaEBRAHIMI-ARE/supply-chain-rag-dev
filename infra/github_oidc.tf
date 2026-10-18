# Rule: AWS trusts ID cards (tokens) signed by GitHub Actions
resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}

# Who may use the role: only our repo, only on pull requests or on main
data "aws_iam_policy_document" "github_trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:AlirezaEBRAHIMI-ARE/supply-chain-rag-dev:pull_request",
        "repo:AlirezaEBRAHIMI-ARE/supply-chain-rag-dev:ref:refs/heads/main",
      ]
    }
  }
}

# The role GitHub will wear (name must start with github-actions-)
resource "aws_iam_role" "github_plan" {
  name               = "github-actions-plan"
  assume_role_policy = data.aws_iam_policy_document.github_trust.json
}

# Read-only power: look at everything, change nothing
resource "aws_iam_role_policy_attachment" "github_plan_readonly" {
  role       = aws_iam_role.github_plan.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

output "github_plan_role_arn" {
  value = aws_iam_role.github_plan.arn
}

# Lets the GitHub role read the state notebook (and write the lock file)
resource "aws_iam_role_policy" "github_plan_state" {
  name = "state-access"
  role = aws_iam_role.github_plan.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = "arn:aws:s3:::rag-supply-tfstate-308087722552"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = "arn:aws:s3:::rag-supply-tfstate-308087722552/*"
      }
    ]
  })
}
