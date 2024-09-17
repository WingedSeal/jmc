#![allow(dead_code)]

use std::error::Error;
use std::path::PathBuf;
use std::ptr::NonNull;

use super::tokenizer::Token;
use super::tokenizer::Tokenizer;
use JMCErrorType::*;

fn create_error_msg(
    message: String,
    token: Option<&Token>,
    tokenizer: &Tokenizer,
    is_length_include_col: bool,
    is_display_col_length: bool,
    is_entire_line: bool,
    suggestion: Option<String>,
    overide_file_str: Option<fn(&str) -> String>,
) -> String {
    let string: String;
    let length: usize;
    let mut col: usize;
    let mut line: usize;
    match token {
        Some(token) => {
            string = token.get_original_string();
            length = token.length();
            col = token.col as usize;
            line = token.line as usize;
        }
        None => {
            string = "".to_owned();
            length = 1;
            col = tokenizer.col as usize;
            line = tokenizer.line as usize;
        }
    }
    let mut display_line = line;
    let mut display_col = col;
    let newline_count = string.matches('\n').count();
    let char_count_since_last_newline = length
        - match string.rfind('\n') {
            Some(count) => count,
            None => length,
        };

    if is_length_include_col {
        if string.contains('\n') {
            line += newline_count;
            col = char_count_since_last_newline;
        } else {
            col += length;
        }
        display_col += 1;
    }

    if is_display_col_length {
        if string.contains('\n') {
            display_line += newline_count;
            display_col = char_count_since_last_newline + 1;
        } else {
            display_col += length;
        }
    } else {
        display_col += 1;
    }

    let msgs: Vec<&str> = tokenizer.get_file_string().lines().collect();
    let max_space = (display_line + 1).to_string().len();
    let line_;
    match overide_file_str {
        Some(overide_file_str) => {
            line_ = overide_file_str(msgs[display_line - 1]);
        }
        None => line_ = msgs[display_line - 1].to_string(),
    }
    let mut final_msg;
    if is_entire_line {
        let tab_count = line_.matches('\t').count();
        final_msg = format!(
            "In {0}
{message} at line {line}.
{1}{2} |{3}
{4}{5} |{6}
{7}{8}
{9} |{10}
",
            relative_file_name(&tokenizer.file_path_str, Some(line as u32), None),
            display_line - 1,
            " ".repeat(max_space - (display_line - 1).to_string().len()),
            if display_line > 1 {
                msgs[display_line - 2].replace('\t', "    ")
            } else {
                "".to_owned()
            },
            display_line,
            " ".repeat(max_space - (display_line).to_string().len()),
            line_.replace('\t', "    "),
            " ".repeat(col + max_space + 3 * tab_count + 1),
            "^".repeat(line_.len() - col + 1),
            display_line + 1,
            if display_line < msgs.len() {
                msgs[display_line].replace('\t', "    ")
            } else {
                "".to_owned()
            }
        )
    } else {
        let tab_count = line_[0..col - 1].matches('\t').count();
        final_msg = format!(
            "In {0}
{message} at line {line} col {col}.
{1}{2} |{3}
{4}{5} |{6}
{7}{8}
{9} |{10}
",
            relative_file_name(
                &tokenizer.file_path_str,
                Some(line as u32),
                Some(col as u32)
            ),
            display_line - 1,
            " ".repeat(max_space - (display_line - 1).to_string().len()),
            if display_line > 1 {
                msgs[display_line - 2].replace('\t', "    ")
            } else {
                "".to_owned()
            },
            display_line,
            " ".repeat(max_space - (display_line).to_string().len()),
            line_.replace('\t', "    "),
            " ".repeat(col + max_space + 3 * tab_count + 1),
            "^".repeat(display_col - col),
            display_line + 1,
            if display_line < msgs.len() {
                msgs[display_line].replace('\t', "    ")
            } else {
                "".to_owned()
            }
        )
    }
    if let Some(suggestion) = suggestion {
        final_msg.push_str(&suggestion);
    }
    final_msg
}

pub fn relative_file_name(file_name: &str, line: Option<u32>, col: Option<u32>) -> String {
    let file_path = PathBuf::from(file_name);
    let cwd = std::env::current_dir().expect("Current directory should not fail");
    if !file_path.starts_with(&cwd) {
        return file_name.to_owned();
    }
    let mut file_name: String = file_path
        .strip_prefix(&cwd)
        .expect("file_name should be relative to cwd due to recent starts_with check")
        .to_str()
        .expect("path is read from a jmc file which must be a UTF-8 since it's a valid rust String")
        .to_owned();
    if let Some(line) = line {
        file_name.push_str(format!(":{line}").as_str());
    }
    if let Some(col) = col {
        file_name.push_str(format!(":{col}").as_str());
    }
    file_name
}

#[derive(Debug)]
pub enum JMCErrorType {
    EvaluationException,
    HeaderFileNotFoundError,
    HeaderDuplicatedMacro,
    HeaderSyntaxException,
    JMCSyntaxException,
    JMCSyntaxWarning,
    MinecraftSyntaxWarning,
    MinecraftVersionTooLow,
    JMCFileNotFound,
    JMCDecodeJSONError,
}

