#![allow(dead_code)]

use super::exception::JMCError;
use std::fmt::{format, Debug};
use std::rc::Rc;

/// Array of string that, if a line starts with, should automatically terminate line on `{}` without semicolons
const TERMINATE_LINE: [&'static str; 10] = [
    "function", "class", "new", "schedule", "if", "else", "do", "while", "for", "switch",
];

const OPERATORS: &[&'static str] = &[
    "+", "-", "*", "/", ">", "<", "=", "%", ":", "!", "|", "&", "?",
];

#[derive(Eq, PartialEq, Debug)]
pub enum TokenType {
    Keyword,
    Operator,
    Paren,
    ParenRound,
    ParenSquare,
    ParenCurly,
    String,
    Comment,
    Comma,
    Func,
}

impl TokenType {
    fn value(&self) -> &'static str {
        match self {
            TokenType::Keyword => "Keyword",
            TokenType::Operator => "Operator",
            TokenType::Paren => "PAREN",
            TokenType::ParenRound => "RoundParentheses",
            TokenType::ParenSquare => "SquareParentheses",
            TokenType::ParenCurly => "CurlyParentheses",
            TokenType::String => "StringLiteral",
            TokenType::Comment => "Comment",
            TokenType::Comma => "Comma",
            TokenType::Func => "Function",
        }
    }
}

#[derive(Debug)]
pub struct Token {
    pub token_type: TokenType,
    pub line: u32,
    pub col: u32,
    pub string: String,
    pub _macro_length: u32,
    pub quote: char,
}

fn repr(value: impl Debug) -> String {
    format!("{0:?}", value)
}

impl Token {
    /// A dataclass containing information for Token for Lexical Analysis
    ///
    /// * `token_type` - Type of the token
    /// * `line` - Which line it's found in
    /// * `col` - Which column it's found in
    /// * `string` - The string representation (including parentheses, excluding quotation mark)
    pub fn new(
        token_type: TokenType,
        line: u32,
        col: u32,
        string: String,
        _macro_length: Option<u32>,
        quote: Option<char>,
    ) -> Self {
        let _macro_length: u32 = match _macro_length {
            Some(value) => value,
            None => 0,
        };
        let quote: char = match quote {
            Some(value) => value,
            None => '"',
        };
        let token = Self {
            token_type,
            line,
            col,
            string,
            _macro_length,
            quote,
        };
        token.post_init();
        token
    }

    /// Create an empty token
    ///
    /// * `token_type` - New token's TokenType
    /// * `string` - New token's string
    /// * return - New token
    pub fn empty(token_type: TokenType, string: String) -> Self {
        let token = Self {
            token_type,
            line: 0,
            col: 0,
            string,
            _macro_length: 0,
            quote: '"',
        };
        token.post_init();
        token
    }

    /// Edit string and _length according to macros(`#define something`) defined
    fn post_init(&self) {
        if self.token_type != TokenType::ParenCurly {
            return;
        };
        if !self.string.starts_with("{") || !self.string.ends_with("}") {
            panic!("ParenCurly Token created but string doesn't start and end with the parenthesis")
        }
    }

    /// Getting the length of the string in token(including quotation mark)
    pub fn length(&self) -> usize {
        match self.token_type {
            TokenType::String => repr(&self.string).len(),
            _ => self.string.len(),
        }
    }

    /// Get self.string including quotation mark
    pub fn get_full_string(&self) -> String {
        if self.token_type != TokenType::String {
            return self.string.to_owned();
        }
        if self.quote != '`' {
            let string: String = repr(&self.string);
            return format!("`\n{0}\n`", &string[1..string.len() - 1]);
        }
        repr(&self.string)
    }

    /// Get self.string including quotation mark (Raise error when the token_type is not TokenType.STRING)
    pub fn add_quotation(&self) -> String {
        assert!(self.token_type == TokenType::String);
        repr(&self.string)
    }
}
#[derive(Debug)]
struct Pos {
    pub line: u32,
    pub col: u32,
}

mod re {
    use regex::bytes::Regex;

