import React from "react";
import CodeBlock, { CodeText } from "../../components/CodeBlock";

const LoadTick = () => {
    return (
        <section className="min-h-screen bg-primary-dark flex flex-wrap pt-[14vh] pb-5 md:pt-[15vh] px-4 md:px-11 flex-col items-centers">
            <div className="text-primary text-3xl md:text-6xl mx-auto">
                Load and Loop Function
            </div>
            <div className="text-white text-base md:text-2xl mt-4 max-w-full">
                <p>
                    &emsp;Any commands outside a function will run on reload.
                    The function named <code>__tick__</code> will run every game
                    tick. There are 2 ways to change the name, first is to edit{" "}
                    <code>jmc.txt</code> second is to use header file to define
                    other name as <code>__tick__</code>. If you want more than 1
                    function to run on loop, simply call the function inside{" "}
                    <code>__tick__</code> function.
                </p>
                <p>&emsp;Here's an example</p>
                <CodeBlock>
                    say <CodeText type="string">"Load"</CodeText>;{" "}
                    <CodeText type="comment">
                        {"// This will run on load."}
                    </CodeText>
                    <br />
                    <CodeText type="function">load_function_example</CodeText>
                    ();
                    <br />
                    <CodeText type="keyword">function</CodeText>{" "}
                    <CodeText type="function">__tick__</CodeText>() {"{"}
                    <br />
                    &emsp;say <CodeText type="string">"Loop"</CodeText>;{" "}
                    <CodeText type="comment">
                        {"// This will run every tick."}
                    </CodeText>
                    <br />
                    &emsp;
                    <CodeText type="function">loop_function_example</CodeText>
                    ();
                    <br />
                    {"}"}
                    <br />
                    <CodeText type="keyword">function</CodeText>{" "}
                    <CodeText type="function">load_function_example</CodeText>(){" "}
                    {"{"}
                    <br />
                    &emsp;say <CodeText type="string">"Load"</CodeText>;{" "}
                    <CodeText type="comment">
                        {"// This will also run on load."}
                    </CodeText>
                    <br />
                    {"}"}
                    <br />
                    <CodeText type="keyword">function</CodeText>{" "}
                    <CodeText type="function">loop_function_example</CodeText>(){" "}
                    {"{"}
                    <br />
                    &emsp;say <CodeText type="string">"Loop"</CodeText>;{" "}
                    <CodeText type="comment">
                        {"// This will also run every tick."}
                    </CodeText>
                    <br />
                    {"}"}
                </CodeBlock>

                <p className="text-warning">
                    &emsp;JMC will stop you from defining <code>__load__</code>{" "}
                    function.
                </p>
                <CodeBlock>
                    <CodeText type="keyword">function</CodeText>{" "}
                    <CodeText type="error">__load__</CodeText>() {"{"}
                    <br />
                    &emsp;say{" "}
                    <CodeText type="string">
                        "This will throw an error"
                    </CodeText>
                    ;<br />
                    {"}"}
                </CodeBlock>
            </div>
        </section>
    );
};

export default LoadTick;
