# Who may use the apply role: ONLY a job running on the main branch of our repo
data "aws_iam_policy_document" "github_apply_trust" {
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
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:AlirezaEBRAHIMI-ARE@18158087/supply-chain-rag-dev@1402240232:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "github_apply" {
  name               = "github-actions-apply"
  assume_role_policy = data.aws_iam_policy_document.github_apply_trust.json
}

# Same limits as devops-cli (but NOT terraform-week4: the robot must not edit roles)
resource "aws_iam_role_policy_attachment" "github_apply_week2" {
  role       = aws_iam_role.github_apply.name
  policy_arn = "arn:aws:iam::308087722552:policy/terraform-week2"
}

resource "aws_iam_role_policy_attachment" "github_apply_week3" {
  role       = aws_iam_role.github_apply.name
  policy_arn = "arn:aws:iam::308087722552:policy/terraform-week3"
}

# Read everything, so terraform can refresh its state
resource "aws_iam_role_policy_attachment" "github_apply_readonly" {
  role       = aws_iam_role.github_apply.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# Read and write the state notebook and its lock file
resource "aws_iam_role_policy" "github_apply_state" {
  name = "state-access"
  role = aws_iam_role.github_apply.id

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
