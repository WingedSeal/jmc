use super::{
    exception::JMCError,
    tokenizer::{self, Token, TokenType, Tokenizer},
};

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

#[inline]
pub fn is_vanilla_macro(string: &str) -> bool {
    string.starts_with("$(") && string.ends_with(")")
}

/// Turns JMC function/predicate name syntax to vanilla's syntax
///
/// * `prefix` - The class for parsing `this`, defaults to `""`
/// * `is_make_lower` - defaults to `true`
///
/// # Examples
/// ```
/// let token = Token.empty("hello.World");
/// assert_eq!(convention_jmc_to_mc(token.string, &token, tokenizer, "class", true), "hello/world")
/// ```
pub fn convention_jmc_to_mc(
    string: &str,
    token: &Token,
    tokenizer: &Tokenizer,
    prefix: &str,
    is_make_lower: bool,
) -> Result<String, JMCError> {
    use once_cell::unsync::Lazy;
    use regex::Regex;
    const VALID_CHARS: Lazy<Regex> = Lazy::new(|| {
        Regex::new(r"^[a-z0-9_\\/.]+$").expect("the regex should not fail to compile")
    });

    let mut string = string.to_owned();
    if string.starts_with(".") {
        return Err(JMCError::jmc_syntax_exception(
            "A name cannot starts with '.'".to_owned(),
            Some(token),
            tokenizer,
            false,
            true,
            false,
            None,
        ));
    }
    if string.ends_with(".") {
        return Err(JMCError::jmc_syntax_exception(
            "A name cannot ends with '.'".to_owned(),
            Some(token),
            tokenizer,
            false,
            true,
            false,
            None,
        ));
    }

    if !prefix.is_empty() && string.starts_with("this.") {
        string = string.replace("this.", prefix);
    }

    // `This.func_name` should compile to `this.func_name` instead of `class_name.func_name` so `make_ascii_lowercase` should come after
    if is_make_lower {
        string.make_ascii_lowercase();
    }

    if !VALID_CHARS.is_match(string.as_str()) {
        let parens_hint = if string.ends_with("()") {
            Some(format!(
                "If {string} is meant to be a function name, remove the parentheses"
            ))
        } else {
            None
        };
        return Err(JMCError::minecraft_syntax_warning(
            format!("Invalid character detected in '{string}'"),
            Some(token),
            tokenizer,
            false,
            true,
            false,
            parens_hint,
        ));
    }

    Ok(string.replace(".", "/"))
}
