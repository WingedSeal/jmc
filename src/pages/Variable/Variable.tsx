import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";

const Variable = () => {
    return (
        <>
            <section className="min-h-screen bg-secondary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
                <div className="text-secondary text-3xl md:text-6xl mx-auto">
                    Variable
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Variables in JMC always start with <code>$</code>.
                        Any command starting with <code>$</code> will trigger
                        JMC to treat it a a variable command.
                    </p>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Variable Assignment
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Set a variable to an integer. Due to nature of how
                        minecraft scoreboard works, you can assign a variable
                        without declaring it.
                        <CodeBlock>
                            <CodeText type="operator">$</CodeText>
                            {"<variable> "}
                            <CodeText type="operator">=</CodeText>{" "}
                            <CodeText type="number">{"<integer>"}</CodeText>;
                        </CodeBlock>
                        <CodeBlock>
                            <CodeText type="operator">$</CodeText>
                            {"my_variable "}
                            <CodeText type="operator">=</CodeText>{" "}
                            <CodeText type="number">5</CodeText>;
                        </CodeBlock>
                    </p>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Variable Operation
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Perform scoreboard operations, with 6 available
                        operations.
                    </p>
                    <ul className="ml-8 md:ml-10 list-disc">
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
                            set the target score
                        </li>
                    </ul>
                    <CodeBlock>
                        <CodeText type="operator">$</CodeText>
                        {"<variable> "}
                        <CodeText type="operator">{"<operator>"}</CodeText>{" "}
                        <CodeText type="number">{"<integer>"}</CodeText>; <br />
                        <CodeText type="operator">$</CodeText>
                        {"<variable> "}
                        <CodeText type="operator">{"<operator>"}</CodeText>{" "}
                        <CodeText type="operator">$</CodeText>
                        {"<variable>"};
                        <br />
                        <CodeText type="operator">$</CodeText>
                        {"<variable> "}
                        <CodeText type="operator">{"<operator>"}</CodeText>{" "}
                        objective
                        <CodeText type="operator">:</CodeText>
                        selector;
                    </CodeBlock>
                    <CodeBlock>
                        <CodeText type="operator">$</CodeText>
                        my_variable <CodeText type="operator">+=</CodeText>{" "}
                        my_objective
                        <CodeText type="operator">:</CodeText>
                        <CodeText type="param">@s</CodeText>;
                    </CodeBlock>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Scoreboard
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp; Copy value of JMC variable into minecraft
                        scoreboard
                    </p>
                    <CodeBlock>
                        <CodeText type="operator">$</CodeText>
                        {"<variable>"}
                        <CodeText type="operator">{"->"}</CodeText>objective
                        <CodeText type="operator">:</CodeText>
                        selector;
                    </CodeBlock>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Incrementation
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <ul className="ml-8 md:ml-10 list-disc">
                        <li>
                            <code>
                                <CodeText type="operator">$</CodeText>
                                {"<variable>"}
                                <CodeText type="operator">++</CodeText>
                            </code>{" "}
                            is equivalent to{" "}
                            <code>
                                <CodeText type="operator">$</CodeText>
                                {"<variable> "}
                                <CodeText type="operator">+=</CodeText>{" "}
                                <CodeText type="number">1</CodeText>;
                            </code>
                        </li>
                        <li>
                            <code>
                                <CodeText type="operator">$</CodeText>
                                {"<variable>"}
                                <CodeText type="operator">--</CodeText>
                            </code>{" "}
                            is equivalent to{" "}
                            <code>
                                <CodeText type="operator">$</CodeText>
                                {"<variable> "}
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
                        &emsp;To use <code>/scoreboard players get</code>, for{" "}
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
                        <CodeText type="operator">$</CodeText>var
                        <CodeText type="operator">.</CodeText>
                        <CodeText type="function">get</CodeText>();
                    </CodeBlock>
                </div>
                <div className="text-secondary-contrast text-xl md:text-4xl mt-3 md:mt-4">
                    Convert to string
                </div>
                <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                    <p>
                        &emsp;Use{" "}
                        <code>
                            <CodeText type="function">.toString</CodeText>()
                        </code>{" "}
                        method to convert to JSON for tellraw, title, etc. This
                        method is the only one that can be used anywhere in the
                        code. To change the style, pass argument(s) into the
                        method.
                    </p>
                    <CodeBlock>
                        tellraw <CodeText type="param">@a</CodeText> my_var
                        <CodeText type="function">.toString</CodeText>
                        (color<CodeText type="operator">=</CodeText>
                        red<CodeText type="operator">,</CodeText> bold
                        <CodeText type="operator">=</CodeText>true);
                    </CodeBlock>
                </div>
            </section>
        </>
    );
};

export default Variable;
