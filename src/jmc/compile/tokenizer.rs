#![allow(dead_code)]

use crate::jmc::compile::utils::is_decorator;

use super::exception::JMCError;
use super::header::{Header, MacroFactory};
use std::collections::{HashMap, VecDeque};
use std::fmt::{Debug, Display};
use std::iter::Peekable;
use std::rc::Rc;

/// Array of string that, if a line starts with, should automatically terminate line on `{}` without semicolons
const TERMINATE_LINE: [&'static str; 10] = [
    "function", "class", "new", "schedule", "if", "else", "do", "while", "for", "switch",
];

const OPERATORS: [char; 13] = [
    '+', '-', '*', '/', '>', '<', '=', '%', ':', '!', '|', '&', '?',
];

#[derive(Eq, PartialEq, Debug, Clone, Copy, Default)]
pub enum TokenType {
    #[default]
    Keyword,
    Operator,
    ParenRound,
    ParenSquare,
    ParenCurly,
    String,
    Comma,
    Func,
}

#[derive(Eq, PartialEq, Debug)]
enum StateType {
    Keyword,
    Operator,
    Paren,
    ParenRound,
    ParenSquare,
    ParenCurly,
    String,
    Comment,
    Comma,
    None,
}
impl StateType {
    pub fn is_none(&self) -> bool {
        *self == Self::None
    }
    pub fn to_token_type(&self) -> TokenType {
        macro_rules! match_to_token_type {
            ($($x:ident), *) => {
                match self {
                    $(&Self::$x => TokenType::$x,)*
                    _ => panic!("invalid StateType")
                }
            };
        }
        match_to_token_type!(
            Keyword,
            Operator,
            ParenRound,
            ParenSquare,
            ParenCurly,
            String,
            Comma
        )
    }
}

impl Display for TokenType {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            TokenType::Keyword => write!(f, "Keyword"),
            TokenType::Operator => write!(f, "Operator"),
            TokenType::ParenRound => write!(f, "Round-Parentheses"),
            TokenType::ParenSquare => write!(f, "Square-Parentheses"),
            TokenType::ParenCurly => write!(f, "Curly-Parentheses"),
            TokenType::String => write!(f, "String Literal"),
            TokenType::Comma => write!(f, "Comma"),
            TokenType::Func => write!(f, "Function"),
        }
    }
}

#[derive(Debug, Clone, Default)]
pub struct Token {
    pub token_type: TokenType,
    pub line: u32,
    pub col: u32,
    pub string: String,
    pub _macro_length: u32,
    pub quote: char,
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
        debug_assert!(
            token.token_type != TokenType::ParenCurly
                || (token.string.starts_with("{") && token.string.ends_with("}"))
        );
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
        debug_assert!(
            token.token_type != TokenType::ParenCurly
                || (token.string.starts_with("{") && token.string.ends_with("}"))
        );
        token
    }

    /// Getting the length of the string in token(including quotation mark)
    pub fn length(&self) -> usize {
        match self.token_type {
            TokenType::String => {
                Tokenizer::unescape_str_force_quote(&self.string, self.quote).len()
            }
            _ => self.string.len(),
        }
    }

    /// Get self.string including quotation mark
    pub fn get_full_string(&self) -> String {
        if self.token_type != TokenType::String {
            return self.string.to_owned();
        }
        Tokenizer::unescape_str(&self.string, quote::SINGLE)
    }

    /// Get original self.string including quotation mark
    pub fn get_original_string(&self) -> String {
        assert_eq!(self.token_type, TokenType::String);
        let string: String = Tokenizer::unescape_str(&self.string, self.quote);
        if self.quote == quote::BACKTICK {
            return format!("`\n{0}\n`", &string[1..string.len() - 1]);
        }
        string
    }
}
#[derive(Debug, Default)]
struct Pos {
    pub line: u32,
    pub col: u32,
}

mod re {
    use once_cell::sync::Lazy;
    use regex::Regex;
    pub const NEW_LINE: char = '\n';