#[derive(Debug)]
pub struct JMCError {
    pub error_type: JMCErrorType,
    pub msg: String,
}
impl JMCError {
    pub fn evaluation_exception(string: String) -> Self {
        let msg = format!("Unable to evaluate expression '{string}'");
        Self {
            error_type: EvaluationException,
            msg,
        }
    }

    pub fn jmc_file_not_found(msg: String) -> Self {
        Self {
            error_type: JMCFileNotFound,
            msg,
        }
    }

    pub fn header_file_not_found_error(path: &PathBuf) -> Self {
        let msg = format!(
            "Header file not found: {0}",
            path.to_str().expect(
                "path is read from a jmc file which must be a UTF-8 since it's a valid rust String"
            )
        );
        Self {
            error_type: HeaderFileNotFoundError,
            msg,
        }
    }
    pub fn header_duplicated_macro(
        message: String,
        file_name: String,
        line: u32,
        line_str: String,
    ) -> Self {
        let msg = format!(
            "In {0}\n{message} at line {line}\n{line_str}",
            relative_file_name(&file_name, Some(line), None)
        );
        Self {
            error_type: HeaderDuplicatedMacro,
            msg,
        }
    }

    pub fn header_syntax_exception(
        message: String,
        file_name: String,
        line: u32,
        line_str: String,
        suggestion: Option<String>,
    ) -> Self {
        let mut msg = format!(
            "In {0}\n{message} at line {line}\n{line_str}",
            relative_file_name(&file_name, Some(line), None)
        );
        if let Some(suggestion) = suggestion {
            msg.push_str(suggestion.as_str());
        }
        Self {
            error_type: HeaderSyntaxException,
            msg,
        }
    }

    /// Invalid syntax for JMC
    ///
    /// * `is_length_include_col` - should defaults to `false`
    /// * `is_display_col_length` - should defaults to `true`
    /// * `is_entire_line` - should defaults to `false`
    pub fn jmc_syntax_exception(
        message: String,
        token: Option<&Token>,
        tokenizer: &Tokenizer,
        is_length_include_col: bool,
        is_display_col_length: bool,
        is_entire_line: bool,
        suggestion: Option<String>,
    ) -> Self {
        let msg = create_error_msg(
            message,
            token,
            tokenizer,
            is_length_include_col,
            is_display_col_length,
            is_entire_line,
            suggestion,
            None,
        );
        Self {
            error_type: JMCSyntaxException,
            msg,
        }
    }

    /// Warning about JMC syntax but still get treated like an error
    ///
    /// * `is_length_include_col` - should defaults to `false`
    /// * `is_display_col_length` - should defaults to `true`
    /// * `is_entire_line` - should defaults to `false`
    pub fn jmc_syntax_warning(
        message: String,
        token: Option<&Token>,
        tokenizer: &Tokenizer,
        is_length_include_col: bool,
        is_display_col_length: bool,
        is_entire_line: bool,
        suggestion: Option<String>,
    ) -> Self {
        let msg = create_error_msg(
            message,
            token,
            tokenizer,
            is_length_include_col,
            is_display_col_length,
            is_entire_line,
            suggestion,
            None,
        );
        Self {
            error_type: JMCSyntaxWarning,
            msg,
        }
    }

    /// Warning about minecraft syntax but still get treated like an error
    ///
    /// * `is_length_include_col` - should defaults to `false`
    /// * `is_display_col_length` - should defaults to `true`
    /// * `is_entire_line` - should defaults to `false`
    pub fn minecraft_syntax_warning(
        message: String,
        token: Option<&Token>,
        tokenizer: &Tokenizer,
        is_length_include_col: bool,
        is_display_col_length: bool,
        is_entire_line: bool,
        suggestion: Option<String>,
    ) -> Self {
        let msg = create_error_msg(
            message,
            token,
            tokenizer,
            is_length_include_col,
            is_display_col_length,
            is_entire_line,
            suggestion,
            None,
        );
        Self {
            error_type: MinecraftSyntaxWarning,
            msg,
        }
    }

    /// pack_format is too low for the feature
    pub fn minecraft_version_too_low(
        pack_format: super::pack_version::PackFormat,
        token: Option<&Token>,
        tokenizer: &Tokenizer,
        suggestion: Option<String>,
    ) -> Self {
        let msg = create_error_msg(
            format!("Datapack's pack_format is too outdated for this feature. Expected pack_format of {pack_format} or higher"), 
            token, 
            tokenizer, 
            false, 
            true, 
            false, 
            suggestion, 
            None,
        );
        Self {
            error_type: MinecraftVersionTooLow,
            msg,
        }
    }

    pub fn jmc_decode_json_error(
        error: serde_json::Error,
        token: &Token,
        tokenizer: &Tokenizer
    ) -> Self {
        let line = token.line + error.line() as u32 - 1;
        let col = if token.line == line {
            token.col + error.column() as u32 - 1
        } else {
            error.column() as u32
        };
        
        let msg = create_error_msg(error.to_string(), Some(token), tokenizer, false, true, false, None, None);
        // FIXME: figure out how to handle the error msg
        Self {
            error_type: JMCDecodeJSONError,
            msg,
        }
    }

}
