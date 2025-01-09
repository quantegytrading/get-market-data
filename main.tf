terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.38.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4.2"
    }
  }
  required_version = "~> 1.2"
}


resource "null_resource" "install_python_dependencies" {
  provisioner "local-exec" {
    command = "bash ${path.module}/scripts/create_pkg.sh"

    environment = {
      source_code_path = var.path_source_code
      function_name = var.function_name
      path_module = path.module
      runtime = var.runtime
      path_cwd = path.cwd
    }
  }
}


data "archive_file" "function_zip" {
  source_dir  = "src"
  type        = "zip"
  output_path = "${path.module}/quantegy-get-market-data.zip"
  depends_on = [ null_resource.install_python_dependencies ]
}

resource "aws_s3_object" "file_upload" {
  bucket = "quantegy-analyze-soak-us-east-1-lambda"
  key    = "quantegy-get-market-data.zip"
  source = "quantegy-get-market-data.zip"
  depends_on = [ data.archive_file.function_zip ]
}

resource "aws_lambda_function" "function" {
  s3_bucket                       = "quantegy-analyze-soak-us-east-1-lambda"
  s3_key                          = "quantegy-get-market-data.zip"
  function_name                   = "quantegy-get-market-data"
  handler                        = "binance_1h.main"
  runtime                        = "python3.10"
  timeout                        = 900
  memory_size                    = 128
  role                           = "arn:aws:iam::716418748259:role/quantegy-ingest-live-us-east-1-lambdaRole"
  layers = tolist(["arn:aws:lambda:us-east-1:716418748259:layer:quantegy-get-lambda-layer:1"])

  depends_on = [ aws_s3_object.file_upload ]
}



