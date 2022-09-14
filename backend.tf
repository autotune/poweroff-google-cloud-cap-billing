drwxr-xr-x  13 brianadams  staff   416B Sep 14 17:25 .git
terraform {
  backend "gcs" {
    bucket  = "terrateam"
    prefix  = "budgetes/cap"
  }
}