    pub const NEW_LINE: char = '\n';
    pub const BACKSLASH: char = '\\';
    pub const WHITESPACE: Regex = Regex::new(r"\s+").unwrap();
    pub const KEYWORD: Regex = Regex::new(r"[a-zA-Z0-9_\.\/\^\~]").unwrap();
    pub const SEMICOLON: char = ';';
    pub const COMMA: char = ',';
    pub const HASH: char = '#';
    pub const SLASH: char = '/';
}

mod quote {
    pub const SINGLE: char = '\'';
    pub const DOUBLE: char = '"';
    pub const BACKTICK: char = '`';
}

mod paren {
    pub const L_ROUND: char = '(';
    pub const R_ROUND: char = ')';
    pub const L_SQUARE: char = '[';
    pub const R_SQUARE: char = ']';
    pub const L_CURLY: char = '{';
    pub const R_CURLY: char = '}';
}

pub fn get_paren_pair(left_paren: char) -> Result<char, ()> {
    match left_paren {
        paren::L_ROUND => Ok(paren::R_ROUND),
        paren::L_SQUARE => Ok(paren::R_SQUARE),
        paren::L_CURLY => Ok(paren::R_CURLY),
        _ => Err(()),
    }
}
#[derive(Debug)]
struct MacroFactoryInfo {
    name: String,
    macro_factory: String, // TODO: Change to MacroFactory
    /// Argument count
    arg_count: u32,
    pos: Pos,
}
#[derive(Debug)]
/// A class for converting string into tokens
pub struct Tokenizer {
    /// List of lines(list of tokens)
    programs: Vec<Vec<Token>>,
    /// Starts at 1
    pub line: u32,
    /// Starts at 1
    pub col: u32,
    /// Current TokenType
    state: Option<TokenType>,
    /// Current string for token
    token_str: String,
    /// Position for creating token
    token_pos: Option<Pos>,
    /// Current list of tokens
    keywords: Vec<Token>,
    /// List of keywords(list_of_tokens)
    list_of_keywords: Vec<Vec<Token>>,

    /// Raw string read from file/given from another tokenizer
    raw_string: Rc<String>,
    /// Entire string read from current file
    file_string: Option<String>,
    /// File path to current JMC function as string
    pub file_path_str: String,

    // String
    /// Type of quote
    quote: Option<char>,
    /// Whether it is an escaped character (Backslashed)
    is_escaped: bool,

    // Parenthesis
    /// Type of left parenthesis
    left_paren: Option<char>,
    /// Type of right parenthesis
    right_paren: Option<char>,
    /// Count of left parenthesis / Count of current layer
    paren_count: u32,
    /// Whether the current character is in string (For paren TokenType)
    is_string: bool,
    /// Whether the current character is in comment (For paren TokenType)
    is_comment: bool,

    /// Whether to allow semicolon at the next char(For minecraft array `[I;int, ...]`)
    allow_semicolon: bool,
    /// JMC macro factory
    macro_factory: Option<MacroFactoryInfo>,
    skip: usize,
}

impl Tokenizer {
    /// * `raw_string` - Raw string read from file/given from another tokenizer
    /// * `file_path_str` - Entire string read from current file
    /// * `expect_semicolon` - Whether to expect a semicolon at the end
    /// * `allow_semicolon` - Whether to allow last missing last semicolon, defaults to False
    pub fn new(
        raw_string: String,
        file_path_str: String,
        file_string: Option<String>,
        expect_semicolon: bool,
        allow_semicolon: bool,
    ) -> Result<Self, JMCError> {
        let mut tokenizer = Self {
            programs: vec![],
            line: 0,
            col: 0,
            state: None,
            token_str: String::new(),
            token_pos: None,
            keywords: vec![],
            list_of_keywords: vec![],
            raw_string: Rc::new(raw_string),
            file_string,
            file_path_str,
            quote: None,
            is_escaped: false,
            left_paren: None,
            right_paren: None,
            paren_count: 0,
            is_string: false,
            is_comment: false,
            allow_semicolon,
            macro_factory: None,
            skip: 0,
        };
        tokenizer.parse(expect_semicolon, false)?;
        Ok(tokenizer)
    }

    pub fn get_file_string(&self) -> &str {
        match &self.file_string {
            Some(file_string) => &file_string,
            None => &self.raw_string,
        }
    }

