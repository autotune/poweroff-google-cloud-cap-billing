terraform {
  backend "gcs" {
    bucket  = "terrateam"
    prefix  = "budgetes/cap"
  }
}
