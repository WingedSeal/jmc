import React from "react";
import Feature from "../../components/Feature";
import CodeBlock, { CodeText, Command } from "../../components/CodeBlock";

const BuiltInFunction = () => {
    return <section className="bg-secondary-dark min-h-screen w-screen flex flex-col px-2 md:px-10 pt-[17vh]">
        <Feature id="how_to_read" summary="How to use built-in function" keywords="tutorial explaination parameter type help">
            <p>Documentation will always be in the following format.</p>
            <Command name="Module.function_name" type="FunctionType" params={[
                { key: "parameter1", type: "ParameterType", default: "default" },
                { key: "parameter2", type: "ParameterType", default: "default" },
                { key: "parameter3", type: "ParameterType", default: "default" }
            ]} />
            <p>Module is actually a part of the function name and bare no special meaning. If you mistype the name, JMC will assume you are calling your own custom function and throw an error saying "Custom function's parameter is not supported."</p>
            <p>Unlike JavaScript, JMC actually support named parameter, which mean you can specify which argument it is.</p>
            <p>To use a function, just call it like this.</p>
            <CodeBlock copy_text="">
                <CodeText type="class">Module</CodeText><CodeText type="operator">.</CodeText><CodeText type="function">function_name</CodeText>(argument1<CodeText type="operator">,</CodeText> argument2<CodeText type="operator">,</CodeText> parameter3<CodeText type="operator">=</CodeText>argument3);
            </CodeBlock>
            <p>Parameter types are</p>
            <CodeBlock>
                <CodeText type="class">string</CodeText> <CodeText type="operator">=</CodeText> <CodeText type="string">"string"</CodeText><br />
                <CodeText type="class">integer</CodeText> <CodeText type="operator">=</CodeText> <CodeText type="number">1</CodeText><br />
                <CodeText type="class">float</CodeText> <CodeText type="operator">=</CodeText> <CodeText type="number">9.99</CodeText><br />
                <CodeText type="class">JSON</CodeText> <CodeText type="operator">=</CodeText> {'{'}<CodeText type="string">"key1"</CodeText><CodeText type="operator">:</CodeText><CodeText type="string">"value"</CodeText><CodeText type="operator">,</CodeText> <CodeText type="string">"key2"</CodeText><CodeText type="operator">:</CodeText><CodeText type="string">"value"</CodeText>{'}'}<br />
                <CodeText type="class">JSObject{"<ParameterType1, ParameterType2>"}</CodeText> <CodeText type="operator">=</CodeText> {'{'}<CodeText type="class">ParameterType1</CodeText><CodeText type="operator">:</CodeText> <CodeText type="class">ParameterType2</CodeText><CodeText type="operator">,</CodeText> <CodeText type="class">ParameterType1</CodeText><CodeText type="operator">:</CodeText> <CodeText type="class">ParameterType2</CodeText>{'}'}<br />
                <CodeText type="class">List{"<ParameterType>"}</CodeText> <CodeText type="operator">=</CodeText> [<CodeText type="class">ParameterType</CodeText><CodeText type="operator">,</CodeText> <CodeText type="class">ParameterType</CodeText>]<br />
                <CodeText type="class">ArrowFunction</CodeText> <CodeText type="operator">=</CodeText> {'()=>{'}say <CodeText type="string">"Hello World"</CodeText>;{'}'}<br />
                <CodeText type="class">FunctionName</CodeText> <CodeText type="operator">=</CodeText> my_function<br />
                <CodeText type="class">Function</CodeText> <CodeText type="operator">=</CodeText> <CodeText type="class">ArrowFunction</CodeText> <CodeText type="operator">or</CodeText> <CodeText type="class">FunctionName</CodeText><br />
                <CodeText type="class">TargetSelector</CodeText> <CodeText type="operator">=</CodeText> @a[tag<CodeText type="operator">=</CodeText>test]<br />
                <CodeText type="class">Scoreboard</CodeText> <CodeText type="operator">=</CodeText> objective<CodeText type="operator">:</CodeText><CodeText type="class">TargetSelector</CodeText> <CodeText type="operator">or</CodeText> $variable<br />
                <CodeText type="class">ScoreboardInteger</CodeText> <CodeText type="operator">=</CodeText> <CodeText type="class">integer</CodeText> <CodeText type="operator">or</CodeText> <CodeText type="class">Scoreboard</CodeText><br />
                <CodeText type="class">Objective</CodeText> <CodeText type="operator">=</CodeText> my_objective<br />
                <CodeText type="class">Keyword</CodeText> <CodeText type="operator">=</CodeText> anyKeyword<br />
            </CodeBlock>
            <p>Function types are</p>
            <CodeBlock>
                - <CodeText type="class">Bool</CodeText> <CodeText type="operator">:</CodeText> Used in condition such as if, while etc.<br />
                if ( <CodeText type="class">Bool</CodeText><CodeText type="operator">.</CodeText><CodeText type="function">example</CodeText>(argument) ) {'{'}<br />&emsp;say <CodeText type="string">"Hello World"</CodeText>;<br />{'}'}<br />
                - <CodeText type="class">ExecuteExcluded</CodeText> <CodeText type="operator">:</CodeText> Cannot be used in execute command<br />
                - <CodeText type="class">LoadOnly</CodeText> <CodeText type="operator">:</CodeText> Can only be used in load (Can't be used inside any function)<br />
                - <CodeText type="class">LoadOnce</CodeText> <CodeText type="operator">:</CodeText> Can only be used in load and only once<br />
                - <CodeText type="class">VariableOperation</CodeText> <CodeText type="operator">:</CodeText> Need to store result into minecraft scoreboard or jmc variable<br />
                $my_var <CodeText type="operator">=</CodeText> <CodeText type="class">VariableOperation</CodeText><CodeText type="operator">.</CodeText><CodeText type="function">example</CodeText>(argument)<br />
                - <CodeText type="class">JMCFunction</CodeText> <CodeText type="operator">:</CodeText> Normal JMC function without restrictions<br />
            </CodeBlock>
            <p>Example:</p>
            <CodeBlock>
                <CodeText type="class">Item</CodeText><CodeText type="operator">.</CodeText><CodeText type="function">create</CodeText>(<br />
                &emsp;veryCoolSword<CodeText type="operator">,</CodeText><br />
                &emsp;carrot_on_a_stick<CodeText type="operator">,</CodeText><br />
                &emsp;<CodeText type="string">{'"&<gold, bold>A very cool sword"'}</CodeText><CodeText type="operator">,</CodeText><br />
                &emsp;[<CodeText type="string">{'"&<red>It is, indeed, very cool."'}</CodeText><CodeText type="operator">,</CodeText><br />
                &emsp;<CodeText type="string">{'"&<red>Right click to be cool."'}</CodeText>]<CodeText type="operator">,</CodeText><br />
                &emsp;nbt<CodeText type="operator">=</CodeText>{'{'}CustomModelData<CodeText type="operator">:</CodeText><CodeText type="number">100</CodeText>{'}'}<CodeText type="operator">,</CodeText><br />
                &emsp;onClick<CodeText type="operator">=</CodeText>{'()=>{'}<br />
                &emsp;&emsp;say <CodeText type="string">"I'm very cool"</CodeText>;<br />
                &emsp;&emsp;effect give @s speed 1 255 True;<br />
                );<br />
                execute as @a run <CodeText type="class">Item</CodeText><CodeText type="operator">.</CodeText><CodeText type="function">give</CodeText>(veryCoolSword);
            </CodeBlock>


        </Feature>
        <Feature id="player_on_event" summary="Player.onEvent()" keywords="scoreboard jump drop craft stats change">
            <p>Run commands on positive change of scoreboard and reset the score.</p>
            <Command name="Player.onEvent" type="LoadOnly" params={[
                { key: "objective", type: "Objective" },
                { key: "function", type: "Function" },
            ]} />
        </Feature>
        <Feature id="player_first_join" summary="Player.firstJoin()" keywords="world">
            <p>Run commands as player and at player when joining the World for the first time.</p>
            <p className="text-warning">Revoking all advancements will cause this to be called again.</p>
            <Command name="Player.firstJoin" type="LoadOnce" params={[
                { key: "function", type: "Function" }
            ]} />
        </Feature>
        <Feature id="player_rejoin" summary="Player.rejoin()" keywords="leave">
            <p>Run commands as player and at player when a player leave a world then join back.</p>
            <p className="text-warning">Will not run when player join the world for the first time.</p>
            <Command name="Player.rejoin" type="LoadOnce" params={[
                { key: "function", type: "Function" }
            ]} />
        </Feature>
        <Feature id="player_die" summary="Player.die()" keywords="death respawn died">
            <p>Run onDeath as player and at player's last position when the player die</p>
            <p>Run onRespawn as player and at player spawn location when the player respawn</p>
            <Command name="Player.die" type="LoadOnce" params={[
                { key: "onDeath", type: "Function", default: "()=>{}" },
                { key: "onRespawn", type: "Function", default: "()=>{}" }
            ]} />
        </Feature>
        <Feature id="item_create" summary="Item.create()" keywords="death respawn died">
            <p>Create a custom item and save it for further use.</p>
            <p>onClick can only be used with "carrot_on_a_stick" itemType.</p>
            <p>itemId is the unique name of this item so that it can be referenced in other Item function.</p>
            <Command name="Item.create" type="LoadOnly" params={[
                { key: "itemId", type: "Keyword" },
                { key: "itemType", type: "Keyword" },
                { key: "displayName", type: "String" },
                { key: "lore", type: "List<String>", default: "[]" },
                { key: "nbt", type: "JSObject", default: "{}" },
                { key: "onClick", type: "Function", default: "()=>{}" },
            ]} />
        </Feature>
    </section >
};

export default BuiltInFunction;

