import Feature from "../../components/Feature";
import CodeBlock, { CodeText, Command } from "../../components/CodeBlock";
import howTo from "./HowTo";
import formattedText from "./FormattedText";
import { Tab } from "../../components/CodeBlock/CodeBlock";

const BuildinFeatures = [
    howTo,
    formattedText,
    <Feature
        id="player_on_event"
        summary="Player.onEvent()"
        keywords="scoreboard jump drop craft stats change"
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
        keywords="world"
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
    <Feature id="player_rejoin" summary="Player.rejoin()" keywords="leave">
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
                { key: "displayName", type: "FormattedString" },
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
            name="Item.create"
            type="LoadOnly"
            params={[
                { key: "itemId", type: "Keyword" },
                { key: "variant", type: "Keyword" },
                { key: "displayName", type: "FormattedString" },
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
                { key: "mob_type", type: "Keyword" },
                { key: "displayName", type: "FormattedString" },
                { key: "onPlace", type: "Function", default: "()=>{}" },
                { key: "lore", type: "List<FormattedString>", default: "[]" },
                { key: "nbt", type: "JSObject", default: "{}" },
            ]}
            newline
        />
    </Feature>,
    <Feature id="item_give" summary="Item.give()" keywords="gave">
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
    <Feature id="math_sqrt" summary="Math.sqrt()" keywords="square root">
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
        keywords="randomize randomization lcg linear congruential generator"
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
                { key: "min", type: "integer", default: "1" },
                { key: "max", type: "integer", default: "2147483647" },
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
        keywords="copy paste list"
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
                { key: "strings", type: "List" },
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
            name="Trigger.setup"
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
                <code>target</code> is acceptable target for collution.
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
            Ignore any parsing and output the command directly. Mainly used for
            bypass compiler failures.
        </p>
        <Command
            name="JMC.put"
            type="JMCFunction"
            params={[{ key: "command", type: "string" }]}
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
                { key: "type", type: "Keyword" },
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
                { key: "type1", type: "Keyword" },
                { key: "source1", type: "string" },
                { key: "path1", type: "Keyword" },
                { key: "type2", type: "Keyword" },
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
    <Feature id="team_add" summary="Team.add()" keywords="vanilla">
        <p>Add team, an alternative to vanilla syntax</p>
        <Command
            name="Team.add"
            type="JMCFunction"
            params={[
                { key: "id", type: "Keyword" },
                { key: "name", type: "FormattedString", default: '""' },
            ]}
        />
    </Feature>,
];

export default BuildinFeatures;