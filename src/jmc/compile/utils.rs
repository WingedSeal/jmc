pub fn is_decorator(string: &str) -> bool {
    return string.len() > 2 && string.starts_with("@");
}
