import Feature from "../../components/Feature";
import CodeBlock, { CodeText, Command } from "../../components/CodeBlock";
import { Tab } from "../../components/CodeBlock/CodeBlock";

const howTo = (
    <Feature
        id="how_to_read"
        summary="How to use built-in function"
        keywords="tutorial explaination parameter type help basic"
        className="text-tertiary"
    >
        <p>Documentation will always be in the following format.</p>
        <Command
            name="Module.function_name"
            type="FunctionType"
            params={[
                {
                    key: "parameter1",
                    type: "ParameterType",
                    default: "default",
                },
                {
                    key: "parameter2",
                    type: "ParameterType",
                    default: "default",
                },
                {
                    key: "parameter3",
                    type: "ParameterType",
                    default: "default",
                },
            ]}
        />
        <p>
            Default means that you do not need to provide the argument and JMC
            wil automatically fallback to that value
        </p>
        <p>
            Module is actually a part of the function name and bare no special
            meaning. If you mistype the name, JMC will assume you are calling
            your own custom function and throw an error saying "Custom
            function's parameter is not supported."
        </p>
        <p>
            Unlike JavaScript, JMC actually support named parameter, which mean
            you can specify which argument it is.
        </p>
        <p>To use a function, just call it like this.</p>
        <CodeBlock copy_text="">
            <CodeText type="class">Module</CodeText>
            <CodeText type="operator">.</CodeText>
            <CodeText type="function">function_name</CodeText>(argument1
            <CodeText type="operator">,</CodeText> argument2
            <CodeText type="operator">,</CodeText> parameter3
            <CodeText type="operator">=</CodeText>argument3);
        </CodeBlock>
        <p>Parameter types are</p>
        <CodeBlock>
            <CodeText type="class">string</CodeText>{" "}
            <CodeText type="operator">=</CodeText>{" "}
            <CodeText type="string">"string"</CodeText>
            <br />
            <CodeText type="class">integer</CodeText>{" "}
            <CodeText type="operator">=</CodeText>{" "}
            <CodeText type="number">1</CodeText>
            <br />
            <CodeText type="class">float</CodeText>{" "}
            <CodeText type="operator">=</CodeText>{" "}
            <CodeText type="number">9.99</CodeText>{" "}
            <CodeText type="comment">{"//"} Also known as decimal</CodeText>
            <br />
            <CodeText type="class">boolean</CodeText>{" "}
            <CodeText type="operator">=</CodeText>{" "}
            <CodeText type="operator">true or false</CodeText>
            <br />
            <CodeText type="class">JSON</CodeText>{" "}
            <CodeText type="operator">=</CodeText> {"{"}
            <CodeText type="string">"key1"</CodeText>
            <CodeText type="operator">:</CodeText>
            <CodeText type="string">"value"</CodeText>
            <CodeText type="operator">,</CodeText>{" "}
            <CodeText type="string">"key2"</CodeText>
            <CodeText type="operator">:</CodeText>
            <CodeText type="string">"value"</CodeText>
            {"}"}
            <br />
            <CodeText type="class">
                JSObject{"<ParameterType1, ParameterType2>"}
            </CodeText>{" "}
            <CodeText type="operator">=</CodeText> {"{"}
            <CodeText type="class">ParameterType1</CodeText>
            <CodeText type="operator">:</CodeText>{" "}
            <CodeText type="class">ParameterType2</CodeText>
            <CodeText type="operator">,</CodeText>{" "}
            <CodeText type="class">ParameterType1</CodeText>
            <CodeText type="operator">:</CodeText>{" "}
            <CodeText type="class">ParameterType2</CodeText>
            {"}"}
            <br />
            <CodeText type="class">List{"<ParameterType>"}</CodeText>{" "}
            <CodeText type="operator">=</CodeText> [
            <CodeText type="class">ParameterType</CodeText>
            <CodeText type="operator">,</CodeText>{" "}
            <CodeText type="class">ParameterType</CodeText>]<br />
            <CodeText type="class">ArrowFunction</CodeText>{" "}
            <CodeText type="operator">=</CodeText> {"()"}
            <CodeText type="keyword">{"=>"}</CodeText>
            {"{"}say <CodeText type="string">"Hello World"</CodeText>;{"}"}{" "}
            <CodeText type="comment">
                {"//"} Unnamed function that's meant to be used once
            </CodeText>
            <br />
            <CodeText type="class">FunctionName</CodeText>{" "}
            <CodeText type="operator">=</CodeText> my_function{" "}
            <CodeText type="comment">
                {"//"} Function that's already defined elsewhere
            </CodeText>
            <br />
            <CodeText type="class">Function</CodeText>{" "}
            <CodeText type="operator">=</CodeText>{" "}
            <CodeText type="class">ArrowFunction</CodeText>{" "}
            <CodeText type="operator">or</CodeText>{" "}
            <CodeText type="class">FunctionName</CodeText>
            <br />
            <CodeText type="class">TargetSelector</CodeText>{" "}
            <CodeText type="operator">=</CodeText> @a[tag
            <CodeText type="operator">=</CodeText>test]
            <br />
            <CodeText type="class">Scoreboard</CodeText>{" "}
            <CodeText type="operator">=</CodeText> objective
            <CodeText type="operator">:</CodeText>
            <CodeText type="class">TargetSelector</CodeText>{" "}
            <CodeText type="operator">or</CodeText> $variable
            <br />
            <CodeText type="class">ScoreboardInteger</CodeText>{" "}
            <CodeText type="operator">=</CodeText>{" "}
            <CodeText type="class">integer</CodeText>{" "}
            <CodeText type="operator">or</CodeText>{" "}
            <CodeText type="class">Scoreboard</CodeText>
            <br />
            <CodeText type="class">Objective</CodeText>{" "}
            <CodeText type="operator">=</CodeText> my_objective{" "}
            <CodeText type="comment">{"//"} An existing objective</CodeText>
            <br />
            <CodeText type="class">Item</CodeText>{" "}
            <CodeText type="operator">=</CodeText> carrot_on_a_stick{" "}
            <CodeText type="comment">{"//"} A minecraft item's id</CodeText>
            <br />
            <CodeText type="class">Keyword</CodeText>{" "}
            <CodeText type="operator">=</CodeText> anyKeyword
            <br />
        </CodeBlock>
        <p>Function types are</p>
        <CodeBlock>
            - <CodeText type="class">Bool</CodeText>{" "}
            <CodeText type="operator">:</CodeText> Used in condition such as if,
            while etc.
            <br />
            if ( <CodeText type="class">Bool</CodeText>
            <CodeText type="operator">.</CodeText>
            <CodeText type="function">example</CodeText>(argument) ) {"{"}
            <br />
            <Tab />
            say <CodeText type="string">"Hello World"</CodeText>;
            <br />
            {"}"}
            <br />- <CodeText type="class">ExecuteExcluded</CodeText>{" "}
            <CodeText type="operator">:</CodeText> Cannot be used in execute
            command
            <br />- <CodeText type="class">LoadOnly</CodeText>{" "}
            <CodeText type="operator">:</CodeText> Can only be used in load
            (Can't be used inside any function)
            <br />- <CodeText type="class">LoadOnce</CodeText>{" "}
            <CodeText type="operator">:</CodeText> Can only be used in load and
            only once
            <br />- <CodeText type="class">VariableOperation</CodeText>{" "}
            <CodeText type="operator">:</CodeText> Need to store result into
            minecraft scoreboard or jmc variable
            <br />
            $my_var <CodeText type="operator">=</CodeText>{" "}
            <CodeText type="class">VariableOperation</CodeText>
            <CodeText type="operator">.</CodeText>
            <CodeText type="function">example</CodeText>(argument)
            <br />- <CodeText type="class">JMCFunction</CodeText>{" "}
            <CodeText type="operator">:</CodeText> Normal JMC function without
            restrictions
            <br />
        </CodeBlock>
        <p>Example:</p>
        <Command
            name="Item.create"
            type="LoadOnly"
            params={[
                { key: "itemId", type: "Keyword" },
                { key: "itemType", type: "Item" },
                { key: "displayName", type: "string" },
                { key: "lore", type: "List<string>", default: "[]" },
                { key: "nbt", type: "JSObject", default: "{}" },
                { key: "onClick", type: "Function", default: "()=>{}" },
            ]}
        />
        <CodeBlock>
            <CodeText type="class">Item</CodeText>
            <CodeText type="operator">.</CodeText>
            <CodeText type="function">create</CodeText>(<br />
            <Tab />
            veryCoolSword<CodeText type="operator">,</CodeText>{" "}
            <CodeText type="comment">{"// Keyword"}</CodeText>
            <br />
            <Tab />
            carrot_on_a_stick
            <CodeText type="operator">,</CodeText>{" "}
            <CodeText type="comment">{"// Item"}</CodeText>
            <br />
            <Tab />
            <CodeText type="string">
                {'"&<gold, bold>A very cool sword"'}
            </CodeText>
            <CodeText type="operator">,</CodeText>{" "}
            <CodeText type="comment">{"// string"}</CodeText>
            <br />
            <Tab />[
            <CodeText type="string">
                {'"&<red>It is, indeed, very cool."'}
            </CodeText>
            <CodeText type="operator">,</CodeText>
            <br />
            <Tab />
            <CodeText type="string">
                {'"&<red>Right click to be cool."'}
            </CodeText>
            ]<CodeText type="operator">,</CodeText>{" "}
            <CodeText type="comment">{"// List<string>"}</CodeText>
            <br />
            <Tab />
            nbt<CodeText type="operator">=</CodeText>
            {"{"}CustomModelData<CodeText type="operator">:</CodeText>
            <CodeText type="number">100</CodeText>
            {"}"}
            <CodeText type="operator">,</CodeText>{" "}
            <CodeText type="comment">{"// JSObject"}</CodeText>
            <br />
            <Tab />
            onClick<CodeText type="operator">=</CodeText>
            {"()"}
            <CodeText type="keyword">{"=>"}</CodeText>
            {"{"}
            <br />
            <Tab />
            <Tab />
            say <CodeText type="string">"I'm very cool"</CodeText>;
            <br />
            <Tab />
            <Tab />
            effect give @s speed 1 255 True;
            <br />
            <Tab />
            {"} "}
            <CodeText type="comment">{"// ArrowFunction"}</CodeText>
            <br />
            );
            <br />
            execute as @a run <CodeText type="class">Item</CodeText>
            <CodeText type="operator">.</CodeText>
            <CodeText type="function">give</CodeText>(veryCoolSword);
        </CodeBlock>
    </Feature>
);

const BuildinFeatures = [
    howTo,
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
                { key: "objective", type: "Objective" },
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
    <Feature id="item_create" summary="Item.create()" keywords="new">
        <p>Create a custom item and save it for further use.</p>
        <p>onClick can only be used with "carrot_on_a_stick" itemType.</p>
        <p>
            itemId is the unique name of this item so that it can be referenced
            in other Item function.
        </p>
        <Command
            name="Item.create"
            type="LoadOnly"
            params={[
                { key: "itemId", type: "Keyword" },
                { key: "itemType", type: "Item" },
                { key: "displayName", type: "string" },
                { key: "lore", type: "List<string>", default: "[]" },
                { key: "nbt", type: "JSObject", default: "{}" },
                { key: "onClick", type: "Function", default: "()=>{}" },
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
                href="https://en.wikipedia.org/wiki/Linear_congruential_generato1"
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
        <p>
            Whether the timer of the entity running it(<code>@s</code>) is over
            or not.
        </p>
        <Command
            name="Timer.isOver"
            type="Boolean"
            params={[{ key: "objective", type: "Objective" }]}
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
                { key: "boxSize", type: "float", default: "0.001" },
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
];

export default BuildinFeatures;