    /// Parse string
    ///
    /// * `string` - String to parse
    /// * `listne` - Current line
    /// * `costl` - Current column
    /// * `expect_semicolon` - Whether to expect a semicolon at the end
    /// * `allow_last_missing_semicolon` - Whether to allow last missing last semicolon, defaults to False
    /// * return - List of keywords(list of tokens)
    fn parse(
        &mut self,
        expect_semicolon: bool,
        allow_last_missing_semicolon: bool,
    ) -> Result<&Vec<Vec<Token>>, JMCError> {
        self.parse_chars(expect_semicolon)?;

        match self.state {
            Some(TokenType::String) => {
                return Err(JMCError::jmc_syntax_exception(
                    "String literal contains an unescaped linebreak".to_owned(),
                    None,
                    self,
                    true,
                    false,
                    true,
                    Some(
                        "If you intended to use multiple line, try multiline string '`'".to_owned(),
                    ),
                ));
            }
            Some(TokenType::Paren) => {
                let token_pos = match &self.token_pos {
                    Some(token_pos) => token_pos,
                    None => panic!("token_pos is None"),
                };
                assert!(!self.token_pos.is_none());
                let paren: String = match &self.left_paren {
                    Some(left_paren) => left_paren.to_string(),
                    None => "".to_owned(),
                };
                return Err(JMCError::jmc_syntax_exception(
                    "Bracket was never closed".to_owned(),
                    Some(&Token::new(
                        TokenType::Keyword,
                        token_pos.line,
                        token_pos.col,
                        paren,
                        None,
                        None,
                    )),
                    self,
                    false,
                    true,
                    false,
                    Some("This can be the result of unclosed string as well".to_owned()),
                ));
            }
            _ => {}
        }
        if expect_semicolon && (!self.keywords.is_empty() || !self.token_str.is_empty()) {
            if !self.token_str.is_empty() {
                self.append_token();
            }
            if allow_last_missing_semicolon {
                self.append_keywords();
            }
            return Err(JMCError::jmc_syntax_exception(
                "Expected semicolon(;)".to_owned(),
                Some(&self.keywords[self.keywords.len() - 1]),
                &self,
                true,
                true,
                false,
                None,
            ));
        }

        if !expect_semicolon {
            if !self.token_str.is_empty() {
                self.append_token();
            }
            if !self.keywords.is_empty() {
                self.append_keywords();
            }
        }
        Ok(&self.list_of_keywords)
    }

    fn parse_chars(&mut self, expect_semicolon: bool) -> Result<(), JMCError> {
        self.skip = 0;
        let raw_string = Rc::clone(&self.raw_string);
        for (i, ch) in raw_string.chars().enumerate() {
            // TODO: Try to implement this without cloning string
            if self.skip > 0 {
                self.skip -= 1;
                continue;
            }
            self.col += 1;
            if ch == re::SEMICOLON && self.state.is_none() && !expect_semicolon {
                return Err(JMCError::jmc_syntax_exception(
                    "Unexpected semicolon(;)".to_owned(),
                    None,
                    &self,
                    false,
                    true,
                    false,
                    None,
                ));
            }

            if ch == re::NEW_LINE {
                self.parse_newline(ch)?;
                continue;
            }

            if ch == re::SLASH
                && raw_string.chars().nth(i + 1).unwrap() == re::SLASH
                && self.state != Some(TokenType::Paren)
                && self.state != Some(TokenType::String)
            {
                self.skip = 1;
                if !self.token_str.is_empty() {
                    self.append_token();
                }
                self.state = Some(TokenType::Comment);
                continue;
            }

            match self.state {
                Some(TokenType::Keyword | TokenType::Operator) => {
                    if self.parse_keyword_and_operator(ch, expect_semicolon)? {
                        continue;
                    }
                }
                Some(TokenType::Paren) => {
                    if self.parse_paren(ch, expect_semicolon)? {
                        continue;
                    }
                }
                Some(TokenType::String) => self.parse_string(i, ch)?,
                Some(TokenType::Comment) => self.parse_comment(ch)?,
                None => self.parse_none(ch)?,
                _ => panic!("Invalid state"),
            }
        }
        Ok(())
    }