    pub const BACKSLASH: char = '\\';
    pub static WHITESPACE: Lazy<Regex> =
        Lazy::new(|| Regex::new(r"\s+").expect("the regex should not fail to compile"));
    pub static KEYWORD: Lazy<Regex> = Lazy::new(|| {
        Regex::new(r"[a-zA-Z0-9_\.\/\^\~]").expect("the regex should not fail to compile")
    });
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

fn get_paren_pair(left_paren: char) -> Result<char, ()> {
    match left_paren {
        paren::L_ROUND => Ok(paren::R_ROUND),
        paren::L_SQUARE => Ok(paren::R_SQUARE),
        paren::L_CURLY => Ok(paren::R_CURLY),
        _ => Err(()),
    }
}
#[derive(Debug)]
struct MacroFactoryInfo {
    pub name: String,
    pub macro_factory: Rc<MacroFactory>,
    /// Argument count
    pub arg_count: usize,
    pub pos: Pos,
}
#[derive(Debug)]
/// A class for converting string into tokens
pub struct Tokenizer {
    /// List of lines(list of tokens)
    pub programs: Vec<Vec<Token>>,
    /// Starts at 1
    pub line: u32,
    /// Starts at 1
    pub col: u32,
    /// Current TokenType
    state: StateType,
    /// Current string for token
    token_str: String,
    /// Position for creating token
    token_pos: Pos,
    /// Current list of tokens
    keywords: Vec<Token>,
    /// List of keywords(list_of_tokens)
    list_of_keywords: Vec<Vec<Token>>,

    /// Raw string read from file/given from another tokenizer
    raw_string: Rc<String>,
    /// Entire string read from current file
    file_string: Option<Rc<String>>,
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
    macro_factory_info: Option<MacroFactoryInfo>,
    /// Header shared between compilation
    header: Rc<Header>,
}

impl Clone for Tokenizer {
    fn clone(&self) -> Self {
        let file_string = match &self.file_string {
            Some(file_string) => Some(Rc::clone(&file_string)),
            None => None,
        };
        Self::new(
            &self.header,
            Rc::clone(&self.raw_string),
            self.file_path_str.clone(),
            file_string,
            self.allow_semicolon,
        )
    }
}

impl Tokenizer {
    /// * `raw_string` - Raw string read from file/given from another tokenizer
    /// * `file_path_str` - Entire string read from current file
    /// * `allow_semicolon` - Whether to allow last missing last semicolon, defaults to `false`
    pub fn new(
        header: &Rc<Header>,
        raw_string: Rc<String>,
        file_path_str: String,
        file_string: Option<Rc<String>>,
        allow_semicolon: bool,
    ) -> Self {
        Self {
            programs: vec![],
            line: 0,
            col: 0,
            state: StateType::None,
            token_str: String::new(),
            token_pos: Pos::default(),
            keywords: vec![],
            list_of_keywords: vec![],
            raw_string,
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
            macro_factory_info: None,
            header: Rc::clone(header),
        }
    }

    pub fn get_file_string(&self) -> &str {
        match &self.file_string {
            Some(file_string) => &file_string,
            None => &self.raw_string,
        }
    }

    /// * `raw_string` - Raw string read from file/given from another tokenizer
    /// * `file_path_str` - Entire string read from current file
    /// * `expect_semicolon` - Whether to expect a semicolon at the end
    /// * `allow_semicolon` - Whether to allow last missing last semicolon, defaults to `false`
    pub fn parse_raw_string(
        header: &Rc<Header>,
        raw_string: Rc<String>,
        file_path_str: String,
        file_string: Option<Rc<String>>,
        expect_semicolon: bool,
        allow_semicolon: bool,
    ) -> Result<Self, JMCError> {
        let mut tokenizer = Self::new(
            header,
            raw_string,
            file_path_str,
            file_string,
            allow_semicolon,
        );
        tokenizer.parse(&Rc::clone(&tokenizer.raw_string), expect_semicolon, false)?;
        Ok(tokenizer)
    }

