import Feature from "../../components/Feature";
import CodeBlock, { CodeText, Command } from "../../components/CodeBlock";
import { Tab } from "../../components/CodeBlock/CodeBlock";
import { Link } from "react-router-dom";
import { scrollToHash } from "../../utils/scrollToHash";

const howTo = (
    <Feature
        id="how_to_use"
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
        <Command
            name="Module.function_name"
            type="FunctionType"
            params={[
                {
                    key: "parameter1",
                    type: "ParameterType",
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
            newline
        />
        <p className="text-gray-400">
            Note: A "parameter" is a variable in a function definition. It is a
            placeholder and hence does not have a concrete value. An "argument"
            is a value passed during function invocation.
        </p>
        <ul>
            <li>
                <span>
                    <code>Module.function_name</code> refers to the name of the
                    function. <code>Module</code> is a part of a function name
                    in JMC. If you mistype the name, JMC will assume you are
                    calling your own custom function and throw an error saying
                    "Custom function's parameter is not supported."
                </span>
            </li>
            <li>
                <span>
                    <code>ParameterType</code> is the type of the value that the
                    parameter expects.
                </span>
            </li>
            <li>
                <code>default</code> allow the parameters to be initialized with
                default values if no value is passed. If there's no{" "}
                <code>default</code>, a value is required.
            </li>
            <li>
                <span>
                    <code>FunctionType</code> means the type of the function
                    specifying which condition it can be used in.
                </span>
            </li>
        </ul>
        <br />
        <p>
            Unlike JavaScript, JMC supports "named parameter", which means you
            can specify which argument it is.
        </p>
        <br />
        <p>Parameter types:</p>
        <CodeBlock>
            <CodeText type="class">string</CodeText>{" "}
            <CodeText type="operator">=</CodeText>{" "}
            <CodeText type="string">"string"</CodeText>{" "}
            <CodeText type="comment">
                {"//"} A plain text to be used as is
            </CodeText>
            <br />
            <CodeText type="class">string</CodeText>{" "}
            <CodeText type="operator">=</CodeText>{" "}
            <CodeText type="string">`</CodeText>
            <br />
            <CodeText type="string">
                {" "}
                line1
                <br />
                line2
                <br />`
            </CodeText>{" "}
            <CodeText type="comment">{"//"} A multiline string</CodeText>
            <br />
            <CodeText type="class">FormattedString</CodeText>{" "}
            <CodeText type="operator">=</CodeText>{" "}
            <CodeText type="string">{'"&<gold,bold>Cooler String"'}</CodeText>{" "}
            <CodeText type="comment">
                {"//"} See{" "}
                <Link
                    to="/documentation/built-in-function#formatted_text"
                    onClick={() => {
                        scrollToHash("formatted_text");
                    }}
                >
                    Formatted Text
                </Link>{" "}
                section
            </CodeText>
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
            <CodeText type="class">Criteria</CodeText>{" "}
            <CodeText type="operator">=</CodeText> used.carrot_on_a_stick{" "}
            <CodeText type="comment">{"//"} An scoreboard criteria</CodeText>
            <br />
            <CodeText type="class">Item</CodeText>{" "}
            <CodeText type="operator">=</CodeText> carrot_on_a_stick{" "}
            <CodeText type="comment">{"//"} A minecraft item's id</CodeText>
            <br />
            <CodeText type="class">Keyword</CodeText>{" "}
            <CodeText type="operator">=</CodeText> anyKeyword
            <br />
        </CodeBlock>
        <p>Function types:</p>
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
        <p>To use a function, you can call it like the following.</p>
        <CodeBlock>
            <CodeText type="class">Module</CodeText>
            <CodeText type="operator">.</CodeText>
            <CodeText type="function">function_name</CodeText>(argument1
            <CodeText type="operator">,</CodeText> argument2
            <CodeText type="operator">,</CodeText> parameter3
            <CodeText type="operator">=</CodeText>argument3);
        </CodeBlock>
        <CodeBlock>
            <CodeText type="class">Module</CodeText>
            <CodeText type="operator">.</CodeText>
            <CodeText type="function">function_name</CodeText>(<br />
            <Tab />
            argument1
            <CodeText type="operator">,</CodeText>
            <br />
            <Tab />
            argument2
            <CodeText type="operator">,</CodeText>
            <br />
            <Tab />
            parameter3
            <CodeText type="operator">=</CodeText>argument3
            <br />
            );
        </CodeBlock>
        <p>Example:</p>
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
            <CodeText type="comment">{"// FormattedString"}</CodeText>
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
            <CodeText type="comment">
                {"// List<FormattedString> (List of FormattedString)"}
            </CodeText>
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
            <CodeText type="comment">
                {"// ArrowFunction (A type of Function)"}
            </CodeText>
            <br />
            );{" "}
            <CodeText type="comment">
                {
                    '// "-> LoadOnly" means this function can only be used in load (outside any function)'
                }
            </CodeText>
            <br />
            execute as @a run <CodeText type="class">Item</CodeText>
            <CodeText type="operator">.</CodeText>
            <CodeText type="function">give</CodeText>(veryCoolSword);
        </CodeBlock>
    </Feature>
);

export default howTo;
