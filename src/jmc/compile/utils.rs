use super::tokenizer::Token;

#[inline]
pub fn is_decorator(string: &str) -> bool {
    return string.len() > 2 && string.starts_with("@");
}

#[inline]
/// Whether 2 tokens are next to each other
pub fn is_connected(current_token: &Token, previous_token: &Token) -> bool {
    if previous_token._macro_length == 0 {
        previous_token.line == current_token.line
            && previous_token.col + previous_token.length() as u32 == current_token.col
    } else {
        todo!()
    }
}
