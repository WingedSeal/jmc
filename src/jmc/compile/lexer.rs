use std::{collections::HashSet, path::PathBuf};

use phf::{phf_map, phf_set};

use super::super::terminal::configuration::Configuration;

use super::datapack::Datapack;
use super::tokenizer::{Token, Tokenizer};

/// List of all possible vanilla json file types
static JSON_FILE_TYPES: phf::Set<&'static str> = phf_set! {
    "advancements",
    "dimension",
    "dimension_type",
    "loot_tables",
    "predicates",
    "recipes",
    "item_modifiers",
    "structures",
    "worldgen/biome",
    "worldgen/configured_carver",
    "worldgen/configured_feature",
    "worldgen/configured_surface_builder",
    "worldgen/density_function",
    "worldgen/flat_level_generator_preset",
    "worldgen/noise",
    "worldgen/noise_settings",
    "worldgen/placed_feature",
    "worldgen/processor_list",
    "worldgen/structure",
    "worldgen/structure_set",
    "worldgen/template_pool",
    "worldgen/world_preset",
    "trim_material",
    "trim_pattern",
    "chat_type",
    "damage_type",
};

/// Dictionary of JMC's custom file type that'll be automatically converted to vanilla ones
static JMC_JSON_FILE_TYPES: phf::Map<&'static str, &'static str> = phf_map! {
    "advancement" => "advancements",
    "loot_table" => "loot_tables",
    "structure" => "structures",
    "recipe" => "recipes",
};

type ConditionToken = Token;
/// Curly Parenthesis Token
type CodeBlockToken = Token;

#[derive(Debug)]
pub struct Lexer {
    if_else_box: Vec<(Option<ConditionToken>, Vec<CodeBlockToken>)>,
    do_while_box: Option<CodeBlockToken>,
    /// Tokenizer for load function
    load_tokenizer: Tokenizer,
    /// Set of path that's already imported
    imports: HashSet<PathBuf>,
    config: Configuration,
    datapack: Datapack,
}

impl Lexer {
    pub fn new(config: Configuration) {}
}
