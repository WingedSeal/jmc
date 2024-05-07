use super::{
    exception::JMCError,
    tokenizer::{Token, Tokenizer},
};

pub type PackFormat = u32;

#[derive(Debug, Copy, Clone, PartialEq, Eq, PartialOrd, Ord)]
/// Class containing information about pack_format
struct PackVersion {
    pack_format: PackFormat,
}

impl PackVersion {
    pub fn new(pack_format: PackFormat) -> Self {
        Self { pack_format }
    }

    /// Raise MinecraftVersionTooLow when pack_format is too low
    ///
    /// * `pack_format` - required(minimum) pack_format
    /// * `token` - Token to raise error
    /// * `tokenizer` - token's Tokenizer
    /// * `suggestion` - error suggestion, defaults to None
    pub fn requires(
        &self,
        pack_format: PackFormat,
        token: &Token,
        tokenizer: &Tokenizer,
        suggestion: Option<String>,
    ) -> Result<(), JMCError> {
        if self.pack_format == 0 {
            return Ok(());
        }
        if self.pack_format < pack_format {
            return Err(JMCError::minecraft_version_too_low(
                pack_format,
                Some(token),
                tokenizer,
                suggestion,
            ));
        }
        Ok(())
    }
}