    fn parse_newline(&mut self, ch: char) -> Result<(), JMCError> {
        self.is_comment = false;
        match self.state {
            Some(TokenType::String) => {
                if self.quote == Some(quote::BACKTICK) {
                    self.token_str.push(ch);
                } else {
                    return Err(JMCError::jmc_syntax_exception(
                        "String literal contains unescaped line break".to_owned(),
                        None,
                        self,
                        false,
                        false,
                        true,
                        None,
                    ));
                }
            }
            Some(TokenType::Comment) => self.state = None,
            Some(TokenType::Keyword | TokenType::Operator) => {
                self.append_token();
            }
            Some(TokenType::Paren) => {
                self.token_str.push(ch);
            }
            _ => {}
        }
        self.line += 1;
        self.col = 0;
        Ok(())
    }
    fn unescape(ch: char) -> Result<char, ()> {
        match ch {
            'n' => Ok('\n'),
            't' => Ok('\t'),
            '?' => todo!(),
            _ => Err(()),
        }
    }
    fn parse_string(&mut self, i: usize, ch: char) -> Result<(), JMCError> {
        if ch == re::BACKSLASH {
            if i >= self.raw_string.len() {
                return Err(JMCError::jmc_syntax_exception(
                    "String literal contains unescaped line break".to_owned(),
                    None,
                    self,
                    false,
                    false,
                    true,
                    None,
                ));
            }
            self.skip = 1;
            match Self::unescape(self.raw_string.chars().nth(i + 1).unwrap()) {
                Ok(unescaped) => self.token_str.push(unescaped),
                Err(_) => {
                    self.token_str.push('\\');
                    self.token_str.push(ch)
                }
            }
            return Ok(());
        }
        if Some(ch) != self.quote {
            self.token_str.push(ch);
            return Ok(());
        }
        if ch == quote::BACKTICK {
            self.validate_multiline_string()?;
        }
        Ok(())
    }

    fn validate_multiline_string(&mut self) -> Result<(), JMCError> {
        let first_newline = self.raw_string.find('\n');
        let last_newline = self.raw_string.rfind('\n');
        let first_line: &str;
        let last_line: &str;
        match (first_newline, last_newline) {
            (None, None) => Err(JMCError::jmc_syntax_exception(
                "Expected newline after open backtick(`) for multiline string".to_owned(),
                None,
                self,
                false,
                false,
                false,
                None,
            )),
            (Some(first_newline), Some(last_newline)) => {
                if first_newline == last_newline {
                    return Err(JMCError::jmc_syntax_exception(
                        "Expected newline before close backtick(`) for multiline string".to_owned(),
                        None,
                        self,
                        false,
                        true,
                        false,
                        None,
                    ));
                }
                first_line = &self.raw_string[..first_newline];
                last_line = &self.raw_string[last_newline + 1..];
                if !first_line.is_empty() && !re::WHITESPACE.is_match(first_line) {
                    return Err(JMCError::jmc_syntax_exception(
                        format!(
                            "Expected whitespaces line after open backtick(`) (got {first_line:?})"
                        ),
                        None,
                        self,
                        false,
                        true,
                        false,
                        None,
                    ));
                }
                if !last_line.is_empty() && !re::WHITESPACE.is_match(last_line) {
                    return Err(JMCError::jmc_syntax_exception(
                        format!(
                            "Expected whitespaces line before open backtick(`) (got {last_line:?})"
                        ),
                        None,
                        self,
                        false,
                        true,
                        false,
                        None,
                    ));
                }
                Ok(())
            }
            _ => panic!("Unreachable"),
        }
    }

    fn parse_comment(&mut self, ch: char) -> Result<(), JMCError> {
        todo!()
    }

    fn parse_keyword_and_operator(
        &mut self,
        ch: char,
        expect_semicolon: bool,
    ) -> Result<bool, JMCError> {
        todo!()
    }

    fn parse_paren(&mut self, ch: char, expect_semicolon: bool) -> Result<bool, JMCError> {
        todo!()
    }

    fn parse_none(&mut self, ch: char) -> Result<(), JMCError> {
        todo!()
    }

    fn append_token(&mut self) {
        todo!()
    }

    fn append_keywords(&mut self) {
        todo!()
    }
}
