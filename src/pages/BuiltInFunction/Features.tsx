import Feature from "../../components/Feature";
import CodeBlock, { CodeText, Command } from "../../components/CodeBlock";
import howTo from "./HowTo";
import formattedText from "./FormattedText";
import { Tab } from "../../components/CodeBlock/CodeBlock";

const BuildinFeatures = [
    howTo,
    formattedText,
    <Feature
        id="print"
        summary="print()"
        keywords="variable printf tellraw announce"
    >
        <p>Print a variable for all players in chat.</p>
        <Command
            name="print"
            type="JMCFunction"
            params={[{ key: "value", type: "Scoreboard" }]}
        />
    </Feature>,
    <Feature
        id="printf"
        summary="printf()"
        keywords="variable tellraw announce"
    >
        <p>
            Print a text for all players in chat. Works the same as{" "}
            <code>Text.tellraw(@a, text);</code>
        </p>
        <Command
            name="printf"
            type="JMCFunction"
            params={[{ key: "text", type: "FormattedString" }]}
        />
    </Feature>,
    <Feature
        id="player_on_event"
        summary="Player.onEvent()"
        keywords="scoreboard jump drop craft stats change"
        examples={[
            "jmc=AoGwhgngpgTgdAewHYFEBuUkBcAUArAVwFsAHAGgAIcBKAXgD4BvAKAEgBnSCgIgEkLCpKABMAhNwDczAL7UJQA",
        ]}
    >
        <p>
            Run commands on positive change of scoreboard and reset the score.
        </p>
        <Command
            name="Player.onEvent"
            type="LoadOnly"
            params={[
                { key: "criteria", type: "Criteria" },
                { key: "function", type: "Function" },
            ]}
        />
    </Feature>,
    <Feature
        id="player_first_join"
        summary="Player.firstJoin()"
        keywords="world connect login"
    >
        <p>
            Run commands as player and at player when joining the World for the
            first time.
        </p>
        <p className="text-warning">
            Revoking all advancements will cause this to be called again.
        </p>
        <Command
            name="Player.firstJoin"
            type="LoadOnce"
            params={[{ key: "function", type: "Function" }]}
        />
    </Feature>,
    <Feature
        id="player_rejoin"
        summary="Player.rejoin()"
        keywords="leave reconnect relog"
    >
        <p>
            Run commands as player and at player when a player leave a world
            then join back.
        </p>
        <p className="text-warning">
            Will not run when player join the world for the first time.
        </p>
        <Command
            name="Player.rejoin"
            type="LoadOnce"
            params={[{ key: "function", type: "Function" }]}
        />
    </Feature>,
    <Feature
        id="player_join"
        summary="Player.join()"
        keywords="world connect login"
    >
        <p>
            Run commands as player and at player every time a player joins the
            world.
        </p>
        <Command
            name="Player.join"
            type="LoadOnce"
            params={[{ key: "function", type: "Function" }]}
        />
    </Feature>,
    <Feature
        id="player_die"
        summary="Player.die()"
        keywords="death respawn died"
    >
        <p>
            Run onDeath as player and at player's last position when the player
            die
        </p>
        <p>
            Run onRespawn as player and at player spawn location when the player
            respawn
        </p>
        <Command
            name="Player.die"
            type="LoadOnce"
            params={[
                { key: "onDeath", type: "Function", default: "()=>{}" },
                {
                    key: "onRespawn",
                    type: "Function",
                    default: "()=>{}",
                },
            ]}
        />
    </Feature>,
    <Feature id="item_create" summary="Item.create()" keywords="new rightclick">
        <p>Create a custom item and save it for further use.</p>
        <p>
            onClick can only be used with "carrot_on_a_stick" or
            "warped_fungus_on_a_stick" itemType.
        </p>
        <p>
            <code>itemId</code> is the unique name of this item so that it can
            be referenced in other Item function.
        </p>
        <Command
            name="Item.create"
            type="LoadOnly"
            params={[
                { key: "itemId", type: "Keyword" },
                { key: "itemType", type: "Item" },
                { key: "displayName", type: "FormattedString", default: '""' },
                { key: "lore", type: "List<FormattedString>", default: "[]" },
                { key: "nbt", type: "JSObject", default: "{}" },
                { key: "onClick", type: "Function", default: "()=>{}" },
            ]}
            newline
        />
    </Feature>,
    <Feature
        id="item_create_sign"
        summary="Item.createSign()"
        keywords="new sign"
    >
        <p>Create a custom sign and save it for further use.</p>
        <p>
            <code>variant</code> is wood variant of the sign such as oak,
            spruce, etc.
        </p>
        <p>
            <code>itemId</code> is the unique name of this item so that it can
            be referenced in other Item function.
        </p>
        <Command
            name="Item.createSign"
            type="LoadOnly"
            params={[
                { key: "itemId", type: "Keyword" },
                { key: "variant", type: "Keyword" },
                { key: "displayName", type: "FormattedString", default: '""' },
                { key: "lore", type: "List<FormattedString>", default: "[]" },
                { key: "texts", type: "List<FormattedString>", default: "[]" },
                { key: "nbt", type: "JSObject", default: "{}" },
                { key: "onClick", type: "Function", default: "()=>{}" },
            ]}
            newline
        />
    </Feature>,
    <Feature
        id="item_create_spawn_egg"
        summary="Item.createSpawnEgg()"
        keywords="new spawner"
    >
        <p>Create a custom spawn egg and save it for further use.</p>
        <p>
            The spawn egg will not summon any mob unless specified in{" "}
            <code>onPlace</code>
        </p>
        <Command
            name="Item.createSpawnEgg"
            type="LoadOnly"
            params={[
                { key: "itemId", type: "Keyword" },
                { key: "mobType", type: "Keyword" },
                { key: "displayName", type: "FormattedString", default: '""' },
                { key: "onPlace", type: "Function", default: "()=>{}" },
                { key: "lore", type: "List<FormattedString>", default: "[]" },
                { key: "nbt", type: "JSObject", default: "{}" },
            ]}
            newline
        />
    </Feature>,
    <Feature
        id="item_give"
        summary="Item.give()"
        keywords="gave"
        examples={[
            "jmc=JIFwpgtgdAxgTmAhuAFAKAJAQJ6kgGkwBMBLRCAewDsjCMAiAMgCMBBAAgDcw5t2YKFADbtGQ0uWpF6aAJQBuNGjzQA5iW4ocK-OwACiBUA",
        ]}
    >
        <p>
            Give item created from <code>Item.create</code> to a player
        </p>
        <Command
            name="Item.give"
            type="JMCFunction"
            params={[
                { key: "itemId", type: "Keyword" },
                { key: "selector", type: "TargetSelector", default: "@s" },
                { key: "amount", type: "integer", default: "1" },
            ]}
        />
    </Feature>,
    <Feature
        id="item_clear"
        summary="Item.clear()"
        keywords="remove erase take away"
    >
        <p>
            Clear item created from <code>Item.create</code> from a player.{" "}
            <code>amount</code> at -1 means to clear all.
        </p>
        <Command
            name="Item.clear"
            type="JMCFunction"
            params={[
                { key: "itemId", type: "Keyword" },
                { key: "selector", type: "TargetSelector", default: "@s" },
                { key: "amount", type: "integer", default: "-1" },
            ]}
        />
    </Feature>,
    <Feature id="item_summon" summary="Item.summon()" keywords="spawn">
        <p>
            Spawn item entity from <code>Item.create</code>.
        </p>
        <Command
            name="Item.summon"
            type="JMCFunction"
            params={[
                { key: "itemId", type: "Keyword" },
                { key: "pos", type: "string" },
                { key: "count", type: "integer", default: "1" },
                { key: "nbt", type: "JSObject", default: "{}" },
            ]}
        />
    </Feature>,
    <Feature id="item_replace_block" summary="Item.replaceBlock()" keywords="">
        <p>
            Use <code>/item replace block</code> with item from{" "}
            <code>Item.create</code>.
        </p>
        <Command
            name="Item.replaceBlock"
            type="JMCFunction"
            params={[
                { key: "itemId", type: "Keyword" },
                { key: "pos", type: "string" },
                { key: "slot", type: "string" },
                { key: "count", type: "integer", default: "1" },
            ]}
        />
    </Feature>,
    <Feature
        id="item_replace_entity"
        summary="Item.replaceEntity()"
        keywords=""
    >
        <p>
            Use <code>/item replace entity</code> with item from{" "}
            <code>Item.create</code>.
        </p>
        <Command
            name="Item.replaceEntity"
            type="JMCFunction"
            params={[
                { key: "itemId", type: "Keyword" },
                { key: "selector", type: "TargetSelector" },
                { key: "slot", type: "string" },
                { key: "count", type: "integer", default: "1" },
            ]}
        />
    </Feature>,
    <Feature id="text_tellraw" summary="Text.tellraw()" keywords="formatted">
        <p>Use formatted text on tellraw</p>
        <Command
            name="Text.tellraw"
            type="JMCFunction"
            params={[
                { key: "selector", type: "TargetSelector" },
                { key: "message", type: "FormattedString" },
            ]}
        />
    </Feature>,
    <Feature id="text_title" summary="Text.title()" keywords="formatted">
        <p>Use formatted text on title</p>
        <Command
            name="Text.title"
            type="JMCFunction"
            params={[
                { key: "selector", type: "TargetSelector" },
                { key: "message", type: "FormattedString" },
            ]}
        />
    </Feature>,
    <Feature id="text_subtitle" summary="Text.subtitle()" keywords="formatted">
        <p>Use formatted text on subtitle</p>
        <Command
            name="Text.subtitle"
            type="JMCFunction"
            params={[
                { key: "selector", type: "TargetSelector" },
                { key: "message", type: "FormattedString" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_actionbar"
        summary="Text.actionbar()"
        keywords="formatted"
    >
        <p>Use formatted text on actionbar</p>
        <Command
            name="Text.actionbar"
            type="JMCFunction"
            params={[
                { key: "selector", type: "TargetSelector" },
                { key: "message", type: "FormattedString" },
            ]}
        />
    </Feature>,
    <Feature
        id="math_sqrt"
        summary="Math.sqrt()"
        keywords="square root"
        examples={["jmc=CQQwBAvGCMAMDcAoYAjSYCyIAuALAdAM4COATtgBSgCU8QA"]}
    >
        <p>
            Use{" "}
            <a
                href="https://en.wikipedia.org/wiki/Newton%27s_method"
                target="_blank"
                rel="noreferrer"
            >
                Newton-Raphson method
            </a>{" "}
            to perfectly calculate square root of any integer. And, like normal
            minecraft operators, this function will{" "}
            <a
                href="https://en.wikipedia.org/wiki/Floor_and_ceiling_functions"
                target="_blank"
                rel="noreferrer"
            >
                floor
            </a>
            (round down) the result.
        </p>
        <Command
            name="Math.sqrt"
            type="VariableOperation"
            params={[{ key: "n", type: "Scoreboard" }]}
        />
    </Feature>,
    <Feature
        id="math_random"
        summary="Math.random()"
        keywords="randomize randomization rng lcg linear congruential generator"
    >
        <p>
            Simplify integer randomization process using{" "}
            <a
                href="https://en.wikipedia.org/wiki/Linear_congruential_generator"
                target="_blank"
                rel="noreferrer"
            >
                Linear congruential generator
            </a>
            .
        </p>
        <Command
            name="Math.random"
            type="VariableOperation"
            params={[
                { key: "min", type: "ScoreboardInteger", default: "1" },
                {
                    key: "max",
                    type: "ScoreboardInteger",
                    default: "2147483647",
                },
            ]}
        />
    </Feature>,
    <Feature id="timer_add" summary="Timer.add()" keywords="scoreboard">
        <p>
            Create a scoreboard timer with 3 run <code>mode</code>
        </p>
        <ul>
            <li>
                <code>runOnce</code>: run the commands once after the timer is
                over.
            </li>
            <li>
                <code>runTick</code>: run the commands every tick if timer is
                over.
            </li>
            <li>
                <code>none</code>: do not run any command.
            </li>
        </ul>
        <p>
            Selector is the entities that the game will search for when ticking
            down the timer.{" "}
            <span className="text-warning">
                Avoid using expensive selector like <code>@e</code>.
            </span>
        </p>
        <Command
            name="Timer.add"
            type="LoadOnly"
            params={[
                { key: "objective", type: "Objective" },
                { key: "mode", type: "Keyword" },
                { key: "selector", type: "TargetSelector" },
                { key: "function", type: "Function", default: "()=>{}" },
            ]}
            newline
        />
    </Feature>,
    <Feature id="timer_set" summary="Timer.set()" keywords="scoreboard">
        <p>Set entity's score to start the timer.</p>
        <Command
            name="Timer.set"
            type="JMCFunction"
            params={[
                { key: "objective", type: "Objective" },
                { key: "selector", type: "TargetSelector" },
                { key: "tick", type: "ScoreboardInteger" },
            ]}
        />
    </Feature>,
    <Feature id="timer_is_over" summary="Timer.isOver()" keywords="scoreboard">
        <p>Whether the timer of the selector is over or not.</p>
        <Command
            name="Timer.isOver"
            type="Boolean"
            params={[
                { key: "objective", type: "Objective" },
                { key: "selector", type: "TargetSelector", default: "@s" },
            ]}
        />
    </Feature>,
    <Feature
        id="recipe_table"
        summary="Recipe.table()"
        keywords="custom crafting knowledge book"
    >
        <p>
            Create a custom recipe for Crafting Table allowing NBT in result
            item and running function on craft
        </p>
        <Command
            name="Recipe.table"
            type="LoadOnly"
            params={[
                { key: "recipe", type: "JSON" },
                {
                    key: "baseItem",
                    type: "Item",
                    default: "knowledge_book",
                },
                { key: "onCraft", type: "Function", default: "()=>{}" },
            ]}
        />
    </Feature>,
    <Feature
        id="hardcode_repeat"
        summary="Hardcode.repeat()"
        keywords="copy paste"
        examples={[
            "jmc=BIQwTgJgxg9hCmA6M8AO8QBcAUAoAkAEQDaAlgHYIAeAuoQDQHYCUAvAHwDeB%2BAziAE8ABCQrU6AbgIBfRn0zhMrAAxzemGKlYBGZbmYSgA",
            "jmc=BIQwTgJgxg9hCmA6M8AO8QBcAUAoAkAEQDaAlgHYIAeAuoQDQHYCUAvAHwDeB%2BAziAE8ABIVCRYCRFBAAbKNjKV4tAFQqATM0IBuAgF9GfTOEysADId6YYqVgEYzuZtqA",
        ]}
    >
        <p>
            Some features in minecraft datapack require hard coding, this
            function will be a tool to help you. JMC will replace text that's
            the same as <code>indexString</code> with the number.
        </p>
        <p>
            <code>start</code> is inclusive, <code>stop</code> is exclusive.
        </p>
        <p className="text-warning">
            This do not work on Switch Case statement. Use{" "}
            <code>Hardcode.switch()</code> instead.
        </p>
        <Command
            name="Hardcode.repeat"
            type="ExecuteExcluded"
            params={[
                { key: "indexString", type: "string" },
                { key: "function", type: "ArrowFunction" },
                { key: "start", type: "integer" },
                { key: "stop", type: "integer" },
                { key: "step", type: "integer", default: "1" },
            ]}
            newline
        />
        <p>
            To do more complex task, you can use{" "}
            <code>Hardcode.calc({"<expression>"})</code> ANYWHERE in the
            function. JMC will replace the entire section with the result after
            replacing <code>indexString</code>
        </p>
        <p>
            <code>+</code>(add), <code>-</code>(subtract), <code>*</code>
            (multiply), <code>/</code>(divide by), <code>**</code>(power) are
            allowed in the expression. An example of expression with{" "}
            <code>indexString="index"</code> is
        </p>
        <CodeBlock>
            tellraw <CodeText type="param">@a</CodeText>{" "}
            <CodeText type="string">"index^2=Hardcode.calc(index**2)"</CodeText>
            ;
        </CodeBlock>
    </Feature>,
    <Feature
        id="hardcode_repeat_list"
        summary="Hardcode.repeatList()"
        keywords="copy paste list array"
        examples={[
            "jmc=BIQwTgJgxg9hCmA6M8AO8QBcAyBLAzpgBQBQAkAEQDauAdggB4C6FANOUQJQC8AfAN7ky%2BEAE8ABNTqMWAbnIBfdmSoUQbSQCMNFKDogUmJTrKA",
        ]}
    >
        <p>
            Does the same thing as <code>Hardcode.repeat</code> but use list to
            loop through instead of numbers
        </p>
        <Command
            name="Hardcode.repeatList"
            type="ExecuteExcluded"
            params={[
                { key: "indexString", type: "string" },
                { key: "function", type: "ArrowFunction" },
                { key: "strings", type: "List<string>" },
            ]}
            newline
        />
    </Feature>,
    <Feature
        id="hardcode_repeat_lists"
        summary="Hardcode.repeatLists()"
        keywords="copy paste lists arrays"
        examples={[
            "jmc=BIQwTgJgxg9hCmA6M8AO8QBcAyBLAzpvgBQBQAkANoXkBEluAdggB4CMAurQDQ31OsATFwode5YgEoAvAD4A3jXwgAngAJ%2BzeOw5qAtGoZaWw2gG4KAX3HVyVWiDY8NAIyfcNUdxohOxNSgdBZ1oXYI9aKHCfYI5RUkkzIA",
        ]}
    >
        <p>
            Does the same thing as <code>Hardcode.repeatList</code> but it can
            replace multiple indexes at the same time.
        </p>
        <Command
            name="Hardcode.repeatLists"
            type="ExecuteExcluded"
            params={[
                { key: "indexStrings", type: "List<string>" },
                { key: "function", type: "ArrowFunction" },
                { key: "stringLists", type: "List<List<string>>" },
            ]}
            newline
        />
    </Feature>,
    <Feature
        id="hardcode_switch"
        summary="Hardcode.switch()"
        keywords="copy paste switch case"
    >
        <p>
            Similar to <code>Hardcode.repeat()</code> but for switch statement.
        </p>
        <Command
            name="Hardcode.switch"
            type="ExecuteExcluded"
            params={[
                { key: "switch", type: "Scoreboard" },
                { key: "indexString", type: "string" },
                { key: "function", type: "ArrowFunction" },
                { key: "count", type: "integer" },
                { key: "begin_at", type: "integer", default: "1" },
            ]}
            newline
        />
        <p>
            To do more complex task, you can use{" "}
            <code>Hardcode.calc({"<expression>"})</code> ANYWHERE in the
            function. JMC will replace the entire section with the result after
            replacing <code>indexString</code>
        </p>
        <p>
            <code>+</code>(add), <code>-</code>(subtract), <code>*</code>
            (multiply), <code>/</code>(divide by), <code>**</code>(power) are
            allowed in the expression. An example of expression with{" "}
            <code>indexString="index"</code> is
        </p>
        <CodeBlock>
            tellraw <CodeText type="param">@a</CodeText>{" "}
            <CodeText type="string">"index^2=Hardcode.calc(index**2)"</CodeText>
            ;
        </CodeBlock>
    </Feature>,
    <Feature
        id="trigger_setup"
        summary="Trigger.setup()"
        keywords="permissions perms scoreboard op"
        examples={[
            "jmc=GYVwdgxgLglg9mABAWwJ4DFwQBQEpEDeAUAJADOAhqogEQCSiAThUgAZSMwDmXApoylQAVTj36IyvKIgBMrGgG4iAXyJER3PowB0kqCAAO2NBrGMANIVIBGAFyI8AXgB8BStXpMWidqK2DTLXkFZXNSGXs0TEgVXAUgA",
        ]}
    >
        <p>
            Setup a trigger system for custom command or allowing players with
            no permission to click a text button. User can use the function with{" "}
            <code>{"/trigger <objective> set <id>"}</code>
        </p>
        <p className="text-warning">
            Do not define/create objective with the same name as{" "}
            <code>objective</code>
        </p>
        <Command
            name="Trigger.setup"
            type="LoadOnly"
            params={[
                { key: "objective", type: "Keyword" },
                { key: "triggers", type: "JSObject<integer, Function>" },
            ]}
        />
    </Feature>,
    <Feature
        id="trigger_add"
        summary="Trigger.add()"
        keywords="permissions perms scoreboard op"
    >
        <p>
            Add a trigger command. (Shortcut for <code>Trigger.setup()</code>)
        </p>
        <p className="text-warning">
            Do not define/create objective with the same name as{" "}
            <code>objective</code>
        </p>
        <Command
            name="Trigger.add"
            type="LoadOnly"
            params={[
                { key: "objective", type: "Keyword" },
                { key: "function", type: "Function" },
            ]}
        />
    </Feature>,
    <Feature
        id="predicate_location"
        summary="Predicate.locations()"
        keywords="offset location_check"
    >
        <p>Automation for making massive location check.</p>
        <Command
            name="Predicate.locations"
            type="LoadOnly"
            params={[
                { key: "name", type: "string" },
                { key: "predicate", type: "JSON" },
                { key: "xMin", type: "integer" },
                { key: "xMax", type: "integer" },
                { key: "yMin", type: "integer" },
                { key: "yMax", type: "integer" },
                { key: "zMin", type: "integer" },
                { key: "zMax", type: "integer" },
            ]}
            newline
        />
    </Feature>,
    <Feature
        id="right_click_setup"
        summary="RightClick.setup()"
        keywords="detect carrot on a stick carrot_on_a_stick"
    >
        <p>
            Setup basic carrot_on_a_stick right click detection with selected
            item detection. You can map any id to a series of commands. When any
            player right click with the item, the command matching the id will
            be run.{" "}
            <span className="text-warning">
                While ID 0 being default which will be run if player right click
                with *any* Carrot on a stick that doesn't have an ID.
            </span>{" "}
            You are allowed to setup multiple times with different id_name but
            that isn't recommended due to optimization issue. An example of{" "}
            <code>idName</code> is <code>my_id</code> for nbt{" "}
            <code>{"{my_id:2}"}</code>
        </p>
        <Command
            name="RightClick.setup"
            type="LoadOnly"
            params={[
                { key: "idName", type: "Keyword" },
                { key: "functionMap", type: "JSObject<integer, Function>" },
            ]}
        />
    </Feature>,
    <Feature id="particle_line" summary="Particle.circle()" keywords="">
        <p>
            Make circle shaped particles. The higher the spread number, the less
            distance between particle becomes.
        </p>
        <Command
            name="Particle.circle"
            type="JMCFunction"
            params={[
                { key: "particle", type: "string" },
                { key: "radius", type: "float" },
                { key: "spread", type: "integer" },
                { key: "speed", type: "integer", default: "1" },
                { key: "count", type: "integer", default: "1" },
                { key: "mode", type: "Keyword", default: "normal" },
            ]}
            newline
        />
    </Feature>,
    <Feature id="particle_spiral" summary="Particle.spiral()" keywords="">
        <p>
            Make spiral shaped particles. The higher the spread number, the less
            distance between particle becomes.
        </p>
        <Command
            name="Particle.spiral"
            type="JMCFunction"
            params={[
                { key: "particle", type: "string" },
                { key: "radius", type: "float" },
                { key: "height", type: "float" },
                { key: "spread", type: "integer" },
                { key: "speed", type: "integer", default: "1" },
                { key: "count", type: "integer", default: "1" },
                { key: "mode", type: "Keyword", default: "normal" },
            ]}
            newline
        />
    </Feature>,
    <Feature id="particle_helix" summary="Particle.helix ()" keywords="">
        <p>
            Make spiral shaped particles. The higher the spread number, the less
            distance between particle becomes. (Alias to{" "}
            <code>Particle.spiral</code>)
        </p>
        <Command
            name="Particle.helix "
            type="JMCFunction"
            params={[
                { key: "particle", type: "string" },
                { key: "radius", type: "float" },
                { key: "height", type: "float" },
                { key: "spread", type: "integer" },
                { key: "speed", type: "integer", default: "1" },
                { key: "count", type: "integer", default: "1" },
                { key: "mode", type: "Keyword", default: "normal" },
            ]}
            newline
        />
    </Feature>,
    <Feature id="particle_cylinder" summary="Particle.cylinder()" keywords="">
        <p>
            Make cylinder shaped particles. The higher the spread number, the
            less distance between particle becomes.
        </p>
        <Command
            name="Particle.cylinder"
            type="JMCFunction"
            params={[
                { key: "particle", type: "string" },
                { key: "radius", type: "float" },
                { key: "height", type: "float" },
                { key: "spreadXZ", type: "integer" },
                { key: "spreadY", type: "integer" },
                { key: "speed", type: "integer", default: "1" },
                { key: "count", type: "integer", default: "1" },
                { key: "mode", type: "Keyword", default: "normal" },
            ]}
            newline
        />
    </Feature>,
    <Feature id="particle_line" summary="Particle.line()" keywords="">
        <p>
            Make line shaped particles. The higher the spread number, the less
            distance between particle becomes.
        </p>
        <Command
            name="Particle.line"
            type="JMCFunction"
            params={[
                { key: "particle", type: "string" },
                { key: "distance", type: "float" },
                { key: "spread", type: "integer" },
                { key: "speed", type: "integer", default: "1" },
                { key: "count", type: "integer", default: "1" },
                { key: "mode", type: "Keyword", default: "normal" },
            ]}
            newline
        />
    </Feature>,
    <Feature id="particle_square" summary="Particle.square()" keywords="">
        <p>
            Make square shaped particles. The higher the spread number, the less
            distance between particle becomes.
        </p>
        <p>
            Available <code>align</code> are <code>corner</code> and{" "}
            <code>center</code>.
        </p>
        <Command
            name="Particle.square"
            type="JMCFunction"
            params={[
                { key: "particle", type: "string" },
                { key: "length", type: "float" },
                { key: "spread", type: "integer" },
                { key: "align", type: "Keyword", default: "corner" },
                { key: "speed", type: "integer", default: "1" },
                { key: "count", type: "integer", default: "1" },
                { key: "mode", type: "Keyword", default: "normal" },
            ]}
            newline
        />
    </Feature>,
    <Feature id="particle_cube" summary="Particle.cube()" keywords="">
        <p>
            Make cube shaped particles. The higher the spread number, the less
            distance between particle becomes.
        </p>
        <p>
            Available <code>align</code> are <code>corner</code> and{" "}
            <code>center</code>.
        </p>
        <Command
            name="Particle.square"
            type="JMCFunction"
            params={[
                { key: "particle", type: "string" },
                { key: "length", type: "float" },
                { key: "spread", type: "integer" },
                { key: "align", type: "Keyword", default: "corner" },
                { key: "speed", type: "integer", default: "1" },
                { key: "count", type: "integer", default: "1" },
                { key: "mode", type: "Keyword", default: "normal" },
            ]}
            newline
        />
    </Feature>,
    <Feature id="particle_sphere" summary="Particle.sphere()" keywords="">
        <p>
            Make sphere shaped particles. The higher the spread number, the less
            distance between particle becomes.
        </p>
        <Command
            name="Particle.sphere"
            type="JMCFunction"
            params={[
                { key: "particle", type: "string" },
                { key: "radius", type: "float" },
                { key: "spread", type: "integer" },
                { key: "speed", type: "integer", default: "1" },
                { key: "count", type: "integer", default: "1" },
                { key: "mode", type: "Keyword", default: "normal" },
            ]}
            newline
        />
    </Feature>,
    <Feature
        id="raycast_simple"
        summary="Raycast.simple()"
        keywords="gun shoot"
    >
        <p>Cast simple raycast</p>
        <ul>
            <li>
                <code>interval</code> is distance between checks.
            </li>
            <li>
                <code>maxIter</code> is maximum number of iteration.
            </li>
            <li>
                <code>boxSize</code> is the size of entity detection cube.
            </li>
            <li>
                <code>target</code> is acceptable target for collision.
            </li>
            <li>
                <code>startAtEye</code> is wheter to start at the entity's eyes.
                If set to false it'll use the current position of the command.
            </li>
            <li>
                <code>stopAtEntity</code> is wheter to stop the raycast when
                colliding with the entity.
            </li>
            <li>
                <code>stopAtBlock</code> is wheter to stop the raycast when
                colliding with a block.
            </li>
            <li>
                <code>runAtEnd</code> is wheter to run <code>onHit</code>{" "}
                function even if doesn't collide with entity. (It'll run as the
                caster in this case.)
            </li>
            <li>
                <code>modifyExecuteBeforeStep</code> is part of execute command
                that come before positioning forward. Example:{" "}
                <code>"rotated ~ ~5"</code>
            </li>
            <li>
                <code>modifyExecuteAfterStep</code> is part of execute command
                that come after positioning forward.
            </li>
            <li>
                <code>overideString</code> is string that'll be replaced with
                the recursion function's name (In vanilla syntax).{" "}
                <span className="text-warning">
                    Must be used with <code>overideRecursion</code>. Do not use
                    unless it's necessary
                </span>
            </li>
            <li>
                <code>overideRecursion</code> is function that'll overide the
                recursion line entirely.{" "}
                <span className="text-warning">
                    Must be used with <code>overideString</code>. Do not use
                    unless it's necessary
                </span>
            </li>
        </ul>
        <Command
            name="Raycast.simple"
            type="ExecuteExcluded"
            params={[
                { key: "onHit", type: "Function" },
                { key: "onStep", type: "Function", default: "()=>{}" },
                { key: "onBeforeStep", type: "Function", default: "()=>{}" },
                { key: "interval", type: "float", default: "0.1" },
                { key: "maxIter", type: "integer", default: "1000" },
                { key: "boxSize", type: "float", default: "0.1" },
                { key: "target", type: "TargetSelector", default: "@e" },
                { key: "startAtEye", type: "boolean", default: "true" },
                { key: "stopAtEntity", type: "boolean", default: "true" },
                { key: "stopAtBlock", type: "boolean", default: "true" },
                { key: "runAtEnd", type: "boolean", default: "false" },
                { key: "casterTag", type: "Keyword", default: "__self__" },
                { key: "removeCasterTag", type: "boolean", default: "true" },
                {
                    key: "modifyExecuteBeforeStep",
                    type: "string",
                    default: '""',
                },
                {
                    key: "modifyExecuteAfterStep",
                    type: "string",
                    default: '""',
                },
                { key: "overideString", type: "string", default: '""' },
                {
                    key: "overideRecursion",
                    type: "ArrowFunction",
                    default: "()=>{}",
                },
            ]}
            newline
        />
    </Feature>,
    <Feature id="jmc_put" summary="JMC.put()" keywords="">
        <p>
            Ignore any parsing and output the command directly. Usually used to
            bypass compiler failures.
        </p>
        <Command
            name="JMC.put"
            type="JMCFunction"
            params={[{ key: "command", type: "string" }]}
        />
    </Feature>,
    <Feature
        id="jmc_python"
        summary="JMC.python()"
        keywords="code program javascript run"
        examples={[
            "jmc=FIWQwgdADgngLgCwPYDsAUADAUAEwKYBmABAM5QCGAtmgJQBcWAkAUgE5ED6RAlika%2BRQBzPGgCMABnpNGeStzhoARCXIwiACTwAbbUiIB1NtpxKaWDABoiSyuV5mA3Fiyr1SgzoDGSSniJw%2BngAHlRQ2nhKzqCQsIiomK4U1OZWNnYONI5AA",
            "jmc=FIWQwgdADgngLgCwPYDsAUADAUAEwKYBmABAUkmnHgB5wCUAXFgJB4C2AlnGgQEQDOAQxhEA3pRoBfHrSylyPAEYCATtKwZaAbixZQkWIlSZchEmQrU6jFhy69BwnOwIE8yvCjijxcKTLloiipqGppAA",
            "jmc=FIWQwgdADgngLgCwPYDsAUADAUAMyUgAgF4CAiAZwEMYCBGUrDAGjIFMUA3egSgG4tQkWIlSZc%2BYmSo0ATA2ZtOcvgPDR4ydNlYBbAJZw0eJN0YtS7LqT5A",
        ]}
    >
        <p>
            Allow you to use python code directly inside jmc, use{" "}
            <code>emit()</code> function to return one or more commands
        </p>
        <p>
            Use the same <code>env</code> to continue using old
            variables/functions declared earlier (By default, it generates new
            environment)
        </p>
        <Command
            name="JMC.python"
            type="JMCFunction"
            params={[
                { key: "pythonCode", type: "string" },
                { key: "env", type: "string ", default: '""' },
            ]}
        />
    </Feature>,
    <Feature
        id="string_is_equal"
        summary="String.isEqual()"
        keywords="compare nbt"
    >
        <p>Whether the value inside NBT path is equal to the string.</p>
        <Command
            name="String.isEqual"
            type="Boolean"
            params={[
                { key: "source", type: "string" },
                { key: "path", type: "Keyword" },
                { key: "string", type: "string" },
            ]}
        />
    </Feature>,
    <Feature
        id="object_is_equal"
        summary="Object.isEqual()"
        keywords="compare nbt"
    >
        <p>
            Whether the value inside NBT path is equal to the value inside
            another NBT path.
        </p>
        <Command
            name="Object.isEqual"
            type="Boolean"
            params={[
                { key: "source1", type: "string" },
                { key: "path1", type: "Keyword" },
                { key: "source2", type: "string" },
                { key: "path2", type: "Keyword" },
            ]}
        />
    </Feature>,
    <Feature id="gui_template" summary="GUI.template()" keywords="create">
        <p>
            Create template for GUI that can be configured with{" "}
            <code>GUI.register</code> and <code>GUI.registers</code> then create
            the GUI with <code>GUI.create</code> and used with{" "}
            <code>GUI.run</code>. GUI module doesn't work on Player's inventory.
        </p>
        <p>
            Available modes are <code>entity</code>, <code>block</code> and{" "}
            <code>enderchest</code>
        </p>
        <p>Example of template is</p>
        <CodeBlock>
            [<br />
            <Tab />
            <CodeText type="string">"---------"</CodeText>,<br />
            <Tab />
            <CodeText type="string">"---A-B---"</CodeText>,<br />
            <Tab />
            <CodeText type="string">"---------"</CodeText>
            <br />]
        </CodeBlock>
        <Command
            name="GUI.template"
            type="LoadOnly"
            params={[
                { key: "name", type: "Keyword" },
                { key: "template", type: "List<string>" },
                { key: "mode", type: "Keyword" },
            ]}
        />
    </Feature>,
    <Feature id="gui_register" summary="GUI.register()" keywords="map">
        <p>Map an item to an id(chatacter) in template</p>
        <Command
            name="GUI.register"
            type="LoadOnly"
            params={[
                { key: "name", type: "Keyword" },
                { key: "id", type: "string" },
                { key: "item", type: "Item" },
                { key: "displayName", type: "FormattedString", default: '""' },
                { key: "lore", type: "List<FormattedString>", default: "[]" },
                { key: "nbt", type: "JSObject", default: "{}" },
                { key: "onClick", type: "Function", default: "()=>{}" },
                { key: "onClickAsGUI", type: "Function", default: "()=>{}" },
            ]}
            newline
        />
    </Feature>,
    <Feature id="gui_registers" summary="GUI.registers()" keywords="map">
        <p>
            Map multiple items created from <code>Item.create</code> to an
            id(chatacter) in template depending on variable
        </p>
        <Command
            name="GUI.registers"
            type="LoadOnly"
            params={[
                { key: "name", type: "Keyword" },
                { key: "id", type: "string" },
                { key: "items", type: "List<Keyword>" },
                { key: "variable", type: "Scoreboard" },
                { key: "onClick", type: "Function", default: "()=>{}" },
                { key: "onClickAsGUI", type: "Function", default: "()=>{}" },
            ]}
            newline
        />
    </Feature>,
    <Feature id="gui_create" summary="GUI.create()" keywords="template">
        <p>
            Create a GUI that's been configured from <code>GUI.template</code>,{" "}
            <code>GUI.register</code> and <code>GUI.registers</code>
        </p>
        <Command
            name="GUI.create"
            type="LoadOnly"
            params={[{ key: "name", type: "Keyword" }]}
        />
    </Feature>,
    <Feature id="gui_run" summary="GUI.run()" keywords="">
        <p>
            Run a GUI, on entity/block. This function must be run every tick, as
            the entity at the entity/at the block containing that GUI.
        </p>
        <Command
            name="GUI.run"
            type="JMCFunction"
            params={[{ key: "name", type: "Keyword" }]}
        />
    </Feature>,
    <Feature
        id="advancement_grant"
        summary="Advancement.grant()"
        keywords="vanilla"
    >
        <p>Grant advancement, an alternative to vanilla syntax</p>
        <p>
            Available <code>type</code> are "everything", "from", "only",
            "through", "until"
        </p>
        <Command
            name="Advancement.grant"
            type="JMCFunction"
            params={[
                { key: "target", type: "TargetSelector" },
                { key: "type", type: "Keyword" },
                { key: "advancement", type: "Keyword" },
                { key: "namespace", type: "Keyword", default: '""' },
            ]}
        />
    </Feature>,
    <Feature
        id="advancement_revoke"
        summary="Advancement.revoke()"
        keywords="vanilla"
    >
        <p>Revoke advancement, an alternative to vanilla syntax</p>
        <p>
            Available <code>type</code> are "everything", "from", "only",
            "through", "until"
        </p>
        <Command
            name="Advancement.revoke"
            type="JMCFunction"
            params={[
                { key: "target", type: "TargetSelector" },
                { key: "type", type: "Keyword" },
                { key: "advancement", type: "Keyword" },
                { key: "namespace", type: "Keyword", default: '""' },
            ]}
        />
    </Feature>,
    <Feature
        id="scoreboard_add"
        summary="Scoreboard.add()"
        keywords="objective vanilla"
    >
        <p>Add scoreboard objective, an alternative to vanilla syntax</p>
        <Command
            name="Scoreboard.add"
            type="JMCFunction"
            params={[
                { key: "objective", type: "Keyword" },
                { key: "criteria", type: "Criteria", default: "dummy" },
                { key: "displayName", type: "FormattedString", default: '""' },
            ]}
        />
    </Feature>,
    <Feature id="bossbar_add" summary="Bossbar.add()" keywords="vanilla">
        <p>Add bossbar, an alternative to vanilla syntax</p>
        <Command
            name="Bossbar.add"
            type="JMCFunction"
            params={[
                { key: "team", type: "Keyword" },
                { key: "displayName", type: "FormattedString", default: '""' },
            ]}
        />
    </Feature>,
    <Feature
        id="bossbar_setName"
        summary="Bossbar.setName()"
        keywords="vanilla"
    >
        <p>
            Change the name of existing bossbar, an alternative to vanilla
            syntax
        </p>
        <Command
            name="Bossbar.setName"
            type="JMCFunction"
            params={[
                { key: "team", type: "Keyword" },
                { key: "displayName", type: "FormattedString", default: '""' },
            ]}
        />
    </Feature>,
    <Feature id="team_add" summary="Team.add()" keywords="vanilla">
        <p>Add team, an alternative to vanilla syntax</p>
        <p>
            Example of <code>properties</code> is{" "}
            <code>{"{nametagVisibility: never}"}</code>
        </p>
        <Command
            name="Team.add"
            type="LoadOnly"
            params={[
                { key: "id", type: "Keyword" },
                { key: "name", type: "FormattedString", default: '""' },
                {
                    key: "properties",
                    type: "JSObject<Keyword, Keyword>",
                    default: "{}",
                },
            ]}
        />
    </Feature>,
    <Feature
        id="entity_launch"
        summary="Entity.launch()"
        keywords="motion shoot"
    >
        <p>
            Launch the entity running the command foward(the direction the
            command is running). Usually used with <code>execute</code>.
        </p>
        <Command
            name="Entity.launch"
            type="JMCFunction"
            params={[{ key: "power", type: "float", default: "1" }]}
        />
    </Feature>,
    <Feature
        id="text_prop_click_command"
        summary="TextProp.clickCommand()"
        keywords="run_command clickevent"
    >
        <p>
            Create custom property for FormattedString, <code>local</code> will
            delete the property after it has been used once.
        </p>
        <p>Add run_command clickEvent to the text.</p>
        <Command
            name="TextProp.clickCommand"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "function", type: "ArrowFunction" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_props_click_command"
        summary="TextProps.clickCommand()"
        keywords="run_command clickevent"
    >
        <p>
            Similar to <code>TextProp.clickCommand</code>, but you can use
            <code>indexString</code> as a parameter within <code>function</code>
            , (same as how it works in the <code>Hardcode</code> functions)
        </p>
        <p>
            Add run_command clickEvent to the text, replacing{" "}
            <code>indexString</code> with an argument.
        </p>
        <Command
            name="TextProps.clickCommand"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "indexString", type: "string" },
                { key: "function", type: "ArrowFunction" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_prop_suggest_command"
        summary="TextProp.suggestCommand()"
        keywords="suggest_command clickevent"
    >
        <p>
            Does the same thing as <code>TextProp.clickCommand</code>, but it
            only suggests the command in chat instead of running it immediately.
            <code>local</code> will delete the property after it has been used
            once.
        </p>
        <p>Add suggest_command clickEvent to the text.</p>
        <Command
            name="TextProp.suggestCommand"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "function", type: "ArrowFunction" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_props_suggest_command"
        summary="TextProps.suggestCommand()"
        keywords="suggest_command clickevent"
    >
        <p>
            Similar to <code>TextProp.suggestCommand</code>, but you can use
            <code>indexString</code> as a parameter within <code>function</code>
            , (same as how it works in the <code>Hardcode</code> functions)
        </p>
        <p>
            Add suggest_command clickEvent to the text, replacing{" "}
            <code>indexString</code> with an argument.
        </p>
        <Command
            name="TextProps.suggestCommand"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "indexString", type: "string" },
                { key: "function", type: "ArrowFunction" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_prop_click_url"
        summary="TextProp.clickURL()"
        keywords="open_url clickevent"
    >
        <p>
            Create clickable web link inside FormattedString, <code>local</code>{" "}
            will delete the property after it has been used once.
        </p>
        <p>Add open_url clickEvent to the text.</p>
        <Command
            name="TextProp.clickURL"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "url", type: "string" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_props_click_url"
        summary="TextProps.clickURL()"
        keywords="open_url clickevent"
    >
        <p>
            Similar to <code>TextProp.clickURL</code>, but you can use
            <code>indexString</code> as a parameter within <code>url</code>,
            (same as how it works in the <code>Hardcode</code> functions)
        </p>
        <p>
            Add open_url clickEvent to the text, replacing{" "}
            <code>indexString</code> with an argument.
        </p>
        <Command
            name="TextProps.clickURL"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "indexString", type: "string" },
                { key: "url", type: "string" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_prop_click_page"
        summary="TextProp.clickPage()"
        keywords="change_page clickevent"
    >
        <p>
            Change page of book when FormattedString text is clicked,{" "}
            <code>local</code>
            will delete the property after it has been used once.
        </p>
        <p>
            Add change_page clickEvent to the text. <b>Only</b> works in books!
        </p>
        <Command
            name="TextProp.clickPage"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "page", type: "integer" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_props_click_page"
        summary="TextProps.clickPage()"
        keywords="change_page clickevent"
    >
        <p>
            Similar to <code>TextProp.clickPage</code>, but you can use a
            parameter when referencing it in FormattedText, similar to macro
            factory arguments.
        </p>
        <p>
            Add argument-based change_page clickEvent to the text.
            <b>Only</b> works in books!
        </p>
        <Command
            name="TextProps.clickPage"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_prop_clipboard"
        summary="TextProp.clipboard()"
        keywords="copy_to_clipboard clickevent"
    >
        <p>
            Make copiable text inside FormattedString, <code>local</code>
            will delete the property after it has been used once.
        </p>
        <p>Add copy_to_clipboard clickEvent to the text.</p>
        <Command
            name="TextProp.clipboard"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "text", type: "string" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_props_clipboard"
        summary="TextProps.clipboard()"
        keywords="copy_to_clipboard clickevent"
    >
        <p>
            Similar to <code>TextProp.clipboard</code>, but you can use
            <code>indexString</code> as a parameter within <code>text</code>,
            (same as how it works in the <code>Hardcode</code> functions)
        </p>
        <p>
            Add copy_to_clipboard clickEvent to the text, replacing{" "}
            <code>indexString</code> with an argument.
        </p>
        <Command
            name="TextProps.clipboard"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "indexString", type: "string" },
                { key: "text", type: "string" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_prop_hover_text"
        summary="TextProp.hoverText()"
        keywords="show_text hoverevent"
    >
        <p>
            Create custom hover property for FormattedString, <code>local</code>{" "}
            will delete the property after it has been used once.
        </p>
        <p>Add show_text hoverEvent to the text.</p>
        <Command
            name="TextProp.hoverText"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "text", type: "FormattedString" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_props_hover_text"
        summary="TextProps.hoverText()"
        keywords="show_text hoverevent"
    >
        <p>
            Similar to <code>TextProp.hoverText</code>, but you can use
            <code>indexString</code> as a parameter within <code>text</code>,
            (same as how it works in the <code>Hardcode</code> functions)
        </p>
        <p>
            Add show_text hoverEvent to the text, replacing{" "}
            <code>indexString</code> with an argument.
        </p>
        <Command
            name="TextProps.hoverText"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "indexString", type: "string" },
                { key: "text", type: "FormattedString" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_prop_hover_item"
        summary="TextProp.hoverItem()"
        keywords="show_item hoverevent"
    >
        <p>
            Does the same thing as <code>TextProp.hoverText</code>, but displays
            an item description/tooltip instead of regular text.
        </p>
        <p>Add show_item hoverEvent to the text.</p>
        <Command
            name="TextProp.hoverItem"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "item", type: "JSON" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_props_hover_item"
        summary="TextProps.hoverItem()"
        keywords="show_item hoverevent"
    >
        <p>
            Similar to <code>TextProp.hoverItem</code>, but you can use
            <code>indexString</code> as a parameter within <code>item</code>,
            (same as how it works in the <code>Hardcode</code> functions)
        </p>
        <p>
            Add show_item hoverEvent to the text, replacing{" "}
            <code>indexString</code> with an argument.
        </p>
        <Command
            name="TextProps.hoverItem"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "indexString", type: "string" },
                { key: "item", type: "JSON" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_prop_hover_entity"
        summary="TextProp.hoverEntity()"
        keywords="show_entity hoverevent"
    >
        <p>
            Does the same thing as <code>TextProp.hoverText</code>, but displays
            an entity's name and UUID, instead of regular text.
        </p>
        <p>Add show_entity hoverEvent to the text.</p>
        <Command
            name="TextProp.hoverEntity"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "entity", type: "JSON" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_props_hover_entity"
        summary="TextProps.hoverEntity()"
        keywords="show_entity hoverevent"
    >
        <p>
            Similar to <code>TextProp.hoverEntity</code>, but you can use
            <code>indexString</code> as a parameter within <code>entity</code>,
            (same as how it works in the <code>Hardcode</code> functions)
        </p>
        <p>
            Add show_entity hoverEvent to the text, replacing{" "}
            <code>indexString</code> with an argument.
        </p>
        <Command
            name="TextProps.hoverEntity"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "indexString", type: "string" },
                { key: "entity", type: "JSON" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature id="text_prop_font" summary="TextProp.font()" keywords="">
        <p>
            Use a custom font for FormattedString, <code>local</code> will
            delete the property after it has been used once.
        </p>
        <p>Add run_command clickEvent to the text.</p>
        <Command
            name="TextProp.font"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "font", type: "string" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature id="text_props_font" summary="TextProps.font()" keywords="">
        <p>
            Similar to <code>TextProp.font</code>, but you can use
            <code>indexString</code> as a parameter within <code>font</code>,
            (same as how it works in the <code>Hardcode</code> functions)
        </p>
        <p>
            Add run_command clickEvent to the text, replacing{" "}
            <code>indexString</code> with an argument.
        </p>
        <Command
            name="TextProps.font"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "indexString", type: "string" },
                { key: "font", type: "string" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_prop_keybind"
        summary="TextProp.keybind()"
        keywords="keybind key control"
    >
        <p>
            Display one of the player's keybind (e.g. jump, sneak, attack, etc.)
            as a property inside FormattedString. <code>local</code> will delete
            the property after it has been used once.
        </p>
        <p>Add keybind to the text.</p>
        <Command
            name="TextProp.keybind"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "keybind", type: "string" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_props_keybind"
        summary="TextProps.keybind()"
        keywords="keybind key control"
    >
        <p>
            Similar to <code>TextProp.keybind</code>, but you can use
            <code>indexString</code> as a parameter within <code>keybind</code>,
            (same as how it works in the <code>Hardcode</code> functions)
        </p>
        <p>
            Add keybind to the text, replacing <code>indexString</code> with an
            argument.
        </p>
        <Command
            name="TextProps.keybind"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "indexString", type: "string" },
                { key: "keybind", type: "string" },
                { key: "local", type: "boolean", default: "false" },
            ]}
        />
    </Feature>,
    <Feature
        id="text_prop_nbt"
        summary="TextProp.nbt()"
        keywords="resolve embed nbt"
    >
        <p>
            Embed the NBT path inside FormattedString. <code>interpret</code>{" "}
            determines whether or not to resolve the value of the NBT path as
            JSON text string.
            <code>local</code> will delete the property after it has been used
            once.
        </p>
        <p>Add nbt to the text.</p>
        <Command
            name="TextProp.nbt"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "type", type: "Keyword" },
                { key: "source", type: "string" },
                { key: "path", type: "Keyword" },
                { key: "separator", type: "string", default: '""' },
                { key: "interpret", type: "boolean", default: "false" },
                { key: "local", type: "boolean", default: "false" },
            ]}
            newline
        />
    </Feature>,
    <Feature
        id="text_props_nbt"
        summary="TextProps.nbt()"
        keywords="resolve embed nbt"
    >
        <p>
            Similar to <code>TextProp.nbt</code>, but you can use
            <code>indexString</code> as a parameter within <code>path</code>,
            (same as how it works in the <code>Hardcode</code> functions)
        </p>
        <p>
            Add nbt to the text, replacing <code>indexString</code> in{" "}
            <code>path</code> with an argument.
        </p>
        <Command
            name="TextProps.nbt"
            type="LoadOnly"
            params={[
                { key: "propertyName", type: "string" },
                { key: "indexString", type: "string" },
                { key: "type", type: "Keyword" },
                { key: "source", type: "string" },
                { key: "path", type: "Keyword" },
                { key: "separator", type: "string", default: '""' },
                { key: "interpret", type: "boolean", default: "false" },
                { key: "local", type: "boolean", default: "false" },
            ]}
            newline
        />
    </Feature>,
    <Feature
        id="tag_update"
        summary="Tag.update()"
        keywords="filter specific entities"
    >
        <p>
            Simply remove the tag from <code>removeFrom</code> and add it back
            to <code>selector</code>.
        </p>
        <Command
            name="Tag.update"
            type="JMCFunction"
            params={[
                { key: "selector", type: "TargetSelector" },
                { key: "tag", type: "Keyword" },
                { key: "removeFrom", type: "TargetSelector", default: "@e" },
            ]}
            newline
        />
    </Feature>,
];

export default BuildinFeatures;
