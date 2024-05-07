use super::{
    exception::JMCError,
    tokenizer::{Token, Tokenizer},
};

pub type PackFormat = u32;
pub type MinecraftVersion = (u16, u16, u16);

#[derive(Debug, Copy, Clone, PartialEq, Eq, PartialOrd, Ord)]
/// Class containing information about pack_format
struct PackVersion {
    pack_format: PackFormat,
}

impl PackVersion {
    pub fn new(pack_format: PackFormat) -> Self {
        Self { pack_format }
    }

    /// Convert from MinecraftVersion to PackVersion, fails if the version is so low that datapack didn't exist.
    pub fn try_from(minecraft_version: MinecraftVersion) -> Result<Self, ()> {
        for (minecraft_version_thresold, pack_format) in PACK_VERSIONS {
            if minecraft_version > minecraft_version_thresold {
                return Ok(Self { pack_format });
            }
        }
        Err(())
    }

    /// Return MinecraftVersionTooLow when pack_format is too low
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

/// https://minecraft.wiki/w/Data_pack#Pack_format
const PACK_VERSIONS: [(MinecraftVersion, PackFormat); 12] = [
    ((1, 20, 5), 41),
    ((1, 20, 3), 26),
    ((1, 20, 2), 18),
    ((1, 20, 0), 15),
    ((1, 19, 4), 12),
    ((1, 19, 0), 10),
    ((1, 18, 2), 9),
    ((1, 18, 0), 8),
    ((1, 17, 0), 7),
    ((1, 16, 2), 6),
    ((1, 15, 0), 5),
    ((1, 13, 0), 4),
];
