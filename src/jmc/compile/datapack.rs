use std::{
    collections::{HashMap, HashSet},
    rc::Rc,
};

use super::super::terminal::configuration::Configuration;

use super::{
    datapack_data::Data,
    lexer::Lexer,
    pack_version::PackVersion,
    tokenizer::{Token, Tokenizer},
};

type PrivateType = String;
type FunctionName = String;
type JsonName = String;
type PrivateName = String;
type ScoreboardName = String;
type ScoreboardCriteria = String;
type Command = String;
type TokenInfo<'header> = (Token, Rc<Tokenizer<'header>>);

#[derive(Debug)]
pub struct Datapack<'header, 'config, 'lexer> {
    /// Datapack's version details
    pub version: PackVersion,

    pub config: &'config Configuration,
    /// Set of integers going to be used in scoreboard
    pub ints: HashSet<i64>,
    /// Map of function name and a Function object
    pub functions: HashMap<FunctionName, McFunction>,
    /// Map of of function name that is called by user and its coresponding token and tokenizer
    pub functions_called: HashMap<FunctionName, TokenInfo<'header>>,
    /// Map of json name and json body defined by user
    pub jsons: HashMap<JsonName, serde_json::Value>,
    /// Map of function's group name and (Map of function name and a Function object)
    pub private_functions: HashMap<PrivateName, HashMap<FunctionName, McFunction>>,
    /// Minecraft scoreboards that are going to be created
    pub scoreboards: HashMap<ScoreboardName, ScoreboardCriteria>,
    /// Output list of commands for load
    pub loads: Vec<Command>,
    /// Output list of commands for tick
    pub ticks: Vec<Command>,
    /// Output list of commands at the end of load
    pub after_loads: Vec<Command>,
    /// Output list of commands at the end of tick
    pub after_ticks: Vec<Command>,
    /// Output list of commands at the end of any function
    pub after_func: HashMap<FunctionName, Vec<Command>>,
    /// Output list of token responsible for adding after_func
    pub after_func_token: HashMap<FunctionName, TokenInfo<'header>>,
    /// Datapack's namespace
    pub namespace: &'config str,
    /// Used JMC command that's for one time call only
    pub used_command: HashMap<String, String>,
    /// Lexer object
    pub lexer: Option<&'lexer mut Lexer<'header, 'config, 'lexer>>,
    /// Extra information that can be shared across all JMC function
    pub data: Data,
    /// Map of mcfunction or json path and it's first defined token and tokenizer
    pub defined_file_pos: HashMap<String, TokenInfo<'header>>,
    /// Map of lazy function name and PreFunction object
    pub lazy_func: HashMap<FunctionName, PreMcFunction>,
}

impl<'header, 'config, 'lexer> Datapack<'header, 'config, 'lexer> {
    pub fn new(config: &'config Configuration) -> Self {
        Self {
            version: config.pack_version,
            namespace: &config.namespace,
            config,
            // Lexer shall be a dangling reference, hence it must be initialzed
            // right after the initialization of Datapack. If you fail to do this,
            // you deserve whatever happens to you.
            lexer: None,
            ints: HashSet::new(),
            functions: HashMap::new(),
            functions_called: HashMap::new(),
            jsons: HashMap::new(),
            private_functions: HashMap::new(),
            scoreboards: HashMap::new(),
            loads: vec![],
            ticks: vec![],
            after_loads: vec![],
            after_ticks: vec![],
            after_func: HashMap::new(),
            after_func_token: HashMap::new(),
            used_command: HashMap::new(),
            data: Data::default(),
            defined_file_pos: HashMap::new(),
            lazy_func: HashMap::new(),
        }
    }
}

#[derive(Debug)]
pub struct McFunction {}

impl McFunction {
    pub fn extend(&self, command: Vec<String>) {
        todo!()
    }
}

#[derive(Debug)]
pub struct PreMcFunction {}