    /// Parse string
    ///
    /// * `string` - String to parse
    /// * `expect_semicolon` - Whether to expect a semicolon at the end
    /// * `allow_last_missing_semicolon` - Whether to allow last missing last semicolon, defaults to False
    /// * return - List of keywords(list of tokens)
    fn parse(
        &mut self,
        string: &str,
        expect_semicolon: bool,
        allow_last_missing_semicolon: bool,
    ) -> Result<&Vec<Vec<Token>>, JMCError> {
        self.parse_chars(string, expect_semicolon)?;

        match self.state {
            StateType::String => {
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
            StateType::Paren => {
                let paren: String = match &self.left_paren {
                    Some(left_paren) => left_paren.to_string(),
                    None => "".to_owned(),
                };
                return Err(JMCError::jmc_syntax_exception(
                    "Bracket was never closed".to_owned(),
                    Some(&Token::new(
                        TokenType::Keyword,
                        self.token_pos.line,
                        self.token_pos.col,
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
                self.append_token()?;
            }
            if allow_last_missing_semicolon {
                self.append_keywords()?;
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
                self.append_token()?;
            }
            if !self.keywords.is_empty() {
                self.append_keywords()?;
            }
        }
        Ok(&self.list_of_keywords)
    }

    fn parse_chars(&mut self, string: &str, expect_semicolon: bool) -> Result<(), JMCError> {
        let mut string_iter = string.chars().peekable();
        while let Some(ch) = string_iter.next() {
            self.col += 1;
            if ch == re::SEMICOLON && self.state == StateType::None && !expect_semicolon {
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
                && string_iter.peek() == Some(&re::SLASH)
                && self.state != StateType::Paren
                && self.state != StateType::String
            {
                string_iter.next();
                if !self.token_str.is_empty() {
                    self.append_token()?;
                }
                self.state = StateType::Comment;
                continue;
            }
            if let StateType::Keyword | StateType::Operator = self.state {
                if self.parse_keyword_and_operator(ch, expect_semicolon)? {
                    continue;
                }
            }
            match self.state {
                StateType::Paren => self.parse_paren(&mut string_iter, ch, expect_semicolon)?,
                StateType::String => self.parse_string(&mut string_iter, ch)?,
                StateType::Comment => continue,
                StateType::None => self.parse_none(ch)?,
                _ => panic!("invalid state"),
            }
        }
        Ok(())
    }

    fn parse_newline(&mut self, ch: char) -> Result<(), JMCError> {
        self.is_comment = false;
        match self.state {
            StateType::String => {
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
            StateType::Comment => self.state = StateType::None,
            StateType::Keyword | StateType::Operator => {
                self.append_token()?;
            }
            StateType::Paren => {
                self.token_str.push(ch);
            }
            _ => {}
        }
        self.line += 1;
        self.col = 0;
        Ok(())
    }

    fn escape(ch: char) -> Result<char, ()> {
        match ch {
            'n' => Ok('\n'),
            'r' => Ok('\r'),
            't' => Ok('\t'),
            '\\' => Ok('\\'),
            '0' => Ok('\0'),
            '\'' => Ok('\''),
            '"' => Ok('"'),
            _ => Err(()),
        }
    }

    /// Unescape string and surround it by the most suited quote, prefering `prefered_quote` then return that with the prefered quote
    pub fn unescape_str(string: &str, prefered_quote: char) -> String {
        let choosen_quote;
        let single_quote_count = string.matches('\'').count();
        let double_quote_count = string.matches('\"').count();
        if single_quote_count > double_quote_count {
            choosen_quote = '"';
        } else if single_quote_count < double_quote_count {
            choosen_quote = '\'';
        } else {
            choosen_quote = prefered_quote
        }
        Self::unescape_str_force_quote(string, choosen_quote)
    }

    /// Unescape string and surround it by the chosen `forced_quote`
    fn unescape_str_force_quote(string: &str, mut forced_quote: char) -> String {
        const QUOTES: [char; 2] = ['\'', '"'];
        if !QUOTES.contains(&forced_quote) {
            forced_quote = '"'
        }
        let mut unescaped_string = forced_quote.to_string();
        for ch in string.chars().into_iter() {
            match Self::unescape(ch, forced_quote) {
                Some(unescaped_str) => unescaped_string.push_str(unescaped_str),
                None => unescaped_string.push(ch),
            }
        }
        unescaped_string.push(forced_quote);
        unescaped_string
    }

    fn unescape(ch: char, prefered_quote: char) -> Option<&'static str> {
        match ch {
            '\n' => Some("\\n"),
            '\r' => Some("\\r"),
            '\t' => Some("\\t"),
            '\\' => Some("\\\\"),
            '\0' => Some("\\0"),
            '\'' => {
                if prefered_quote == quote::SINGLE {
                    Some("\\'")
                } else {
                    Some("'")
                }
            }
            '"' => {
                if prefered_quote == quote::DOUBLE {
                    Some("\\\"")
                } else {
                    Some("\"")
                }
            }
            _ => None,
        }
    }

    fn parse_string(
        &mut self,
        raw_string_iter: &mut Peekable<impl Iterator<Item = char>>,
        ch: char,
    ) -> Result<(), JMCError> {
        if ch == re::BACKSLASH {
            let next_char: char = match raw_string_iter.peek() {
                Some(next_char) => *next_char,
                None => {
                    return Err(JMCError::jmc_syntax_exception(
                        "String literal contains unescaped line break".to_owned(),
                        None,
                        self,
                        false,
                        false,
                        true,
                        Some("You are currently trying to escape(\\) nothing.".to_owned()),
                    ));
                }
            };
            raw_string_iter.next();
            match Self::escape(next_char) {
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
            _ => panic!("first_newline and last_line have to be both None or Some"),
        }
    }

    /// Return `false` if it's not a keyword/operator anymore and the current char should be checked further
    fn parse_keyword_and_operator(
        &mut self,
        ch: char,
        expect_semicolon: bool,
    ) -> Result<bool, JMCError> {
        const NON_KEYWORD: [char; 7] = [
            quote::SINGLE,
            quote::DOUBLE,
            quote::BACKTICK,
            paren::L_CURLY,
            paren::L_ROUND,
            paren::L_SQUARE,
            re::COMMA,
        ];
        if ch.is_whitespace() || NON_KEYWORD.contains(&ch) {
            self.append_keywords()?;
            return Ok(false);
        }
        let is_operator = OPERATORS.contains(&ch);
        if self.state == StateType::Keyword && is_operator {
            self.append_token()?;
            self.token_pos = self.get_pos();
            self.state = StateType::Operator;
        } else if self.state == StateType::Operator && !is_operator && ch != re::SEMICOLON {
            self.append_token()?;
            self.token_pos = self.get_pos();
            self.state = StateType::Keyword;
        }

        if ch != re::SEMICOLON {
            self.token_str.push(ch);
            return Ok(true);
        }
        if expect_semicolon {
            self.append_token()?;
            return Ok(false);
        }
        if !self.allow_semicolon {
            return Err(JMCError::jmc_syntax_exception(
                "Unexpected semicolon(;)".to_owned(),
                None,
                self,
                false,
                true,
                false,
                None,
            ));
        }
        self.allow_semicolon = false;

        const MINECRAFT_ARRAY_TYPE: [&'static str; 3] = ["I", "B", "L"];
        if MINECRAFT_ARRAY_TYPE.contains(&self.token_str.as_str()) {
            self.token_str.push(ch);
            return Ok(true);
        }
        Err(JMCError::jmc_syntax_exception(
            "Unexpected semicolon(;)".to_owned(),
            None,
            self,
            false,
            true,
            false,
            None,
        ))
    }

    fn parse_paren(
        &mut self,
        raw_string_iter: &mut Peekable<impl Iterator<Item = char>>,
        ch: char,
        expect_semicolon: bool,
    ) -> Result<(), JMCError> {
        self.token_str.push(ch);
        if self.is_string {
            match ch {
                re::BACKSLASH => {
                    match raw_string_iter.next() {
                        Some(next) => self.token_str.push(next),
                        None => return Err(JMCError::jmc_syntax_exception(
                            "String literal contains an unescaped linebreak".to_owned(),
                            None,
                            self,
                            true,
                            false,
                            true,
                            Some(
                                "If you intended to use multiple line, try multiline string '`'"
                                    .to_owned(),
                            ),
                        )),
                    }
                }
                re::NEW_LINE => {
                    return Err(JMCError::jmc_syntax_exception(
                        "String literal contains an unescaped linebreak".to_owned(),
                        None,
                        self,
                        true,
                        false,
                        true,
                        Some(
                            "If you intended to use multiple line, try multiline string '`'"
                                .to_owned(),
                        ),
                    ));
                }
                _ if Some(ch) == self.quote => {
                    self.is_string = false;
                }
                _ => {}
            }
            return Ok(());
        }
        if self.is_comment {
            return Ok(());
        }

        match ch {
            _ if Some(ch) == self.left_paren => self.paren_count += 1,
            _ if Some(ch) == self.right_paren => {
                if self.paren_count != 0 {
                    self.paren_count -= 1;
                    return Ok(());
                }
                let mut is_paren_curly = false;
                match self.left_paren {
                    Some(paren::L_CURLY) => {
                        self.state = StateType::ParenCurly;
                        is_paren_curly = true;
                    }
                    Some(paren::L_ROUND) => self.state = StateType::ParenRound,
                    Some(paren::L_SQUARE) => self.state = StateType::ParenRound,
                    _ => panic!("self.left_paren shouldn't be None at this point"),
                }
                if is_paren_curly
                    && expect_semicolon
                    && self.should_terminate_line(0)
                    && (!self.is_shorten_if() || self.should_terminate_line(2))
                {
                    self.append_keywords()?;
                }
            }
            quote::SINGLE | quote::DOUBLE | quote::BACKTICK => {
                self.is_string = true;
                self.quote = Some(ch);
            }
            re::SLASH if raw_string_iter.peek() == Some(&re::SLASH) => self.is_comment = true,
            re::HASH if self.keywords.is_empty() => self.is_comment = true,
            _ => {}
        }
        Ok(())
    }

    fn parse_none(&mut self, ch: char) -> Result<(), JMCError> {
        match ch {
            quote::SINGLE | quote::DOUBLE | quote::BACKTICK => {
                self.token_str.push(ch);
                self.token_pos = self.get_pos();
                self.state = StateType::String;
                self.quote = Some(ch);
            }
            re::SEMICOLON => match &self.macro_factory_info {
                Some(macro_factory) => {
                    return Err(JMCError::jmc_syntax_warning(
                        format!(
                            "Expected a round bracket after macro factory({0})",
                            macro_factory.name
                        ),
                        None,
                        self,
                        false,
                        true,
                        false,
                        Some("Macro factory is a macro that acts like a function (requires parameter(s))".to_owned()),
                    ));
                }
                None => self.append_keywords()?,
            },
            paren::L_CURLY | paren::L_ROUND | paren::L_SQUARE => {
                self.token_str.push(ch);
                self.token_pos = self.get_pos();
                self.state = StateType::Paren;
                self.left_paren = Some(ch);
                self.right_paren =
                    Some(get_paren_pair(ch).expect("should only pair when it's paren"))
            }
            paren::R_CURLY | paren::R_ROUND | paren::R_SQUARE => {
                return Err(JMCError::jmc_syntax_exception(
                    format!("Unexpected closing bracket ({ch})"),
                    None,
                    self,
                    false,
                    false,
                    false,
                    None,
                ));
            }
            re::HASH if self.keywords.is_empty() => self.state = StateType::Comment,
            re::COMMA => {
                self.token_str.push(ch);
                self.token_pos = self.get_pos();
                self.state = StateType::Comma;
                self.append_token()?;
            }
            _ if OPERATORS.contains(&ch) => {
                self.token_str.push(ch);
                self.token_pos = self.get_pos();
                self.state = StateType::Operator;
            }
            // _ if ch.is_whitespace() => return Ok(()),
            _ => {
                self.token_str.push(ch);
                self.token_pos = self.get_pos();
                self.state = StateType::Keyword;
            }
        }
        Ok(())
    }

    /// Append keywords into list_of_keywords
    fn append_keywords(&mut self) -> Result<(), JMCError> {
        if self.keywords.len() == 0 {
            Err(JMCError::jmc_syntax_warning(
                "Unnecessary semicolon(;)".to_owned(),
                None,
                self,
                false,
                true,
                false,
                None,
            ))
        } else {
            self.list_of_keywords
                .push(std::mem::replace(&mut self.keywords, vec![]));
            Ok(())
        }
    }

    /// Append the current token into self.keywords
    fn append_token(&mut self) -> Result<(), JMCError> {
        debug_assert!(!self.state.is_none());
        let new_token = Token::new(
            self.state.to_token_type(),
            self.token_pos.line,
            self.token_pos.col,
            std::mem::take(&mut self.token_str),
            None,
            self.quote,
        );
        let token_pos = std::mem::take(&mut self.token_pos);
        let is_macro = new_token.token_type == TokenType::Keyword
            && self.header.macros.contains_key(&new_token.string);
        if is_macro {
            let (macro_factory, arg_count) = self
                .header
                .macros
                .get(&new_token.string)
                .expect("should exist in macro due to contains_key check");
            if *arg_count == 0 {
                self.keywords
                    .append(&mut macro_factory.call(&[], token_pos.line, token_pos.col))
            } else {
                self.macro_factory_info = Some(MacroFactoryInfo {
                    name: new_token.string,
                    macro_factory: Rc::clone(macro_factory),
                    arg_count: *arg_count,
                    pos: token_pos,
                })
            }
        } else if self.macro_factory_info.is_some() {
            let macro_factory_info = std::mem::replace(&mut self.macro_factory_info, None)
                .expect("macro_factory_info shouldn't be none, it was checked with is_some");
            if new_token.token_type != TokenType::ParenRound {
                return Err(JMCError::jmc_syntax_warning(
                    format!(
                        "Expect round bracket after macro factory({})",
                        macro_factory_info.name
                    ),
                    Some(&new_token),
                    self,
                    false,
                    false,
                    false,
                    Some(format!(
                        "Macro factory({0}) requires {1} argument. Try '{0}({2})'",
                        macro_factory_info.name,
                        macro_factory_info.arg_count,
                        (1..macro_factory_info.arg_count + 1)
                            .map(|i| format!("arg{i}"))
                            .collect::<Vec<String>>()
                            .join(", ")
                    )),
                ));
            }
            let mut arg_tokens: Vec<Token> = vec![];
            let (args, kwargs) = self.clone().parse_func_args_round(&new_token)?;
            for arg in args {
                if arg.len() > 1 {
                    arg_tokens.push(arg[0].clone())
                } else {
                    arg_tokens.push(self.merge_tokens(&arg[0], &arg[1..]))
                }
            }
            if !kwargs.is_empty() {
                return Err(JMCError::jmc_syntax_warning(
                    format!(
                        "Macro factory does not support keyword argument ({}=)",
                        kwargs
                            .keys()
                            .next()
                            .expect("kwargs shouldn't be empty due to is_empty check")
                    ),
                    Some(&new_token),
                    self,
                    true,
                    false,
                    true,
                    None,
                ));
            }
            if arg_tokens.len() != macro_factory_info.arg_count {
                return Err(JMCError::jmc_syntax_warning(
                    format!(
                        "This Macro factory ({0}) expect {1} arguments (got {2})",
                        macro_factory_info.name,
                        macro_factory_info.arg_count,
                        arg_tokens.len()
                    ),
                    Some(&new_token),
                    self,
                    true,
                    false,
                    true,
                    None,
                ));
            }
            self.keywords
                .append(&mut macro_factory_info.macro_factory.call(
                    &arg_tokens,
                    token_pos.line,
                    token_pos.col,
                ))
        } else {
            self.keywords.push(new_token);
        }
        self.state = StateType::None;
        Ok(())
    }

    fn merge_tokens(&self, token: &Token, other_tokens: &[Token]) -> Token {
        let token_type = match token.token_type {
            TokenType::Operator => TokenType::Keyword,
            other => other,
        };
        let mut string = token.string.clone();
        for other_token in other_tokens {
            string.push_str(&other_token.string)
        }
        Token::new(token_type, token.line, token.col, string, None, None)
    }

    fn should_terminate_line(&self, start_at: usize) -> bool {
        if self.keywords.len() < 2 {
            return false;
        }
        let keyword = self.keywords[start_at].string.as_str();
        let is_in_terminate_line = TERMINATE_LINE.contains(&keyword);
        const RUN_EXPAND: [&'static str; 2] = ["run", "expand"];
        let is_run_expand = keyword == "execute"
            && RUN_EXPAND.contains(&self.keywords[self.keywords.len() - 2].string.as_str());
        let is_a_decorator = is_decorator(keyword);
        let is_return_run = keyword.len() > 3
            && self.keywords[self.keywords.len() - 3].string.as_str() == "return"
            && self.keywords[self.keywords.len() - 2].string.as_str() == "run";
        is_in_terminate_line || is_run_expand || is_a_decorator || is_return_run
    }

    fn is_shorten_if(&self) -> bool {
        if self.keywords.len() < 3 {
            return false;
        }
        let is_if = self.keywords[0].string.as_str() == "if";
        let is_not_expand = self.keywords[2].string != "expand"
            && self.keywords[2].token_type != TokenType::ParenCurly;
        is_if && is_not_expand
    }

    fn parse_func_args_round(
        &mut self,
        token: &Token,
    ) -> Result<(Vec<Vec<Token>>, HashMap<String, Vec<Token>>), JMCError> {
        self.parse_func_args(token, TokenType::ParenRound)
    }

    fn parse_func_args(
        &mut self,
        token: &Token,
        token_type: TokenType,
    ) -> Result<(Vec<Vec<Token>>, HashMap<String, Vec<Token>>), JMCError> {
        if token.token_type != token_type {
            return Err(JMCError::jmc_syntax_exception(
                format!("Expected {token_type} (got {0})", token.token_type),
                Some(token),
                self,
                false,
                false,
                false,
                None,
            ));
        }
        self.line = token.line;
        self.col = token.col + 1;
        self.parse(&token.string, false, false)?;
        let keywords: Vec<Token> = self.programs.swap_remove(0);
        let mut args: Vec<Vec<Token>> = vec![];
        let mut kwargs: HashMap<String, Vec<Token>> = HashMap::new();
        let (comma_separated_tokens, comma_tokens) = Self::find_token(keywords, ",", false);
        if comma_separated_tokens[comma_separated_tokens.len() - 1].is_empty() {
            return Err(JMCError::jmc_syntax_exception(
                "Unexpected comma at the end of function arguments".to_owned(),
                Some(&comma_tokens[comma_tokens.len() - 1]),
                self,
                false,
                true,
                false,
                None,
            ));
        }
        // List of tokens between commas
        for (i, mut comma_separated_token) in comma_separated_tokens.into_iter().enumerate() {
            // TODO: find if remove(0) or vecdeque is faster?
            if comma_separated_token.is_empty() {
                return Err(JMCError::jmc_syntax_exception(
                    "Unexpected comma in function arguments".to_owned(),
                    Some(&comma_tokens[i]),
                    self,
                    false,
                    true,
                    false,
                    None,
                ));
            }
            if comma_separated_token.len() > 1
                && ["=", "=+", "=-"].contains(&comma_separated_token[1].string.as_str())
            {
                let key = comma_separated_token.remove(0);
                // .expect("comma_separated_token should have a length of 2 or more");
                let equal_token = comma_separated_token.remove(0);
                // .expect("comma_separated_token should have a length of 2 or more");
                if comma_separated_token.len() == 2 {
                    return Err(JMCError::jmc_syntax_exception(
                        "Expected keyword argument after '=' in function arguments".to_owned(),
                        Some(&equal_token),
                        self,
                        false,
                        true,
                        false,
                        None,
                    ));
                }
                let mut value: Vec<Token> =
                    self.parse_func_arg(Vec::from(comma_separated_token), false, false)?;
                if let "=+" | "=-" = equal_token.string.as_str() {
                    let mut tmp_value = VecDeque::from(value);
                    let mut string = equal_token.string;
                    string.remove(0); // TODO
                    tmp_value.push_front(Token::new(
                        equal_token.token_type,
                        equal_token.line,
                        equal_token.col + 1,
                        string,
                        Some(equal_token._macro_length),
                        Some(equal_token.quote),
                    ));
                    value = Vec::from(tmp_value);
                }
                if kwargs.contains_key(&key.string) {
                    return Err(JMCError::jmc_syntax_exception(
                        format!("Duplicated key({})", key.string),
                        Some(&key),
                        self,
                        false,
                        true,
                        false,
                        None,
                    ));
                }
                kwargs.insert(key.string, value);
                continue;
            }
            args.push(self.parse_func_arg(comma_separated_token, !kwargs.is_empty(), false)?)
        }
        Ok((args, kwargs))
    }

    /// Parse an argument in function arguments (Used in parse_func_args)
    ///
    /// * `tokens` - List of tokens
    /// * `has_kwargs` - Whether Kwargs is empty to see if it should return an error
    /// * `is_nbt` - Whether it is an NBT/JSobject (If false, it's a function argument), defaults to `false`
    /// * return - Tokens to be pushed to 'args' or 'kwargs'
    fn parse_func_arg(
        &self,
        tokens: Vec<Token>,
        has_kwargs: bool,
        is_nbt: bool,
    ) -> Result<Vec<Token>, JMCError> {
        if let TokenType::Keyword | TokenType::Operator = tokens[0].token_type {
            if tokens.len() != 1 {
                return Ok(tokens);
            }
        }
        // TODO: change .contains to if let
        let where_ = if is_nbt {
            "JSObject/NBT"
        } else {
            "function argument"
        };
        if tokens.len() > 1 {
            if tokens[0].string == "()" && tokens[1].string == "=>" {
                if tokens.len() < 3 {
                    return Err(JMCError::jmc_syntax_exception(
                        "Expected curly bracket after '()=>' (got nothing)".to_owned(),
                        Some(&tokens[1]),
                        self,
                        false,
                        true,
                        false,
                        None,
                    ));
                }
                if tokens[2].token_type != TokenType::ParenCurly {
                    return Err(JMCError::jmc_syntax_exception(
                        format!(
                            "Expected curly bracket after '()=>' (got {0})",
                            tokens[2].token_type
                        ),
                        Some(&tokens[2]),
                        self,
                        false,
                        true,
                        false,
                        None,
                    ));
                }
                if tokens.len() > 3 {
                    return Err(JMCError::jmc_syntax_exception(
                        "Unexpected token after arrow function '()=>{}'".to_owned(),
                        Some(&tokens[3]),
                        self,
                        false,
                        true,
                        false,
                        None,
                    ));
                }
                let new_token: Token = tokens
                    .into_iter()
                    .nth(2)
                    .expect("tokens.len() should be larger than 2");
                return Ok(vec![Token::new(
                    TokenType::Func,
                    new_token.line,
                    new_token.col + 1,
                    new_token.string,
                    Some(new_token._macro_length),
                    Some(new_token.quote),
                )]);
            }
            if tokens[0].token_type == TokenType::ParenRound
                && tokens[0].token_type == TokenType::Operator
            {
                return Ok(tokens);
            }
            return Err(JMCError::jmc_syntax_exception(
                format!(
                    "Unexpected {} after {} in {where_}",
                    tokens[1].token_type, tokens[0].token_type
                ),
                Some(&tokens[1]),
                self,
                false,
                true,
                false,
                Some("You may have missed a comma".to_owned()),
            ));
        }
        if tokens[0].string == (if is_nbt { ":" } else { "=" }) {
            return Err(JMCError::jmc_syntax_exception(
                format!("Empty key in {where_}"),
                Some(&tokens[0]),
                self,
                false,
                true,
                false,
                None,
            ));
        }
        if has_kwargs {
            return Err(JMCError::jmc_syntax_exception(
                "Positional argument follows keyword argument".to_owned(),
                Some(&tokens[0]),
                self,
                false,
                true,
                false,
                Some("There's no way to tell which value belong to which key, try rearranging arguments. Arguments without '=' should come first.".to_owned()),
            ));
        }
        Ok(tokens)
    }

    /// Split list of tokens by token that match the string.
    ///
    /// * `tokens` - List of token
    /// * `string` - String to match for splitting
    /// * `allow_string_token` - Whether to allow string token, defaults to `false`
    /// * return - List of list of tokens and List of comma tokens
    ///
    /// # Examples
    ///
    /// `find_token([a,b,c,d], b.string) == ([[a],[c,d]], [b])`
    fn find_token(
        tokens: Vec<Token>,
        string: &str,
        allow_string_token: bool,
    ) -> (Vec<Vec<Token>>, Vec<Token>) {
        let mut result: Vec<Vec<Token>> = vec![];
        let mut token_array: Vec<Token> = vec![];
        let mut splitter_array: Vec<Token> = vec![];
        for token in tokens {
            let is_append_result: bool;
            if allow_string_token {
                is_append_result = token.string == string;
            } else {
                is_append_result = token.string == string && token.token_type != TokenType::String;
            }
            if is_append_result {
                splitter_array.push(token);
                result.push(std::mem::take(&mut token_array));
            } else {
                token_array.push(token)
            }
        }
        (result, splitter_array)
    }

    #[inline]
    fn get_pos(&self) -> Pos {
        Pos {
            line: self.line,
            col: self.col,
        }
    }
}

#[cfg(test)]
mod token_tests {
    use super::*;

    #[test]
    fn test_get_full_string() {
        assert_eq!(
            Token::new(
                TokenType::Keyword,
                1,
                1,
                "KEYWORD_TOKEN".to_owned(),
                None,
                None,
            )
            .get_full_string(),
            "KEYWORD_TOKEN"
        );
        assert_eq!(
            Token::new(
                TokenType::String,
                1,
                1,
                "STRING_TOKEN".to_owned(),
                None,
                Some('"'),
            )
            .get_full_string(),
            "'STRING_TOKEN'"
        );
        assert_eq!(
            Token::new(
                TokenType::String,
                1,
                1,
                "'STRING_TOKEN'".to_owned(),
                None,
                Some('"'),
            )
            .get_full_string(),
            "\"'STRING_TOKEN'\""
        );
        assert_eq!(
            Token::empty(TokenType::Keyword, "KEYWORD_TOKEN".to_owned()).get_full_string(),
            "KEYWORD_TOKEN"
        );
    }
}

#[cfg(test)]
mod tokenizer_tests {
    use super::*;

    #[test]
    fn test_unescape_string() {
        assert_eq!(
            Tokenizer::unescape_str("\n\t\r TEST \"\"'''", '\''),
            r#""\n\t\r TEST \"\"'''""#
        )
    }

    #[test]
    #[ignore = "waiting for tokenizer"]
    fn test_escape() {
        assert_eq!(
            Tokenizer::new(
                &Rc::new(Header::default()),
                Rc::new(r#""\n\t\r TEST \"\"'''""#.to_owned()),
                String::new(),
                None,
                false
            )
            .programs[0][0]
                .string,
            "\n\t\r TEST \"\"'''"
        )
    }
}
