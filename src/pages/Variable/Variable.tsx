import React from "react";
import { Link } from "react-router-dom";
import CodeBlock, { CodeText } from "../../components/CodeBlock";
import { Tab } from "../../components/CodeBlock/CodeBlock";

const Variable = () => {
    return (
        <>
            <section className="min-h-screen bg-secondary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
                <div className="text-secondary text-3xl md:text-6xl mx-auto">
                    Variable
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Variables in JMC always start with <code>$</code>. Any
                        command starting with <code>$</code> will trigger JMC to
                        treat it a a variable command.
                    </p>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Variable Assignment
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Set a variable to an integer. Due to nature of how
                        minecraft scoreboard works, you can assign a variable
                        without declaring it.
                        <CodeBlock>
                            <CodeText type="variable">{"$<variable>"}</CodeText>{" "}
                            <CodeText type="operator">=</CodeText>{" "}
                            <CodeText type="number">{"<integer>"}</CodeText>;
                        </CodeBlock>
                        <CodeBlock>
                            <CodeText type="variable">$my_variable</CodeText>{" "}
                            <CodeText type="operator">=</CodeText>{" "}
                            <CodeText type="number">5</CodeText>;
                        </CodeBlock>
                        <CodeBlock>
                            <CodeText type="variable">$my_variable</CodeText>{" "}
                            <CodeText type="operator">=</CodeText>{" "}
                            <CodeText type="operator">true</CodeText>;{" "}
                            <CodeText type="comment">
                                {"//"} $my_variable = 1
                            </CodeText>
                        </CodeBlock>
                        <CodeBlock>
                            <CodeText type="variable">$my_variable</CodeText>{" "}
                            <CodeText type="operator">=</CodeText>{" "}
                            <CodeText type="operator">false</CodeText>;{" "}
                            <CodeText type="comment">
                                {"//"} $my_variable = 0
                            </CodeText>
                        </CodeBlock>
                    </p>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Variable Operation
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Perform scoreboard operations, with 6 available
                        operations.
                    </p>
                    <ul className="ml-4 md:ml-6 list-disc list-inside">
                        <li>
                            <code>=</code> Assign: Set target's score to
                            source's score
                        </li>
                        <li>
                            <code>+=</code> Addition: Add source's score to
                            target's score
                        </li>
                        <li>
                            <code>-=</code> Subtraction: Subtract source's score
                            from target's score
                        </li>
                        <li>
                            <code>*=</code> Multiplication: Set target's score
                            to the product of the target's and source's scores
                        </li>
                        <li>
                            <code>/=</code> (Integer) Division: Divide target's
                            score by source' scores, and the result will be
                            rounded down to an integer.
                        </li>
                        <li>
                            <code>%=</code> Modulus: Divide target's score by
                            source's score, and use the positive remainder to
                            set the target score.
                        </li>
                        <li>
                            <code>{">"}</code> Maximum: Compare target and source
                            scores, and set target score to whichever is higher.
                        </li>
                        <li>
                            <code>{"<"}</code> Minimum: Compare target and source
                            scores, and set target score to whichever is lower.
                        </li>
                        <li>
                            <code>{"><"}</code> Swap: Swap target's score with 
                            source's score.
                        </li>
                    </ul>
                    <CodeBlock>
                        <CodeText type="variable">{"$<variable>"}</CodeText>{" "}
                        <CodeText type="operator">{"<operator>"}</CodeText>{" "}
                        <CodeText type="number">{"<integer>"}</CodeText>; <br />
                        <CodeText type="variable">
                            {"$<variable>"}
                        </CodeText>{" "}
                        <CodeText type="operator">{"<operator>"}</CodeText>{" "}
                        <CodeText type="variable">{"$<variable>"}</CodeText>;
                        <br />
                        <CodeText type="variable">
                            {"$<variable>"}
                        </CodeText>{" "}
                        <CodeText type="operator">{"<operator>"}</CodeText>{" "}
                        objective
                        <CodeText type="operator">:</CodeText>
                        selector;
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="variable">$my_variable</CodeText>{" "}
                        <CodeText type="operator">+=</CodeText> my_objective
                        <CodeText type="operator">:</CodeText>
                        <CodeText type="param">@s</CodeText>;
                    </CodeBlock>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Scoreboard
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab /> Copy value of JMC variable into minecraft
                        scoreboard
                    </p>
                    <CodeBlock>
                        <CodeText type="variable">{"$<variable>"}</CodeText>
                        <CodeText type="operator">{"->"}</CodeText>objective
                        <CodeText type="operator">:</CodeText>
                        selector;
                    </CodeBlock>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Incrementation
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <ul className="ml-4 md:ml-6 list-disc list-inside">
                        <li>
                            <code>
                                <CodeText type="variable">
                                    {"$<variable>"}
                                </CodeText>
                                <CodeText type="operator">++</CodeText>
                            </code>{" "}
                            is equivalent to{" "}
                            <code>
                                <CodeText type="variable">
                                    {"$<variable>"}
                                </CodeText>{" "}
                                <CodeText type="operator">+=</CodeText>{" "}
                                <CodeText type="number">1</CodeText>;
                            </code>
                        </li>
                        <li>
                            <code>
                                <CodeText type="variable">
                                    {"$<variable>"}
                                </CodeText>
                                <CodeText type="operator">--</CodeText>
                            </code>{" "}
                            is equivalent to{" "}
                            <code>
                                <CodeText type="variable">
                                    {"$<variable>"}
                                </CodeText>{" "}
                                <CodeText type="operator">-=</CodeText>{" "}
                                <CodeText type="number">1</CodeText>;
                            </code>
                        </li>
                    </ul>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Get variable
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        To use <code>/scoreboard players get</code>, for{" "}
                        <code>/execute store</code>, use{" "}
                        <code>
                            <CodeText type="function">.get</CodeText>()
                        </code>{" "}
                        method
                    </p>
                    <CodeBlock>
                        execute store result entity{" "}
                        <CodeText type="param">@s</CodeText> Motion[
                        <CodeText type="number">0</CodeText>] double{" "}
                        <CodeText type="number">0.01</CodeText> run{" "}
                        <CodeText type="variable">$var</CodeText>
                        <CodeText type="operator">.</CodeText>
                        <CodeText type="function">get</CodeText>();
                    </CodeBlock>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Convert to string
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        <Tab />
                        Use{" "}
                        <code>
                            <CodeText type="function">.toString</CodeText>()
                        </code>{" "}
                        method to convert to JSON for tellraw, title, etc. This
                        method is the only one that can be used anywhere in the
                        code. To change the style, pass argument(s) into the
                        method.
                    </p>
                    <p className="text-warning">
                        <Tab />
                        Using{" "}
                        <Link to="/documentation/built-in-function">
                            FormattedText
                        </Link>{" "}
                        is prefered over <code>.toString</code>
                    </p>
                    <CodeBlock>
                        tellraw <CodeText type="param">@a</CodeText>{" "}
                        <CodeText type="variable">$my_var</CodeText>
                        <CodeText type="function">.toString</CodeText>
                        (color<CodeText type="operator">=</CodeText>
                        red<CodeText type="operator">,</CodeText> bold
                        <CodeText type="operator">=</CodeText>true);
                    </CodeBlock>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Execute store
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <CodeBlock>
                        <CodeText type="variable">{"$<variable>"}</CodeText>{" "}
                        <CodeText type="operator">=</CodeText> {"<command>"}{" "}
                        <CodeText type="comment">
                            {"//"} execute store result
                        </CodeText>
                        <br />
                        <CodeText type="variable">
                            {"$<variable>"}
                        </CodeText>{" "}
                        <CodeText type="operator">?=</CodeText> {"<command>"}{" "}
                        <CodeText type="comment">
                            {"//"} execute store success
                        </CodeText>
                    </CodeBlock>
                    <p>
                        <Tab />
                        Example
                    </p>
                    <CodeBlock>
                        <CodeText type="variable">$my_var</CodeText>{" "}
                        <CodeText type="operator">=</CodeText> data get entity
                        @s SelectedItem.tag.my_var;
                    </CodeBlock>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Null Coalescing
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <CodeBlock>
                        <CodeText type="variable">{"$<variable>"}</CodeText>{" "}
                        <CodeText type="operator">??=</CodeText>{" "}
                        <CodeText type="number">
                            {"<integer>/<$variable>/<objective:selector>"}
                        </CodeText>{" "}
                        <CodeText type="comment">
                            {"//"} if null, set to that integer
                        </CodeText>
                    </CodeBlock>
                    <p>
                        <Tab />
                        Example
                    </p>
                    <CodeBlock>
                        <CodeText type="variable">$my_var</CodeText>{" "}
                        <CodeText type="operator">??=</CodeText>{" "}
                        <CodeText type="number">5</CodeText>;
                    </CodeBlock>
                </div>
            </section>
        </>
    );
};

export default Variable;
