use std::{
    cell::UnsafeCell,
    collections::{HashMap, HashSet},
    path::PathBuf,
    time::SystemTime,
};

use super::tokenizer::Token;

#[derive(Debug)]
/// Store information about how to convert
pub struct MacroFactory {}

impl MacroFactory {
    pub fn call(&self, tokens: &[Token], line: u32, col: u32) -> Vec<Token> {
        todo!()
    }
}

/// Struct containing all information shared in a compilation
#[derive(Debug, Default)]
pub struct Header {
    inner: UnsafeCell<HeaderInner>,
}

impl Header {
    pub fn get(&self) -> &mut HeaderInner {
        unsafe { &mut *self.inner.get() }
    }
    pub fn into_inner(self) -> HeaderInner {
        self.inner.into_inner()
    }
}

#[derive(Debug, Default)]
/// Struct containing all information shared in a compilation
pub struct HeaderInner {
    /// Set of files that was already read (to prevent reading the same file multiple times
    pub file_read: HashSet<PathBuf>,
    /// Map of keyword to replace and tuple of (macro factory function and its amount of argument
    pub macros: HashMap<String, (MacroFactory, usize)>,
    /// Map of text to replace and number to replace with, used in Hardcode.calc, EVAL, etc.
    pub number_macros: HashMap<String, String>,
    /// List of mcfunction comments to be placed at the end of files
    pub credits: Vec<String>,
    /// Whether to allow jmc to take control over minecraft namespace
    pub namespace_overrides: HashSet<String>,
    /// List of extra command(first arguments) to allow
    pub commands: HashSet<String>,
    /// List of extra condition(`execute if` subcommands) to allow
    pub conditions: HashSet<String>,
    /// All path that JMC will not remove
    pub statics: HashSet<PathBuf>,
    /// List of exception to command(first arguments) to ignore
    pub dels: HashSet<String>,
    /// Rust functions to run before building datapack
    pub post_process: Vec<fn(String)>, // TODO: change string to Datapack class
    /// SystemTime when the datapack finish compiling
    pub finished_compiled_time: Option<SystemTime>,
    /// Whether hand pack.mcmeta to user
    pub nometa: bool,
}

impl HeaderInner {
    /// Add path to file_read
    #[inline]
    pub fn add_file_read(&mut self, path: PathBuf) {
        self.file_read.insert(path);
    }

    #[inline]
    /// Check if header is already in file_read
    pub fn is_header_already_exist(&self, path: &PathBuf) -> bool {
        self.file_read.contains(path)
    }
}
