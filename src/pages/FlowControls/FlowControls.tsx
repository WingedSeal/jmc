import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";

const FlowControls = () => {
    return (
        <>
            <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
                <div className="text-primary text-3xl md:text-6xl mx-auto">
                    Flow controls
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Condition
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;A condition which can be used in flow controls as{" "}
                        {"<condition>"}. And due to minecraft command syntax
                        which uses <code>=</code> instead of <code>==</code>,
                        JMC will treat both as the same thing.
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">$</CodeText>
                        {"<variable>"} ({" "}
                        <CodeText type="operator">{">="}</CodeText> |{" "}
                        <CodeText type="operator">{"<="}</CodeText> |{" "}
                        <CodeText type="operator">{"="}</CodeText> |{" "}
                        <CodeText type="operator">{"=="}</CodeText> |{" "}
                        <CodeText type="operator">{">"}</CodeText> |{" "}
                        <CodeText type="operator">{"<"}</CodeText> ){" "}
                        <CodeText type="number">{"<integer>"}</CodeText>
                        <br />
                        <CodeText type="operator">$</CodeText>
                        {"<variable>"} ({" "}
                        <CodeText type="operator">{">="}</CodeText> |{" "}
                        <CodeText type="operator">{"<="}</CodeText> |{" "}
                        <CodeText type="operator">{"="}</CodeText> |{" "}
                        <CodeText type="operator">{"=="}</CodeText> |{" "}
                        <CodeText type="operator">{">"}</CodeText> |{" "}
                        <CodeText type="operator">{"<"}</CodeText> ){" "}
                        <CodeText type="operator">$</CodeText>
                        {"<variable>"}
                        <br />
                        <CodeText type="operator">$</CodeText>
                        {"<variable>"} ({" "}
                        <CodeText type="operator">{"="}</CodeText> |{" "}
                        <CodeText type="operator">{"=="}</CodeText> ) [
                        <CodeText type="number">
                            {"<inclusive_min_integer>"}
                        </CodeText>
                        ]<CodeText type="operator">..</CodeText>[
                        <CodeText type="number">
                            {"<inclusive_max_integer>"}
                        </CodeText>
                        ]
                    </CodeBlock>
                    <p>&emsp;For example:</p>
                    <CodeBlock>
                        <CodeText type="keyword">if</CodeText> (
                        <CodeText type="operator">$</CodeText>deathCount
                        <CodeText type="operator">{">"}</CodeText>
                        <CodeText type="number">5</CodeText> ) {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">"More than 5 death!"</CodeText>;
                        <br />
                        {"}"} <CodeText type="keyword">else if</CodeText> (
                        <CodeText type="operator">$</CodeText>deathCount
                        <CodeText type="operator">{"=="}</CodeText>
                        <CodeText type="number">2</CodeText>
                        <CodeText type="operator">..</CodeText>
                        <CodeText type="number">3</CodeText> ) {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">
                            "Between 2 to 3 death!"
                        </CodeText>
                        ;
                        <br />
                        {"}"}
                        <br />
                    </CodeBlock>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Logic Gate
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;In <code>{"<condition>"}</code>. You are allowed
                        to use following logic gates.
                        <ul className="ml-4 md:ml-6 list-disc list-inside">
                            <li>
                                <code>()</code> Parenthesis
                            </li>
                            <li>
                                <code>||</code> Or
                            </li>
                            <li>
                                <code>&&</code> And
                            </li>
                            <li>
                                <code>!</code> Not
                            </li>
                        </ul>
                    </p>
                    <CodeBlock>
                        <CodeText type="keyword">if</CodeText> (entity{" "}
                        <CodeText type="param">@s</CodeText>
                        [type<CodeText type="operator">
                            =
                        </CodeText>skeleton]{" "}
                        <CodeText type="operator">||</CodeText> (entity{" "}
                        <CodeText type="param">@s</CodeText>
                        [type<CodeText type="operator">=</CodeText>zombie]{" "}
                        <CodeText type="operator">&&</CodeText>{" "}
                        <CodeText type="operator">$</CodeText>deathCount
                        <CodeText type="operator">{">"}</CodeText>
                        <CodeText type="number">5</CodeText>)) {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">
                            "I'm either a zombie with more than 5 deaths or any
                            skeleton."
                        </CodeText>
                        ;
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    If & Else
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Simulate programming languages' <code>if</code>-
                        <code>else</code> using temporary variable and
                        "anonymouse function". So you can write if/else in
                        JavaScript and the compiler will handle the logic and
                        optimization for you. The chain will be terminated once
                        a codition is satisfied.
                    </p>
                    <CodeBlock>
                        <CodeText type="keyword">if</CodeText> ({"<condition>"}){" "}
                        {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">
                            "If {"<condition>"} is true."
                        </CodeText>
                        ;
                        <br />
                        {"}"} <CodeText type="keyword">else if</CodeText> (
                        {"<condition>"}) {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">
                            "If the first {"<condition>"} is false and this one
                            is true."
                        </CodeText>
                        ;
                        <br />
                        {"}"} <CodeText type="keyword">else</CodeText> {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">
                            "If none of the {"<condition>"} is true."
                        </CodeText>
                        ;
                        <br />
                        {"}"}
                        <br />
                        <br />
                        <CodeText type="keyword">if</CodeText> ({"<condition>"}){" "}
                        {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">
                            "If {"<condition>"} is true."
                        </CodeText>
                        ;
                        <br />
                        {"}"} <CodeText type="keyword">else</CodeText> {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">
                            "If first {"<condition>"} is false."
                        </CodeText>
                        ;
                        <br />
                        {"}"}
                        <br />
                        <br />
                        <CodeText type="keyword">if</CodeText> ({"<condition>"}){" "}
                        {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">
                            "If {"<condition>"} is true."
                        </CodeText>
                        ;
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    While Loop
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Simulate programming languages' While loop which
                        continue running commands inside code block until the
                        condition is no longer met using recursion. By
                        definition, it's possible that{" "}
                        <span className="text-warning">
                            you accidentally cause infinite recursion
                        </span>{" "}
                        in while loop. Be extremely aware of that.
                    </p>
                    <CodeBlock>
                        <CodeText type="keyword">while</CodeText> (
                        {"<condition>"}) {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">
                            "Keep running as long as the {"<condition>"} is
                            true."
                        </CodeText>
                        ;
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Do-While Loop
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Similar to while loop, but run the function for
                        the first time before checking for condition. (
                        <span className="text-warning">
                            Don't forget semicolon!
                        </span>
                        )
                    </p>
                    <CodeBlock>
                        <CodeText type="keyword">do</CodeText> {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">
                            "Run at least once and keep running as long as the{" "}
                            {"<condition>"} is true."
                        </CodeText>
                        ;
                        <br />
                        {"}"} <CodeText type="keyword">while</CodeText> (
                        {"<condition>"});
                    </CodeBlock>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    For Loop
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Simulate Javascript's for-loop. It consist of 3
                        statements.
                    </p>
                    <ol className="ml-4 md:ml-6 list-decimal list-inside">
                        <li>
                            <code>
                                <CodeText type="operator">$</CodeText>
                                {"<variable> "}
                                <CodeText type="operator">=</CodeText> (
                                <CodeText type="number">{"<integer>"}</CodeText>
                                <CodeText type="operator">|</CodeText>
                                <CodeText type="operator">$</CodeText>
                                {"<variable>"}
                                <CodeText type="operator">|</CodeText>
                                objective
                                <CodeText type="operator">:</CodeText>
                                selector);
                            </code>{" "}
                            is executed (one time) before the execution of the
                            code block.{" "}
                            <span className="text-warning">
                                And it must be variable assignment with
                                integer/variable/scoreboard and nothing else.
                            </span>
                        </li>
                        <li>
                            <code>{"condition"}</code> defines the condition for
                            executing the code block.
                        </li>
                        <li>
                            <code>{"statement"}</code> is executed (every time)
                            after the code block has been executed.
                        </li>
                    </ol>
                    <CodeBlock>
                        <CodeText type="keyword">for</CodeText>{" "}
                        {"(<statement1>;<statement2>;<statement3>)"} {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">"Code Example"</CodeText>;<br />
                        {"}"}
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="keyword">for</CodeText> (
                        <CodeText type="operator">$</CodeText>i
                        <CodeText type="operator">=</CodeText>
                        <CodeText type="number">0</CodeText>;
                        <CodeText type="operator">$</CodeText>i
                        <CodeText type="operator">{"<"}</CodeText>
                        <CodeText type="number">10</CodeText>;
                        <CodeText type="operator">$</CodeText>i
                        <CodeText type="operator">++</CodeText>) {"{"}
                        <br />
                        &emsp;say{" "}
                        <CodeText type="string">"Code Example"</CodeText>;<br />
                        {"}"}
                    </CodeBlock>
                </div>
                <div className="text-primary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Switch Case
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Perfect for optimization of your code. JMC's
                        switch case will use{" "}
                        <a
                            href="https://en.wikipedia.org/wiki/Binary_search_tree"
                            className="underline"
                            target="_blank"
                            rel="noreferrer"
                        >
                            Binary search
                        </a>{" "}
                        tree with{" "}
                        <a
                            href="https://en.wikipedia.org/wiki/Binary_search_algorithm"
                            className="underline"
                            target="_blank"
                            rel="noreferrer"
                        >
                            Binary search algorithm
                        </a>{" "}
                        to reduce{" "}
                        <a
                            href="https://en.wikipedia.org/wiki/Time_complexity"
                            className="underline"
                            target="_blank"
                            rel="noreferrer"
                        >
                            Time Complexity
                        </a>{" "}
                        of searching for function dedicated to a value of
                        variable to <code>O(logn)</code>. Switch Case will run
                        commands according to the value of given variable.
                    </p>
                    <p>
                        &emsp;But performance come with cost of{" "}
                        <span className="text-warning">restrictions</span>.
                    </p>
                    <ul className="ml-4 md:ml-6 list-disc list-inside">
                        <li>
                            Case can only starts at 1 and increase in ascending
                            order.
                        </li>
                        <li>
                            You cannot skip a number. Case n+1 must comes after
                            Case n.
                        </li>
                        <li>
                            You are required to{" "}
                            <a
                                href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/break"
                                className="underline"
                                target="_blank"
                                rel="noreferrer"
                            >
                                break
                            </a>{" "}
                            out of switch statements. Eventhough, you are not
                            required to explicitly use the <code>break</code>{" "}
                            keyword, JMC will do that for you.
                        </li>
                        <li>
                            Default case cannot be added in JMC. (It is a case
                            that runs when nothing matches.)
                        </li>
                    </ul>
                    <CodeBlock>
                        <CodeText type="keyword">switch</CodeText>(
                        <CodeText type="operator">$</CodeText>
                        {"<variable>"}) {"{"}
                        <br />
                        &emsp;<CodeText type="keyword">case</CodeText>{" "}
                        <CodeText type="number">1</CodeText>
                        <CodeText type="operator">:</CodeText>
                        <br />
                        &emsp;&emsp;say{" "}
                        <CodeText type="string">"If $variable is 1"</CodeText>;
                        <br />
                        &emsp;<CodeText type="keyword">case</CodeText>{" "}
                        <CodeText type="number">2</CodeText>
                        <CodeText type="operator">:</CodeText>
                        <br />
                        &emsp;&emsp;say{" "}
                        <CodeText type="string">"If $variable is 2"</CodeText>;
                        <br />
                        &emsp;<CodeText type="keyword">case</CodeText>{" "}
                        <CodeText type="number">3</CodeText>
                        <CodeText type="operator">:</CodeText>
                        <br />
                        &emsp;&emsp;say{" "}
                        <CodeText type="string">"If $variable is 3"</CodeText>;
                        <br />
                        {"}"}
                    </CodeBlock>
                </div>
            </section>
        </>
    );
};

export default FlowControls;
